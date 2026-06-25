"""
Busca Linear

O que este script demonstra: percorre a lista elemento por elemento, comparando
cada item com o valor procurado, até encontrar ou esgotar a lista. Funciona em
listas ordenadas ou não.
Complexidade: O(n) tempo, O(1) espaço
"""


def busca_linear(lista, alvo):
    """Retorna o índice da primeira ocorrência de `alvo` em `lista`, ou -1."""
    for indice, valor in enumerate(lista):
        if valor == alvo:
            return indice
    return -1


if __name__ == "__main__":
    numeros = [5, 3, 8, 1, 9, 2, 7]

    # Caso comum: elemento presente no meio da lista
    resultado = busca_linear(numeros, 9)
    print(f"Lista: {numeros}")
    print(f"Procurando 9 -> índice: {resultado}")

    # Caso trivial: elemento ausente
    resultado_ausente = busca_linear(numeros, 100)
    print(f"Procurando 100 -> índice: {resultado_ausente}")

    assert busca_linear(numeros, 9) == 4
    assert busca_linear(numeros, 100) == -1
    assert busca_linear([], 1) == -1
    print("Sanity checks OK.")
