import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# Configuração da conexão com o Banco de Dados
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Estrutura do Banco de Dados - Versão Evoluída com Lucro
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    valor_venda = db.Column(db.Float, default=0.0)
    custo_produto = db.Column(db.Float, default=0.0)
    lucro_liquido = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Inteligência de Lucro Ativada"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # 1. Captura de Valores Básicos
        cliente_nome = info.get('contato', {}).get('nome') or info.get('cliente', {}).get('nome') or "Cliente Shopee"
        valor_venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        if valor_venda <= 0.1:
            return jsonify({"status": "ignorado"}), 200

        # 2. Lógica de Custo e Impostos (Ajuste conforme sua realidade)
        # Tentamos pegar o custo do Bling, se não vier, tratamos como 0.0 para não travar
        custo_bruto = float(info.get('valorCusto') or info.get('custo') or 0.0)
        
        # Cálculo de Taxas Shopee (Exemplo: 20% de comissão/taxas)
        taxa_shopee = valor_venda * 0.20
        
        # Lucro Líquido = Venda - Custo - Taxas
        lucro = valor_venda - custo_bruto - taxa_shopee

        tipo = "Nota Fiscal" if 'notafiscal' in json.dumps(dados).lower() else "Pedido"
        
        novo = Registro(
            tipo=tipo,
            numero=str(info.get('numero', '-')),
            valor_venda=valor_venda,
            custo_produto=custo_bruto,
            lucro_liquido=lucro,
            cliente=str(cliente_nome)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        print(f"Erro no James: {e}")
        return jsonify({"status": "erro"}), 500

@app.route('/auditoria')
def auditoria():
    try:
        # Somatórias de Faturamento e Lucro
        total_vendas = db.session.query(func.sum(Registro.valor_venda)).filter(Registro.tipo == "Pedido").scalar() or 0
        total_lucro = db.session.query(func.sum(Registro.lucro_liquido)).filter(Registro.tipo == "Pedido").scalar() or 0
        
        total_notas = db.session.query(func.sum(Registro.valor_venda)).filter(Registro.tipo == "Nota Fiscal").scalar() or 0
        count_pedidos = Registro.query.filter(Registro.tipo == "Pedido").count()

        # Margem média em porcentagem
        margem_percentual = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0

        ultimos = Registro.query.order_by(Registro.id.desc()).limit(15).all()
        lista = []
        for r in ultimos:
            lista.append({
                "id": r.numero,
                "venda": f"R$ {r.valor_venda:,.2f}",
                "lucro_est": f"R$ {r.lucro_liquido:,.2f}",
                "tipo": r.tipo,
                "hora": r.data_registro.strftime('%H:%M')
            })

        return jsonify({
            "01_FATURAMENTO_BRUTO": f"R$ {total_vendas:,.2f}",
            "02_LUCRO_LIQUIDO_ESTIMADO": f"R$ {total_lucro:,.2f}",
            "03_MARGEM_REAL_MEDIA": f"{margem_percentual:.2f}%",
            "04_TOTAL_NOTAS_EMITIDAS": f"R$ {total_notas:,.2f}",
            "05_PEDIDOS_TOTAL": count_pedidos,
            "ULTIMAS_OPERACOES": lista,
            "OBS": "Lucro líquido calculado após 20% de taxas Shopee e custos vindos do Bling."
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
