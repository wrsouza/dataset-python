"""
Leitura e escrita do formato JSON Lines (.jsonl)

O que este script demonstra: escrever um objeto JSON por linha (JSONL) e le-los de
volta de forma incremental, sem precisar carregar o arquivo inteiro como um unico
JSON valido.
Quando usar: em pipelines de dados/logs onde cada linha e um evento/registro
independente e se quer poder anexar (append) novos registros sem reescrever o arquivo.
"""

import json
import os
import tempfile
from typing import Iterator


def escrever_jsonl(caminho: str, registros: list[dict]) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        for registro in registros:
            # cada linha e um JSON completo e independente; sem virgulas entre linhas
            f.write(json.dumps(registro, ensure_ascii=False))
            f.write("\n")


def anexar_jsonl(caminho: str, registro: dict) -> None:
    """Append e o grande beneficio do JSONL: nao precisa reler/reescrever o arquivo todo."""
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False))
        f.write("\n")


def ler_jsonl(caminho: str) -> Iterator[dict]:
    """Le linha a linha - cada linha decodificada isoladamente, memoria O(1) por registro."""
    with open(caminho, "r", encoding="utf-8") as f:
        for numero_linha, linha in enumerate(f, start=1):
            linha = linha.strip()
            if not linha:
                continue  # tolera linhas vazias no fim do arquivo
            try:
                yield json.loads(linha)
            except json.JSONDecodeError as erro:
                raise ValueError(f"Linha {numero_linha} invalida no JSONL: {erro}") from erro


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_jsonl = os.path.join(tmp_dir, "eventos.jsonl")

    try:
        registros_iniciais = [
            {"evento": "login", "usuario": "ana"},
            {"evento": "compra", "usuario": "bruno", "valor": 99.9},
        ]
        escrever_jsonl(caminho_jsonl, registros_iniciais)

        anexar_jsonl(caminho_jsonl, {"evento": "logout", "usuario": "ana"})

        registros_lidos = list(ler_jsonl(caminho_jsonl))
        for registro in registros_lidos:
            print(registro)

        assert len(registros_lidos) == 3, "Deveria ter 2 iniciais + 1 anexado"
        assert registros_lidos[-1]["evento"] == "logout"
        print("OK: escrita, append e leitura de JSONL funcionaram corretamente.")
    finally:
        if os.path.exists(caminho_jsonl):
            os.remove(caminho_jsonl)
        os.rmdir(tmp_dir)
