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
    return "James Pro SaaS - Monitoramento de Pedidos Reais"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # 1. Extração de Identidade e Valor
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or ""
        valor_venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        # 2. O FILTRO DE RUÍDO (A inteligência do James)
        # Ignora se o valor for zero ou se o nome contiver asteriscos ou for genérico
        if valor_venda <= 0 or "*" in cliente_nome or not cliente_nome or "Cliente" in cliente_nome:
            return jsonify({"status": "ignorado", "motivo": "ruido ou sem dados reais"}), 200

        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido em Aberto"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', info.get('numeroPedido', '-'))),
            valor=valor_venda,
            cliente=str(cliente_nome)
        )
        db.session.add(novo)
        db.session.commit()
        
        return jsonify({"status": "sucesso", "tipo": tipo}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/auditoria')
def auditoria():
    # Mostra apenas os últimos 50 pedidos reais e limpos
    registros = Registro.query.order_by(Registro.id.desc()).limit(50).all()
    lista = []
    total_em_aberto = 0.0
    
    for r in registros:
        lista.append({
            "id": r.id,
            "tipo": r.tipo,
            "pedido": r.numero,
            "cliente": r.cliente,
            "valor": f"R$ {r.valor:,.2f}",
            "hora": r.data_registro.strftime('%H:%M')
        })
        if r.tipo == "Pedido em Aberto":
            total_em_aberto += r.valor
            
    return jsonify({
        "mensage": "Senhor, aqui estão seus pedidos limpos e reais.",
        "faturamento_pendente_recente": f"R$ {total_em_aberto:,.2f}",
        "lista_de_vendas": lista
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
