"""
Busca Binária (iterativa)

O que este script demonstra: divide repetidamente o espaço de busca pela
metade comparando o alvo com o elemento central, exigindo lista ordenada.
Complexidade: O(log n) tempo, O(1) espaço
"""


def busca_binaria(lista, alvo):
    """Retorna o índice de `alvo` em `lista` ordenada, ou -1.

    Observação didática: `bisect.bisect_left` faria o mesmo, mas aqui
    implementamos manualmente para fins de estudo.
    """
    esquerda, direita = 0, len(lista) - 1

    while esquerda <= direita:
        meio = (esquerda + direita) // 2  # ponto central do intervalo atual
        if lista[meio] == alvo:
            return meio
        elif lista[meio] < alvo:
            esquerda = meio + 1  # alvo está na metade direita
        else:
            direita = meio - 1  # alvo está na metade esquerda

    return -1


if __name__ == "__main__":
    numeros_ordenados = [1, 2, 3, 5, 7, 8, 9, 12, 15, 20]

    # Caso comum: elemento presente
    resultado = busca_binaria(numeros_ordenados, 9)
    print(f"Lista ordenada: {numeros_ordenados}")
    print(f"Procurando 9 -> índice: {resultado}")

    # Caso trivial: elemento ausente
    resultado_ausente = busca_binaria(numeros_ordenados, 4)
    print(f"Procurando 4 -> índice: {resultado_ausente}")

    assert busca_binaria(numeros_ordenados, 9) == 6
    assert busca_binaria(numeros_ordenados, 4) == -1
    assert busca_binaria([], 1) == -1
    assert busca_binaria([5], 5) == 0
    print("Sanity checks OK.")
