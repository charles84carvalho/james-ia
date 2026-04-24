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

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    conteudo_bruto = db.Column(db.Text)

with app.app_context():
    db.create_all() # Sem drop_all agora: seus dados estão protegidos

@app.route('/')
def home():
    return "James Pro SaaS - Monitoramento Real-Time"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # Busca profunda pelo nome do cliente
        cliente = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or "Cliente"
        
        # Busca profunda pelo valor (tenta vários campos possíveis do Bling v3)
        valor_bruto = info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0
        
        # Identificação do Tipo
        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', info.get('numeroPedido', '-'))),
            valor=float(valor_bruto),
            cliente=str(cliente),
            conteudo_bruto=json.dumps(dados)
        )
        db.session.add(novo)
        db.session.commit()
        
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/auditoria')
def auditoria():
    registros = Registro.query.order_by(Registro.id.desc()).limit(20).all()
    lista = []
    for r in registros:
        lista.append({
            "id": r.id,
            "tipo": r.tipo,
            "numero": r.numero,
            "cliente": r.cliente,
            "valor": f"R$ {r.valor:,.2f}",
            "hora": r.data_registro.strftime('%H:%M')
        })
    return jsonify({"registros_totais": Registro.query.count(), "ultimas_vendas": lista})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
