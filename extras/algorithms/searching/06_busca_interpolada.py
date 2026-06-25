"""
Busca Interpolada (Interpolation Search)

O que este script demonstra: em vez de sempre olhar o elemento central como a
busca binária, estima a posição provável do alvo usando interpolação linear
com base nos valores nas extremidades do intervalo. Funciona melhor quando os
dados são numéricos e uniformemente distribuídos.
Complexidade: O(log log n) tempo médio (dados uniformes), O(n) pior caso, O(1) espaço
"""


def busca_interpolada(lista, alvo):
    """Retorna o índice de `alvo` em `lista` ordenada (numérica), ou -1."""
    esquerda, direita = 0, len(lista) - 1

    while esquerda <= direita and lista[esquerda] <= alvo <= lista[direita]:
        # Caso especial: evita divisão por zero quando todos os valores no
        # intervalo são iguais.
        if lista[direita] == lista[esquerda]:
            if lista[esquerda] == alvo:
                return esquerda
            return -1

        # Fórmula de interpolação: estima a posição proporcionalmente à
        # posição do valor entre os extremos do intervalo.
        posicao = esquerda + (
            (direita - esquerda) * (alvo - lista[esquerda])
        ) // (lista[direita] - lista[esquerda])

        if lista[posicao] == alvo:
            return posicao
        elif lista[posicao] < alvo:
            esquerda = posicao + 1
        else:
            direita = posicao - 1

    return -1


if __name__ == "__main__":
    numeros_uniformes = list(range(0, 200, 2))  # [0, 2, 4, ..., 198]

    # Caso comum: dados uniformemente distribuídos, interpolação converge rápido
    resultado = busca_interpolada(numeros_uniformes, 84)
    print(f"Lista: 0, 2, 4, ..., 198 (passo 2, {len(numeros_uniformes)} elementos)")
    print(f"Procurando 84 -> índice: {resultado}")

    # Caso trivial: valor ausente (ímpar em lista de pares)
    resultado_ausente = busca_interpolada(numeros_uniformes, 85)
    print(f"Procurando 85 -> índice: {resultado_ausente}")

    assert busca_interpolada(numeros_uniformes, 84) == 42
    assert busca_interpolada(numeros_uniformes, 85) == -1
    assert busca_interpolada([], 1) == -1
    assert busca_interpolada([5, 5, 5], 5) == 0
    assert busca_interpolada([5, 5, 5], 3) == -1
    print("Sanity checks OK.")
