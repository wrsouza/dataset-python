"""
Quebra de Moedas (Coin Change) - Numero Minimo de Moedas

O que este script demonstra: tabulacao para encontrar o menor numero de moedas
necessario para formar um valor alvo, dado um conjunto de moedas disponiveis
em quantidade ilimitada, usando dp[v] = minimo de moedas para formar o valor v.
Complexidade: O(n * valor) tempo, O(valor) espaco (n = quantidade de tipos de moeda)
"""

INFINITO = float("inf")


def numero_minimo_moedas(moedas: list[int], valor_alvo: int):
    """Retorna (numero_minimo_de_moedas, moedas_usadas) ou (None, None) se impossivel."""
    # dp[v] = menor numero de moedas para formar o valor v
    dp = [INFINITO] * (valor_alvo + 1)
    dp[0] = 0  # valor 0 nao precisa de nenhuma moeda

    # escolha[v] = qual moeda foi usada por ultimo para formar dp[v] (para reconstrucao)
    escolha = [-1] * (valor_alvo + 1)

    for v in range(1, valor_alvo + 1):
        for moeda in moedas:
            if moeda <= v and dp[v - moeda] + 1 < dp[v]:
                dp[v] = dp[v - moeda] + 1
                escolha[v] = moeda

    if dp[valor_alvo] == INFINITO:
        return None, None

    # Reconstrucao: segue as escolhas guardadas ate chegar em valor 0
    moedas_usadas = []
    v = valor_alvo
    while v > 0:
        moeda = escolha[v]
        moedas_usadas.append(moeda)
        v -= moeda

    return dp[valor_alvo], moedas_usadas


if __name__ == "__main__":
    moedas = [1, 5, 10, 25]
    valor_alvo = 63

    minimo, usadas = numero_minimo_moedas(moedas, valor_alvo)
    print(f"Moedas disponiveis: {moedas}")
    print(f"Valor alvo: {valor_alvo}")
    print(f"Numero minimo de moedas: {minimo}")
    print(f"Moedas usadas: {usadas}")

    # Caso trivial: valor 0
    minimo_zero, usadas_zero = numero_minimo_moedas(moedas, 0)
    print(f"\nValor 0 -> minimo={minimo_zero}, moedas usadas={usadas_zero}")

    # Caso impossivel: nao ha moeda de valor 1, alvo nao multiplo das moedas
    minimo_impossivel, _ = numero_minimo_moedas([5, 10], 3)
    print(f"Moedas [5, 10] para valor 3 (impossivel) -> {minimo_impossivel}")

    # Sanity checks
    assert sum(usadas) == valor_alvo
    assert minimo == len(usadas)
    assert minimo_zero == 0 and usadas_zero == []
    assert minimo_impossivel is None
    print("\nOK: combinacao de moedas encontrada soma corretamente ao valor alvo.")
