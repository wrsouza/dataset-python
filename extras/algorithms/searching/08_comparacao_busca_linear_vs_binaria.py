"""
Comparação: Busca Linear vs Busca Binária (benchmark)

O que este script demonstra: mede o tempo de execução de busca linear e busca
binária em listas ordenadas de tamanhos crescentes, buscando sempre o último
elemento (pior caso para ambos os algoritmos), evidenciando a diferença entre
O(n) e O(log n) na prática.
Complexidade: O(n) tempo para busca linear, O(log n) para busca binária (por chamada)
"""

import time


def busca_linear(lista, alvo):
    """Implementação local (cópia) da busca linear, O(n)."""
    for indice, valor in enumerate(lista):
        if valor == alvo:
            return indice
    return -1


def busca_binaria(lista, alvo):
    """Implementação local (cópia) da busca binária iterativa, O(log n)."""
    esquerda, direita = 0, len(lista) - 1
    while esquerda <= direita:
        meio = (esquerda + direita) // 2
        if lista[meio] == alvo:
            return meio
        elif lista[meio] < alvo:
            esquerda = meio + 1
        else:
            direita = meio - 1
    return -1


def medir_tempo(funcao_busca, lista, alvo, repeticoes=50):
    """Executa a busca várias vezes e retorna o tempo médio em segundos.

    Repetir a chamada reduz o ruído de medição, já que uma única execução de
    busca binária pode ser tão rápida que o relógio nem percebe.
    """
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        funcao_busca(lista, alvo)
    fim = time.perf_counter()
    return (fim - inicio) / repeticoes


if __name__ == "__main__":
    tamanhos = [1_000, 10_000, 100_000, 1_000_000]

    print(f"{'Tamanho':>10} | {'Linear (s)':>14} | {'Binária (s)':>14}")
    print("-" * 45)

    for tamanho in tamanhos:
        lista_ordenada = list(range(tamanho))
        alvo = tamanho - 1  # pior caso: último elemento (mais distante do início)

        tempo_linear = medir_tempo(busca_linear, lista_ordenada, alvo)
        tempo_binaria = medir_tempo(busca_binaria, lista_ordenada, alvo)

        print(f"{tamanho:>10} | {tempo_linear:>14.8f} | {tempo_binaria:>14.8f}")

    # Caso trivial: lista pequena, diferença pouco perceptível
    lista_pequena = list(range(5))
    print("\nCaso trivial (lista pequena, tamanho 5):")
    print(f"  busca_linear -> índice {busca_linear(lista_pequena, 4)}")
    print(f"  busca_binaria -> índice {busca_binaria(lista_pequena, 4)}")

    # Sanity checks: os dois algoritmos devem concordar nos resultados
    lista_teste = list(range(0, 1000, 3))
    for alvo_teste in (0, 99, 999, 501):
        assert busca_linear(lista_teste, alvo_teste) == busca_binaria(lista_teste, alvo_teste)
    print("\nSanity checks OK.")
