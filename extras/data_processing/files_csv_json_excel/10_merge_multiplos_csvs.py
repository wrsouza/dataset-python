"""
Combinar N arquivos CSV em um unico dataset

O que este script demonstra: ler varios arquivos CSV (possivelmente com colunas em
ordens diferentes) e concatena-los em um unico dataset consistente, registrando a
origem de cada linha.
Quando usar: ao consolidar exports particionados (ex: um CSV por mes, ou por loja)
em uma base unica para analise.
"""

import csv
import os
import tempfile

import pandas as pd


def gerar_csvs_de_exemplo(pasta: str) -> list[str]:
    """Gera 3 CSVs com mesmas colunas mas em ordens diferentes, simulando exports reais."""
    arquivos = []

    caminho1 = os.path.join(pasta, "loja_norte.csv")
    with open(caminho1, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["produto", "quantidade", "preco"])
        writer.writerow(["Mouse", 10, 49.9])
        writer.writerow(["Teclado", 5, 120.0])
    arquivos.append(caminho1)

    caminho2 = os.path.join(pasta, "loja_sul.csv")
    with open(caminho2, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["preco", "produto", "quantidade"])  # ordem diferente
        writer.writerow([35.0, "Mousepad", 20])
    arquivos.append(caminho2)

    caminho3 = os.path.join(pasta, "loja_leste.csv")
    with open(caminho3, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["produto", "quantidade", "preco"])
        writer.writerow(["Monitor", 3, 800.0])
    arquivos.append(caminho3)

    return arquivos


def merge_csvs(caminhos: list[str]) -> pd.DataFrame:
    """
    Concatena todos os CSVs alinhando colunas pelo NOME (nao pela posicao), o que
    e essencial quando arquivos de origens diferentes nao garantem a mesma ordem.
    Adiciona uma coluna 'arquivo_origem' para rastreabilidade.
    """
    dataframes = []
    for caminho in caminhos:
        df = pd.read_csv(caminho)
        df["arquivo_origem"] = os.path.basename(caminho)
        dataframes.append(df)
    # ignore_index reindexa o resultado final (0..N-1) em vez de repetir indices por arquivo
    return pd.concat(dataframes, ignore_index=True)


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()

    try:
        caminhos = gerar_csvs_de_exemplo(tmp_dir)
        dataset = merge_csvs(caminhos)

        print(dataset)
        print(f"\nTotal de linhas combinadas: {len(dataset)}")

        assert len(dataset) == 4, "Deveria combinar 2 + 1 + 1 = 4 linhas"
        assert set(dataset.columns) == {"produto", "quantidade", "preco", "arquivo_origem"}
        assert "loja_sul.csv" in dataset["arquivo_origem"].values
        print("OK: merge de multiplos CSVs com colunas em ordens diferentes funcionou.")
    finally:
        for caminho in os.listdir(tmp_dir):
            os.remove(os.path.join(tmp_dir, caminho))
        os.rmdir(tmp_dir)
