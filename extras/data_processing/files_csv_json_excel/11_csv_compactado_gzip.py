"""
Leitura e escrita de CSV compactado (.csv.gz)

O que este script demonstra: usar o modulo gzip para escrever e ler um CSV
compactado diretamente, sem precisar descompactar para um arquivo intermediario.
Quando usar: ao lidar com arquivos de log/export grandes onde economizar espaco em
disco (e largura de banda, se for transferido) compensa o custo de (de)compressao.
"""

import csv
import gzip
import io
import os
import tempfile


def escrever_csv_gz(caminho: str, linhas: list[list]) -> None:
    """
    Abre o .gz em modo texto ('wt') para poder usar csv.writer normalmente -
    gzip.open cuida da compressao por baixo dos panos de forma transparente.
    """
    with gzip.open(caminho, "wt", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(linhas)


def ler_csv_gz(caminho: str) -> list[list]:
    with gzip.open(caminho, "rt", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def tamanho_compactado_vs_original(linhas: list[list]) -> tuple[int, int]:
    """Calcula o tamanho do CSV puro vs compactado, so para fins ilustrativos."""
    buffer_texto = io.StringIO()
    csv.writer(buffer_texto).writerows(linhas)
    tamanho_original = len(buffer_texto.getvalue().encode("utf-8"))

    buffer_gz = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer_gz, mode="wb") as gz:
        gz.write(buffer_texto.getvalue().encode("utf-8"))
    tamanho_compactado = len(buffer_gz.getvalue())

    return tamanho_original, tamanho_compactado


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_gz = os.path.join(tmp_dir, "dados.csv.gz")

    try:
        cabecalho = ["id", "descricao"]
        # texto repetitivo compacta bem, e util para visualizar a diferenca de tamanho
        linhas = [cabecalho] + [[i, "produto repetido " * 5] for i in range(200)]

        escrever_csv_gz(caminho_gz, linhas)
        linhas_lidas = ler_csv_gz(caminho_gz)

        tamanho_original, tamanho_compactado = tamanho_compactado_vs_original(linhas)
        print(f"Tamanho original (estimado): {tamanho_original} bytes")
        print(f"Tamanho compactado (estimado): {tamanho_compactado} bytes")
        print(f"Linhas lidas de volta: {len(linhas_lidas)}")

        assert linhas_lidas[0] == cabecalho
        assert len(linhas_lidas) == len(linhas)
        assert tamanho_compactado < tamanho_original, "Compressao deveria reduzir o tamanho"
        print("OK: CSV compactado em gzip escrito e lido corretamente.")
    finally:
        if os.path.exists(caminho_gz):
            os.remove(caminho_gz)
        os.rmdir(tmp_dir)
