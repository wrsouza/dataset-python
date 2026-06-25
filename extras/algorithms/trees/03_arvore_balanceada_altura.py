"""
Altura da Arvore e Verificacao de Balanceamento (estilo AVL)

O que este script demonstra: como calcular a altura de uma arvore binaria
e como verificar se ela e balanceada (a diferenca de altura entre as
subarvores esquerda e direita de QUALQUER no e <= 1, igual ao criterio
usado em arvores AVL).
Complexidade: O(n) tempo (versao eficiente visita cada no uma vez),
O(h) espaco de pilha de recursao.
"""


class No:
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita


def altura(no):
    """Altura = numero de arestas do no ate a folha mais profunda.
    Arvore vazia tem altura -1; um unico no tem altura 0."""
    if no is None:
        return -1
    return 1 + max(altura(no.esquerda), altura(no.direita))


def eh_balanceada(no):
    """
    Versao ingenua (didatica) chamaria altura() em cada no, custando O(n^2)
    no pior caso. Aqui usamos uma abordagem O(n): uma unica passada que
    retorna a altura e propaga um sinal de "desbalanceado" (-2) para cima
    assim que detectado, evitando recalculo.
    """
    SINAL_DESBALANCEADO = -2

    def verificar(no):
        if no is None:
            return -1  # altura da arvore vazia

        altura_esq = verificar(no.esquerda)
        if altura_esq == SINAL_DESBALANCEADO:
            return SINAL_DESBALANCEADO

        altura_dir = verificar(no.direita)
        if altura_dir == SINAL_DESBALANCEADO:
            return SINAL_DESBALANCEADO

        if abs(altura_esq - altura_dir) > 1:
            return SINAL_DESBALANCEADO

        return 1 + max(altura_esq, altura_dir)

    return verificar(no) != SINAL_DESBALANCEADO


if __name__ == "__main__":
    # Arvore balanceada:
    #        1
    #       / \
    #      2   3
    #     / \
    #    4   5
    balanceada = No(1, No(2, No(4), No(5)), No(3))

    # Arvore desbalanceada (lista encadeada para a esquerda):
    #        1
    #       /
    #      2
    #     /
    #    3
    #   /
    #  4
    desbalanceada = No(1, No(2, No(3, No(4))))

    print("Arvore balanceada:")
    print("  altura:", altura(balanceada))
    print("  eh_balanceada:", eh_balanceada(balanceada))

    print("\nArvore desbalanceada (lista encadeada):")
    print("  altura:", altura(desbalanceada))
    print("  eh_balanceada:", eh_balanceada(desbalanceada))

    print("\nCaso trivial: arvore vazia")
    print("  altura(None):", altura(None))
    print("  eh_balanceada(None):", eh_balanceada(None))

    print("\nCaso trivial: um unico no")
    unico = No(10)
    print("  altura:", altura(unico))
    print("  eh_balanceada:", eh_balanceada(unico))

    assert altura(balanceada) == 2
    assert eh_balanceada(balanceada) is True
    assert eh_balanceada(desbalanceada) is False
    assert altura(None) == -1
    print("\nSanity checks OK.")
