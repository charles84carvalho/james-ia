import os
import requests

class JamesIA:
    def __init__(self):
        self.nome = "James"
        # Tentativa 1: Nome padrão
        self.api_key = os.environ.get('BLING_API_KEY')
        
    def investigar(self):
        print(f"--- {self.nome}: Diagnóstico de Variáveis ---")
        
        # Lista as chaves disponíveis no sistema (sem mostrar os valores por segurança)
        chaves_encontradas = list(os.environ.keys())
        print(f"Variáveis que eu consigo ler: {chaves_encontradas}")
        
        if not self.api_key:
            return "❌ Senhor, a chave BLING_API_KEY ainda não aparece no meu sistema."
        
        # Se achou, tenta conectar
        print(f"✅ Chave encontrada! Iniciando conexão com o Bling...")
        url = f"https://bling.com.br/Api/v2/produtos/json/?apikey={self.api_key.strip()}"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return "🚀 SUCESSO: James está conectado ao Bling!"
            else:
                return f"⚠️ Erro no Bling: Status {res.status_code}"
        except Exception as e:
            return f"❌ Erro técnico: {e}"

if __name__ == "__main__":
    james = JamesIA()
    print(james.investigar())
