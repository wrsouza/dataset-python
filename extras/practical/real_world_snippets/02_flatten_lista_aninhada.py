"""
Flatten de listas aninhadas com profundidade arbitraria

Cenario: respostas de APIs/JSON ou estruturas de arvore (ex.: categorias
de produtos, comentarios com replies) costumam vir aninhadas em niveis
variados e precisam ser "achatadas" para processamento tabular ou export.
O que este script demonstra: flatten recursivo generico e uma variante
iterativa com pilha (evita limite de recursao em estruturas muito profundas).
"""

from typing import Any, Iterable, List


def flatten_recursivo(estrutura: Iterable[Any]) -> List[Any]:
    """Achata listas/tuplas aninhadas em qualquer profundidade.

    Strings e bytes sao tratados como "atomos" (nao sao iterados
    elemento a elemento), senão "abc" seria quebrado em ['a','b','c'].
    """
    resultado = []
    for item in estrutura:
        if isinstance(item, (list, tuple)):
            resultado.extend(flatten_recursivo(item))
        else:
            resultado.append(item)
    return resultado


def flatten_iterativo(estrutura: Iterable[Any]) -> List[Any]:
    """Mesma semantica, mas sem recursao -- util quando a profundidade
    pode ser muito grande e estourar o limite padrao de recursao do Python.
    """
    pilha = list(estrutura)[::-1]  # invertido para preservar ordem ao usar pop()
    resultado = []
    while pilha:
        item = pilha.pop()
        if isinstance(item, (list, tuple)):
            pilha.extend(list(item)[::-1])
        else:
            resultado.append(item)
    return resultado


if __name__ == "__main__":
    categorias = [1, [2, 3, [4, [5, 6], 7]], 8, [[9, [10]]]]
    print("Estrutura original:", categorias)
    print("Flatten recursivo:", flatten_recursivo(categorias))
    print("Flatten iterativo:", flatten_iterativo(categorias))
