import os
import requests

class JamesIA:
    def __init__(self):
        self.api_key = os.getenv('BLING_API_KEY', '').strip()

    def testar_duas_portas(self):
        if not self.api_key: return "Chave não encontrada."
        
        # Teste 1: Porta V2
        url_v2 = f"https://bling.com.br/Api/v2/produtos/json/?apikey={self.api_key}"
        res_v2 = requests.get(url_v2)
        
        if res_v2.status_code == 200:
            return "✅ SUCESSO! Conectado via API V2."
        
        # Teste 2: Porta V3 (Usando a chave como Bearer Token)
        url_v3 = "https://www.bling.com.br/Api/v3/produtos"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        res_v3 = requests.get(url_v3, headers=headers)
        
        if res_v3.status_code == 200:
            return "✅ SUCESSO! Conectado via API V3."
            
        return f"❌ Ambas falharam. V2 deu {res_v2.status_code} e V3 deu {res_v3.status_code}."

if __name__ == "__main__":
    james = JamesIA()
    print(james.testar_duas_portas())
