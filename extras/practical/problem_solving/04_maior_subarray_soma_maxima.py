"""
Maior Subarray com Soma Máxima (Algoritmo de Kadane)

Cenário: análise financeira (maior ganho acumulado em uma sequência de
variações diárias de preço), detecção do melhor trecho contíguo de
performance em séries temporais (vendas, latência, lucro).
O que este script demonstra: o algoritmo de Kadane, que resolve o problema
em O(n) mantendo a soma máxima "até aqui" e descartando prefixos que pioram
o resultado, junto com a recuperação dos índices do subarray.
"""


def maior_subarray_soma_maxima(valores: list[float]) -> tuple[float, int, int]:
    """Retorna (soma_maxima, indice_inicio, indice_fim) do subarray contíguo com maior soma."""
    if not valores:
        raise ValueError("Lista vazia não possui subarray.")

    soma_atual = soma_maxima = valores[0]
    inicio = fim = melhor_inicio = 0

    for i in range(1, len(valores)):
        # Se a soma acumulada até o índice anterior é negativa, ela só prejudica
        # qualquer subarray futuro - é melhor "recomeçar" a partir do índice atual.
        if soma_atual < 0:
            soma_atual = valores[i]
            inicio = i
        else:
            soma_atual += valores[i]

        if soma_atual > soma_maxima:
            soma_maxima = soma_atual
            melhor_inicio = inicio
            fim = i

    return soma_maxima, melhor_inicio, fim


if __name__ == "__main__":
    variacoes_diarias = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    soma, ini, fim = maior_subarray_soma_maxima(variacoes_diarias)
    print(f"Variações diárias: {variacoes_diarias}")
    print(f"Melhor janela contígua: índices [{ini}, {fim}] -> {variacoes_diarias[ini:fim + 1]}")
    print(f"Soma máxima (maior ganho acumulado): {soma}")
