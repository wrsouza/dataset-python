"""
Ordenacao de arrays: sort, argsort, argmax, argmin

O que este script demonstra: como ordenar valores diretamente (np.sort) e como obter
os INDICES que ordenariam/maximizariam/minimizariam um array (argsort/argmax/argmin).
Quando usar: quando a posicao original do dado importa tanto quanto o valor (ex:
"quais sao os 3 melhores e em que posicao do array original eles estavam").
"""

import numpy as np

if __name__ == "__main__":
    pontuacoes = np.array([55, 89, 12, 76, 34, 99, 41])

    # sort: retorna uma NOVA array com os valores ordenados (nao altera o original)
    ordenado = np.sort(pontuacoes)

    # argsort: retorna os INDICES que ordenariam o array original (ascendente)
    indices_ordenados = np.argsort(pontuacoes)

    # para ordem descendente, basta inverter os indices
    indices_desc = indices_ordenados[::-1]
    top3_indices = indices_desc[:3]
    top3_valores = pontuacoes[top3_indices]

    # argmax/argmin: indice do maior/menor valor (atalho para argsort()[-1]/[0])
    indice_maior = np.argmax(pontuacoes)
    indice_menor = np.argmin(pontuacoes)

    print("pontuacoes originais:", pontuacoes)
    print("ordenado (np.sort):", ordenado)
    print("indices que ordenam (argsort):", indices_ordenados)
    print("top3 indices (originais):", top3_indices, "-> valores:", top3_valores)
    print("indice do maior (argmax):", indice_maior, "valor:", pontuacoes[indice_maior])
    print("indice do menor (argmin):", indice_menor, "valor:", pontuacoes[indice_menor])

    # sanity checks
    assert ordenado.tolist() == [12, 34, 41, 55, 76, 89, 99]
    assert pontuacoes[indices_ordenados].tolist() == ordenado.tolist()
    assert pontuacoes[indice_maior] == 99
    assert pontuacoes[indice_menor] == 12
    assert top3_valores.tolist() == [99, 89, 76]
    print("OK: todos os asserts passaram.")
