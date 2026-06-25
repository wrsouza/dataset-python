"""
Criacao de arrays com numpy

O que este script demonstra: as principais formas de criar arrays (np.array, zeros,
ones, arange, linspace) e como cada uma se comporta em termos de shape e dtype.
Quando usar: sempre que precisar inicializar dados numericos antes de processa-los.
"""

import numpy as np

if __name__ == "__main__":
    # np.array converte uma lista (ou lista de listas) em array, inferindo o dtype
    a = np.array([1, 2, 3, 4])
    matriz = np.array([[1, 2], [3, 4]])

    # zeros/ones recebem o shape desejado como tupla -- util para alocar buffers
    zeros = np.zeros((2, 3))
    ones = np.ones((3, 2))

    # arange gera valores com passo fixo (similar ao range do Python, mas em array)
    sequencia = np.arange(0, 10, 2)

    # linspace gera N valores igualmente espacados entre inicio e fim (inclusive)
    # diferente do arange, aqui controlamos a QUANTIDADE de pontos, nao o passo
    espacados = np.linspace(0, 1, 5)

    print("array 1D:", a)
    print("matriz 2D:\n", matriz)
    print("zeros:\n", zeros)
    print("ones:\n", ones)
    print("arange:", sequencia)
    print("linspace:", espacados)

    # sanity checks
    assert a.shape == (4,)
    assert matriz.shape == (2, 2)
    assert zeros.shape == (2, 3) and np.all(zeros == 0)
    assert ones.shape == (3, 2) and np.all(ones == 1)
    assert sequencia.tolist() == [0, 2, 4, 6, 8]
    assert len(espacados) == 5 and espacados[0] == 0 and espacados[-1] == 1
    print("OK: todos os asserts passaram.")
