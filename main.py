import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações do Railway
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
REDIRECT_URI = "https://james-ia-production.up.railway.app/callback"

def get_access_token():
    """Função para obter um token válido via Client Credentials (ou Refresh)"""
    url = "https://www.bling.com.br/Api/v3/oauth/token"
    auth = (CLIENT_ID, CLIENT_SECRET)
    data = {"grant_type": "client_credentials"} # Para consultas rápidas de cadastro
    try:
        response = requests.post(url, data=data, auth=auth)
        return response.json().get('access_token')
    except:
        return None

def buscar_nome_contato(contato_id):
    """Consulta o nome do cliente no Bling usando o ID"""
    token = get_access_token()
    if not token or not contato_id:
        return "Nome não identificado"
    
    url = f"https://www.bling.com.br/Api/v3/contatos/{contato_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            dados = res.json()
            return dados.get('data', {}).get('nome', "Nome não encontrado")
    except:
        pass
    return "Erro ao buscar nome"

@app.route('/')
def home():
    auth_url = f"https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=james_ia_security"
    return f'<h1>James IA: Online</h1><p><a href="{auth_url}">AUTORIZAR ACESSO</a></p>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI}
    response = requests.post(token_url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    return "<h1>✅ AUTORIZADO!</h1>" if response.status_code == 200 else "<h1>Erro na Autorização</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json()
        evento = dados.get('event', '')
        info_data = dados.get('data', {})
        
        # Extração de IDs conforme o tipo de evento
        contato_id = info_data.get('contato', {}).get('id')
        
        # O James agora busca o nome ativamente!
        nome_cliente = buscar_nome_contato(contato_id)
        
        print(f"--- EVENTO: {evento} ---")
        print(f"CLIENTE: {nome_cliente} (ID: {contato_id})")
        print(f"DETALHES: {info_data}")
        
        return jsonify({"status": "processed", "client": nome_cliente}), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
