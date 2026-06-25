"""
Mascaras booleanas para filtragem e edicao in-place

O que este script demonstra: como criar mascaras booleanas a partir de condicoes e
usa-las tanto para LER (filtrar) quanto para ESCREVER (editar in-place) em arrays.
Quando usar: para aplicar regras condicionais em datasets numericos sem loops.
"""

import numpy as np

if __name__ == "__main__":
    temperaturas = np.array([15.0, 22.5, 31.0, 8.0, 27.3, -2.0, 40.1])

    # mascara: array booleano do mesmo shape, True onde a condicao e satisfeita
    mascara_quente = temperaturas > 25

    # usar a mascara para LER (filtrar) -- retorna so os elementos True
    dias_quentes = temperaturas[mascara_quente]

    # usar a mascara para EDITAR in-place: tudo abaixo de 0 e "travado" em 0
    # (simula um sensor que nao registra temperaturas negativas)
    temperaturas_corrigidas = temperaturas.copy()
    temperaturas_corrigidas[temperaturas_corrigidas < 0] = 0.0

    # mascaras podem ser combinadas com operadores logicos do numpy (&, |, ~)
    mascara_moderada = (temperaturas >= 10) & (temperaturas <= 30)
    dias_moderados = temperaturas[mascara_moderada]

    print("temperaturas:", temperaturas)
    print("mascara > 25:", mascara_quente)
    print("dias quentes:", dias_quentes)
    print("temperaturas corrigidas (sem negativos):", temperaturas_corrigidas)
    print("dias moderados (10 a 30):", dias_moderados)

    # sanity checks
    assert dias_quentes.tolist() == [31.0, 27.3, 40.1]
    assert temperaturas_corrigidas.min() == 0.0
    assert (temperaturas_corrigidas < 0).sum() == 0
    assert dias_moderados.tolist() == [15.0, 22.5, 27.3]
    print("OK: todos os asserts passaram.")
