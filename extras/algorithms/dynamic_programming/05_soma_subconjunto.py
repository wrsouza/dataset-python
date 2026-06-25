"""
Soma de Subconjunto (Subset Sum)

O que este script demonstra: tabulacao para responder se existe um subconjunto
dos numeros dados que soma exatamente a um valor alvo, e reconstrucao desse
subconjunto a partir da tabela booleana dp[i][s].
Complexidade: O(n * soma_alvo) tempo, O(n * soma_alvo) espaco
"""


def existe_subconjunto_com_soma(numeros: list[int], alvo: int):
    """Retorna (existe: bool, subconjunto: list[int] | None)."""
    n = len(numeros)

    # dp[i][s] = True se e possivel obter soma s usando os primeiros i numeros
    dp = [[False] * (alvo + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = True  # soma 0 sempre e possivel (subconjunto vazio)

    for i in range(1, n + 1):
        valor = numeros[i - 1]
        for s in range(alvo + 1):
            # opcao 1: nao usar o numero i
            dp[i][s] = dp[i - 1][s]
            # opcao 2: usar o numero i, se nao exceder a soma s
            if not dp[i][s] and valor <= s:
                dp[i][s] = dp[i - 1][s - valor]

    if not dp[n][alvo]:
        return False, None

    # Reconstrucao: caminha de tras para frente vendo onde o numero foi "usado"
    subconjunto = []
    s = alvo
    for i in range(n, 0, -1):
        if s >= numeros[i - 1] and dp[i - 1][s - numeros[i - 1]] and not dp[i - 1][s]:
            subconjunto.append(numeros[i - 1])
            s -= numeros[i - 1]
        elif not dp[i - 1][s]:
            # dp[i][s] so e True por causa do numero i (caso dp[i-1][s] seja False)
            subconjunto.append(numeros[i - 1])
            s -= numeros[i - 1]
    subconjunto.reverse()

    return True, subconjunto


if __name__ == "__main__":
    numeros = [3, 34, 4, 12, 5, 2]
    alvo = 9

    existe, subconjunto = existe_subconjunto_com_soma(numeros, alvo)
    print(f"Numeros: {numeros}")
    print(f"Alvo: {alvo}")
    print(f"Existe subconjunto com essa soma? {existe}")
    if existe:
        print(f"Subconjunto encontrado: {subconjunto} (soma={sum(subconjunto)})")

    # Caso trivial: alvo 0 sempre existe (subconjunto vazio)
    existe_zero, subconjunto_zero = existe_subconjunto_com_soma(numeros, 0)
    print(f"\nAlvo 0 -> existe={existe_zero}, subconjunto={subconjunto_zero}")

    # Caso impossivel
    existe_impossivel, _ = existe_subconjunto_com_soma(numeros, 1000)
    print(f"Alvo 1000 (impossivel) -> existe={existe_impossivel}")

    # Sanity checks
    assert existe is True
    assert sum(subconjunto) == alvo
    assert existe_zero is True and subconjunto_zero == []
    assert existe_impossivel is False
    print("\nOK: subconjunto encontrado soma corretamente ao alvo.")
