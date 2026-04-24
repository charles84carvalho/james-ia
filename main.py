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

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Filtro Inteligente Ativado"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # Extração
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or ""
        valor_venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        # FILTRO RÍGIDO: Ignora R$ 0, asteriscos ou se o nome for apenas "Cliente"
        if valor_venda <= 0.1 or "*" in cliente_nome or cliente_nome.strip() in ["", "Cliente", "Cliente Pedido"]:
            return jsonify({"status": "ignorado", "motivo": "ruido"}), 200

        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido em Aberto"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', info.get('numeroPedido', '-'))),
            valor=valor_venda,
            cliente=str(cliente_nome)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/auditoria')
def auditoria():
    # Buscamos apenas o que tem valor e nome real
    registros = Registro.query.filter(Registro.valor > 0).order_by(Registro.id.desc()).limit(50).all()
    
    lista = []
    soma_aberto = 0.0
    
    for r in registros:
        lista.append({
            "cliente": r.cliente,
            "valor": f"R$ {r.valor:,.2f}",
            "tipo": r.tipo,
            "pedido": r.numero,
            "hora": r.data_registro.strftime('%H:%M')
        })
        if r.tipo == "Pedido em Aberto":
            soma_aberto += r.valor
            
    return jsonify({
        "status_geral": "Lista de Vendas Reais e Limpas",
        "faturamento_pendente_estimado": f"R$ {soma_aberto:,.2f}",
        "pedidos": lista
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
