"""
Numeros aleatorios reprodutiveis com seed

O que este script demonstra: como np.random.default_rng(seed) garante que a mesma
sequencia de numeros "aleatorios" seja gerada toda vez, dado o mesmo seed.
Quando usar: em experimentos/testes onde a reprodutibilidade dos resultados e
essencial (ex: comparar modelos, depurar pipelines).
"""

import numpy as np

if __name__ == "__main__":
    seed = 42

    # cada Generator e independente -- usar o mesmo seed produz a mesma sequencia,
    # mesmo sendo duas instancias diferentes criadas em momentos distintos
    rng1 = np.random.default_rng(seed)
    amostra1 = rng1.integers(0, 100, size=5)

    rng2 = np.random.default_rng(seed)
    amostra2 = rng2.integers(0, 100, size=5)

    # com seed diferente, a sequencia muda completamente
    rng3 = np.random.default_rng(seed + 1)
    amostra3 = rng3.integers(0, 100, size=5)

    print("amostra1 (seed=42):", amostra1)
    print("amostra2 (seed=42):", amostra2)
    print("amostra3 (seed=43):", amostra3)

    # sanity checks
    assert np.array_equal(amostra1, amostra2)  # mesmo seed -> mesma sequencia
    assert not np.array_equal(amostra1, amostra3)  # seed diferente -> sequencia diferente
    print("OK: todos os asserts passaram.")
