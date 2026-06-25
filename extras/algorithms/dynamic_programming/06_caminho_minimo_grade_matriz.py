"""
Caminho de Custo Minimo em Grade/Matriz

O que este script demonstra: tabulacao para encontrar o caminho de menor custo
do canto superior-esquerdo ao canto inferior-direito de uma matriz, podendo se
mover apenas para a direita ou para baixo a cada passo.
Complexidade: O(n * m) tempo, O(n * m) espaco (n, m = dimensoes da grade)
"""


def caminho_minimo(grade: list[list[int]]):
    """Retorna (custo_minimo, caminho) movendo so para direita ou baixo."""
    n = len(grade)
    m = len(grade[0])

    # dp[i][j] = custo minimo para chegar na celula (i, j) partindo de (0, 0)
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = grade[0][0]

    # Primeira linha: so pode vir de mover para a direita
    for j in range(1, m):
        dp[0][j] = dp[0][j - 1] + grade[0][j]
    # Primeira coluna: so pode vir de mover para baixo
    for i in range(1, n):
        dp[i][0] = dp[i - 1][0] + grade[i][0]

    for i in range(1, n):
        for j in range(1, m):
            dp[i][j] = grade[i][j] + min(dp[i - 1][j], dp[i][j - 1])

    # Reconstrucao do caminho: caminha de tras para frente escolhendo o vizinho mais barato
    caminho = []
    i, j = n - 1, m - 1
    while (i, j) != (0, 0):
        caminho.append((i, j))
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        elif dp[i - 1][j] <= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    caminho.append((0, 0))
    caminho.reverse()

    return dp[n - 1][m - 1], caminho


if __name__ == "__main__":
    grade = [
        [1, 3, 1],
        [1, 5, 1],
        [4, 2, 1],
    ]

    custo, caminho = caminho_minimo(grade)
    print("Grade:")
    for linha in grade:
        print(f"  {linha}")
    print(f"Custo minimo: {custo}")
    print(f"Caminho (linha, coluna): {caminho}")

    # Caso trivial: grade 1x1
    custo_trivial, caminho_trivial = caminho_minimo([[7]])
    print(f"\nGrade 1x1 [[7]] -> custo={custo_trivial}, caminho={caminho_trivial}")

    # Sanity checks
    assert custo == 7  # 1 -> 3 -> 1 -> 1 -> 1
    assert caminho[0] == (0, 0) and caminho[-1] == (len(grade) - 1, len(grade[0]) - 1)
    assert custo_trivial == 7 and caminho_trivial == [(0, 0)]
    print("\nOK: custo minimo e caminho reconstruido conferem com o esperado.")
