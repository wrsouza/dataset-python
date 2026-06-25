"""
Ordenação de DataFrame: sort_values multi-coluna e sort_index

O que este script demonstra: ordenar por mais de uma coluna com direções diferentes, e reordenar
pelo índice depois de embaralhar as linhas.
Quando usar: gerar rankings, relatórios ordenados ou restaurar a ordem original de um DataFrame.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "categoria": ["Tela", "Periférico", "Periférico", "Tela"],
        "preco": [800, 50, 120, 600],
    })

    # ordena por categoria crescente e, dentro de cada categoria, por preço decrescente
    ordenado = df.sort_values(by=["categoria", "preco"], ascending=[True, False]).reset_index(drop=True)

    # embaralha as linhas e depois usa sort_index para restaurar a ordem original
    embaralhado = df.sample(frac=1, random_state=42)
    restaurado = embaralhado.sort_index()

    assert ordenado.loc[0, "categoria"] == "Periférico"
    assert ordenado.loc[0, "preco"] == 120
    assert restaurado.equals(df)
    print(ordenado)
    print(restaurado)
