import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Conexão com o Banco de Dados do Railway
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Tabela onde as vendas serão guardadas
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_nf = db.Column(db.String(50), unique=True)
    valor = db.Column(db.Float)
    cliente = db.Column(db.String(100))
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)

# Cria as tabelas se não existirem
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Sistema de Monitoramento Ativo"

@app.route('/webhook', methods=['POST'])
def webhook():
    # O Bling envia dados aqui. Por enquanto, vamos apenas confirmar o recebimento
    # para testar a conexão do Webhook.
    return jsonify({"status": "recebido"}), 200

@app.route('/auditoria')
def auditoria():
    # Esta é a página que deu "Not Found". Agora ela vai existir!
    total = Venda.query.count()
    ultimas = Venda.query.order_by(Venda.id.desc()).limit(10).all()
    
    vendas_list = []
    for v in ultimas:
        vendas_list.append({"nf": v.numero_nf, "valor": v.valor, "cliente": v.cliente})
        
    return jsonify({
        "mensagem": "Caminho encontrado com sucesso!",
        "total_no_banco": total,
        "ultimas_10": vendas_list
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
