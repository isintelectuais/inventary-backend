def calcular_percentuais(dados, total):
    """
    Calcula percentuais para estatísticas de agendamentos
    """
    resultado = []
    for item in dados:
        percentual = (item['quantidade'] / total) * 100 if total > 0 else 0
        resultado.append({
            "status": item['status'],
            "quantidade": item['quantidade'],
            "percentual": round(percentual, 2)
        })
    return resultado