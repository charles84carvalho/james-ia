import os
import requests

class JamesIA:
    def __init__(self):
        self.nome = "James"
        self.custo_fixo_mensal = 8000.00
        self.imposto_percentual = 0.05
        # O James busca a chave que o senhor salvou no Railway
        self.api_key = os.getenv('BLING_API_KEY')

    def testar_conexao_bling(self):
        if not self.api_key:
            return "Senhor, não encontrei a chave API nas configurações do Railway."
        
        # Testando a conexão com a API do Bling
        url = "https://bling.com.br/Api/v2/produtos/json/"
        params = {'apikey': self.api_key}
        
        try:
            resposta = requests.get(url, params=params)
            if resposta.status_code == 200:
                return "Conexão com o Bling estabelecida com sucesso! Já consigo enxergar seus dados, senhor."
            else:
                return f"Senhor, o Bling respondeu com um erro. Status: {resposta.status_code}"
        except Exception as e:
            return f"Houve um erro técnico na tentativa de conexão: {e}"

if __name__ == "__main__":
    mordomo = JamesIA()
    print(f"--- Sistema {mordomo.nome} Online ---")
    print(mordomo.testar_conexao_bling())
