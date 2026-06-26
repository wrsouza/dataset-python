"""
Two Sum - Par de Números que Somam um Valor Alvo

Cenário: conciliação financeira (encontrar duas transações que somadas
batem com um valor esperado), validação de carrinho de compras (dois itens
cujo preço total atinge um cupom mínimo), problema clássico de entrevistas.
O que este script demonstra: solução O(n) com dicionário de complementos já
vistos, em contraste com a força bruta O(n^2), e retorno dos índices
originais (não apenas dos valores).
"""


def two_sum_forca_bruta(numeros: list[int], alvo: int) -> tuple[int, int] | None:
    """O(n^2): compara todos os pares - útil como baseline de corretude."""
    for i in range(len(numeros)):
        for j in range(i + 1, len(numeros)):
            if numeros[i] + numeros[j] == alvo:
                return i, j
    return None


def two_sum_otimizado(numeros: list[int], alvo: int) -> tuple[int, int] | None:
    """O(n): para cada número, verifica se o complemento (alvo - numero) já foi visto."""
    vistos = {}  # valor -> índice onde foi encontrado
    for i, num in enumerate(numeros):
        complemento = alvo - num
        if complemento in vistos:
            return vistos[complemento], i
        # Só registra depois de checar, para não usar o mesmo índice duas vezes.
        vistos[num] = i
    return None


if __name__ == "__main__":
    transacoes = [120, 45, 78, 32, 90, 15]
    valor_esperado = 123  # ex: 45 + 78

    par_bruta = two_sum_forca_bruta(transacoes, valor_esperado)
    par_otimo = two_sum_otimizado(transacoes, valor_esperado)
    assert par_bruta == par_otimo, "Implementações divergiram - bug!"

    if par_otimo:
        i, j = par_otimo
        print(f"Transações: {transacoes}")
        print(f"Par encontrado nos índices {par_otimo}: {transacoes[i]} + {transacoes[j]} = {valor_esperado}")
    else:
        print("Nenhum par encontrado para o valor alvo.")
