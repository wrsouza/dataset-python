"""
Rotação e Transposição de Matriz em-place

Cenário: processamento de imagens (rotacionar uma matriz de pixels em 90
graus), manipulação de planilhas/tabelas (transpor linhas e colunas),
operações em grids de jogos (tabuleiros, puzzles).
O que este script demonstra: transposição em-place (trocar matriz[i][j] com
matriz[j][i]) seguida de inversão de cada linha para obter rotação de 90
graus no sentido horário, sem alocar uma matriz nova.
"""


def transpor_em_place(matriz: list[list]) -> None:
    """Troca matriz[i][j] <-> matriz[j][i] apenas no triângulo superior, evitando trocar duas vezes."""
    n = len(matriz)
    for i in range(n):
        for j in range(i + 1, n):
            matriz[i][j], matriz[j][i] = matriz[j][i], matriz[i][j]


def rotacionar_90_graus_horario_em_place(matriz: list[list]) -> None:
    """Rotação 90° horário = transpor + inverter cada linha. Funciona apenas para matrizes quadradas."""
    transpor_em_place(matriz)
    for linha in matriz:
        linha.reverse()  # reverse() em-place evita criar listas intermediárias


def imprimir_matriz(matriz: list[list]) -> None:
    for linha in matriz:
        print(linha)


if __name__ == "__main__":
    matriz = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print("Matriz original:")
    imprimir_matriz(matriz)

    rotacionar_90_graus_horario_em_place(matriz)

    print("\nMatriz após rotação 90° horário (em-place):")
    imprimir_matriz(matriz)
