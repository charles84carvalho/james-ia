# NOVA FUNÇÃO: O James agora varre TODAS as notas do dia para não perder nada
@app.route('/faturamento_hoje', methods=['GET'])
def faturamento_hoje():
    if not API_KEY_V2:
        return jsonify({"erro": "Chave API_KEY_V2 não configurada"}), 500
    
    hoje = datetime.now().strftime('%d/%m/%Y')
    # Removemos o filtro de situação [6] para ver TUDO
    url = f"https://bling.com.br/Api/v2/notafiscal/json/"
    params = {
        'filters': f'dataEmissao[{hoje} TO {hoje}]',
        'apikey': API_KEY_V2
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        dados = res.json()
        
        if 'notafiscais' in dados.get('retorno', {}):
            notas = dados['retorno']['notafiscais']
            lista = []
            for n in notas:
                nf = n['notafiscal']
                lista.append({
                    "numero": nf['numero'],
                    "valor": nf['valorNota'],
                    "situacao": nf['situacao'], # Aqui veremos se está emitida, pendente ou autorizada
                    "cliente": nf['cliente']['nome']
                })
            return jsonify({"status": "sucesso", "total_notas": len(lista), "notas": lista})
        return jsonify({"status": "vazio", "msg": "Nenhuma nota encontrada hoje"}), 404
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500
