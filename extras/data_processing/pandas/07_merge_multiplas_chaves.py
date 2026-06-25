"""
Merge por múltiplas colunas-chave

O que este script demonstra: combinar DataFrames usando uma chave composta (mais de uma coluna em "on").
Quando usar: quando uma única coluna não identifica unicamente o relacionamento entre as tabelas.
"""

import pandas as pd

if __name__ == "__main__":
    estoque = pd.DataFrame({
        "loja": ["A", "A", "B", "B"],
        "produto": ["Mouse", "Teclado", "Mouse", "Teclado"],
        "estoque": [10, 5, 20, 15],
    })
    vendas = pd.DataFrame({
        "loja": ["A", "A", "B"],
        "produto": ["Mouse", "Teclado", "Mouse"],
        "vendido": [3, 1, 8],
    })

    # a combinação (loja, produto) é a chave real; usar só "produto" geraria duplicação incorreta
    combinado = pd.merge(estoque, vendas, on=["loja", "produto"], how="left")
    combinado["vendido"] = combinado["vendido"].fillna(0)
    combinado["saldo"] = combinado["estoque"] - combinado["vendido"]

    assert combinado.shape[0] == 4
    assert combinado.loc[(combinado["loja"] == "B") & (combinado["produto"] == "Teclado"), "vendido"].iloc[0] == 0
    print(combinado)
