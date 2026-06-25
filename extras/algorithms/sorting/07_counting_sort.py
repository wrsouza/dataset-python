"""
Counting Sort

O que este script demonstra: ordena inteiros NAO-NEGATIVOS contando quantas
vezes cada valor aparece e usando essa contagem para reconstruir a lista
ordenada, sem nenhuma comparacao entre elementos.
Complexidade: O(n + k) tempo, O(n + k) espaco, onde k = maior valor da lista
"""


def counting_sort(items):
    """Ordena 'items' (inteiros >= 0) em ordem crescente e retorna uma
    NOVA lista. Lanca ValueError se houver valor negativo."""
    if not items:
        return []
    if any(x < 0 for x in items):
        raise ValueError("counting_sort so suporta inteiros nao-negativos")

    maior_valor = max(items)
    # contagem[v] = quantas vezes o valor v aparece em 'items'
    contagem = [0] * (maior_valor + 1)
    for valor in items:
        contagem[valor] += 1

    # reconstroi a lista ordenada percorrendo as contagens em ordem
    resultado = []
    for valor, qtd in enumerate(contagem):
        resultado.extend([valor] * qtd)
    return resultado


if __name__ == "__main__":
    exemplo = [5, 2, 9, 1, 5, 6, 0]
    print("Antes:", exemplo)
    resultado = counting_sort(exemplo)
    print("Depois:", resultado)

    # caso trivial: lista vazia e lista de 1 elemento
    assert counting_sort([]) == []
    assert counting_sort([42]) == [42]
    assert counting_sort([3, 1, 2]) == [1, 2, 3]

    # caso de erro esperado: valor negativo deve lancar ValueError
    try:
        counting_sort([3, -1, 2])
        assert False, "deveria ter lancado ValueError"
    except ValueError:
        pass

    print("Sanity check ok.")
