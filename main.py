import os
import requests
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import func

app = Flask(__name__)

# Configurações
API_KEY_BLING = "83b5b0a291f5d7951f9d4cb90383879abf49a1837dc9203a22c58b235836b3e42494d80f"
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    custo = db.Column(db.Float, default=0.0)
    lucro = db.Column(db.Float, default=0.0)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def buscar_vendas_direto_bling():
    """Consulta o Bling via API para pegar pedidos de hoje"""
    url = "https://www.bling.com.br/Api/v3/pedidos/vendas"
    hoje = date.today().strftime("%Y-%m-%d")
    params = {"dataInicial": hoje, "dataFinal": hoje}
    headers = {"Authorization": f"Bearer {API_KEY_BLING}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        print(f"Erro ao consultar Bling: {e}")
    return []

@app.route('/')
def home():
    return "James Pro - Conectado ao Bling"

@app.route('/status_agora')
def status_agora():
    vendas = buscar_vendas_direto_bling()
    total_pedidos = len(vendas)
    faturamento = sum(float(v.get('total', 0)) for v in vendas)
    
    return jsonify({
        "status": "Conexão Direta Ativa",
        "pedidos_hoje_no_bling": total_pedidos,
        "faturamento_bruto_atual": f"R$ {faturamento:,.2f}",
        "aviso": "Senhor, estes dados foram puxados agora diretamente do seu Bling."
    })

# Mantendo o Webhook para registrar no banco histórico
@app.route('/webhook', methods=['POST'])
def webhook():
    # ... (lógica anterior de recebimento automático) ...
    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
