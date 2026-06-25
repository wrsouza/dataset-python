"""
Busca Binária Recursiva

O que este script demonstra: mesma ideia da busca binária iterativa, porém
implementada com chamadas recursivas que reduzem o intervalo [esquerda, direita]
a cada chamada.
Complexidade: O(log n) tempo, O(log n) espaço (pilha de recursão)
"""


def busca_binaria_recursiva(lista, alvo, esquerda=0, direita=None):
    """Retorna o índice de `alvo` em `lista` ordenada, ou -1, via recursão."""
    if direita is None:
        direita = len(lista) - 1

    # Caso base: intervalo vazio, alvo não encontrado
    if esquerda > direita:
        return -1

    meio = (esquerda + direita) // 2
    if lista[meio] == alvo:
        return meio
    elif lista[meio] < alvo:
        return busca_binaria_recursiva(lista, alvo, meio + 1, direita)
    else:
        return busca_binaria_recursiva(lista, alvo, esquerda, meio - 1)


if __name__ == "__main__":
    numeros_ordenados = [1, 4, 6, 8, 10, 13, 17, 21, 25, 30]

    # Caso comum: elemento presente
    resultado = busca_binaria_recursiva(numeros_ordenados, 17)
    print(f"Lista ordenada: {numeros_ordenados}")
    print(f"Procurando 17 -> índice: {resultado}")

    # Caso trivial: elemento ausente
    resultado_ausente = busca_binaria_recursiva(numeros_ordenados, 18)
    print(f"Procurando 18 -> índice: {resultado_ausente}")

    assert busca_binaria_recursiva(numeros_ordenados, 17) == 6
    assert busca_binaria_recursiva(numeros_ordenados, 18) == -1
    assert busca_binaria_recursiva([], 1) == -1
    print("Sanity checks OK.")
