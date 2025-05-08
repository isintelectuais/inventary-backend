from django.db import transaction

def gerar_codigo_barra(armazem):
    return (
        f"{armazem.codigo_armazem}-{armazem.qtd_niveis}-"
        f"{armazem.qtd_cidades}-{armazem.qtd_bairros_por_cidade}-"
        f"{armazem.qtd_ruas_por_bairro}-{armazem.qtd_predios_por_rua}"
    )

@transaction.atomic
def atualizar_armazem_com_transacao(armazem, data):
    for field, value in data.items():
        setattr(armazem, field, value)
    armazem.save()
    return armazem