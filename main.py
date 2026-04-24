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
    return "James Pro SaaS - Inteligência Comercial Ativa"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(silent=True) or {}
        info = dados.get('data', {})
        
        # Busca profunda pelo nome (evita o "Cliente" genérico)
        contato = info.get('contato', {})
        cliente_nome = contato.get('nome') or info.get('cliente', {}).get('nome') or ""
        
        valor_venda = float(info.get('total') or info.get('totalVenda') or info.get('valor') or 0.0)
        
        # Filtro: Só registra se tiver valor e se não for nome genérico demais
        if valor_venda <= 0.5 or cliente_nome.strip() in ["", "Cliente"]:
            return jsonify({"status": "ignorado"}), 200

        # Identifica o tipo
        tipo_bruto = json.dumps(dados).lower()
        tipo_final = "Nota Fiscal" if 'notafiscal' in tipo_bruto else "Pedido"
        
        novo = Registro(
            tipo=tipo_final,
            numero=str(info.get('numero', '-')),
            valor=valor_venda,
            cliente=str(cliente_nome)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro"}), 500

@app.route('/auditoria')
def auditoria():
    # Filtra apenas o que é relevante
    registros = Registro.query.filter(Registro.valor > 0).order_by(Registro.id.desc()).limit(50).all()
    
    lista = []
    total_pedidos = 0.0
    
    for r in registros:
        lista.append({
            "cliente": r.cliente,
            "valor": f"R$ {r.valor:,.2f}",
            "tipo": r.tipo,
            "pedido": r.numero,
            "hora": r.data_registro.strftime('%H:%M')
        })
        # Soma todos os pedidos para o senhor ver o volume
        if r.tipo == "Pedido":
            total_pedidos += r.valor
            
    return jsonify({
        "mensagem": "Senhor, relatório de faturamento atualizado.",
        "faturamento_em_pedidos_recente": f"R$ {total_pedidos:,.2f}",
        "lista": lista
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
