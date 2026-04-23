import os
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
API_KEY_V2 = os.getenv('BLING_API_KEY')

def buscar_notas_paginadas(data_str):
    todas = []
    # Limitamos a 10 páginas (1000 notas) para evitar que o servidor trave
    for pagina in range(1, 11):
        url = f"https://bling.com.br/Api/v2/notafiscal/json/"
        params = {
            'filters': f'dataEmissao[{data_str} TO {data_str}]',
            'apikey': API_KEY_V2,
            'page': pagina
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            dados = res.json()
            if 'notafiscais' in dados.get('retorno', {}):
                notas_pagina = dados['retorno']['notafiscais']
                todas.extend(notas_pagina)
                if len(notas_pagina) < 100: break # Se veio menos de 100, é a última página
            else:
                break
        except:
            break
    return todas

@app.route('/faturamento_hoje')
def faturamento_hoje():
    if not API_KEY_V2:
        return jsonify({"erro": "Configure a BLING_API_KEY no Railway"}), 500
    
    # Tenta buscar o dia 22/04/2026 especificamente, onde está o seu lote grande
    data_alvo = "22/04/2026"
    notas = buscar_notas_paginadas(data_alvo)
    
    if not notas:
        return jsonify({"status": "vazio", "msg": f"Nenhuma nota no dia {data_alvo}"}), 404

    total_valor = sum(float(n['notafiscal'].get('valorNota', 0)) for n in notas)
    # Pega a nota com maior número (a mais recente)
    numeros = [int(n['notafiscal']['numero']) for n in notas]
    ultima = max(numeros) if numeros else "N/A"

    return jsonify({
        "status": "sucesso",
        "data": data_alvo,
        "total_notas": len(notas),
        "faturamento_total": round(total_valor, 2),
        "ultima_nota_detectada": ultima,
        "james_status": "Operação completa"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
