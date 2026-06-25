"""
Tratamento de valores NaN (Not a Number)

O que este script demonstra: como detectar NaN com np.isnan, substituir valores
com np.nan_to_num e calcular medias ignorando NaN com np.nanmean.
Quando usar: ao processar dados reais com leituras ausentes/invalidas, comuns em
sensores, planilhas exportadas e pipelines de ETL.
"""

import numpy as np

if __name__ == "__main__":
    # array com valores ausentes representados por np.nan (simula leituras com falha)
    leituras = np.array([23.5, np.nan, 19.8, 25.1, np.nan, 21.0])

    # isnan: mascara booleana, True onde o valor e NaN
    mascara_nan = np.isnan(leituras)
    quantidade_nan = mascara_nan.sum()

    # mean() comum propaga NaN -- o resultado todo "contamina" com NaN
    media_comum = leituras.mean()

    # nanmean: calcula a media IGNORANDO os NaN (so considera valores validos)
    media_sem_nan = np.nanmean(leituras)

    # nan_to_num: substitui NaN por um valor fixo (default=0.0), util para depois
    # processar o array com funcoes que nao lidam bem com NaN
    leituras_substituidas = np.nan_to_num(leituras, nan=media_sem_nan)

    print("leituras:", leituras)
    print("mascara de NaN:", mascara_nan)
    print("quantidade de NaN:", quantidade_nan)
    print("media comum (propaga NaN):", media_comum)
    print("media com nanmean (ignora NaN):", media_sem_nan)
    print("leituras com NaN substituido pela media:", leituras_substituidas)

    # sanity checks
    assert quantidade_nan == 2
    assert np.isnan(media_comum)  # mean() comum fica contaminado por NaN
    assert not np.isnan(media_sem_nan)
    assert not np.any(np.isnan(leituras_substituidas))
    print("OK: todos os asserts passaram.")
