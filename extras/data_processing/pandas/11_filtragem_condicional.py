"""
Filtragem condicional: booleanos, query() e isin()

O que este script demonstra: três formas equivalentes de filtrar linhas de um DataFrame.
Quando usar: query() para legibilidade com expressões complexas; isin() para listas de valores aceitos.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "produto": ["Mouse", "Teclado", "Monitor", "Cabo", "Webcam"],
        "preco": [50, 120, 800, 15, 200],
        "categoria": ["Periférico", "Periférico", "Tela", "Acessório", "Periférico"],
    })

    # indexação booleana clássica
    caros = df[df["preco"] > 100]

    # query() lê como uma expressão SQL-like, útil para condições compostas
    caros_perifericos = df.query("preco > 100 and categoria == 'Periférico'")

    # isin() filtra por pertencimento a uma lista de valores
    selecionados = df[df["categoria"].isin(["Tela", "Acessório"])]

    assert len(caros) == 3
    assert len(caros_perifericos) == 2
    assert len(selecionados) == 2
    print(caros)
    print(caros_perifericos)
    print(selecionados)
