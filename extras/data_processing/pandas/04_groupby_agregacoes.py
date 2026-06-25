"""
GroupBy com múltiplas agregações

O que este script demonstra: uso de groupby().agg() para calcular várias métricas por grupo de uma vez.
Quando usar: ao resumir dados transacionais em estatísticas por categoria (soma, média, contagem etc.).
"""

import pandas as pd

if __name__ == "__main__":
    vendas = pd.DataFrame({
        "categoria": ["Eletrônicos", "Eletrônicos", "Roupas", "Roupas", "Roupas", "Alimentos"],
        "valor": [1200, 800, 150, 200, 90, 30],
        "quantidade": [2, 1, 3, 2, 1, 10],
    })

    # agg com dict permite funções diferentes por coluna em uma única passada
    resumo = vendas.groupby("categoria").agg(
        total_valor=("valor", "sum"),
        media_valor=("valor", "mean"),
        qtd_pedidos=("valor", "count"),
        total_itens=("quantidade", "sum"),
    ).reset_index()

    assert resumo.loc[resumo["categoria"] == "Roupas", "qtd_pedidos"].iloc[0] == 3
    print(resumo)
