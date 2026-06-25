"""
Arvore Binaria de Busca (BST)

O que este script demonstra: implementacao manual de uma BST com insercao,
busca e remocao (incluindo o caso de remover um no com dois filhos usando
o sucessor in-order).
Complexidade: O(h) tempo por operacao, onde h e a altura da arvore
(O(log n) se balanceada, O(n) no pior caso, ex.: insercao sequencial
crescente). Espaco: O(n) para armazenar a arvore, O(h) de pilha em
chamadas recursivas.
"""


class No:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None


class ArvoreBinariaBusca:
    def __init__(self):
        self.raiz = None

    def inserir(self, valor):
        self.raiz = self._inserir(self.raiz, valor)

    def _inserir(self, no, valor):
        if no is None:
            return No(valor)
        if valor < no.valor:
            no.esquerda = self._inserir(no.esquerda, valor)
        elif valor > no.valor:
            no.direita = self._inserir(no.direita, valor)
        # valores iguais sao ignorados (sem duplicatas)
        return no

    def buscar(self, valor):
        return self._buscar(self.raiz, valor)

    def _buscar(self, no, valor):
        if no is None:
            return False
        if valor == no.valor:
            return True
        if valor < no.valor:
            return self._buscar(no.esquerda, valor)
        return self._buscar(no.direita, valor)

    def remover(self, valor):
        self.raiz = self._remover(self.raiz, valor)

    def _remover(self, no, valor):
        if no is None:
            return None
        if valor < no.valor:
            no.esquerda = self._remover(no.esquerda, valor)
        elif valor > no.valor:
            no.direita = self._remover(no.direita, valor)
        else:
            # caso 1: no folha ou com apenas um filho
            if no.esquerda is None:
                return no.direita
            if no.direita is None:
                return no.esquerda
            # caso 2: dois filhos -> substitui pelo sucessor in-order
            # (menor valor da subarvore direita), depois remove o sucessor
            sucessor = self._minimo(no.direita)
            no.valor = sucessor.valor
            no.direita = self._remover(no.direita, sucessor.valor)
        return no

    def _minimo(self, no):
        while no.esquerda is not None:
            no = no.esquerda
        return no

    def em_ordem(self):
        resultado = []

        def percorrer(no):
            if no is not None:
                percorrer(no.esquerda)
                resultado.append(no.valor)
                percorrer(no.direita)

        percorrer(self.raiz)
        return resultado


if __name__ == "__main__":
    bst = ArvoreBinariaBusca()
    valores = [50, 30, 70, 20, 40, 60, 80]
    for v in valores:
        bst.inserir(v)

    print("Valores inseridos:", valores)
    print("Em ordem (deve estar ordenado):", bst.em_ordem())

    print("\nBuscas:")
    for v in [40, 99]:
        print(f"  buscar({v}) -> {bst.buscar(v)}")

    print("\nRemovendo 30 (no com dois filhos):")
    bst.remover(30)
    print("Em ordem apos remocao:", bst.em_ordem())

    print("\nCaso trivial: arvore vazia")
    vazia = ArvoreBinariaBusca()
    print("  buscar em arvore vazia:", vazia.buscar(1))
    print("  em_ordem em arvore vazia:", vazia.em_ordem())

    assert bst.em_ordem() == sorted(bst.em_ordem())
    assert bst.buscar(30) is False
    assert bst.buscar(60) is True
    print("\nSanity checks OK.")
