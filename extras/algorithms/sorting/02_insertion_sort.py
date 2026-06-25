"""
Insertion Sort

O que este script demonstra: constroi a lista ordenada incrementalmente,
pegando cada elemento e inserindo-o na posicao correta entre os elementos
ja ordenados a esquerda.
Complexidade: O(n^2) tempo (pior e medio caso), O(1) espaco
"""


def insertion_sort(items):
    """Ordena 'items' em ordem crescente, em-place, e retorna a lista."""
    for i in range(1, len(items)):
        chave = items[i]
        j = i - 1
        # desloca para a direita os elementos maiores que 'chave'
        # ate encontrar a posicao correta de insercao
        while j >= 0 and items[j] > chave:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = chave
    return items


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = insertion_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert insertion_sort([]) == []
    assert insertion_sort([42]) == [42]
    assert insertion_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
