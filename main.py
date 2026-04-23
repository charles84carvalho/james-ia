import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Credenciais recuperadas do ambiente do Railway
CLIENT_ID = os.getenv('BLING_CLIENT_ID')
CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET')
API_KEY_V2 = os.getenv('BLING_API_KEY') 

def get_access_token():
    """Conexão com API v3 (para dados de contatos e pedidos)"""
    url = "https://www.bling.com.br/Api/v3/oauth/token"
    try:
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=5)
        return response.json().get('access_token')
    except:
        return None

@app.route('/')
def home():
    return "James Monitor v2 - Operação Transparente"

@app.route('/faturamento_hoje', methods=['GET'])
def faturamento_hoje():
    """O James varre TODAS as notas do dia para relatar a realidade"""
    if not API_KEY_V2:
        return jsonify({"erro": "Variável BLING_API_KEY não configurada"}), 500
    
    # Pega a data atual no formato do Bling
    hoje = datetime.now().strftime('%d/%m/%Y')
    
    # Consultamos sem filtro de situação para ver as pendentes e as autorizadas
    url = f"https://bling.com.br/Api/v2/notafiscal/json/"
    params = {
        'filters': f'dataEmissao[{hoje} TO {hoje}]',
        'apikey': API_KEY_V2
    }
    
    try:
        res = requests.get(url, params=params, timeout=12)
        dados = res.json()
        
        if 'notafiscais' in dados.get('retorno', {}):
            notas = dados['retorno']['notafiscais']
            lista_detalhada = []
            total_valor = 0.0
            
            for n in notas:
                nf = n['notafiscal']
                valor = float(nf.get('valorNota', 0))
                total_valor += valor
                
                lista_detalhada.append({
                    "numero": nf.get('numero'),
                    "valor": valor,
                    "situacao": nf.get('situacao'), # 6=Autorizada, 1=Pendente/Emitida
                    "cliente": nf.get('cliente', {}).get('nome', 'N/A')
                })
            
            # Ordena pela nota mais recente
            lista_detalhada.sort(key=lambda x: x['numero'], reverse=True)
            
            return jsonify({
                "status": "sucesso",
                "data": hoje,
                "quantidade_total": len(lista_detalhada),
                "valor_total_dia": round(total_valor, 2),
                "notas": lista_detalhada
            })
        
        return jsonify({"status": "vazio", "msg": "Nenhuma nota encontrada no Bling hoje."}), 404
        
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe alertas de novos eventos (Ouvinte)"""
    try:
        dados = request.get_json()
        print(f"--- Evento Recebido: {datetime.now().strftime('%H:%M:%S')} ---")
        return jsonify({"status": "received"}), 200
    except:
        return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    # O Railway define a porta automaticamente
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
