"""
Achatamento (flatten) de JSON aninhado para tabela

O que este script demonstra: transformar estruturas JSON aninhadas (dicts dentro de
dicts, listas de objetos) em linhas planas adequadas para um CSV/DataFrame.
Quando usar: ao consumir APIs ou exports que retornam JSON hierarquico mas o destino
final e uma tabela (planilha, banco relacional, CSV).
"""

import json
from typing import Any


def flatten_dict(d: dict, prefixo: str = "", separador: str = ".") -> dict:
    """
    Achata um dict recursivamente. Chaves aninhadas viram "pai.filho".
    Listas sao mantidas como estao (serializadas) pois "explodir" listas em
    colunas geraria numero variavel de colunas - tratamos isso separadamente
    quando a lista representa registros (ver flatten_registros_com_lista).
    """
    resultado = {}
    for chave, valor in d.items():
        nova_chave = f"{prefixo}{separador}{chave}" if prefixo else chave
        if isinstance(valor, dict):
            resultado.update(flatten_dict(valor, nova_chave, separador))
        elif isinstance(valor, list):
            # lista de valores simples -> junta em string; lista de dicts -> serializa
            if valor and isinstance(valor[0], dict):
                resultado[nova_chave] = json.dumps(valor, ensure_ascii=False)
            else:
                resultado[nova_chave] = ";".join(str(v) for v in valor)
        else:
            resultado[nova_chave] = valor
    return resultado


def flatten_registros(registros: list[dict]) -> list[dict]:
    """Aplica flatten_dict em uma lista de registros JSON."""
    return [flatten_dict(r) for r in registros]


def colunas_unificadas(linhas_planas: list[dict]) -> list[str]:
    """Coleta o conjunto de todas as colunas vistas, preservando ordem de aparicao."""
    colunas: list[str] = []
    vistas = set()
    for linha in linhas_planas:
        for chave in linha:
            if chave not in vistas:
                vistas.add(chave)
                colunas.append(chave)
    return colunas


if __name__ == "__main__":
    dados_json = [
        {
            "id": 1,
            "nome": "Pedido 1",
            "cliente": {"nome": "Ana", "endereco": {"cidade": "Sao Paulo", "uf": "SP"}},
            "tags": ["urgente", "fragil"],
        },
        {
            "id": 2,
            "nome": "Pedido 2",
            "cliente": {"nome": "Bruno", "endereco": {"cidade": "Curitiba", "uf": "PR"}},
            "tags": [],
        },
    ]

    linhas = flatten_registros(dados_json)
    colunas = colunas_unificadas(linhas)

    print("Colunas resultantes:", colunas)
    for linha in linhas:
        print(linha)

    assert "cliente.endereco.cidade" in colunas, "Chave aninhada profunda deveria existir"
    assert linhas[0]["cliente.endereco.cidade"] == "Sao Paulo"
    assert linhas[0]["tags"] == "urgente;fragil"
    assert linhas[1]["tags"] == ""
    print("OK: JSON aninhado achatado corretamente.")
