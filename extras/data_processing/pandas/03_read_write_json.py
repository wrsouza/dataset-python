"""
Leitura e escrita de JSON com pandas

O que este script demonstra: read_json/to_json com diferentes orientações e normalização de JSON aninhado.
Quando usar: ao integrar com APIs ou arquivos JSON que precisam virar tabela (ou vice-versa).
"""

import io
import pandas as pd
from pandas import json_normalize

if __name__ == "__main__":
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "produto": ["Mouse", "Teclado", "Monitor"],
        "preco": [50.0, 120.0, 800.0],
    })

    # orient="records" gera uma lista de objetos, formato mais comum em APIs
    json_records = df.to_json(orient="records", force_ascii=False)
    # read_json trata strings simples como caminho de arquivo; um buffer evita essa ambiguidade
    df_de_volta = pd.read_json(io.StringIO(json_records), orient="records")
    assert df_de_volta.shape == df.shape

    # JSON aninhado típico de uma API: precisa de normalização para virar tabela plana
    dados_aninhados = [
        {"id": 1, "cliente": {"nome": "Ana", "endereco": {"cidade": "SP"}}},
        {"id": 2, "cliente": {"nome": "Bruno", "endereco": {"cidade": "RJ"}}},
    ]
    df_normalizado = json_normalize(dados_aninhados, sep="_")

    assert "cliente_endereco_cidade" in df_normalizado.columns
    print(df_de_volta)
    print(df_normalizado)
