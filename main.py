import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# 1. Configuração da conexão com o Banco de Dados
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. Definição da Tabela (Modelo Simples e Flexível)
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.Text)  # Campo flexível para guardar os dados do Bling
    data = db.Column(db.DateTime, default=datetime.utcnow)

# 3. Comando de Inicialização e Reset
with app.app_context():
    # ATENÇÃO: As duas linhas abaixo limpam e recriam a tabela para corrigir erros de coluna
    db.drop_all() 
    db.create_all()

# 4. Rota Inicial
@app.route('/')
def home():
    return "James Pro SaaS - Sistema Online e Operacional"

# 5. O "Ouvido" do James (Webhook do Bling)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Captura os dados brutos enviados pelo Bling
        dados_brutos = request.get_data(as_text=True)
        
        # Salva no banco de dados para auditoria
        nova_venda = Venda(info=dados_brutos)
        db.session.add(nova_venda)
        db.session.commit()
        
        return jsonify({"status": "sucesso", "mensagem": "Dados guardados pelo James"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

# 6. Rota de Auditoria (Para o senhor testar)
@app.route('/auditoria')
def auditoria():
    try:
        total = Venda.query.count()
        ultimas = Venda.query.order_by(Venda.id.desc()).limit(5).all()
        
        logs = []
        for v in ultimas:
            logs.append({"id": v.id, "data": v.data.strftime('%d/%m %H:%M'), "conteudo": v.info[:100]})
            
        return jsonify({
            "status": "James está ouvindo",
            "total_no_banco": total,
            "ultimos_recebidos": logs
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
