"""
Merge Sort

O que este script demonstra: algoritmo de divisao e conquista que divide a
lista recursivamente pela metade ate sublistas de 1 elemento, e depois
intercala (merge) as sublistas ordenadas de volta em uma unica lista ordenada.
Complexidade: O(n log n) tempo (todos os casos), O(n) espaco
"""


def merge_sort(items):
    """Retorna uma NOVA lista ordenada (nao modifica 'items' em-place)."""
    if len(items) <= 1:
        # caso base da recursao: lista vazia ou com 1 elemento ja esta ordenada
        return list(items)

    meio = len(items) // 2
    esquerda = merge_sort(items[:meio])
    direita = merge_sort(items[meio:])
    return _merge(esquerda, direita)


def _merge(esquerda, direita):
    """Intercala duas listas ja ordenadas em uma unica lista ordenada."""
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    # anexa o que restou de cada lado (um dos dois ja foi totalmente consumido)
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6]
    print("Antes:", exemplo)
    resultado = merge_sort(exemplo)
    print("Depois:", resultado)
    print("Original inalterada:", exemplo)

    # caso trivial: lista vazia e lista de 1 elemento
    assert merge_sort([]) == []
    assert merge_sort([42]) == [42]
    assert merge_sort([3, 1, 2]) == [1, 2, 3]
    print("Sanity check ok.")
