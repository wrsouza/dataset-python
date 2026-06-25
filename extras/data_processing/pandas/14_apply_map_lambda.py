"""
apply, map e applymap com lambdas

O que este script demonstra: diferenças entre Series.map (elemento a elemento em uma coluna),
DataFrame.apply (por coluna/linha) e DataFrame.map (elemento a elemento no DataFrame todo).
Quando usar: transformações que não têm uma função vetorizada pronta no pandas/numpy.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "produto": ["mouse", "teclado", "monitor"],
        "preco": [50, 120, 800],
        "desconto_pct": [10, 5, 15],
    })

    # Series.map: transforma cada valor de uma coluna usando uma função ou dict
    df["produto"] = df["produto"].map(lambda nome: nome.capitalize())

    # DataFrame.apply com axis=1: recebe a linha inteira, útil quando o cálculo cruza colunas
    df["preco_final"] = df.apply(lambda linha: linha["preco"] * (1 - linha["desconto_pct"] / 100), axis=1)

    # aplicar uma função elemento a elemento só nas colunas numéricas (map substitui o antigo applymap)
    colunas_numericas = ["preco", "desconto_pct", "preco_final"]
    df[colunas_numericas] = df[colunas_numericas].map(lambda v: round(v, 2))

    assert df.loc[0, "produto"] == "Mouse"
    assert df.loc[0, "preco_final"] == 45.0
    print(df)
