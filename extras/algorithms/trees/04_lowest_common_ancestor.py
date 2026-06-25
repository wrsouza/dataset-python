"""
Lowest Common Ancestor (LCA) em Arvore Binaria Generica

O que este script demonstra: como encontrar o ancestral comum mais
profundo (LCA) de dois nos em uma arvore binaria qualquer (nao
necessariamente uma BST), usando uma busca recursiva que retorna o
proprio no quando o encontra e propaga esse resultado para cima.
Complexidade: O(n) tempo (no pior caso visita todos os nos), O(h)
espaco de pilha de recursao.
"""


class No:
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita


def encontrar_lca(raiz, valor1, valor2):
    """
    Ideia: percorre a arvore recursivamente. Se o no atual e None ou e
    igual a um dos valores buscados, retorna o proprio no atual (sinal
    de "encontrei um dos alvos aqui"). Se as buscas na subarvore
    esquerda e direita retornarem nos diferentes de None, significa que
    valor1 e valor2 estao em ramos diferentes a partir deste no -> este
    no e o LCA. Caso contrario, propaga o lado que encontrou algo.

    Pressupoe que valor1 e valor2 existem na arvore.
    """
    if raiz is None:
        return None
    if raiz.valor == valor1 or raiz.valor == valor2:
        return raiz

    esquerda = encontrar_lca(raiz.esquerda, valor1, valor2)
    direita = encontrar_lca(raiz.direita, valor1, valor2)

    if esquerda is not None and direita is not None:
        # valor1 e valor2 foram encontrados em ramos diferentes
        return raiz
    return esquerda if esquerda is not None else direita


def montar_arvore_exemplo():
    """
    Monta a arvore:
              3
            /   \
           5     1
          / \   / \
         6   2 0   8
            / \
           7   4
    """
    no7 = No(7)
    no4 = No(4)
    no2 = No(2, no7, no4)
    no6 = No(6)
    no5 = No(5, no6, no2)
    no0 = No(0)
    no8 = No(8)
    no1 = No(1, no0, no8)
    raiz = No(3, no5, no1)
    return raiz


if __name__ == "__main__":
    raiz = montar_arvore_exemplo()

    casos = [
        (5, 1, 3),   # ramos diferentes a partir da raiz
        (6, 4, 5),   # ambos na subarvore esquerda, LCA = 5
        (7, 4, 2),   # irmaos diretos, LCA = pai comum (2)
        (0, 8, 1),   # ambos na subarvore direita, LCA = 1
    ]

    for v1, v2, esperado in casos:
        lca = encontrar_lca(raiz, v1, v2)
        print(f"LCA({v1}, {v2}) = {lca.valor}  (esperado: {esperado})")
        assert lca.valor == esperado

    print("\nCaso trivial: um dos valores e a propria raiz")
    lca_raiz = encontrar_lca(raiz, 3, 7)
    print(f"LCA(3, 7) = {lca_raiz.valor}  (esperado: 3)")
    assert lca_raiz.valor == 3

    print("\nCaso trivial: arvore vazia")
    print("encontrar_lca(None, 1, 2) ->", encontrar_lca(None, 1, 2))

    print("\nSanity checks OK.")
