import os
import requests

class JamesIA:
    def __init__(self):
        self.nome = "James"
        # Buscando a chave com um comando que ignora espaços extras
        self.api_key = os.getenv('BLING_API_KEY', '').strip()

    def status_do_sistema(self):
        print(f"--- {self.nome} Relatando ---")
        
        if not self.api_key:
            return "Senhor, a variável 'BLING_API_KEY' está vazia ou não foi criada no Railway."
        
        # Mostra apenas os 4 primeiros dígitos da chave para segurança, confirmando que ela existe
        print(f"Chave detectada (Início): {self.api_key[:4]}...")
        
        # Teste real de conexão
        url = "https://bling.com.br/Api/v2/produtos/json/"
        params = {'apikey': self.api_key}
        
        try:
            res = requests.get(url, params=params)
            if res.status_code == 200:
                return "SUCESSO: Conexão total com o Bling estabelecida!"
            elif res.status_code == 401:
                return "ERRO: A chave API foi encontrada, mas o Bling diz que ela é inválida."
            else:
                return f"ERRO: O Bling respondeu com status {res.status_code}."
        except Exception as e:
            return f"ERRO TÉCNICO: {e}"

if __name__ == "__main__":
    james = JamesIA()
    print(james.status_do_sistema())
