"""
Tratamento de valores nulos: fillna, dropna, interpolate

O que este script demonstra: três estratégias diferentes para lidar com dados ausentes em uma série/DataFrame.
Quando usar: fillna para valores padrão; dropna quando a linha incompleta não tem uso; interpolate para
séries numéricas onde faz sentido estimar o valor intermediário (ex.: séries temporais).
"""

import numpy as np
import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "dia": [1, 2, 3, 4, 5],
        "temperatura": [20.0, np.nan, np.nan, 26.0, 27.0],
        "observacao": ["ok", None, "sensor falhou", "ok", None],
    })

    # fillna com valor fixo para a coluna textual
    df_fillna = df.copy()
    df_fillna["observacao"] = df_fillna["observacao"].fillna("sem registro")

    # dropna remove linhas que têm qualquer nulo (útil quando a linha inteira é inútil sem o dado)
    df_dropna = df.dropna()

    # interpolate estima valores numéricos ausentes com base na tendência da série
    df_interp = df.copy()
    df_interp["temperatura"] = df_interp["temperatura"].interpolate()

    assert df_fillna["observacao"].isna().sum() == 0
    assert len(df_dropna) == 2
    assert not df_interp["temperatura"].isna().any()
    print(df_fillna)
    print(df_dropna)
    print(df_interp)
