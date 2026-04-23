import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Credenciais do James
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
API_KEY_V2 = os.getenv('BLING_API_KEY') # A chave que geramos hoje

def get_access_token():
    url = "https://www.bling.com.br/Api/v3/oauth/token"
    try:
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=5)
        return response.json().get('access_token')
    except:
        return None

# NOVA FUNÇÃO: O James agora consulta notas de forma ativa e certeira
@app.route('/consultar_nota/<numero>', methods=['GET'])
def consultar_nota(numero):
    if not API_KEY_V2:
        return jsonify({"erro": "Chave API_KEY_V2 não configurada no Railway"}), 500
    
    url = f"https://bling.com.br/Api/v2/notafiscal/{numero}/json/"
    params = {'apikey': API_KEY_V2}
    
    try:
        res = requests.get(url, params=params, timeout=10)
        dados = res.json()
        
        if 'notafiscais' in dados.get('retorno', {}):
            nf = dados['retorno']['notafiscais'][0]['notafiscal']
            return jsonify({
                "status": "sucesso",
                "numero": nf['numero'],
                "valor": nf['valorNota'],
                "cliente": nf['cliente']['nome'],
                "situacao": nf['situacao']
            })
        return jsonify({"status": "nao_encontrado", "msg": "Nota ainda não consta no Bling"}), 404
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/')
def home():
    return "James Online - Vigilante com Consulta Ativa"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Mantém sua função de receber alertas de novos pedidos
    try:
        dados = request.get_json()
        if not dados: return jsonify({"error": "No data"}), 400
        print(f"--- SINAL RECEBIDO: {datetime.now().strftime('%H:%M:%S')} ---")
        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
