import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
REDIRECT_URI = "https://james-ia-production.up.railway.app/callback"

def get_access_token():
    url = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {"grant_type": "client_credentials"}
    try:
        response = requests.post(url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
        return response.json().get('access_token')
    except:
        return None

def buscar_nome_contato(contato_id):
    token = get_access_token()
    if not token or not contato_id: return "Desconhecido"
    url = f"https://www.bling.com.br/Api/v3/contatos/{contato_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('data', {}).get('nome', "Desconhecido")
    except: pass
    return "Erro na busca"

@app.route('/')
def home():
    return "<h1>James IA: Sistema de Monitoramento Ativo</h1>"

@app.route('/callback')
def callback():
    return "<h1>Conexão Atualizada</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json()
        evento = dados.get('event', '')
        info = dados.get('data', {})
        
        # Filtro: Só processar se houver um número de pedido e não for teste
        pedido_n = info.get('numero')
        contato_id = info.get('contato', {}).get('id')
        loja_id = info.get('loja', {}).get('id')
        
        nome_cliente = buscar_nome_contato(contato_id)
        
        # Se o nome for o seu, Charles, eu apenas registro no log interno
        if "Charles" in nome_cliente:
            print(f"--- ATIVIDADE DO ADMINISTRADOR (CHARLES) DETECTADA ---")
        else:
            print(f"--- NOVO PEDIDO REAL ---")
            print(f"Cliente: {nome_cliente} | Pedido: {pedido_n} | Loja: {loja_id}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
