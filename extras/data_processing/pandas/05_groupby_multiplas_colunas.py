"""
GroupBy por múltiplas colunas e transform

O que este script demonstra: agrupar por mais de uma coluna e usar transform para devolver valores
agregados alinhados ao DataFrame original (sem reduzir o número de linhas).
Quando usar: ao precisar comparar cada linha com a estatística do seu próprio grupo (ex.: % do total).
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "regiao": ["Sul", "Sul", "Sul", "Norte", "Norte"],
        "loja": ["A", "A", "B", "C", "C"],
        "venda": [100, 150, 200, 80, 120],
    })

    # groupby com lista de colunas cria chaves compostas (regiao, loja)
    agrupado = df.groupby(["regiao", "loja"])["venda"].sum().reset_index()

    # transform mantém o mesmo shape do df original, útil para cálculos linha a linha
    df["total_regiao"] = df.groupby("regiao")["venda"].transform("sum")
    df["pct_da_regiao"] = df["venda"] / df["total_regiao"]

    assert len(df) == 5
    assert abs(df.loc[df["regiao"] == "Sul", "pct_da_regiao"].sum() - 1.0) < 1e-9
    print(agrupado)
    print(df)
