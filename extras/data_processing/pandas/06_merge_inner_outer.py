"""
Merge com inner/outer/left/right

O que este script demonstra: como o parâmetro how de pd.merge muda quais linhas sobrevivem ao combinar
dois DataFrames pela mesma chave.
Quando usar: ao juntar tabelas relacionadas (ex.: pedidos e clientes) e decidir o que fazer com chaves sem par.
"""

import pandas as pd

if __name__ == "__main__":
    clientes = pd.DataFrame({"cliente_id": [1, 2, 3], "nome": ["Ana", "Bruno", "Célia"]})
    pedidos = pd.DataFrame({"cliente_id": [2, 3, 4], "valor": [100, 200, 300]})

    # inner: só chaves presentes em ambos
    inner = pd.merge(clientes, pedidos, on="cliente_id", how="inner")
    # outer: todas as chaves, com NaN onde não há correspondência
    outer = pd.merge(clientes, pedidos, on="cliente_id", how="outer")
    # left: mantém todos os clientes, mesmo sem pedido
    left = pd.merge(clientes, pedidos, on="cliente_id", how="left")
    # right: mantém todos os pedidos, mesmo sem cliente cadastrado
    right = pd.merge(clientes, pedidos, on="cliente_id", how="right")

    assert len(inner) == 2
    assert len(outer) == 4
    assert len(left) == 3
    assert len(right) == 3
    print(inner)
    print(outer)
