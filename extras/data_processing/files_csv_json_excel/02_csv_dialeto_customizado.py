"""
Deteccao automatica de dialeto CSV com csv.Sniffer

O que este script demonstra: usar csv.Sniffer para detectar automaticamente o
delimitador, aspas e outras caracteristicas de um CSV cujo formato e desconhecido.
Quando usar: ao receber arquivos CSV de fontes externas onde nao se sabe se o
separador e virgula, ponto-e-virgula, tab, etc.
"""

import csv
import io
import os
import tempfile


def gerar_csv_ponto_e_virgula(caminho: str) -> None:
    """Simula um CSV exportado de uma planilha em locale europeu (delimitador ';')."""
    conteudo = (
        "nome;idade;cidade\n"
        "Ana;30;Sao Paulo\n"
        "Bruno;25;Rio de Janeiro\n"
        "Carla;40;Belo Horizonte\n"
    )
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)


def detectar_dialeto(caminho: str) -> csv.Dialect:
    """
    Sniffer analisa uma amostra do arquivo e infere o dialeto (delimitador,
    aspas, etc). E preciso fornecer delimitadores candidatos para aumentar a
    chance de acerto quando a amostra e pequena ou ambigua.
    """
    with open(caminho, newline="", encoding="utf-8") as f:
        amostra = f.read(2048)
    sniffer = csv.Sniffer()
    dialeto = sniffer.sniff(amostra, delimiters=",;\t|")
    return dialeto


def ler_com_dialeto_detectado(caminho: str) -> list[dict]:
    dialeto = detectar_dialeto(caminho)
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, dialect=dialeto)
        return list(reader)


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_csv = os.path.join(tmp_dir, "europeu.csv")

    try:
        gerar_csv_ponto_e_virgula(caminho_csv)

        dialeto = detectar_dialeto(caminho_csv)
        print(f"Delimitador detectado: {dialeto.delimiter!r}")

        linhas = ler_com_dialeto_detectado(caminho_csv)
        for linha in linhas:
            print(linha)

        assert dialeto.delimiter == ";", "Deveria detectar ponto-e-virgula"
        assert len(linhas) == 3, "Deveria ler 3 linhas de dados"
        assert linhas[0]["nome"] == "Ana"
        print("OK: dialeto detectado e dados lidos corretamente.")
    finally:
        if os.path.exists(caminho_csv):
            os.remove(caminho_csv)
        os.rmdir(tmp_dir)
