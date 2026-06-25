"""
Indexação com loc/iloc, slicing e at/iat

O que este script demonstra: a diferença entre indexação por rótulo (loc) e por posição (iloc),
além dos acessores escalares at/iat, mais rápidos para um único valor.
Quando usar: loc quando você conhece o rótulo do índice/coluna; iloc quando importa só a posição.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame(
        {"produto": ["Mouse", "Teclado", "Monitor"], "preco": [50, 120, 800]},
        index=["p1", "p2", "p3"],
    )

    # loc usa rótulos: linha "p2", coluna "preco"
    preco_teclado = df.loc["p2", "preco"]

    # iloc usa posição inteira: primeira linha, todas as colunas
    primeira_linha = df.iloc[0, :]

    # slicing com loc inclui o limite final; com iloc, exclui (como em listas Python)
    fatia_loc = df.loc["p1":"p2"]
    fatia_iloc = df.iloc[0:2]

    # at/iat são otimizados para acessar um único escalar
    preco_via_at = df.at["p3", "preco"]
    preco_via_iat = df.iat[2, 1]

    assert preco_teclado == 120
    assert primeira_linha["produto"] == "Mouse"
    assert len(fatia_loc) == 2 and len(fatia_iloc) == 2
    assert preco_via_at == preco_via_iat == 800
    print(fatia_loc)
    print(fatia_iloc)
