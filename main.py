import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# Configuração da conexão com o Banco de Dados (PostgreSQL)
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Estrutura do Banco de Dados
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

# Criar o banco se não existir (Sem apagar os dados antigos)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Monitoramento Comercial Completo"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # Busca o nome do cliente e valor
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or ""
        valor_venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        # Filtro de ruído: Ignora se o valor for insignificante ou zerado
        if valor_venda <= 0.1:
            return jsonify({"status": "ignorado"}), 200

        # Define se é Nota Fiscal ou Pedido
        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', info.get('numeroPedido', '-'))),
            valor=valor_venda,
            cliente=str(cliente_nome)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception:
        return jsonify({"status": "erro"}), 500

@app.route('/auditoria')
def auditoria():
    try:
        # A MÁGICA: Soma TODO o histórico do banco de dados
        total_pedidos = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_notas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Nota Fiscal").scalar() or 0
        
        count_pedidos = Registro.query.filter(Registro.tipo == "Pedido").count()
        count_notas = Registro.query.filter(Registro.tipo == "Nota Fiscal").count()

        # Lista apenas as últimas 20 para conferência rápida na tela
        ultimos = Registro.query.order_by(Registro.id.desc()).limit(20).all()
        lista = []
        for r in ultimos:
            lista.append({
                "cliente": r.cliente if r.cliente else "N/A",
                "pedido": r.numero,
                "valor": f"R$ {r.valor:,.2f}",
                "tipo": r.tipo,
                "hora": r.data_registro.strftime('%H:%M')
            })

        return jsonify({
            "TOTAL_GERAL_PEDIDOS": f"R$ {total_pedidos:,.2f}",
            "QTD_PEDIDOS_ACUMULADOS": count_pedidos,
            "TOTAL_GERAL_NOTAS": f"R$ {total_notas:,.2f}",
            "QTD_NOTAS_EMITIDAS": count_notas,
            "TICKET_MEDIO": f"R$ {(total_pedidos/count_pedidos if count_pedidos > 0 else 0):,.2f}",
            "ULTIMAS_20_OPERACOES": lista
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
