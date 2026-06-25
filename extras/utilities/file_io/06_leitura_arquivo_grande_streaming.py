"""
Leitura de arquivo grande via streaming (linha a linha)

O que este script demonstra: como processar um arquivo grande iterando linha por linha
em vez de usar read()/readlines(), mantendo o uso de memória constante.
Quando usar: ao processar arquivos (logs, CSVs) maiores que a memória disponível.
"""

import tempfile
from pathlib import Path

def gerar_arquivo_grande(caminho: Path, n_linhas: int):
    # escreve em streaming também, sem montar uma string gigante em memória antes
    with open(caminho, mode="w", encoding="utf-8") as f:
        for i in range(n_linhas):
            f.write(f"linha numero {i}\n")

def contar_linhas_streaming(caminho: Path):
    contador = 0
    # iterar sobre o objeto arquivo le uma linha por vez (buffer interno), nao tudo de uma vez
    with open(caminho, mode="r", encoding="utf-8") as f:
        for _linha in f:
            contador += 1
    return contador

def somar_valor_de_linhas_filtradas(caminho: Path, prefixo_buscado, limite=None):
    # processa o arquivo sem nunca manter mais que uma linha por vez em memória
    total_encontrado = 0
    with open(caminho, mode="r", encoding="utf-8") as f:
        for numero_linha, linha in enumerate(f, start=1):
            if linha.startswith(prefixo_buscado):
                total_encontrado += 1
            if limite is not None and numero_linha >= limite:
                break
    return total_encontrado


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        caminho = Path(tmp_dir) / "arquivo_grande.txt"

        n_linhas = 50_000  # simula um arquivo "grande" sem realmente ocupar muita memória
        gerar_arquivo_grande(caminho, n_linhas)
        print("Tamanho do arquivo gerado:", caminho.stat().st_size, "bytes")

        total = contar_linhas_streaming(caminho)
        print("Total de linhas contadas via streaming:", total)
        assert total == n_linhas

        # busca limitada às primeiras 100 linhas, todas começam com "linha"
        encontradas = somar_valor_de_linhas_filtradas(caminho, "linha", limite=100)
        print("Linhas com prefixo 'linha' nas primeiras 100:", encontradas)
        assert encontradas == 100

        print("Todos os testes de sanity check passaram.")
