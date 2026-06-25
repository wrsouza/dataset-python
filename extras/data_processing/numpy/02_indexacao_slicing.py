"""
Indexacao e slicing em arrays numpy

O que este script demonstra: slicing classico, indexacao booleana e fancy indexing
(indexar com listas/arrays de indices) em arrays 1D e 2D.
Quando usar: para selecionar subconjuntos de dados sem copiar tudo manualmente.
"""

import numpy as np

if __name__ == "__main__":
    arr = np.arange(10)  # [0..9]

    # slicing devolve uma VIEW (compartilha memoria com o array original)
    fatia = arr[2:7]
    fatia_passo = arr[::2]  # de 2 em 2

    matriz = np.arange(12).reshape(3, 4)
    # indexacao 2D: [linhas, colunas]
    linha0 = matriz[0, :]
    coluna1 = matriz[:, 1]
    submatriz = matriz[0:2, 1:3]

    # indexacao booleana: cria uma mascara e usa para filtrar
    mascara = arr % 2 == 0
    pares = arr[mascara]

    # fancy indexing: passar uma lista/array de indices explicitos
    indices = [0, 3, 5]
    selecionados = arr[indices]

    print("array original:", arr)
    print("fatia [2:7]:", fatia)
    print("fatia com passo [::2]:", fatia_passo)
    print("matriz:\n", matriz)
    print("linha0:", linha0)
    print("coluna1:", coluna1)
    print("submatriz:\n", submatriz)
    print("pares (mascara booleana):", pares)
    print("fancy indexing:", selecionados)

    # sanity checks
    assert fatia.tolist() == [2, 3, 4, 5, 6]
    assert fatia_passo.tolist() == [0, 2, 4, 6, 8]
    assert linha0.tolist() == [0, 1, 2, 3]
    assert coluna1.tolist() == [1, 5, 9]
    assert pares.tolist() == [0, 2, 4, 6, 8]
    assert selecionados.tolist() == [0, 3, 5]
    print("OK: todos os asserts passaram.")
