"""
Ufuncs nativas, np.vectorize e ufunc customizada com np.frompyfunc

O que este script demonstra: uso de ufuncs nativas (np.sqrt, np.exp), como envolver
uma funcao Python pura com np.vectorize/np.frompyfunc para aplica-la elementwise.
Quando usar: quando a operacao desejada nao existe nativamente no numpy mas precisa
ser aplicada a cada elemento de um array.
"""

import numpy as np

if __name__ == "__main__":
    valores = np.array([1.0, 4.0, 9.0, 16.0, 25.0])

    # ufuncs nativas: implementadas em C, operam elementwise automaticamente
    raizes = np.sqrt(valores)
    exponenciais = np.exp(valores / 10)  # divide para evitar overflow no exemplo

    # funcao Python pura, sem suporte nativo a arrays
    def categoriza(x):
        # logica arbitraria que so faz sentido escalar a escalar
        if x < 5:
            return "baixo"
        elif x < 15:
            return "medio"
        return "alto"

    # np.vectorize: aplica a funcao Python elemento a elemento (conveniencia, NAO
    # e mais rapido que um loop puro, e apenas uma forma vetorizada de escrever)
    categoriza_vetorizado = np.vectorize(categoriza)
    categorias = categoriza_vetorizado(valores)

    # np.frompyfunc: cria uma ufunc generica a partir de uma funcao Python,
    # precisa informar numero de entradas e numero de saidas
    dobro_mais_um = np.frompyfunc(lambda x: x * 2 + 1, 1, 1)
    resultado_custom = dobro_mais_um(valores).astype(float)

    print("valores:", valores)
    print("sqrt (ufunc nativa):", raizes)
    print("exp/10 (ufunc nativa):", exponenciais)
    print("categorias (np.vectorize):", categorias)
    print("dobro+1 (np.frompyfunc):", resultado_custom)

    # sanity checks
    assert raizes.tolist() == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert categorias.tolist() == ["baixo", "baixo", "medio", "alto", "alto"]
    assert resultado_custom.tolist() == [3.0, 9.0, 19.0, 33.0, 51.0]
    print("OK: todos os asserts passaram.")
