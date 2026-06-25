"""
Leitura e escrita de Excel multi-aba

O que este script demonstra: gravar múltiplos DataFrames em abas separadas de um .xlsx e lê-los de volta.
Quando usar: quando o destino/origem dos dados é uma planilha Excel com várias abas relacionadas.
"""

import os
import tempfile
import pandas as pd

if __name__ == "__main__":
    vendas = pd.DataFrame({"produto": ["A", "B", "C"], "qtd": [10, 5, 8]})
    clientes = pd.DataFrame({"id": [1, 2], "nome": ["Loja X", "Loja Y"]})

    # arquivo temporário evita lixo persistente no repositório
    caminho = os.path.join(tempfile.gettempdir(), "exemplo_pandas_excel.xlsx")
    try:
        with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
            vendas.to_excel(writer, sheet_name="vendas", index=False)
            clientes.to_excel(writer, sheet_name="clientes", index=False)

        # sheet_name=None retorna um dict {nome_aba: DataFrame}
        abas = pd.read_excel(caminho, sheet_name=None, engine="openpyxl")

        assert set(abas.keys()) == {"vendas", "clientes"}
        assert abas["vendas"].shape == vendas.shape
        print(abas["vendas"])
        print(abas["clientes"])
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
