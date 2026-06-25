"""
Calculo de idade exata a partir da data de nascimento

O que este script demonstra: como calcular idade em anos completos (e
opcionalmente meses/dias restantes) a partir de uma data de nascimento,
tratando corretamente o caso de aniversario ainda nao ocorrido no ano.
Quando usar: para validacao de maioridade, exibicao de perfil de usuario
ou calculos atuariais simples.
"""

from datetime import date


def calcular_idade(nascimento: date, referencia: date = None) -> int:
    """Calcula idade em anos completos na data de referencia (padrao: hoje).

    A subtracao simples de anos (referencia.year - nascimento.year) erra
    quando o aniversario ainda nao chegou no ano de referencia - por isso
    subtraimos 1 se o (mes, dia) de nascimento ainda nao ocorreu.
    """
    if referencia is None:
        referencia = date.today()

    idade = referencia.year - nascimento.year
    aniversario_ja_passou = (referencia.month, referencia.day) >= (nascimento.month, nascimento.day)
    if not aniversario_ja_passou:
        idade -= 1
    return idade


def calcular_idade_detalhada(nascimento: date, referencia: date = None) -> dict:
    """Calcula idade decomposta em anos, meses e dias completos.

    Calculamos anos completos primeiro, depois meses completos desde o
    ultimo "aniversario anual", depois os dias restantes - como cada
    componente desconta o anterior, o resultado nunca tem meses >= 12
    ou dias >= ~31.
    """
    if referencia is None:
        referencia = date.today()

    anos = calcular_idade(nascimento, referencia)

    # Data do ultimo aniversario completado (ano de nascimento + anos completos)
    try:
        ultimo_aniversario = nascimento.replace(year=nascimento.year + anos)
    except ValueError:
        # caso de nascido em 29/fev e o ano de referencia nao ser bissexto
        ultimo_aniversario = nascimento.replace(year=nascimento.year + anos, day=28)

    meses = 0
    cursor = ultimo_aniversario
    while True:
        proximo_mes = cursor.month % 12 + 1
        proximo_ano = cursor.year + (1 if cursor.month == 12 else 0)
        dia_no_mes = min(cursor.day, 28)  # aproximacao segura para nao quebrar em fevereiro
        candidato = date(proximo_ano, proximo_mes, dia_no_mes)
        if candidato > referencia:
            break
        cursor = candidato
        meses += 1

    dias = (referencia - cursor).days

    return {"anos": anos, "meses": meses, "dias": dias}


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    nascimento = date(1990, 8, 15)
    hoje_simulado = date(2026, 6, 25)

    idade_simples = calcular_idade(nascimento, hoje_simulado)
    print(f"Nascimento: {nascimento}, referencia: {hoje_simulado}")
    print(f"Idade em anos completos: {idade_simples}")

    idade_detalhe = calcular_idade_detalhada(nascimento, hoje_simulado)
    print(f"Idade detalhada: {idade_detalhe['anos']} anos, "
          f"{idade_detalhe['meses']} meses e {idade_detalhe['dias']} dias")

    # caso de aniversario no dia exato da referencia
    nascido_hoje_simulado = date(2000, 6, 25)
    print(f"\nQuem nasceu em {nascido_hoje_simulado} tem hoje "
          f"{calcular_idade(nascido_hoje_simulado, hoje_simulado)} anos")

    # sanity checks
    assert calcular_idade(date(1990, 8, 15), date(2026, 6, 25)) == 35  # aniversario ainda nao chegou
    assert calcular_idade(date(1990, 6, 25), date(2026, 6, 25)) == 36  # aniversario e hoje
    assert calcular_idade(date(1990, 6, 26), date(2026, 6, 25)) == 35  # aniversario e amanha
    print("\nOK: sanity checks passaram.")
