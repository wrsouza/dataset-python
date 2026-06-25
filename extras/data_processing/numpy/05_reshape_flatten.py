"""
Reshape, ravel, flatten e transpose

O que este script demonstra: como mudar a forma (shape) de um array sem alterar seus
dados, e a diferenca entre ravel (view, quando possivel) e flatten (sempre copia).
Quando usar: para adaptar a forma dos dados ao formato exigido por uma operacao ou
algoritmo, sem precisar reconstruir o array do zero.
"""

import numpy as np

if __name__ == "__main__":
    arr = np.arange(12)  # 12 elementos, shape (12,)

    # reshape: reorganiza os mesmos dados em outra shape (linha a linha, ordem C)
    matriz = arr.reshape(3, 4)

    # ravel: tenta devolver uma VIEW 1D (compartilha memoria quando o array e contiguo)
    achatado_view = matriz.ravel()

    # flatten: SEMPRE devolve uma COPIA 1D independente
    achatado_copia = matriz.flatten()

    # transpose (.T): inverte os eixos -- (3,4) vira (4,3)
    transposta = matriz.T

    # provando que ravel compartilha memoria quando possivel: alterar a "view"
    # afeta o original SE o array for contiguo (caso deste exemplo). Em casos onde
    # o array nao e contiguo (ex: apos um slicing com passo), ravel cai para copia.
    achatado_view[0] = 999
    afeta_original = bool(matriz[0, 0] == 999)

    # restaura para nao confundir os proximos asserts
    matriz[0, 0] = 0
    achatado_view[0] = 0

    print("array original:", arr)
    print("matriz (3,4):\n", matriz)
    print("ravel (view):", achatado_view)
    print("flatten (copia):", achatado_copia)
    print("transposta (4,3):\n", transposta)
    print("ravel altera o original?", afeta_original)

    # sanity checks
    assert matriz.shape == (3, 4)
    assert transposta.shape == (4, 3)
    assert afeta_original is True
    assert achatado_copia[0] == 0  # flatten foi tirado antes da alteracao via ravel
    print("OK: todos os asserts passaram.")
