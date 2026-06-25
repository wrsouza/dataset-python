"""
Pivot table com múltiplas métricas

O que este script demonstra: pivot_table cruzando categorias em linhas/colunas e aplicando
mais de uma função de agregação ao mesmo tempo.
Quando usar: para gerar relatórios cruzados tipo "tabela dinâmica" de planilha eletrônica.
"""

import pandas as pd

if __name__ == "__main__":
    vendas = pd.DataFrame({
        "mes": ["Jan", "Jan", "Fev", "Fev", "Jan", "Fev"],
        "regiao": ["Sul", "Norte", "Sul", "Norte", "Sul", "Sul"],
        "valor": [100, 80, 150, 90, 120, 200],
    })

    # values, index e columns definem a forma da tabela; aggfunc pode ser uma lista
    tabela = pd.pivot_table(
        vendas,
        values="valor",
        index="mes",
        columns="regiao",
        aggfunc=["sum", "mean"],
        fill_value=0,
    )

    assert tabela.shape[0] == 2
    print(tabela)
