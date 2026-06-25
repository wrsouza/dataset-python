"""
Leitura de CSV grande em chunks (blocos)

O que este script demonstra: ler um arquivo CSV grande em pedaços (chunks) ao invés de
carregar tudo na memoria de uma vez, usando csv.reader e pandas.read_csv(chunksize=...).
Quando usar: quando o arquivo CSV nao cabe confortavelmente na RAM disponivel ou quando
so e necessario agregar/filtrar dados sem manter o dataset completo em memoria.
"""

import csv
import os
import tempfile

import pandas as pd


def gerar_csv_grande(caminho: str, n_linhas: int = 10_000) -> None:
    """Gera um CSV sintetico com n_linhas para simular um arquivo grande."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "categoria", "valor"])
        for i in range(n_linhas):
            # categoria ciclica so para ter algo para agregar depois
            categoria = ["A", "B", "C"][i % 3]
            writer.writerow([i, categoria, i * 1.5])


def somar_valores_com_csv_reader(caminho: str, tamanho_bloco: int = 1000) -> float:
    """
    Le o arquivo em blocos manualmente com o modulo csv, acumulando apenas o total.
    Util quando nao se quer a dependencia do pandas ou se precisa de controle fino.
    """
    total = 0.0
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        bloco = []
        for linha in reader:
            bloco.append(linha)
            if len(bloco) >= tamanho_bloco:
                total += sum(float(r["valor"]) for r in bloco)
                bloco = []  # libera o bloco processado da memoria
        # processa o que restou (ultimo bloco pode ser menor que tamanho_bloco)
        if bloco:
            total += sum(float(r["valor"]) for r in bloco)
    return total


def somar_valores_com_pandas_chunksize(caminho: str, tamanho_bloco: int = 1000) -> float:
    """
    pandas.read_csv com chunksize retorna um iterador de DataFrames, cada um com
    no maximo `tamanho_bloco` linhas - a leitura real do disco tambem e incremental.
    """
    total = 0.0
    for chunk in pd.read_csv(caminho, chunksize=tamanho_bloco):
        total += chunk["valor"].sum()
    return total


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_csv = os.path.join(tmp_dir, "grande.csv")

    try:
        gerar_csv_grande(caminho_csv, n_linhas=10_000)

        total_csv = somar_valores_com_csv_reader(caminho_csv)
        total_pandas = somar_valores_com_pandas_chunksize(caminho_csv)

        print(f"Total via csv.DictReader em blocos: {total_csv}")
        print(f"Total via pandas chunksize:        {total_pandas}")

        # ambos os metodos devem chegar ao mesmo resultado (tolerancia por float)
        assert abs(total_csv - total_pandas) < 1e-6, "Os totais deveriam ser iguais"
        print("OK: leitura em chunks consistente entre csv e pandas.")
    finally:
        if os.path.exists(caminho_csv):
            os.remove(caminho_csv)
        os.rmdir(tmp_dir)
