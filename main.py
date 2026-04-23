import os
import requests
from flask import Flask, jsonify
from datetime import datetime
import time

app = Flask(__name__)
API_KEY_V2 = os.getenv('BLING_API_KEY')

@app.route('/faturamento_hoje', methods=['GET'])
def faturamento_hoje():
    if not API_KEY_V2:
        return jsonify({"erro": "API_KEY_V2 ausente"}), 500
    
    hoje = datetime.now().strftime('%d/%m/%Y')
    todas_as_notas = []
    pagina = 1
    
    while True:
        url = f"https://bling.com.br/Api/v2/notafiscal/json/"
        params = {
            'filters': f'dataEmissao[{hoje} TO {hoje}]',
            'apikey': API_KEY_V2,
            'page': pagina
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            dados = res.json()
            
            # Se encontrar notas na página atual
            if 'notafiscais' in dados.get('retorno', {}):
                notas_pagina = dados['retorno']['notafiscais']
                todas_as_notas.extend(notas_pagina)
                
                # Se a página veio cheia (100 notas), busca a próxima
                if len(notas_pagina) >= 100:
                    pagina += 1
                    time.sleep(0.2) # Evita bloqueio por excesso de requisições
                else:
                    break # Chegou na última página
            else:
                break # Não há mais notas
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    # Processamento dos dados acumulados
    total_valor = 0.0
    num_notas = len(todas_as_notas)
    
    if num_notas > 0:
        # Pega a última nota (a mais recente emitida)
        ultima_nota = todas_as_notas[0]['notafiscal']['numero']
        for n in todas_as_notas:
            total_valor += float(n['notafiscal'].get('valorNota', 0))

        return jsonify({
            "status": "sucesso",
            "data": hoje,
            "total_notas_detectadas": num_notas,
            "faturamento_total": round(total_valor, 2),
            "ultima_nota_emitida": ultima_nota
        })
    
    return jsonify({"status": "vazio", "msg": "Nenhuma nota hoje"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
