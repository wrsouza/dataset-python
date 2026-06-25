"""
Heap Sort

O que este script demonstra: constroi manualmente um max-heap binario (sem
usar o modulo heapq, para evidenciar o algoritmo) representado como lista,
e repetidamente extrai o maior elemento, movendo-o para o final da lista.
Complexidade: O(n log n) tempo (todos os casos), O(1) espaco (em-place)
"""


def heap_sort(items):
    """Ordena 'items' em ordem crescente, em-place, e retorna a lista."""
    n = len(items)

    # fase 1: constroi o max-heap a partir do fim, "afundando" cada nó
    # nao-folha. Comecar do ultimo nó pai garante que subarvores menores
    # ja estejam organizadas quando processamos as maiores.
    for i in range(n // 2 - 1, -1, -1):
        _afundar(items, n, i)

    # fase 2: repetidamente move a raiz (maior elemento) para o final
    # da porcao ainda nao ordenada, depois restaura a propriedade de heap
    for fim in range(n - 1, 0, -1):
        items[0], items[fim] = items[fim], items[0]
        _afundar(items, fim, 0)

    return items


def _afundar(items, tamanho_heap, raiz):
    """Garante a propriedade de max-heap a partir de 'raiz', "afundando"
    o valor para baixo enquanto houver filho maior."""
    maior = raiz
    esquerda = 2 * raiz + 1
    direita = 2 * raiz + 2

    if esquerda < tamanho_heap and items[esquerda] > items[maior]:
        maior = esquerda
    if direita < tamanho_heap and items[direita] > items[maior]:
        maior = direita

    if maior != raiz:
        items[raiz], items[maior] = items[maior], items[raiz]
        # como trocamos, a subarvore abaixo de 'maior' pode ter sido violada
        _afundar(items, tamanho_heap, maior)


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = heap_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert heap_sort([]) == []
    assert heap_sort([42]) == [42]
    assert heap_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
