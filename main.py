from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup


url_base = 'https://lista.mercadolivre.com.br/'
produto_nome = input('Buscar produto: ')
response = requests.get(url_base + produto_nome)


# Define os escopos necessários para acessar a API do Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ID e intervalo da planilha
SAMPLE_SPREADSHEET_ID = "1ns87fsrOGXw755udA-nL9L4X8awcU606IafyG1UJBDg"
SAMPLE_RANGE_NAME = "Página3!A1:B10"

# Caminho para o arquivo de credenciais da conta de serviço
SERVICE_ACCOUNT_FILE = "credentials.json"


def main():
    # Autentica com as credenciais da conta de serviço
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        # Constrói o serviço para acessar a API do Google Sheets
        service = build("sheets", "v4", credentials=creds)

        # Chamando a API do Google Sheets para buscar os dados

        # lendo os dados
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        
        values = result.get("values", [])

        if not values:
            print("Nenhum dado encontrado.")
            return

        # Imprime os dados retornados da planilha
        # print(result)

        # Adicionando novos dados (sem sobrescrever)
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            site = BeautifulSoup(response.text, 'html.parser')

            # Ajustando o seletor para obter a lista de resultados
            produtos = site.find_all('div', attrs={'class': 'ui-search-result__wrapper'})

            if produtos:
                print(f'Foram encontrados {len(produtos)} produtos:')
                for i, produto in enumerate(produtos[:5]):  # Exibe os 5 primeiros produtos
                    titulo = produto.find('h2', attrs={'class': 'poly-component__title-wrapper'})
                    preco = produto.find('span', attrs={'class': 'andes-money-amount andes-money-amount--cents-superscript'})
                    
                    if titulo and preco:
                        print(f"{i+1}. {titulo.text.strip()} - {preco.text.strip()}")
                        valores_adicionar = [[titulo.text, preco.text]]
                        result = (
                            sheet.values()
                            .append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Página3!A1", 
                                    valueInputOption="USER_ENTERED",
                                    body={'values': valores_adicionar})
                            .execute()
                        )
                    else:
                        print(f"{i+1}. Detalhes do produto não disponíveis.")
                print('Dados adicionados com sucesso!')
            else:
                print('Nenhum produto encontrado.')
        else:
            print(f'Erro ao acessar o site: {response.status_code}')

        

    except Exception as err:
        print(f"Erro ao acessar a API do Google Sheets: {err}")


if __name__ == "__main__":
    main()
