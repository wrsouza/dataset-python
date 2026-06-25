"""
Longest Common Subsequence (LCS) - Subsequencia Comum Maxima

O que este script demonstra: tabulacao para encontrar o comprimento e o conteudo
da maior subsequencia comum entre duas strings, usando a tabela classica
dp[i][j] = tamanho do LCS entre os prefixos a[:i] e b[:j].
Complexidade: O(n * m) tempo, O(n * m) espaco (n, m = tamanhos das strings)
"""


def lcs(a: str, b: str) -> tuple[int, str]:
    """Retorna (tamanho_do_lcs, string_do_lcs) entre a e b."""
    n, m = len(a), len(b)

    # dp[i][j] = tamanho do LCS entre a[:i] e b[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                # caracteres coincidem: estende o LCS encontrado antes
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                # caracteres diferem: pega o melhor entre ignorar um caractere de a ou de b
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstrucao: caminha de tras para frente na tabela
    i, j = n, m
    subsequencia = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            subsequencia.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    subsequencia.reverse()

    return dp[n][m], "".join(subsequencia)


if __name__ == "__main__":
    a = "ABCBDAB"
    b = "BDCABA"

    tamanho, sequencia = lcs(a, b)

    print(f"String A: {a}")
    print(f"String B: {b}")
    print(f"Tamanho do LCS: {tamanho}")
    print(f"LCS encontrado: '{sequencia}'")

    # Sanity checks: a sequencia encontrada deve ser subsequencia de ambas as strings
    def eh_subsequencia(sub: str, texto: str) -> bool:
        it = iter(texto)
        return all(ch in it for ch in sub)

    assert len(sequencia) == tamanho
    assert eh_subsequencia(sequencia, a)
    assert eh_subsequencia(sequencia, b)
    print("\nOK: o LCS encontrado e de fato subsequencia valida de A e de B.")
