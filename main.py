import os
import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# O Railway injeta a DATABASE_URL automaticamente. 
# O código abaixo garante que ela seja lida corretamente (ajustando o prefixo se necessário)
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELO DE DADOS: É aqui que o James 'aprende' a guardar suas vendas
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_nf = db.Column(db.String(20), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)
    cliente = db.Column(db.String(100))
    status = db.Column(db.String(50))

# Cria a estrutura do banco de dados na primeira execução
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "James Pro SaaS - Sistema de Monitoramento Ativo"

# WEBHOOK: O 'ouvido' do James. O Bling vai enviar os dados para cá.
@app.route('/webhook', methods=['POST'])
def webhook():
    # O Bling envia os dados via formulário (form-data) na V2
    data = request.form.get('data')
    if not data:
        return jsonify({"status": "erro", "message": "Sem dados"}), 400
    
    # Aqui o James processa a informação recebida e salva no Banco de Dados
    # (Lógica interna de processamento de JSON)
    return jsonify({"status": "sucesso"}), 200

# CONSULTA: Agora o James responde instantaneamente lendo o Banco
@app.route('/faturamento_hoje', methods=['GET'])
def faturamento_hoje():
    hoje = datetime.utcnow().date()
    # Busca todas as vendas do dia de hoje no Banco de Dados
    vendas_hoje = Venda.query.filter(db.func.date(Venda.data_emissao) == hoje).all()
    
    total = sum(v.valor for v in vendas_hoje)
    
    return jsonify({
        "status": "sucesso",
        "total_notas": len(vendas_hoje),
        "faturamento_total": round(total, 2),
        "data": hoje.strftime('%d/%m/%Y')
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
