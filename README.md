# GoosleAdsScraper

GoogleAdsScraper é uma ferramenta desenvolvida em Python para coletar e analisar anúncios de transparência publicados no Google. Ele utiliza o Selenium WebDriver para navegar automaticamente nas páginas e extrair informações relevantes sobre anúncios de empresas específicas.

## Funcionalidades

- **Coleta de anúncios por trimestre**: Busca anúncios de uma empresa para períodos específicos.
- **Detalhamento de anúncios**: Acessa cada link coletado e extrai informações detalhadas.
- **Geração de relatórios em JSON**: Exporta os dados coletados em arquivos organizados por trimestre.
- **Logs detalhados**: Registra todas as ações e erros para facilitar o monitoramento e depuração.

## Requisitos

- Python 3.8 ou superior
- Google Chrome instalado
- ChromeDriver compatível com a versão do Google Chrome
- Dependências Python (instaláveis via `pip`):
  - selenium

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/odoricoveloso/GoogleAdsScraper.git
   cd GoogleAdsScraper
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Certifique-se de que o ChromeDriver esteja no PATH ou configure seu local.

## Uso

1. Execute o script principal:
   ```bash
   python GoogleAdsScraper.py
   ```

2. Insira as informações solicitadas:
   - Nome da empresa
   - Quantidade de anúncios desejados por trimestre
   - Ano de interesse

3. Os resultados serão salvos como arquivos JSON na mesma pasta do script.

## Estrutura do Projeto

- `GoogleAdsScraper.py`: Script principal contendo toda a lógica de coleta e análise de anúncios.
- `GoogleAdsScraper.log`: Arquivo de log gerado durante a execução do script (se necessário).
- `links_anuncios_{empresa}.json`: Arquivo contendo os links dos anúncios coletados.
- `anuncios_detalhados_{trimestre}_{empresa}.json`: Arquivos com detalhes dos anúncios coletados.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Observações

- Certifique-se de que sua conexão com a internet seja estável durante a execução.
- Dependendo da quantidade de anúncios solicitada, o processo pode demorar.
- Se houver alterações na interface do site do Google Ads Transparency, o script pode necessitar de ajustes.

