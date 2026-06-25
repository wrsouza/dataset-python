"""
Calculo de dias uteis entre duas datas

O que este script demonstra: como contar dias uteis (seg-sex, excluindo
feriados) entre duas datas e como avancar N dias uteis a partir de uma data.
Quando usar: para calcular prazos de SLA, vencimentos de boletos ou entregas
que so contam dias comerciais.
"""

from datetime import date, timedelta

# Feriados fixos de exemplo (poderiam vir de um arquivo ou API em um caso real)
FERIADOS_EXEMPLO = {
    date(2026, 1, 1),   # Ano Novo
    date(2026, 4, 21),  # Tiradentes
    date(2026, 9, 7),   # Independencia
    date(2026, 12, 25),  # Natal
}


def eh_dia_util(dia: date, feriados: set = frozenset()) -> bool:
    """Um dia e util se nao for sabado/domingo e nao estiver na lista de feriados.

    weekday() retorna 0=segunda ... 6=domingo, por isso comparamos com 5 e 6.
    """
    return dia.weekday() < 5 and dia not in feriados


def contar_dias_uteis(inicio: date, fim: date, feriados: set = frozenset()) -> int:
    """Conta quantos dias uteis existem no intervalo [inicio, fim], inclusive.

    Iteramos dia a dia porque o intervalo tipico (semanas/meses) e pequeno;
    para intervalos muito grandes valeria calcular por semanas completas.
    """
    if inicio > fim:
        inicio, fim = fim, inicio

    total = 0
    dia_atual = inicio
    while dia_atual <= fim:
        if eh_dia_util(dia_atual, feriados):
            total += 1
        dia_atual += timedelta(days=1)
    return total


def avancar_dias_uteis(data_base: date, quantidade: int, feriados: set = frozenset()) -> date:
    """Avanca `quantidade` dias uteis a partir de data_base (nao inclui data_base)."""
    dia_atual = data_base
    avancados = 0
    while avancados < quantidade:
        dia_atual += timedelta(days=1)
        if eh_dia_util(dia_atual, feriados):
            avancados += 1
    return dia_atual


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    inicio = date(2026, 9, 1)   # terca-feira
    fim = date(2026, 9, 10)     # quinta-feira (semana seguinte)

    uteis_sem_feriado = contar_dias_uteis(inicio, fim)
    uteis_com_feriado = contar_dias_uteis(inicio, fim, FERIADOS_EXEMPLO)

    print(f"Dias uteis entre {inicio} e {fim} (sem considerar feriados): {uteis_sem_feriado}")
    print(f"Dias uteis entre {inicio} e {fim} (considerando feriados): {uteis_com_feriado}")
    print("(7 de setembro e feriado e cai em uma segunda-feira no intervalo)")

    prazo_5_dias_uteis = avancar_dias_uteis(date(2026, 9, 1), 5, FERIADOS_EXEMPLO)
    print(f"\n5 dias uteis depois de 2026-09-01 (com feriados): {prazo_5_dias_uteis}")

    # sanity checks
    assert uteis_com_feriado == uteis_sem_feriado - 1
    assert eh_dia_util(date(2026, 9, 5)) is False  # sabado
    assert eh_dia_util(date(2026, 9, 7), FERIADOS_EXEMPLO) is False  # feriado
    print("\nOK: sanity checks passaram.")
