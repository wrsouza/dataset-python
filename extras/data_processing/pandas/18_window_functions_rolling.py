"""
Window functions: rolling, expanding e médias móveis

O que este script demonstra: cálculo de média móvel com janela fixa (rolling) e estatística
acumulada desde o início da série (expanding).
Quando usar: análise de séries temporais, suavização de ruído e cálculos acumulados (ex.: saldo total).
"""

import pandas as pd

if __name__ == "__main__":
    datas = pd.date_range("2024-01-01", periods=10, freq="D")
    vendas = pd.Series([100, 120, 90, 150, 200, 180, 130, 170, 160, 190], index=datas)

    # rolling(3): média dos últimos 3 dias; os 2 primeiros ficam NaN por falta de janela completa
    media_movel_3d = vendas.rolling(window=3).mean()

    # expanding: acumula desde o primeiro ponto até a linha atual (cresce a cada passo)
    media_acumulada = vendas.expanding().mean()

    # min_periods permite obter resultado mesmo sem a janela completa no início
    media_movel_flex = vendas.rolling(window=3, min_periods=1).mean()

    assert media_movel_3d.iloc[:2].isna().all()
    assert not media_movel_flex.iloc[:2].isna().any()
    assert media_acumulada.iloc[-1] == round(vendas.mean(), 10) or abs(media_acumulada.iloc[-1] - vendas.mean()) < 1e-9
    print(media_movel_3d)
    print(media_acumulada)
