"""
Problema da Mochila 0/1 (Knapsack)

O que este script demonstra: tabulacao classica do knapsack 0/1, construindo uma
tabela dp[i][w] = valor maximo usando os primeiros i itens com capacidade w,
e depois reconstruindo quais itens foram escolhidos.
Complexidade: O(n * W) tempo, O(n * W) espaco (n = num itens, W = capacidade)
"""


def knapsack_01(pesos: list[int], valores: list[int], capacidade: int):
    """Retorna (valor_maximo, itens_escolhidos) para o knapsack 0/1."""
    n = len(pesos)

    # dp[i][w] = valor maximo possivel usando os primeiros i itens com capacidade w
    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        peso_item = pesos[i - 1]
        valor_item = valores[i - 1]
        for w in range(capacidade + 1):
            # opcao 1: nao usar o item i
            dp[i][w] = dp[i - 1][w]
            # opcao 2: usar o item i, se couber na capacidade w
            if peso_item <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - peso_item] + valor_item)

    # Reconstrucao: anda de tras para frente vendo onde o valor mudou
    itens_escolhidos = []
    w = capacidade
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:  # item i foi usado
            itens_escolhidos.append(i - 1)
            w -= pesos[i - 1]
    itens_escolhidos.reverse()

    return dp[n][capacidade], itens_escolhidos


if __name__ == "__main__":
    pesos = [2, 3, 4, 5]
    valores = [3, 4, 5, 6]
    capacidade = 5

    valor_maximo, itens = knapsack_01(pesos, valores, capacidade)

    print(f"Pesos:      {pesos}")
    print(f"Valores:    {valores}")
    print(f"Capacidade: {capacidade}")
    print(f"Valor maximo: {valor_maximo}")
    print(f"Itens escolhidos (indices): {itens}")
    for idx in itens:
        print(f"  item {idx}: peso={pesos[idx]}, valor={valores[idx]}")

    # Sanity check: peso total escolhido nao pode exceder a capacidade
    peso_total = sum(pesos[i] for i in itens)
    valor_total = sum(valores[i] for i in itens)
    assert peso_total <= capacidade
    assert valor_total == valor_maximo
    print("\nOK: solucao respeita a capacidade e reproduz o valor maximo calculado.")
