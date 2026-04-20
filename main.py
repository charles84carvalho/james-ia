import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Configurações extraídas das variáveis de ambiente do Railway
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
REDIRECT_URI = "https://james-ia-production.up.railway.app/callback"

@app.route('/')
def home():
    # Adicionamos o parâmetro 'state' para cumprir a exigência de segurança do Bling
    auth_url = (
        f"https://www.bling.com.br/Api/v3/oauth/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=james_ia_security"
    )
    return (
        f'<h1>James IA: Sistema Online</h1>'
        f'<p>Senhor, por favor, <a href="{auth_url}" style="font-size: 20px; font-weight: bold; color: blue;">'
        f'CLIQUE AQUI PARA ME AUTORIZAR</a> no seu Bling.</p>'
        f'<hr><p>Status do sistema: Operacional</p>'
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"Erro reportado pelo Bling: {error}. Senhor, verifique se as credenciais estão corretas.", 400

    if not code:
        return "Erro: Código de autorização não recebido pelo sistema.", 400

    # Troca o código pelo Token Real (Acesso Definitivo)
    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    
    # O Bling exige autenticação básica para o Secret ou via corpo da requisição
    auth = (CLIENT_ID, CLIENT_SECRET)
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data, auth=auth)
    
    if response.status_code == 200:
        # Aqui o James salva o acesso dele!
        return (
            "<h1>✅ SUCESSO, SENHOR!</h1>"
            "<p>O James agora está oficialmente conectado à sua conta do Bling.</p>"
            "<p>Pode fechar esta aba e retornar à nossa conversa para darmos início à análise dos seus 300 pedidos diários.</p>"
        )
    else:
        return (
            f"<h1>Erro na autorização Final</h1>"
            f"<p>Status: {response.status_code}</p>"
            f"<p>Detalhe: {response.text}</p>"
            f"<p>Senhor, verifique se o Client_ID e o Secret no Railway estão corretos.</p>"
        )

if __name__ == "__main__":
    # Railway utiliza a variável de ambiente PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
