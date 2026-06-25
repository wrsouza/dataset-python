"""
Busca da Primeira e Última Ocorrência (lista ordenada com duplicatas)

O que este script demonstra: duas buscas binárias modificadas — uma que, ao
encontrar o alvo, continua buscando para a esquerda (primeira ocorrência), e
outra que continua buscando para a direita (última ocorrência).
Complexidade: O(log n) tempo, O(1) espaço
"""


def _busca_limite(lista, alvo, buscar_primeira):
    """Busca binária que retorna o índice do limite (primeiro ou último)
    onde `alvo` aparece, ou -1 se ausente."""
    esquerda, direita = 0, len(lista) - 1
    resultado = -1

    while esquerda <= direita:
        meio = (esquerda + direita) // 2
        if lista[meio] == alvo:
            resultado = meio  # candidato encontrado, mas pode haver melhor
            if buscar_primeira:
                direita = meio - 1  # continua procurando mais à esquerda
            else:
                esquerda = meio + 1  # continua procurando mais à direita
        elif lista[meio] < alvo:
            esquerda = meio + 1
        else:
            direita = meio - 1

    return resultado


def primeira_ocorrencia(lista, alvo):
    return _busca_limite(lista, alvo, buscar_primeira=True)


def ultima_ocorrencia(lista, alvo):
    return _busca_limite(lista, alvo, buscar_primeira=False)


if __name__ == "__main__":
    numeros = [1, 2, 2, 2, 3, 4, 4, 5, 5, 5, 5, 6]

    # Caso comum: valor com múltiplas ocorrências
    primeiro = primeira_ocorrencia(numeros, 5)
    ultimo = ultima_ocorrencia(numeros, 5)
    print(f"Lista: {numeros}")
    print(f"Valor 5 -> primeira ocorrência: {primeiro}, última ocorrência: {ultimo}")

    # Caso trivial: valor ausente
    primeiro_ausente = primeira_ocorrencia(numeros, 100)
    print(f"Valor 100 (ausente) -> primeira ocorrência: {primeiro_ausente}")

    assert primeira_ocorrencia(numeros, 5) == 7
    assert ultima_ocorrencia(numeros, 5) == 10
    assert primeira_ocorrencia(numeros, 100) == -1
    assert ultima_ocorrencia(numeros, 100) == -1
    assert primeira_ocorrencia(numeros, 2) == 1
    print("Sanity checks OK.")
