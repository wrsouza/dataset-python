"""
Diferenciar lista vazia de None

Cenario: uma funcao de busca (ex: consulta a um banco/API) pode retornar uma
lista vazia ("buscou e nao achou nada") ou None ("a busca nem aconteceu,
houve erro ou parametro invalido"). Tratar os dois casos da mesma forma
("if not resultado") esconde bugs reais, porque None costuma indicar uma
falha que precisa de tratamento diferente de uma lista vazia legitima.
Demonstra: checagem explicita com "is None" vs "len(lista) == 0", e como isso
muda o fluxo de decisao em codigo real.
"""


def buscar_pedidos_do_cliente(cliente_id, banco_simulado):
    """Retorna None se o cliente nao existe na base; lista (possivelmente
    vazia) se o cliente existe mas pode ou nao ter pedidos."""
    if cliente_id not in banco_simulado:
        return None  # cliente desconhecido: erro de uso, nao "zero pedidos"
    return banco_simulado[cliente_id]  # pode ser [] e ainda assim ser valido


def processar_resultado_busca(cliente_id, resultado):
    """Mostra por que misturar os dois casos com 'if not resultado' e perigoso."""
    # Errado (comentado de proposito): "if not resultado:" trataria None e []
    # como o mesmo caso, escondendo a diferenca entre "cliente nao existe" e
    # "cliente existe mas sem pedidos".

    if resultado is None:
        return f"[ERRO] Cliente {cliente_id} nao encontrado na base."
    if len(resultado) == 0:
        return f"[OK] Cliente {cliente_id} existe, mas nao tem pedidos ainda."
    return f"[OK] Cliente {cliente_id} tem {len(resultado)} pedido(s): {resultado}"


if __name__ == "__main__":
    banco_simulado = {
        "cliente_001": ["PED-100", "PED-101"],
        "cliente_002": [],  # cliente existe, mas sem pedidos -> lista vazia valida
        # "cliente_003" propositalmente ausente -> simula cliente inexistente
    }

    ids_para_consultar = ["cliente_001", "cliente_002", "cliente_003"]

    for cliente_id in ids_para_consultar:
        resultado = buscar_pedidos_do_cliente(cliente_id, banco_simulado)
        mensagem = processar_resultado_busca(cliente_id, resultado)
        print(mensagem)

    print("\nResumo da diferenca:")
    print("  None       -> busca falhou / cliente nao existe (precisa de tratamento de erro)")
    print("  lista []   -> busca funcionou, simplesmente nao ha dados (fluxo normal)")
