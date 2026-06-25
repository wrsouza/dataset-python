"""
np.where e np.select para logica condicional vetorizada

O que este script demonstra: np.where para uma condicao simples (if/else vetorizado)
e np.select para multiplas condicoes (equivalente a if/elif/elif/else vetorizado).
Quando usar: para classificar ou transformar dados numericos com base em regras,
sem escrever loops com if/else.
"""

import numpy as np

if __name__ == "__main__":
    notas = np.array([45, 62, 78, 90, 33, 55, 100, 71])

    # np.where(condicao, valor_se_true, valor_se_false) -- like um if/else vetorizado
    aprovado = np.where(notas >= 60, "aprovado", "reprovado")

    # np.select recebe uma LISTA de condicoes e uma LISTA de valores correspondentes
    # (a primeira condicao verdadeira "vence", igual um if/elif/elif/else)
    condicoes = [
        notas >= 90,
        notas >= 70,
        notas >= 60,
    ]
    valores = ["A", "B", "C"]
    conceito = np.select(condicoes, valores, default="D")

    print("notas:", notas)
    print("aprovado (np.where):", aprovado)
    print("conceito (np.select):", conceito)

    # sanity checks
    assert aprovado.tolist() == [
        "reprovado", "aprovado", "aprovado", "aprovado",
        "reprovado", "reprovado", "aprovado", "aprovado",
    ]
    assert conceito.tolist() == ["D", "C", "B", "A", "D", "D", "A", "B"]
    print("OK: todos os asserts passaram.")
