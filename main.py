import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# 1. Configuração do Banco de Dados
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. Modelo de Dados Evoluído
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))  # 'Pedido' ou 'Nota Fiscal'
    numero = db.Column(db.String(50))
    valor = db.Column(db.Float, default=0.0)
    cliente = db.Column(db.String(200))
    status = db.Column(db.String(100))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    conteudo_bruto = db.Column(db.Text)

# 3. Inicialização (Mantendo o Reset para aplicar a nova estrutura)
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def home():
    return "James Pro SaaS - Inteligência de Vendas Ativa"

# 4. O Ouvido Inteligente (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"status": "vazio"}), 200

        tipo = "Desconhecido"
        numero = "-"
        valor = 0.0
        cliente = "Não Identificado"
        status = "-"

        # Lógica para identificar se é Nota Fiscal (v3)
        if 'notafiscal' in str(dados).lower():
            tipo = "Nota Fiscal"
            # Tentativa de extrair dados da estrutura Bling v3
            nf_data = dados.get('data', {})
            numero = nf_data.get('numero', '-')
            valor = float(nf_data.get('valor', 0.0))
            cliente = nf_data.get('contato', {}).get('nome', 'Cliente NF')
            status = "Autorizada" if 'situacao' not in nf_data else nf_data.get('situacao')

        # Lógica para identificar se é Pedido/Venda
        elif 'venda' in str(dados).lower() or 'pedido' in str(dados).lower():
            tipo = "Pedido"
            venda_data = dados.get('data', {})
            numero = venda_data.get('numero', '-')
            valor = float(venda_data.get('totalVenda', 0.0) or venda_data.get('total', 0.0))
            cliente = venda_data.get('contato', {}).get('nome', 'Cliente Pedido')
            status = "Em Aberto"

        # Salva o registro processado
        novo = Registro(
            tipo=tipo,
            numero=str(numero),
            valor=valor,
            cliente=cliente,
            status=str(status),
            conteudo_bruto=json.dumps(dados)
        )
        db.session.add(novo)
        db.session.commit()
        
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

# 5. Auditoria Organizada
@app.route('/auditoria')
def auditoria():
    try:
        total_geral = Registro.query.count()
        registros = Registro.query.order_by(Registro.id.desc()).limit(20).all()
        
        lista = []
        faturamento_pedidos = 0.0
        faturamento_notas = 0.0

        for r in registros:
            lista.append({
                "id": r.id,
                "tipo": r.tipo,
                "numero": r.numero,
                "cliente": r.cliente,
                "valor": f"R$ {r.valor:,.2f}",
                "data": r.data_registro.strftime('%H:%M')
            })
            if r.tipo == "Pedido": faturamento_pedidos += r.valor
            if r.tipo == "Nota Fiscal": faturamento_notas += r.valor

        return jsonify({
            "total_registros": total_geral,
            "resumo_recente": {
                "em_pedidos": f"R$ {faturamento_pedidos:,.2f}",
                "em_notas": f"R$ {faturamento_notas:,.2f}"
            },
            "ultimas_operacoes": lista
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
