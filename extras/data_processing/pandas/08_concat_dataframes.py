"""
Concat de DataFrames por linha e por coluna

O que este script demonstra: pd.concat empilhando DataFrames verticalmente (axis=0) e
combinando-os lado a lado horizontalmente (axis=1).
Quando usar: ao juntar lotes de dados com o mesmo esquema, ou ao alinhar colunas extras pelo índice.
"""

import pandas as pd

if __name__ == "__main__":
    lote1 = pd.DataFrame({"id": [1, 2], "valor": [10, 20]})
    lote2 = pd.DataFrame({"id": [3, 4], "valor": [30, 40]})

    # axis=0 (padrão): empilha linhas, ignore_index evita índices duplicados
    empilhado = pd.concat([lote1, lote2], axis=0, ignore_index=True)

    extra = pd.DataFrame({"observacao": ["ok", "ok", "revisar", "ok"]})
    # axis=1: junta colunas lado a lado, alinhando pelo índice posicional
    com_observacao = pd.concat([empilhado, extra], axis=1)

    assert empilhado.shape == (4, 2)
    assert com_observacao.shape == (4, 3)
    print(empilhado)
    print(com_observacao)
