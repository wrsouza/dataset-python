"""
Busca em Matriz Ordenada (staircase search)

O que este script demonstra: em uma matriz onde cada linha e cada coluna estão
ordenadas crescentemente, é possível buscar um valor partindo do canto
superior direito (ou inferior esquerdo): se o valor atual for maior que o
alvo, anda para a esquerda; se for menor, anda para baixo. Isso forma um
"caminho de escada" que elimina uma linha ou coluna a cada passo.
Complexidade: O(n + m) tempo, O(1) espaço (n = linhas, m = colunas)
"""


def busca_em_matriz_ordenada(matriz, alvo):
    """Retorna (linha, coluna) do alvo na matriz, ou None se não encontrado.

    Pré-condição: cada linha está ordenada crescentemente da esquerda para a
    direita, e cada coluna está ordenada crescentemente de cima para baixo.
    """
    if not matriz or not matriz[0]:
        return None

    linha = 0
    coluna = len(matriz[0]) - 1  # começa no canto superior direito

    while linha < len(matriz) and coluna >= 0:
        atual = matriz[linha][coluna]
        if atual == alvo:
            return (linha, coluna)
        elif atual > alvo:
            coluna -= 1  # valor muito grande: descarta a coluna (anda p/ esquerda)
        else:
            linha += 1  # valor muito pequeno: descarta a linha (anda p/ baixo)

    return None


if __name__ == "__main__":
    matriz_exemplo = [
        [1, 4, 7, 11, 15],
        [2, 5, 8, 12, 19],
        [3, 6, 9, 16, 22],
        [10, 13, 14, 17, 24],
        [18, 21, 23, 26, 30],
    ]

    # Caso comum: valor presente em posição não trivial
    resultado = busca_em_matriz_ordenada(matriz_exemplo, 16)
    print("Matriz:")
    for linha_atual in matriz_exemplo:
        print(linha_atual)
    print(f"Procurando 16 -> posição: {resultado}")

    # Caso trivial: valor ausente
    resultado_ausente = busca_em_matriz_ordenada(matriz_exemplo, 100)
    print(f"Procurando 100 -> posição: {resultado_ausente}")

    assert busca_em_matriz_ordenada(matriz_exemplo, 16) == (2, 3)
    assert busca_em_matriz_ordenada(matriz_exemplo, 100) is None
    assert busca_em_matriz_ordenada([], 1) is None
    assert busca_em_matriz_ordenada([[5]], 5) == (0, 0)
    print("Sanity checks OK.")
