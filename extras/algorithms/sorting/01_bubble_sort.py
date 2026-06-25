"""
Bubble Sort

O que este script demonstra: ordena uma lista comparando pares de elementos
adjacentes e trocando-os de posicao quando estao fora de ordem, repetindo
ate que nenhuma troca seja necessaria.
Complexidade: O(n^2) tempo (pior e medio caso), O(1) espaco
"""


def bubble_sort(items):
    """Ordena 'items' em ordem crescente, em-place, e retorna a lista."""
    n = len(items)
    for i in range(n):
        trocou = False
        # a cada passada, o maior elemento restante "borbulha" para o final,
        # por isso o limite superior diminui (n - 1 - i)
        for j in range(0, n - 1 - i):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                trocou = True
        # otimizacao: se nao houve troca, a lista ja esta ordenada
        if not trocou:
            break
    return items


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = bubble_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert bubble_sort([]) == []
    assert bubble_sort([42]) == [42]
    assert bubble_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
