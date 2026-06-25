"""
Quick Sort

O que este script demonstra: algoritmo de divisao e conquista que escolhe um
pivo, particiona a lista em elementos menores e maiores que o pivo, e ordena
recursivamente cada particao (esquema Lomuto com pivo do meio).
Complexidade: O(n log n) tempo medio, O(n^2) pior caso (pivo sempre mal
escolhido), O(log n) espaco (pilha de recursao, em-place)
"""


def quick_sort(items):
    """Ordena 'items' em ordem crescente, em-place, e retorna a lista."""
    _quick_sort(items, 0, len(items) - 1)
    return items


def _quick_sort(items, inicio, fim):
    if inicio >= fim:
        # 0 ou 1 elemento no intervalo: nada a fazer
        return
    indice_pivo = _particionar(items, inicio, fim)
    _quick_sort(items, inicio, indice_pivo - 1)
    _quick_sort(items, indice_pivo + 1, fim)


def _particionar(items, inicio, fim):
    """Esquema de Lomuto, escolhendo o elemento do meio como pivo
    (evita o pior caso O(n^2) em listas ja ordenadas, comum quando se
    escolhe sempre o primeiro ou ultimo elemento)."""
    meio = (inicio + fim) // 2
    items[meio], items[fim] = items[fim], items[meio]  # move pivo para o fim
    pivo = items[fim]

    fronteira = inicio
    for i in range(inicio, fim):
        if items[i] <= pivo:
            items[fronteira], items[i] = items[i], items[fronteira]
            fronteira += 1
    items[fronteira], items[fim] = items[fim], items[fronteira]
    return fronteira


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = quick_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert quick_sort([]) == []
    assert quick_sort([42]) == [42]
    assert quick_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
