import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração da URL do Banco
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Tabela simplificada para o teste de pulso
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.Text) # Guardaremos o dado bruto aqui para não dar erro
    data = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Sistema Online"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Registra qualquer sinal que chegar
        nova_venda = Venda(info="Sinal Recebido do Bling")
        db.session.add(nova_venda)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except:
        return jsonify({"status": "erro interno"}), 500

@app.route('/auditoria')
def auditoria():
    try:
        total = Venda.query.count()
        return jsonify({"total_no_banco": total, "status": "operacional"})
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
