"""
Precisao de float e uso de Decimal

Cenario: sistema financeiro somando valores monetarios (ex: total de uma
fatura com varios itens). Float usa representacao binaria e nao consegue
representar exatamente a maioria dos decimais (ex: 0.1), entao somas
repetidas acumulam erro de arredondamento que pode causar diferencas de
centavos em relatorios contabeis - um problema real e caro em producao.
Demonstra: o erro classico de soma de floats, e a correcao usando o modulo
decimal para aritmetica financeira exata.
"""

from decimal import Decimal, ROUND_HALF_UP, getcontext


def somar_com_float(valores):
    """Soma 'ingenua' usando float - sujeita a erro de arredondamento binario."""
    total = 0.0
    for v in valores:
        total += v
    return total


def somar_com_decimal(valores_str):
    """Soma exata usando Decimal, construido a partir de strings.

    Importante: Decimal(0.1) ainda herda a imprecisao do float original.
    Para precisao real, os valores devem chegar como string (ou ja como
    Decimal), nunca convertidos de um float existente.
    """
    total = Decimal("0")
    for v in valores_str:
        total += Decimal(v)
    return total


def arredondar_para_centavos(valor_decimal):
    """Arredonda para 2 casas decimais usando a regra bancaria (half up)."""
    return valor_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    # Caso classico: 0.1 + 0.2 != 0.3 em float, por causa da representacao
    # binaria de fracoes decimais (0.1 nao tem representacao exata em base 2).
    a, b = 0.1, 0.2
    print(f"float: 0.1 + 0.2 = {a + b!r}  (esperado matematicamente: 0.3)")
    print(f"float: 0.1 + 0.2 == 0.3 ? {a + b == 0.3}")

    print()

    # Simulando uma fatura com 10 itens de R$ 0.10 cada -> deveria dar R$ 1.00
    itens_float = [0.10] * 10
    total_float = somar_com_float(itens_float)
    print(f"Soma de 10x R$0.10 com float: {total_float!r}")
    print(f"  Resultado bate com 1.00 exato? {total_float == 1.0}")

    itens_decimal = ["0.10"] * 10  # valores como string, vindos direto da fonte
    total_decimal = somar_com_decimal(itens_decimal)
    print(f"Soma de 10x R$0.10 com Decimal: {total_decimal}")
    print(f"  Resultado bate com 1.00 exato? {total_decimal == Decimal('1.00')}")

    print()

    # Caso de overflow/precisao maior: getcontext().prec controla os digitos
    # significativos do Decimal, util para calculos financeiros com muitas
    # casas (ex: juros compostos diarios acumulados por anos).
    getcontext().prec = 28
    juros_diario = Decimal("1.0001")
    valor = Decimal("1000.00")
    for _ in range(365):  # 1 ano de juros compostos diarios
        valor *= juros_diario
    valor_final = arredondar_para_centavos(valor)
    print(f"Valor apos 365 dias de juros compostos (Decimal, alta precisao): R$ {valor_final}")
