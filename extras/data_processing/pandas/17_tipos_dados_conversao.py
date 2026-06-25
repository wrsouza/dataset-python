"""
Conversão de tipos de dados: astype, to_datetime, to_numeric

O que este script demonstra: converter colunas de texto para tipos numéricos e de data, incluindo
tratamento de valores inválidos que não podem ser convertidos.
Quando usar: ao receber dados de CSV/Excel onde tudo chega como string e precisa ser tipado corretamente.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "data_compra": ["2024-01-10", "2024-02-15", "2024-03-01", "data invalida"],
        "valor": ["100.50", "200", "abc", "50.25"],
    })

    # astype funciona quando não há valores problemáticos na conversão
    df["id"] = df["id"].astype(int)

    # errors="coerce" transforma entradas inválidas em NaT/NaN em vez de lançar exceção
    df["data_compra"] = pd.to_datetime(df["data_compra"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    assert df["id"].dtype == "int64"
    assert df["data_compra"].isna().sum() == 1
    assert df["valor"].isna().sum() == 1
    print(df)
    print(df.dtypes)
