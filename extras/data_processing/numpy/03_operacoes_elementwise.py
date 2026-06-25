"""
Operacoes elementwise: vetorizado vs loop puro em Python

O que este script demonstra: a mesma operacao matematica feita com loop Python puro
e com operacoes vetorizadas do numpy, comparando o tempo de execucao.
Quando usar: para justificar a troca de loops manuais por operacoes vetorizadas em
processamento numerico de grandes volumes de dados.
"""

import time
import numpy as np

if __name__ == "__main__":
    n = 200_000
    dados = list(range(n))
    dados_np = np.arange(n)

    # versao com loop puro Python: soma 1 e multiplica por 2 em cada elemento
    inicio = time.perf_counter()
    resultado_loop = [(x + 1) * 2 for x in dados]
    tempo_loop = time.perf_counter() - inicio

    # versao vetorizada: a mesma operacao aplicada ao array inteiro de uma vez
    # (o numpy executa em codigo C internamente, sem o overhead do interpretador)
    inicio = time.perf_counter()
    resultado_np = (dados_np + 1) * 2
    tempo_np = time.perf_counter() - inicio

    print(f"tempo loop puro:   {tempo_loop:.6f}s")
    print(f"tempo vetorizado:  {tempo_np:.6f}s")
    print(f"speedup aproximado: {tempo_loop / max(tempo_np, 1e-9):.1f}x")

    # sanity checks: os resultados devem ser equivalentes
    assert resultado_np.tolist() == resultado_loop
    assert resultado_np[0] == 2 and resultado_np[-1] == (n - 1 + 1) * 2
    print("OK: todos os asserts passaram.")
