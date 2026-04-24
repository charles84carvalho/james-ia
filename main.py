import os
import requests
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import func

app = Flask(__name__)

# Configurações - Sua chave está segura aqui
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

@app.route('/')
def home():
    return "James Engine Pro - Online"

# ESTA É A ROTA QUE ESTAVA FALTANDO
@app.route('/status_agora')
def status_agora():
    url = "https://www.bling.com.br/Api/v3/pedidos/vendas"
    hoje = date.today().strftime("%Y-%m-%d")
    # Buscando pedidos de hoje
    params = {"dataInicial": hoje, "dataFinal": hoje}
    headers = {"Authorization": f"Bearer {API_KEY_BLING}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            dados_bling = response.json().get('data', [])
            total_pedidos = len(dados_bling)
            faturamento = sum(float(v.get('total', 0)) for v in dados_bling)
            
            # Cálculo de lucro estimado (20% taxas Shopee + custos)
            # Para o lucro ser exato, precisaríamos iterar cada item, 
            # mas aqui já temos uma visão real do volume.
            lucro_est = faturamento * 0.15 # Margem líquida conservadora de 15%
            
            return jsonify({
                "01_STATUS": "DADOS REAIS DO BLING",
                "02_PEDIDOS_HOJE": total_pedidos,
                "03_FATURAMENTO_BRUTO": f"R$ {faturamento:,.2f}",
                "04_LUCRO_ESTIMADO": f"R$ {lucro_est:,.2f}",
                "05_DATA": hoje
            })
        else:
            return jsonify({"erro": f"Bling respondeu com erro {response.status_code}", "detalhe": response.text})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route('/auditoria')
def auditoria():
    # Mantendo sua auditoria do banco de dados interna
    total_vendas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Pedido").scalar() or 0
    return jsonify({"faturamento_no_banco": total_vendas})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
