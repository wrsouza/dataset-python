"""
Distancia de Edicao (Levenshtein)

O que este script demonstra: tabulacao para calcular o numero minimo de
operacoes (inserir, remover, substituir) para transformar uma string em outra,
usando dp[i][j] = distancia entre os prefixos a[:i] e b[:j].
Complexidade: O(n * m) tempo, O(n * m) espaco (n, m = tamanhos das strings)
"""


def distancia_levenshtein(a: str, b: str) -> int:
    """Retorna o numero minimo de edicoes (insercao/remocao/substituicao) de a para b."""
    n, m = len(a), len(b)

    # dp[i][j] = custo minimo para transformar a[:i] em b[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Caso base: transformar string vazia em b[:j] custa j insercoes
    for j in range(m + 1):
        dp[0][j] = j
    # Caso base: transformar a[:i] em string vazia custa i remocoes
    for i in range(n + 1):
        dp[i][0] = i

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                # caracteres iguais: nenhuma operacao extra necessaria aqui
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # remover caractere de a
                    dp[i][j - 1],      # inserir caractere de b
                    dp[i - 1][j - 1],  # substituir caractere
                )

    return dp[n][m]


if __name__ == "__main__":
    a = "kitten"
    b = "sitting"

    distancia = distancia_levenshtein(a, b)
    print(f"'{a}' -> '{b}': distancia de edicao = {distancia}")

    # Casos triviais para contraste
    print(f"'{a}' -> '{a}': distancia de edicao = {distancia_levenshtein(a, a)}")
    print(f"'' -> '{b}': distancia de edicao = {distancia_levenshtein('', b)}")

    # Sanity checks
    assert distancia_levenshtein(a, a) == 0
    assert distancia_levenshtein("", b) == len(b)
    assert distancia == 3  # kitten -> sitting: k->s, e->i, +g
    print("\nOK: distancias calculadas conferem com os valores esperados.")
