import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Configurações vindas do seu Railway
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
REDIRECT_URI = "https://james-ia-production.up.railway.app/callback"

@app.route('/')
def home():
    # Link que o senhor vai clicar uma única vez para autorizar o James
    auth_url = (
        f"https://www.bling.com.br/Api/v3/oauth/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )
    return f'<h1>James IA</h1><p>Senhor, por favor, <a href="{auth_url}">clique aqui para me autorizar</a> no seu Bling.</p>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Erro: Código de autorização não recebido.", 400

    # Troca o código pelo Token Real
    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return "✅ SUCESSO, SENHOR! O James agora tem acesso total ao seu Bling. Pode fechar esta aba."
    else:
        return f"Erro na autorização: {response.text}", 400

if __name__ == "__main__":
    # O Railway usa a porta que ele mesmo define
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
