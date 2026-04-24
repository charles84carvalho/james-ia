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

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    custo = db.Column(db.Float, default=0.0)
    lucro = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

# COMANDO DE RESET: Isso vai apagar a tabela antiga e criar a nova com LUCRO
with app.app_context():
    # Descomente a linha abaixo (remova o #) se quiser forçar o reset total
    # db.drop_all() 
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Sistema Reiniciado com Sucesso"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or "Cliente"
        venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        if venda <= 0.1:
            return jsonify({"status": "ignorado"}), 200

        # Cálculo: 20% Shopee + Custo
        valor_custo = float(info.get('valorCusto') or info.get('custo') or 0.0)
        valor_lucro = venda - valor_custo - (venda * 0.20)

        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido"
        
        novo = Registro(tipo=tipo, numero=str(info.get('numero', '-')), valor=venda, custo=valor_custo, lucro=valor_lucro, cliente=str(cliente_nome))
        db.session.add(novo)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception:
        return jsonify({"status": "erro"}), 500

@app.route('/auditoria')
def auditoria():
    try:
        total_vendas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_lucro = db.session.query(func.sum(Registro.lucro)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_notas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Nota Fiscal").scalar() or 0
        count_pedidos = Registro.query.filter(Registro.tipo == "Pedido").count()
        margem = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

        ultimos = Registro.query.order_by(Registro.id.desc()).limit(10).all()
        lista = [{"id": r.numero, "venda": f"R$ {r.valor:.2f}", "lucro": f"R$ {r.lucro:.2f}"} for r in ultimos]

        return jsonify({
            "01_FATURAMENTO_TOTAL": f"R$ {total_vendas:.2f}",
            "02_LUCRO_TOTAL": f"R$ {total_lucro:.2f}",
            "03_MARGEM_PERCENTUAL": f"{margem:.2f}%",
            "04_FATURAMENTO_NOTAS": f"R$ {total_notas:.2f}",
            "05_QUANTIDADE_PEDIDOS": count_pedidos,
            "ULTIMAS_VENDAS": lista
        })
    except Exception as e:
        return jsonify({"erro": "Acesse o painel do seu banco de dados e apague a tabela 'registro' para o James recriá-la corretamente."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
