"""
Remoção de duplicatas com duplicated/drop_duplicates

O que este script demonstra: identificar e remover linhas duplicadas, inclusive considerando apenas
um subconjunto de colunas como critério de duplicidade.
Quando usar: ao limpar dados com registros repetidos por erro de coleta ou múltiplas exportações.
"""

import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame({
        "email": ["ana@x.com", "bruno@x.com", "ana@x.com", "celia@x.com"],
        "nome": ["Ana", "Bruno", "Ana Paula", "Célia"],
        "pedido": [1, 2, 3, 4],
    })

    # duplicated() marca True a partir da 2ª ocorrência (mantendo a primeira como referência)
    marcadas = df.duplicated(subset="email")

    # drop_duplicates com keep="last" mantém o registro mais recente por e-mail
    df_sem_duplicatas = df.drop_duplicates(subset="email", keep="last").reset_index(drop=True)

    assert marcadas.sum() == 1
    assert len(df_sem_duplicatas) == 3
    # ana@x.com deve ter ficado com o pedido 3 (a última ocorrência)
    assert df_sem_duplicatas.loc[df_sem_duplicatas["email"] == "ana@x.com", "pedido"].iloc[0] == 3
    print(marcadas)
    print(df_sem_duplicatas)
