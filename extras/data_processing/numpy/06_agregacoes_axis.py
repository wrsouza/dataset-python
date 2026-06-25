"""
Agregacoes com parametro axis em arrays 2D

O que este script demonstra: como sum/mean/std mudam de comportamento conforme o
eixo (axis) escolhido em uma matriz -- axis=0 agrega por coluna, axis=1 por linha.
Quando usar: para calcular estatisticas por linha ou coluna em datasets tabulares.
"""

import numpy as np

if __name__ == "__main__":
    # matriz 3x4: cada linha pode representar uma amostra, cada coluna uma feature
    matriz = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ], dtype=float)

    # sem axis: agrega TODOS os elementos em um unico numero
    soma_total = matriz.sum()

    # axis=0: percorre as LINHAS, agregando coluna a coluna -> resultado tem shape (4,)
    soma_colunas = matriz.sum(axis=0)
    media_colunas = matriz.mean(axis=0)

    # axis=1: percorre as COLUNAS, agregando linha a linha -> resultado tem shape (3,)
    soma_linhas = matriz.sum(axis=1)
    desvio_linhas = matriz.std(axis=1)

    print("matriz:\n", matriz)
    print("soma total:", soma_total)
    print("soma por coluna (axis=0):", soma_colunas)
    print("media por coluna (axis=0):", media_colunas)
    print("soma por linha (axis=1):", soma_linhas)
    print("desvio padrao por linha (axis=1):", desvio_linhas)

    # sanity checks
    assert soma_total == 78
    assert soma_colunas.tolist() == [15, 18, 21, 24]
    assert soma_linhas.tolist() == [10, 26, 42]
    assert soma_colunas.shape == (4,)
    assert soma_linhas.shape == (3,)
    print("OK: todos os asserts passaram.")
