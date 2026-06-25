"""
Travessias In-Order, Pre-Order e Pos-Order

O que este script demonstra: as tres travessias classicas recursivas de
uma arvore binaria (in-order, pre-order e pos-order) e como cada uma
produz uma ordem diferente de visita dos nos.
Complexidade: O(n) tempo (cada no e visitado exatamente uma vez),
O(h) espaco de pilha de recursao (O(n) no pior caso de arvore
degenerada em lista).
"""


class No:
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita


def pre_ordem(no, resultado=None):
    """Visita: raiz -> esquerda -> direita. Util para copiar/serializar a arvore."""
    if resultado is None:
        resultado = []
    if no is not None:
        resultado.append(no.valor)
        pre_ordem(no.esquerda, resultado)
        pre_ordem(no.direita, resultado)
    return resultado


def em_ordem(no, resultado=None):
    """Visita: esquerda -> raiz -> direita. Em uma BST, produz valores ordenados."""
    if resultado is None:
        resultado = []
    if no is not None:
        em_ordem(no.esquerda, resultado)
        resultado.append(no.valor)
        em_ordem(no.direita, resultado)
    return resultado


def pos_ordem(no, resultado=None):
    """Visita: esquerda -> direita -> raiz. Util para deletar/liberar a arvore com seguranca."""
    if resultado is None:
        resultado = []
    if no is not None:
        pos_ordem(no.esquerda, resultado)
        pos_ordem(no.direita, resultado)
        resultado.append(no.valor)
    return resultado


def montar_arvore_exemplo():
    """
    Monta a arvore:
            1
          /   \
         2     3
        / \
       4   5
    """
    return No(1, No(2, No(4), No(5)), No(3))


if __name__ == "__main__":
    arvore = montar_arvore_exemplo()

    print("Pre-ordem  (raiz, esq, dir):", pre_ordem(arvore))
    print("Em-ordem   (esq, raiz, dir):", em_ordem(arvore))
    print("Pos-ordem  (esq, dir, raiz):", pos_ordem(arvore))

    print("\nCaso trivial: arvore vazia")
    print("  pre_ordem(None) ->", pre_ordem(None))
    print("  em_ordem(None)  ->", em_ordem(None))
    print("  pos_ordem(None) ->", pos_ordem(None))

    print("\nCaso trivial: arvore com um unico no")
    unico = No(42)
    print("  pre_ordem ->", pre_ordem(unico))
    print("  em_ordem  ->", em_ordem(unico))
    print("  pos_ordem ->", pos_ordem(unico))

    assert pre_ordem(arvore) == [1, 2, 4, 5, 3]
    assert em_ordem(arvore) == [4, 2, 5, 1, 3]
    assert pos_ordem(arvore) == [4, 5, 2, 3, 1]
    print("\nSanity checks OK.")
