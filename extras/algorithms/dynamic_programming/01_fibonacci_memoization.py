"""
Fibonacci com Memoization vs Recursao Naive

O que este script demonstra: como memoization (cache de subproblemas) transforma
uma recursao exponencial em uma solucao linear, comparando contagem de chamadas
entre a versao naive e a versao memoizada para o mesmo n.
Complexidade: naive O(2^n) tempo / O(n) espaco (pilha); memoizada O(n) tempo / O(n) espaco
"""

import time
from functools import lru_cache

# Contador global so para fins didaticos: mostra quantas chamadas de funcao ocorrem
contador_chamadas_naive = 0
contador_chamadas_memo = 0


def fibonacci_naive(n: int) -> int:
    """Recursao pura, recalcula os mesmos subproblemas muitas vezes."""
    global contador_chamadas_naive
    contador_chamadas_naive += 1
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_memo_dict(n: int, cache: dict | None = None) -> int:
    """Memoization manual usando dict: guarda resultado de cada n ja calculado."""
    global contador_chamadas_memo
    if cache is None:
        cache = {}
    contador_chamadas_memo += 1

    if n <= 1:
        return n
    if n in cache:
        return cache[n]  # subproblema ja resolvido, evita recalculo

    resultado = fibonacci_memo_dict(n - 1, cache) + fibonacci_memo_dict(n - 2, cache)
    cache[n] = resultado
    return resultado


@lru_cache(maxsize=None)
def fibonacci_lru_cache(n: int) -> int:
    """Mesma ideia de memoization, mas delegada ao decorator da stdlib."""
    if n <= 1:
        return n
    return fibonacci_lru_cache(n - 1) + fibonacci_lru_cache(n - 2)


if __name__ == "__main__":
    n = 25

    contador_chamadas_naive = 0
    inicio = time.perf_counter()
    resultado_naive = fibonacci_naive(n)
    tempo_naive = time.perf_counter() - inicio

    contador_chamadas_memo = 0
    inicio = time.perf_counter()
    resultado_memo = fibonacci_memo_dict(n)
    tempo_memo = time.perf_counter() - inicio

    resultado_lru = fibonacci_lru_cache(n)

    print(f"Fibonacci({n})")
    print(f"  naive:      resultado={resultado_naive}  chamadas={contador_chamadas_naive}  tempo={tempo_naive:.6f}s")
    print(f"  memo(dict): resultado={resultado_memo}  chamadas={contador_chamadas_memo}  tempo={tempo_memo:.6f}s")
    print(f"  lru_cache:  resultado={resultado_lru}")

    # Sanity checks: todas as abordagens devem concordar
    assert resultado_naive == resultado_memo == resultado_lru
    # A versao memoizada deve fazer muito menos chamadas que a naive (O(n) vs O(2^n))
    assert contador_chamadas_memo < contador_chamadas_naive
    print("\nOK: resultados consistentes e memoization reduziu drasticamente as chamadas.")
