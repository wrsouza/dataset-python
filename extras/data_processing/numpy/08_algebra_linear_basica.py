"""
Algebra linear basica: produto matricial e inversa

O que este script demonstra: produto matricial com @ (ou np.dot), calculo da matriz
inversa com np.linalg.inv, e a verificacao de que A @ A_inv aproxima a identidade.
Quando usar: para resolver sistemas lineares ou transformar dados via matrizes.
"""

import numpy as np

if __name__ == "__main__":
    # matriz quadrada invertivel (determinante != 0)
    A = np.array([
        [4.0, 7.0],
        [2.0, 6.0],
    ])

    # produto matricial: @ e o operador moderno, np.dot faz o mesmo para 2D
    B = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
    ])
    produto_at_b = A @ B
    produto_dot = np.dot(A, B)

    # inversa: A_inv tal que A @ A_inv == identidade (a menos de erro de ponto flutuante)
    A_inv = np.linalg.inv(A)
    identidade_aproximada = A @ A_inv

    print("A:\n", A)
    print("A @ B (com B = identidade):\n", produto_at_b)
    print("np.dot(A, B):\n", produto_dot)
    print("A_inv:\n", A_inv)
    print("A @ A_inv (deve ser ~ identidade):\n", identidade_aproximada)

    # sanity checks
    assert np.array_equal(produto_at_b, A)  # multiplicar por identidade nao muda nada
    assert np.allclose(produto_dot, produto_at_b)
    # np.allclose tolera erro de ponto flutuante, diferente de == exato
    assert np.allclose(identidade_aproximada, np.eye(2), atol=1e-10)
    print("OK: todos os asserts passaram.")
