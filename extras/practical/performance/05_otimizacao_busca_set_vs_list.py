"""
Busca: set vs list (operador 'in')

Cenario: verificar se um valor "existe em uma colecao" e uma operacao extremamente
comum (ex: checar se um ID ja foi processado, validar se um email esta numa
lista de bloqueio). A estrutura de dados escolhida para essa colecao impacta
diretamente a performance quando a colecao cresce.
O que este script demonstra: medir com timeit o custo do operador 'in' em uma
list (busca linear O(n)) versus em um set (busca por hash O(1) em media),
mostrando como a diferenca se acentua conforme o tamanho da colecao aumenta.
"""

import timeit

TAMANHO = 50_000  # tamanho da colecao
REPETICOES = 1_000  # numero de buscas realizadas em cada medicao


def montar_colecoes(tamanho):
    dados = list(range(tamanho))
    return dados, set(dados)  # mesma colecao de valores, estruturas diferentes


def benchmark():
    lista, conjunto = montar_colecoes(TAMANHO)

    # buscamos por um valor que esta no "fim" da lista -- pior caso para list,
    # caso medio para set (hash nao depende de posicao).
    valor_buscado = TAMANHO - 1

    tempo_list = timeit.timeit(
        lambda: valor_buscado in lista,
        number=REPETICOES,
    )
    tempo_set = timeit.timeit(
        lambda: valor_buscado in conjunto,
        number=REPETICOES,
    )

    return tempo_list, tempo_set


if __name__ == "__main__":
    tempo_list, tempo_set = benchmark()

    print(f"Colecao com {TAMANHO:,} elementos | {REPETICOES:,} buscas por execucao")
    print(f"Busca em list ('in'): {tempo_list:.6f}s")
    print(f"Busca em set ('in'):  {tempo_set:.6f}s")

    if tempo_set > 0:
        fator = tempo_list / tempo_set
        print(f"Set foi aproximadamente {fator:,.0f}x mais rapido que list para esta busca.")

    print(
        "Motivo: list.in faz busca linear (percorre elemento a elemento) enquanto "
        "set.in usa hashing para localizar o item em tempo praticamente constante."
    )
