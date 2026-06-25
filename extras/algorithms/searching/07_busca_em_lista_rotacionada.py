"""
Busca em Lista Ordenada Rotacionada (Rotated Sorted Array)

O que este script demonstra: uma lista ordenada foi "rotacionada" em algum
pivô desconhecido (ex.: [4,5,6,7,0,1,2]). Adaptamos a busca binária: a cada
passo identificamos qual metade do intervalo está ordenada e decidimos se o
alvo pode estar nela antes de continuar a busca.
Complexidade: O(log n) tempo, O(1) espaço
"""


def busca_em_lista_rotacionada(lista, alvo):
    """Retorna o índice de `alvo` em `lista` ordenada e rotacionada, ou -1."""
    esquerda, direita = 0, len(lista) - 1

    while esquerda <= direita:
        meio = (esquerda + direita) // 2

        if lista[meio] == alvo:
            return meio

        if lista[esquerda] <= lista[meio]:
            # Metade esquerda [esquerda..meio] está ordenada normalmente
            if lista[esquerda] <= alvo < lista[meio]:
                direita = meio - 1  # alvo está na metade esquerda ordenada
            else:
                esquerda = meio + 1
        else:
            # Metade direita [meio..direita] está ordenada normalmente
            if lista[meio] < alvo <= lista[direita]:
                esquerda = meio + 1  # alvo está na metade direita ordenada
            else:
                direita = meio - 1

    return -1


if __name__ == "__main__":
    lista_rotacionada = [4, 5, 6, 7, 0, 1, 2]

    # Caso comum: alvo está na parte "rotacionada" (início, valores baixos)
    resultado = busca_em_lista_rotacionada(lista_rotacionada, 0)
    print(f"Lista rotacionada: {lista_rotacionada}")
    print(f"Procurando 0 -> índice: {resultado}")

    # Caso trivial: alvo ausente
    resultado_ausente = busca_em_lista_rotacionada(lista_rotacionada, 3)
    print(f"Procurando 3 -> índice: {resultado_ausente}")

    assert busca_em_lista_rotacionada(lista_rotacionada, 0) == 4
    assert busca_em_lista_rotacionada(lista_rotacionada, 3) == -1
    assert busca_em_lista_rotacionada(lista_rotacionada, 4) == 0
    assert busca_em_lista_rotacionada([], 1) == -1
    assert busca_em_lista_rotacionada([1], 1) == 0
    # Lista sem rotação também deve funcionar (pivô "trivial")
    assert busca_em_lista_rotacionada([1, 2, 3, 4, 5], 4) == 3
    print("Sanity checks OK.")
