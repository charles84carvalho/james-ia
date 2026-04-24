import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mantivemos 'valor' para ser compatível com seu banco atual, mas adicionamos 'custo' e 'lucro'
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0) # Nome original mantido
    custo = db.Column(db.Float, default=0.0) # Nova coluna
    lucro = db.Column(db.Float, default=0.0) # Nova coluna
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Monitoramento de Lucro"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or "Cliente"
        venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        if venda <= 0.1:
            return jsonify({"status": "ignorado"}), 200

        # Lógica de lucro: Descontando 20% de taxas Shopee + Custo do Bling
        valor_custo = float(info.get('valorCusto') or info.get('custo') or 0.0)
        taxas = venda * 0.20
        valor_lucro = venda - valor_custo - taxas

        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', '-')),
            valor=venda,
            custo=valor_custo,
            lucro=valor_lucro,
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
        # Soma usando os nomes de coluna compatíveis
        total_vendas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_lucro = db.session.query(func.sum(Registro.lucro)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_notas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Nota Fiscal").scalar() or 0
        count_pedidos = Registro.query.filter(Registro.tipo == "Pedido").count()

        margem_percentual = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

        ultimos = Registro.query.order_by(Registro.id.desc()).limit(15).all()
        lista = [{"id": r.numero, "venda": f"R$ {r.valor:,.2f}", "lucro": f"R$ {r.lucro:,.2f}", "tipo": r.tipo, "hora": r.data_registro.strftime('%H:%M')} for r in ultimos]

        return jsonify({
            "01_FATURAMENTO_BRUTO_PEDIDOS": f"R$ {total_vendas:,.2f}",
            "02_LUCRO_LIQUIDO_ESTIMADO": f"R$ {total_lucro:,.2f}",
            "03_MARGEM_PERCENTUAL": f"{margem_percentual:.2f}%",
            "04_FATURAMENTO_NOTAS": f"R$ {total_notas:,.2f}",
            "05_TOTAL_PEDIDOS": count_pedidos,
            "ULTIMAS_OPERACOES": lista
        })
    except Exception as e:
        return jsonify({"erro_tecnico": "O banco precisa ser atualizado para as novas colunas de lucro. Se este erro persistir, me avise."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
