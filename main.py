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
    # Parâmetro 'state' para segurança do Bling
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
        return f"Erro reportado pelo Bling: {error}. Senhor, verifique as credenciais.", 400

    if not code:
        return "Erro: Código de autorização não recebido.", 400

    # Troca o código pelo Token de Acesso
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
            "<p>O James agora está oficialmente conectado à sua conta do Bling.</p>"
            "<p>Pode retornar à nossa conversa para darmos início à análise dos seus pedidos.</p>"
        )
    else:
        return (
            f"<h1>Erro na autorização Final</h1>"
            f"<p>Status: {response.status_code}</p>"
            f"<p>Detalhe: {response.text}</p>"
        )

# --- ROTA DO WEBHOOK: ONDE O ACESSO REAL ACONTECE ---
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Recebe os dados JSON enviados pelo Bling (vendas, notas, etc)
        dados = request.get_json()
        
        # Este print aparecerá nos logs do Railway para confirmarmos a chegada
        print(f"--- WEBHOOK RECEBIDO: {dados} ---")
        
        # Retornamos 200 para o Bling saber que a mensagem foi entregue
        return jsonify({"status": "received
