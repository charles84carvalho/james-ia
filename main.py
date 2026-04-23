import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_nf = db.Column(db.String(50))
    valor = db.Column(db.Float)
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Monitoramento Ativo"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Esta parte agora tenta ler o JSON do Bling de forma mais inteligente
    data = request.get_json(silent=True) or request.form.to_dict()
    
    # Criamos um registro genérico só para confirmar que a conexão funciona
    nova_venda = Venda(numero_nf="Teste-Conexão", valor=0.0)
    db.session.add(nova_venda)
    db.session.commit()
    
    print(f"Dados recebidos: {data}") # Isso aparecerá nos seus logs do Railway
    return jsonify({"status": "recebido"}), 200

@app.route('/auditoria')
def auditoria():
    total = Venda.query.count()
    return jsonify({"total_no_banco": total, "status": "online"})
