import os
import time
import json
import random
import logging
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Função para configurar o logger
def configurar_logger(nome_logger, log_filename):
    logger = logging.getLogger(nome_logger)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d_%H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger



# Função para configurar o ChromeDriver
def configurar_chrome_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    return options



# Função para obter as datas de início e fim de cada trimestre de um ano
def obter_datas_trimestres(ano):
    return {
        'Trimestre 1': (date(ano, 1, 1).strftime('%d/%m/%Y'), date(ano, 3, 31).strftime('%d/%m/%Y')),
        'Trimestre 2': (date(ano, 4, 1).strftime('%d/%m/%Y'), date(ano, 6, 30).strftime('%d/%m/%Y')),
        'Trimestre 3': (date(ano, 7, 1).strftime('%d/%m/%Y'), date(ano, 9, 30).strftime('%d/%m/%Y')),
        'Trimestre 4': (date(ano, 10, 1).strftime('%d/%m/%Y'), date(ano, 12, 31).strftime('%d/%m/%Y'))
    }



# Função para salvar os dados em um arquivo JSON
def salvar_json(dados, nome_arquivo):
    with open(os.path.join(os.getcwd(), nome_arquivo), encoding='utf-8', mode='w') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)



#Função para listar os anúncios de uma empresa e salvar os links em um arquivo JSON
def listar_anuncios(empresa, qtd_anuncios_trimestre, ano, logger, chrome_options):
    trimestres = obter_datas_trimestres(ano)
    todos_links_anuncios = {}

    for trimestre, data in trimestres.items():
        data_inicio = data[0]
        data_fim = data[1]

        logger.info(f'Coletando anúncios do {trimestre} ({data_inicio} a {data_fim}) de {ano} para {empresa}.')

        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://adstransparency.google.com/?region=BR'
        driver.get(url)
        time.sleep(3)

        # Seleciona o intervalo de datas para cada trimestre
        try:
            botao_datas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "date-range-filter[class^='side-scrollable'] div[class^='popup-button']"))
            )
            driver.execute_script('arguments[0].click();', botao_datas)
            time.sleep(3)

            campo_data_inicio = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "material-input[class^='start date-input'] input[type='text']"))
            )
            campo_data_inicio.clear()
            campo_data_inicio.send_keys(data_inicio)
            campo_data_inicio.send_keys(Keys.ENTER)
            time.sleep(2)

            campo_data_fim = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "material-input[class^='end date-input'] input[type='text']"))
            )
            campo_data_fim.clear()
            campo_data_fim.send_keys(data_fim)
            campo_data_fim.send_keys(Keys.ENTER)
            time.sleep(2)
            
            botao_ok = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='apply-section'] material-button[aria-label^='Aplicar']"))
            )
            driver.execute_script('arguments[0].click();', botao_ok)
            time.sleep(3)
            
        except Exception as e:
            logger.error(f'Erro ao selecionar datas: {e}')
            return None

        # Localiza o campo de pesquisa e insere o nome da empresa
        try:
            search_box = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            search_box.clear()
            search_box.send_keys(empresa)
            time.sleep(3)

            sugestao_busca = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'search-suggestion-renderer'))
            )

            if empresa in sugestao_busca.text:
                driver.execute_script('arguments[0].click();', sugestao_busca)

            time.sleep(3)

            # Filtrar somente anúncios no formato texto
            try:
                botao_formato = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "creative-type-filter[class^='creative-type-filter'] div[class^='popup-button']"))
                )
                driver.execute_script('arguments[0].click();', botao_formato)
            except Exception as e:
                logger.error(f'Erro ao encontrar botão de formato: {e}')

            try:
                selecao_texto = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='Formato de Texto']"))
                )
                driver.execute_script('arguments[0].click();', selecao_texto)
            except Exception as e:
                logger.error(f'Erro ao selecionar formato de texto: {e}')

            time.sleep(3)
            driver.execute_script('document.body.click();')

        except Exception as e:
            logger.error(f'Erro ao acessar a central de transparência: {e}')
            return None

        # Carrega os anúncios na página  
        try:
            preview_anuncios = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'creative-preview'))
            )
            while len(preview_anuncios) < qtd_anuncios_trimestre:
                driver.execute_script('window.scrollTo(0, 0);')
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(3)
                preview_anuncios = driver.find_elements(By.TAG_NAME, 'creative-preview')
                logger.info(f'Encontrados {len(preview_anuncios)} anúncios. Carregando mais...')
            logger.info(f'Encontrados {len(preview_anuncios)} anúncios. Finalizando carregamento.')
        except Exception as e:
            logger.error(f'Erro ao encontrar anúncios: {e}')
            return None

        # Coleta os links dos anúncios
        try:
            lista_links_anuncios = {}
            for anuncio in preview_anuncios:
                link_anuncio = anuncio.find_element(By.TAG_NAME, 'a').get_attribute('href')
                contagem_anuncio = anuncio.find_element(By.TAG_NAME, 'a').get_attribute('aria-label')
                lista_links_anuncios[contagem_anuncio] = link_anuncio
            logger.info(f'Coletados {len(lista_links_anuncios)} links de anúncios.')
            driver.quit()

            todos_links_anuncios[trimestre] = lista_links_anuncios

        except Exception as e:
            logger.error(f'Erro ao coletar links de anúncios: {e}')
            return None

    salvar_json(todos_links_anuncios, f'links_anuncios_{empresa}.json')
    logger.info('Arquivo com links de anúncios salvo.')

    return todos_links_anuncios

