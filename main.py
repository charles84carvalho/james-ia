import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')

def get_access_token():
    """Tenta obter o token. Se falhar, retorna None"""
    url = "https://www.bling.com.br/Api/v3/oauth/token"
    try:
        # Usando Client Credentials para acesso rápido a dados de contatos
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=5)
        return response.json().get('access_token')
    except:
        return None

def buscar_nome_contato(contato_id):
    if not contato_id: return "ID não informado"
    token = get_access_token()
    if not token: return f"Sem Token (ID: {contato_id})"
    
    url = f"https://www.bling.com.br/Api/v3/contatos/{contato_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get('data', {}).get('nome', "Nome não encontrado")
    except:
        pass
    return f"Erro API (ID: {contato_id})"

@app.route('/')
def home():
    return "James Online - Vigilante"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json()
        if not dados: return jsonify({"error": "No data"}), 400
        
        info = dados.get('data', {})
        pedido_n = info.get('numero', 'S/N')
        contato_id = info.get('contato', {}).get('id')
        
        # Tentamos buscar o nome, mas se falhar, o código continua
        nome_cliente = buscar_nome_contato(contato_id)
        
        print(f"--- EVENTO RECEBIDO ---")
        print(f"PEDIDO: {pedido_n} | CLIENTE: {nome_cliente}")
        
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"ERRO NO WEBHOOK: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
