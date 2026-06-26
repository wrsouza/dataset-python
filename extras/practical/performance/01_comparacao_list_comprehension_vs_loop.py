"""
List comprehension vs loop explicito

Cenario: em pipelines de transformacao de dados (ETL, preparo de dataset, etc.)
e comum escolher entre escrever um loop "for" classico ou uma list comprehension
para gerar uma nova lista a partir de outra.
O que este script demonstra: medir com timeit a diferenca de desempenho entre as
duas abordagens para a mesma transformacao, e mostrar que list comprehension
costuma ser mais rapida porque evita o overhead de chamadas repetidas de
".append()" e o bytecode gerado e mais direto (CPython otimiza a comprehension
em um loop interno especializado).
"""

import timeit

TAMANHO = 100_000  # tamanho pequeno o suficiente para rodar em segundos
REPETICOES = 5


def transformar_com_loop(dados):
    """Constroi a lista resultado usando um loop explicito + append."""
    resultado = []
    for valor in dados:
        if valor % 2 == 0:  # filtra apenas pares, como um filtro de dado real
            resultado.append(valor * 2)
    return resultado


def transformar_com_comprehension(dados):
    """Mesma transformacao, mas usando list comprehension com filtro embutido."""
    return [valor * 2 for valor in dados if valor % 2 == 0]


def benchmark():
    dados = list(range(TAMANHO))

    # timeit.timeit roda a funcao varias vezes e soma o tempo total;
    # passamos os dados via closure (lambda) para nao medir o custo de criar a lista.
    tempo_loop = timeit.timeit(lambda: transformar_com_loop(dados), number=REPETICOES)
    tempo_comp = timeit.timeit(lambda: transformar_com_comprehension(dados), number=REPETICOES)

    return tempo_loop, tempo_comp


if __name__ == "__main__":
    tempo_loop, tempo_comp = benchmark()

    print(f"Tamanho dos dados: {TAMANHO:,} elementos | Repeticoes: {REPETICOES}")
    print(f"Loop explicito:        {tempo_loop:.4f}s")
    print(f"List comprehension:    {tempo_comp:.4f}s")

    diferenca_pct = (tempo_loop - tempo_comp) / tempo_loop * 100
    if tempo_comp < tempo_loop:
        print(f"Comprehension foi {diferenca_pct:.1f}% mais rapida que o loop.")
    else:
        print(f"Loop foi {abs(diferenca_pct):.1f}% mais rapido que a comprehension.")

    # validacao simples de que ambas produzem o mesmo resultado
    dados_teste = list(range(10))
    assert transformar_com_loop(dados_teste) == transformar_com_comprehension(dados_teste)
    print("Resultados equivalentes confirmados (sanity check).")
