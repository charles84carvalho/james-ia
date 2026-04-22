import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações extraídas das variáveis de ambiente do Railway
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
REDIRECT_URI = "https://james-ia-production.up.railway.app/callback"

@app.route('/')
def home():
    auth_url = (
        f"https://www.bling.com.br/Api/v3/oauth/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=james_ia_security"
    )
    return (
        f'<h1>James IA: Sistema Online</h1>'
        f'<p>Senhor, por favor, <a href="{auth_url}" style="font-size: 20px; font-weight: bold; color: blue;">'
        f'CLIQUE AQUI PARA ME AUTORIZAR</a> no seu Bling.</p>'
        f'<hr><p>Status do sistema: Operacional e aguardando Webhooks</p>'
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"Erro reportado pelo Bling: {error}", 400

    if not code:
        return "Erro: Código de autorização não recebido.", 400

    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    auth = (CLIENT_ID, CLIENT_SECRET)
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data, auth=auth)
    
    if response.status_code == 200:
        return (
            "<h1>✅ SUCESSO, SENHOR!</h1>"
            "<p>O James agora está conectado. Pode fechar esta aba.</p>"
        )
    else:
        return f"<h1>Erro na autorização</h1><p>{response.text}</p>"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json()
        print(f"--- WEBHOOK RECEBIDO: {dados} ---")
        # Linha corrigida abaixo:
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
