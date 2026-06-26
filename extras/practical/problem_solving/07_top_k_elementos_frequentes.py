"""
Top K Elementos Mais Frequentes

Cenário: dashboards de analytics (top 5 páginas mais acessadas), sistemas de
recomendação (produtos mais comprados), análise de logs (erros mais comuns
em um período).
O que este script demonstra: uso de Counter.most_common para obter os K
elementos mais frequentes de forma eficiente, e como lidar com empates de
frequência de maneira determinística (ordem de primeira ocorrência).
"""

from collections import Counter


def top_k_frequentes(itens: list[str], k: int) -> list[tuple[str, int]]:
    """
    Counter.most_common já usa um heap internamente para O(n log k) quando k < n,
    em vez de ordenar a lista completa - mais eficiente que sorted() ingênuo.
    """
    if k <= 0:
        return []
    contagem = Counter(itens)
    return contagem.most_common(k)


if __name__ == "__main__":
    acessos_paginas = [
        "home", "produtos", "home", "checkout", "produtos", "home",
        "sobre", "produtos", "checkout", "home", "contato",
    ]

    k = 3
    resultado = top_k_frequentes(acessos_paginas, k)
    print(f"Top {k} páginas mais acessadas:")
    for pagina, contagem in resultado:
        print(f"  {pagina:10} -> {contagem} acessos")
