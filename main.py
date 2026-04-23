@app.route('/faturamento_hoje', methods=['GET'])
def faturamento_hoje():
    if not API_KEY_V2:
        return jsonify({"erro": "API_KEY_V2 ausente"}), 500
    
    # Pegamos a data de hoje e a de ontem para garantir que o relatório não fique vazio na virada do dia
    from datetime import datetime, timedelta
    hoje_dt = datetime.now()
    ontem_dt = hoje_dt - timedelta(days=1)
    
    data_consulta = hoje_dt.strftime('%d/%m/%Y')
    
    # Se o senhor acessar logo após a meia-noite e estiver vazio, 
    # o sistema tentará buscar os dados de 'ontem' automaticamente.
    def buscar_notas(data_str):
        todas_as_notas = []
        pagina = 1
        while True:
            url = f"https://bling.com.br/Api/v2/notafiscal/json/"
            params = {'filters': f'dataEmissao[{data_str} TO {data_str}]', 'apikey': API_KEY_V2, 'page': pagina}
            res = requests.get(url, params=params, timeout=15)
            dados = res.json()
            if 'notafiscais' in dados.get('retorno', {}):
                notas_pagina = dados['retorno']['notafiscais']
                todas_as_notas.extend(notas_pagina)
                if len(notas_pagina) >= 100:
                    pagina += 1
                else: break
            else: break
        return todas_as_notas

    # Tenta hoje
    notas = buscar_notas(data_consulta)
    
    # Se hoje estiver vazio (como agora), ele busca automaticamente o dia 22
    if not notas:
        data_consulta = ontem_dt.strftime('%d/%m/%Y')
        notas = buscar_notas(data_consulta)

    if notas:
        total_valor = sum(float(n['notafiscal'].get('valorNota', 0)) for n in notas)
        return jsonify({
            "status": "sucesso",
            "data_relatorio": data_consulta,
            "total_notas": len(notas),
            "faturamento_total": round(total_valor, 2),
            "ultima_nota_lida": notas[0]['notafiscal']['numero']
        })
    
    return jsonify({"status": "vazio", "msg": "Nenhuma nota encontrada nas últimas 24h"}), 404
