"""
Melt (wide -> long) e o caminho inverso (long -> wide)

O que este script demonstra: usar melt para transformar colunas em linhas (formato longo) e
pivot para reconstruir o formato largo original.
Quando usar: ao preparar dados para ferramentas de plot/análise que exigem formato longo (tidy data).
"""

import pandas as pd

if __name__ == "__main__":
    largo = pd.DataFrame({
        "produto": ["A", "B"],
        "jan": [100, 200],
        "fev": [110, 190],
        "mar": [120, 210],
    })

    # id_vars fica fixo; as demais colunas viram pares (variable, value)
    longo = largo.melt(id_vars="produto", var_name="mes", value_name="valor")

    # pivot reverte: cada combinação (produto, mes) volta a ser uma célula única
    de_volta_largo = longo.pivot(index="produto", columns="mes", values="valor").reset_index()
    de_volta_largo = de_volta_largo[["produto", "jan", "fev", "mar"]]

    assert longo.shape == (6, 3)
    assert de_volta_largo.equals(largo)
    print(longo)
    print(de_volta_largo)
