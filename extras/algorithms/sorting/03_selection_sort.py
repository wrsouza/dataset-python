"""
Selection Sort

O que este script demonstra: a cada iteracao, encontra o menor elemento da
parte ainda nao ordenada da lista e o troca de posicao com o primeiro
elemento dessa parte.
Complexidade: O(n^2) tempo (pior, medio e melhor caso), O(1) espaco
"""


def selection_sort(items):
    """Ordena 'items' em ordem crescente, em-place, e retorna a lista."""
    n = len(items)
    for i in range(n - 1):
        indice_menor = i
        # procura o indice do menor elemento no restante da lista
        for j in range(i + 1, n):
            if items[j] < items[indice_menor]:
                indice_menor = j
        # so troca se encontrou um elemento menor que items[i]
        if indice_menor != i:
            items[i], items[indice_menor] = items[indice_menor], items[i]
    return items


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = selection_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert selection_sort([]) == []
    assert selection_sort([42]) == [42]
    assert selection_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
