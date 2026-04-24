import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, text

app = Flask(__name__)

# Configuração da conexão
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Estrutura Profissional (Com Custo e Lucro)
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    custo = db.Column(db.Float, default=0.0)
    lucro = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

# COMANDO DE LIMPEZA ABSOLUTA
with app.app_context():
    # Esta linha força o banco a aceitar a nova estrutura
    db.session.execute(text("DROP TABLE IF EXISTS registro CASCADE;"))
    db.session.commit()
    db.create_all()
    print("Base de dados reiniciada com sucesso pelo James.")

@app.route('/')
def home():
    return "James Engine Pro - Online e Lucrativo"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or "Cliente"
        venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        if venda <= 0.1:
            return jsonify({"status": "ignorado"}), 200

        # Lógica de Rentabilidade: 20% Shopee + Custo vindo do Bling
        valor_custo = float(info.get('valorCusto') or info.get('custo') or 0.0)
        # Se o custo vier zerado, o lucro será Venda - 20%
        valor_lucro = venda - valor_custo - (venda * 0.20)

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
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/auditoria')
def auditoria():
    try:
        total_vendas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_lucro = db.session.query(func.sum(Registro.lucro)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_notas = db.session.query(func.sum(Registro.valor)).filter(Registro.tipo == "Nota Fiscal").scalar() or 0
        count_pedidos = Registro.query.filter(Registro.tipo == "Pedido").count()
        
        margem = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

        ultimos = Registro.query.order_by(Registro.id.desc()).limit(15).all()
        lista = [{
            "id": r.numero, 
            "venda": f"R$ {r.valor:,.2f}", 
            "lucro_liq": f"R$ {r.lucro:,.2f}",
            "hora": r.data_registro.strftime('%H:%M')
        } for r in ultimos]

        return jsonify({
            "01_FATURAMENTO_TOTAL_HOJE": f"R$ {total_vendas:,.2f}",
            "02_LUCRO_REAL_ESTIMADO": f"R$ {total_lucro:,.2f}",
            "03_MARGEM_PERCENTUAL": f"{margem:.2f}%",
            "04_TOTAL_NOTAS_EMITIDAS": f"R$ {total_notas:,.2f}",
            "05_PEDIDOS_PROCESSADOS": count_pedidos,
            "ULTIMAS_VENDAS": lista
        })
    except Exception as e:
        return jsonify({"status": "aguardando_primeiro_pedido", "erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