# Função para coletar os dados detalhados dos anúncios e salvar em um arquivo JSON
def coletar_anuncios(todos_links_anuncios, empresa, logger, chrome_options):
    lista_anuncios = {}
    for trimestre, links_anuncios in todos_links_anuncios.items():
        driver = webdriver.Chrome(options=chrome_options)
        lista_anuncios = {}
        
        for contagem, link in links_anuncios.items():
            try:
                logger.info(f'Acessando {contagem} em {link}')
                driver.get(link)
                time.sleep(3)
                
                while 'Error' in driver.title:
                    time.sleep(random.randint(5, 10))
                    driver.refresh()
                    time.sleep(3)
                
                try:
                    creative_details = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'creative-details'))
                    )
                    numero_creative_details = creative_details.get_attribute('class').split('-')[-1]
                    anuncio = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"div[class^='content _ngcontent'][class$='{numero_creative_details}']"))
                    )
                except Exception as e:
                    logger.error(f'Erro ao encontrar anúncio {contagem}: {e}')
                
                if anuncio:
                    try:
                        iframe = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='html-container'] iframe"))
                        )
                    except:
                        iframe = None
                    
                    i = 0
                    while not iframe and i < 3:
                        time.sleep(random.randint(5, 10))
                        driver.refresh()
                        time.sleep(5)
                        try:
                            iframe = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='html-container'] iframe"))
                            )
                        except:
                            iframe = None
                        i += 1
                    
                    driver.switch_to.frame(iframe)
                    texto = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-text-ad='1']"))
                    ).text.strip()
                    
                    site_anunciante = texto.split('\n')[-3]
                    titulo_anuncio = texto.split('\n')[-2]
                    texto_anuncio = texto.split('\n')[-1]
                    
                    driver.switch_to.default_content()
                    
                    anunciante = anuncio.find_element(By.TAG_NAME, 'a').text.strip()
                    ultima_exibicao = anuncio.find_element(By.CSS_SELECTOR, "div[class*='last-shown']").text.strip()

                    lista_anuncios[contagem] = {
                        'anunciante': anunciante,
                        'ultima_exibicao': ultima_exibicao,
                        'site_anunciante': site_anunciante,
                        'titulo_anuncio': titulo_anuncio,
                        'texto_anuncio': texto_anuncio
                    }
                
                logger.info(f'{contagem} coletado.')
                time.sleep(random.randint(5, 10))
                
            except Exception as e:
                logger.error(f'Erro ao coletar anúncio {contagem}: {e}')

        driver.close()
        
        salvar_json(lista_anuncios, f'anuncios_detalhados_{trimestre}_{empresa}.json')
        logger.info(f'Arquivo com anúncios do {trimestre} salvo.')
            
    logger.info('Fim da execução.')


# Execução do script
if __name__ == '__main__':
    
    logger = configurar_logger('meu_logger', os.path.join(os.getcwd(), 'GoogleAdsScraper.log'))
    chrome_options = configurar_chrome_driver()
    
    empresa = input('Digite o nome da empresa: ')
    quantidade_anuncios_trimestre = int(input('Digite a quantidade de anúncios por trimestre: '))
    ano = int(input('Digite o ano: '))

    links_anuncios = listar_anuncios(empresa, quantidade_anuncios_trimestre, ano, logger, chrome_options)
    coletar_anuncios(links_anuncios, empresa, logger, chrome_options)
