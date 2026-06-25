"""
Leitura e escrita de CSV com pandas

O que este script demonstra: como ler/escrever CSV controlando encoding, separador e index.
Quando usar: ao trocar dados tabulares com sistemas externos que exigem delimitador ou encoding específicos.
"""

import io
import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "nome": ["Ana", "Bruno", "Célia"],
        "cidade": ["São Paulo", "Rio de Janeiro", "Belo Horizonte"],
        "salario": [5000.50, 6200.75, 4800.00],
    })

    # ; como separador é comum em locais que usam , como separador decimal
    buffer = io.StringIO()
    df.to_csv(buffer, sep=";", index=False, encoding="utf-8")

    # reposiciona o cursor para simular a leitura de um arquivo recém-escrito
    buffer.seek(0)
    df_lido = pd.read_csv(buffer, sep=";", encoding="utf-8")

    assert df_lido.shape == df.shape
    assert list(df_lido.columns) == ["nome", "cidade", "salario"]
    print(df_lido)
