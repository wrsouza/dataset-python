"""
Longest Increasing Subsequence (LIS) - Subsequencia Crescente Maxima

O que este script demonstra: tabulacao O(n^2) para encontrar o comprimento e o
conteudo da maior subsequencia estritamente crescente em uma lista de numeros,
usando dp[i] = tamanho da LIS que termina exatamente no indice i.
Complexidade: O(n^2) tempo, O(n) espaco
(existe uma versao O(n log n) usando busca binaria sobre uma lista auxiliar de
"menores finais possiveis por tamanho", nao implementada aqui por foco didatico)
"""


def lis(numeros: list[int]):
    """Retorna (tamanho_da_lis, subsequencia) para a lista dada."""
    n = len(numeros)
    if n == 0:
        return 0, []

    # dp[i] = tamanho da maior subsequencia crescente que termina em numeros[i]
    dp = [1] * n
    # anterior[i] = indice do elemento anterior na LIS que termina em i (para reconstrucao)
    anterior = [-1] * n

    for i in range(1, n):
        for j in range(i):
            if numeros[j] < numeros[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                anterior[i] = j

    # Encontra o indice com o maior valor de dp (fim da melhor LIS)
    indice_fim = max(range(n), key=lambda i: dp[i])
    tamanho_maximo = dp[indice_fim]

    # Reconstrucao: segue os "anteriores" de tras para frente
    subsequencia = []
    i = indice_fim
    while i != -1:
        subsequencia.append(numeros[i])
        i = anterior[i]
    subsequencia.reverse()

    return tamanho_maximo, subsequencia


if __name__ == "__main__":
    numeros = [10, 9, 2, 5, 3, 7, 101, 18]

    tamanho, subsequencia = lis(numeros)
    print(f"Lista: {numeros}")
    print(f"Tamanho da LIS: {tamanho}")
    print(f"LIS encontrada: {subsequencia}")

    # Caso trivial: lista vazia e lista decrescente (LIS de tamanho 1)
    print(f"\nLista vazia -> {lis([])}")
    decrescente = [5, 4, 3, 2, 1]
    print(f"Lista decrescente {decrescente} -> {lis(decrescente)}")

    # Sanity checks
    assert tamanho == len(subsequencia)
    assert all(subsequencia[i] < subsequencia[i + 1] for i in range(len(subsequencia) - 1))
    assert lis([])[0] == 0
    assert lis(decrescente)[0] == 1
    print("\nOK: subsequencia encontrada e estritamente crescente e tem o tamanho esperado.")
