"""
Dedupe de lista preservando a ordem original

Cenario: ao consolidar logs, IDs de pedidos ou itens importados de varias
fontes, e comum acabar com duplicados, mas a ordem de chegada importa
(ex.: primeira ocorrencia define a posicao para auditoria).
O que este script demonstra: como remover duplicados sem usar set() puro
(que perde ordem) e uma variante para dados nao-hashable (listas/dicts).
"""

from typing import Hashable, Iterable, List, Any


def dedupe_mantendo_ordem(itens: Iterable[Hashable]) -> List[Hashable]:
    """Remove duplicados preservando a ordem de primeira aparicao.

    Um set() simples (list(set(itens))) seria mais rapido, mas a ordem
    de iteracao de um set nao e garantida -- por isso usamos um set
    apenas como "memoria" de vistos, e a lista de saida controla a ordem.
    """
    vistos = set()
    resultado = []
    for item in itens:
        if item not in vistos:
            vistos.add(item)
            resultado.append(item)
    return resultado


def dedupe_nao_hashable(itens: Iterable[Any], chave=None) -> List[Any]:
    """Versao para itens nao-hashable (ex.: dicts), usando lista de vistos.

    Custo O(n*m) -- aceitavel para listas pequenas/medias. Para volumes
    grandes, prefira extrair uma chave hashable (id, tupla de campos) e
    aplicar dedupe_mantendo_ordem com essa chave.
    """
    vistos = []
    resultado = []
    for item in itens:
        valor_comparado = chave(item) if chave else item
        if valor_comparado not in vistos:
            vistos.append(valor_comparado)
            resultado.append(item)
    return resultado


if __name__ == "__main__":
    pedidos = [101, 205, 101, 309, 205, 410, 101]
    print("Pedidos originais:", pedidos)
    print("Pedidos sem duplicar:", dedupe_mantendo_ordem(pedidos))

    eventos = [
        {"usuario": "ana", "acao": "login"},
        {"usuario": "bob", "acao": "login"},
        {"usuario": "ana", "acao": "login"},
    ]
    unicos = dedupe_nao_hashable(eventos, chave=lambda e: (e["usuario"], e["acao"]))
    print("Eventos unicos:", unicos)
