"""
MultiIndex básico: stack e unstack

O que este script demonstra: criar um DataFrame com índice hierárquico (MultiIndex) e converter
entre representação "empilhada" (mais linhas) e "desempilhada" (mais colunas) com stack/unstack.
Quando usar: dados naturalmente hierárquicos (ex.: ano > mês, ou região > loja) e relatórios cruzados.
"""

import pandas as pd

if __name__ == "__main__":
    indice = pd.MultiIndex.from_tuples(
        [("2024", "Jan"), ("2024", "Fev"), ("2025", "Jan"), ("2025", "Fev")],
        names=["ano", "mes"],
    )
    df = pd.DataFrame({"vendas": [100, 120, 150, 170]}, index=indice)

    # unstack move o nível interno do índice (mes) para colunas -> formato largo
    largo = df["vendas"].unstack("mes")

    # stack faz o caminho inverso: colunas voltam a ser um nível do índice -> formato longo
    de_volta_longo = largo.stack().rename("vendas").to_frame()

    # acessar um sub-bloco do MultiIndex pelo primeiro nível
    apenas_2024 = df.loc["2024"]

    assert largo.shape == (2, 2)
    assert len(de_volta_longo) == 4
    assert len(apenas_2024) == 2
    print(largo)
    print(de_volta_longo)
