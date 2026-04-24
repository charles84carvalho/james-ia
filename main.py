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
    status = db.Column(db.String(100))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    conteudo_bruto = db.Column(db.Text)

with app.app_context():
    # Removido o drop_all para preservar seus dados daqui em diante
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Inteligência Ativa"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        
        # O Bling v3 costuma enviar os dados dentro de 'data'
        info = dados.get('data', {})
        
        # Identifica se é Nota ou Pedido pelo conteúdo
        corpo_str = json.dumps(dados).lower()
        
        if 'notafiscal' in corpo_str:
            tipo = "Nota Fiscal"
            numero = info.get('numero', '-')
            valor = float(info.get('valor', 0.0))
            cliente = info.get('contato', {}).get('nome', 'Cliente NF')
        else:
            tipo = "Pedido"
            numero = info.get('numero', '-')
            # No Bling v3 de vendas, o valor pode estar em 'total'
            valor = float(info.get('total', 0.0) or info.get('totalVenda', 0.0))
            cliente = info.get('contato', {}).get('nome', 'Cliente Pedido')

        novo = Registro(
            tipo=tipo,
            numero=str(numero),
            valor=valor,
            cliente=cliente,
            status="Processado",
            conteudo_bruto=json.dumps(dados)
        )
        db.session.add(novo)
        db.session.commit()
        
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/auditoria')
def auditoria():
    try:
        registros = Registro.query.order_by(Registro.id.desc()).limit(20).all()
        lista = []
        for r in registros:
            lista.append({
                "id": r.id,
                "tipo": r.tipo,
                "numero": r.numero,
                "cliente": r.cliente,
                "valor": f"R$ {r.valor:,.2f}",
                "data": r.data_registro.strftime('%H:%M')
            })
            
        return jsonify({
            "total_acumulado": Registro.query.count(),
            "ultimas_operacoes": lista
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
