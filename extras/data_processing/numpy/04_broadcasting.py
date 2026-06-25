"""
Broadcasting entre arrays de shapes diferentes

O que este script demonstra: como o numpy "expande" arrays de shapes compativeis
para realizar operacoes elementwise sem copiar dados explicitamente.
Quando usar: para combinar arrays de dimensoes diferentes (ex: vetor + matriz) sem
escrever loops manuais de repeticao.
"""

import numpy as np

if __name__ == "__main__":
    # regra do broadcasting: dimensoes sao comparadas da direita para a esquerda;
    # sao compativeis se forem iguais OU se uma delas for 1.

    # caso 1: coluna (3,1) com linha (1,4) -> resultado (3,4)
    coluna = np.array([[1], [2], [3]])       # shape (3, 1)
    linha = np.array([[10, 20, 30, 40]])     # shape (1, 4)
    soma = coluna + linha                     # broadcast para (3, 4)

    # caso 2: matriz (3,3) com escalar -> escalar e tratado como shape ()
    matriz = np.arange(9).reshape(3, 3)
    matriz_x10 = matriz * 10

    # caso 3: matriz (3,3) com vetor (3,) -> vetor e replicado em cada linha
    vetor = np.array([1, 2, 3])
    matriz_mais_vetor = matriz + vetor

    print("coluna (3,1):\n", coluna)
    print("linha (1,4):\n", linha)
    print("soma broadcast (3,4):\n", soma)
    print("matriz x10:\n", matriz_x10)
    print("matriz + vetor (broadcast por linha):\n", matriz_mais_vetor)

    # sanity checks
    assert soma.shape == (3, 4)
    assert soma[0, 0] == 11 and soma[2, 3] == 43
    assert np.array_equal(matriz_x10, matriz * 10)
    assert matriz_mais_vetor[0].tolist() == [1, 3, 5]  # [0,1,2] + [1,2,3]
    print("OK: todos os asserts passaram.")
