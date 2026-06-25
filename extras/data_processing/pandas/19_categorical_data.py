"""
Dados categóricos e ordenação categórica

O que este script demonstra: converter uma coluna de texto repetitivo para o tipo category
(menos memória) e definir uma ordem lógica entre as categorias para comparações/ordenação.
Quando usar: colunas com poucos valores distintos repetidos muitas vezes (status, nível, prioridade).
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "chamado": [1, 2, 3, 4, 5],
        "prioridade": ["media", "baixa", "alta", "alta", "media"],
    })

    # categories define a ordem lógica; ordered=True habilita comparações como < e >
    ordem_prioridade = pd.CategoricalDtype(categories=["baixa", "media", "alta"], ordered=True)
    df["prioridade"] = df["prioridade"].astype(ordem_prioridade)

    # com a ordem definida, sort_values respeita baixa < media < alta, não a ordem alfabética
    ordenado = df.sort_values("prioridade")

    # comparação direta só é possível porque a categoria é ordered
    urgentes = df[df["prioridade"] >= "media"]

    assert df["prioridade"].dtype.name == "category"
    assert list(ordenado["prioridade"]) == ["baixa", "media", "media", "alta", "alta"]
    assert len(urgentes) == 4
    print(ordenado)
    print(df["prioridade"].cat.categories)
