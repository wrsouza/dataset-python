"""
Memoization vs recalculo (fibonacci recursivo)

Cenario: funcoes recursivas com subproblemas repetidos (calculo de fibonacci,
problemas de programacao dinamica, recomputo de agregacoes em arvores de
categorias) podem ficar absurdamente lentas se o mesmo subproblema for
recalculado milhares de vezes.
O que este script demonstra: comparar o tempo de execucao do fibonacci recursivo
"ingenuo" (recalcula tudo) contra uma versao com memoization via
functools.lru_cache, mostrando o ganho exponencial de performance ao evitar
trabalho redundante.
"""

import time
from functools import lru_cache

N = 30  # valor pequeno o suficiente para o "sem memoization" nao demorar demais


def fibonacci_sem_memoization(n):
    """Recursao pura: refaz o calculo de cada subproblema repetidamente.
    Complexidade exponencial O(2^n) -- por isso N precisa ser pequeno aqui."""
    if n < 2:
        return n
    return fibonacci_sem_memoization(n - 1) + fibonacci_sem_memoization(n - 2)


@lru_cache(maxsize=None)
def fibonacci_com_memoization(n):
    """Mesma recursao, mas lru_cache guarda o resultado de cada n ja calculado.
    Isso reduz a complexidade para O(n), pois cada subproblema e resolvido
    apenas uma vez e reaproveitado nas chamadas seguintes."""
    if n < 2:
        return n
    return fibonacci_com_memoization(n - 1) + fibonacci_com_memoization(n - 2)


def medir(func, n):
    inicio = time.perf_counter()
    resultado = func(n)
    fim = time.perf_counter()
    return resultado, fim - inicio


if __name__ == "__main__":
    resultado_sem, tempo_sem = medir(fibonacci_sem_memoization, N)

    # lru_cache mantem estado entre chamadas; limpamos antes de medir para
    # garantir uma medicao "fria" (sem cache de uma rodada anterior).
    fibonacci_com_memoization.cache_clear()
    resultado_com, tempo_com = medir(fibonacci_com_memoization, N)

    print(f"Calculo de fibonacci({N})")
    print(f"Sem memoization: resultado={resultado_sem} | tempo={tempo_sem:.4f}s")
    print(f"Com memoization: resultado={resultado_com} | tempo={tempo_com:.6f}s")

    assert resultado_sem == resultado_com

    if tempo_com > 0:
        fator = tempo_sem / tempo_com
        print(f"Versao com memoization foi aproximadamente {fator:,.0f}x mais rapida.")

    info_cache = fibonacci_com_memoization.cache_info()
    print(f"Estatisticas do cache: {info_cache}")
