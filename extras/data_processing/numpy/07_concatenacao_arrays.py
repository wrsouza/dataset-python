"""
Concatenacao e empilhamento de arrays

O que este script demonstra: as diferencas entre np.concatenate, np.stack,
np.hstack e np.vstack ao combinar arrays.
Quando usar: para juntar lotes de dados (ex: batches) ou montar matrizes a partir
de vetores separados.
"""

import numpy as np

if __name__ == "__main__":
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    # concatenate: junta arrays ao longo de um eixo EXISTENTE (nao cria eixo novo)
    concatenado = np.concatenate([a, b])

    # stack: cria um eixo NOVO, empilhando os arrays como se fossem "camadas"
    apilado = np.stack([a, b])  # shape (2, 3)

    # hstack: concatena horizontalmente (equivalente a concatenate para 1D)
    horizontal = np.hstack([a, b])

    # vstack: concatena verticalmente, tratando 1D como linhas de uma matriz 2D
    vertical = np.vstack([a, b])  # shape (2, 3), igual ao stack aqui

    # com matrizes 2D a diferenca entre hstack/vstack fica mais clara
    m1 = np.array([[1, 2], [3, 4]])
    m2 = np.array([[5, 6], [7, 8]])
    m_horizontal = np.hstack([m1, m2])  # junta colunas -> shape (2, 4)
    m_vertical = np.vstack([m1, m2])    # junta linhas -> shape (4, 2)

    print("concatenate 1D:", concatenado)
    print("stack 1D (novo eixo):\n", apilado)
    print("hstack 1D:", horizontal)
    print("vstack 1D:\n", vertical)
    print("hstack 2D:\n", m_horizontal)
    print("vstack 2D:\n", m_vertical)

    # sanity checks
    assert concatenado.tolist() == [1, 2, 3, 4, 5, 6]
    assert apilado.shape == (2, 3)
    assert horizontal.tolist() == [1, 2, 3, 4, 5, 6]
    assert vertical.shape == (2, 3)
    assert m_horizontal.shape == (2, 4)
    assert m_vertical.shape == (4, 2)
    print("OK: todos os asserts passaram.")
