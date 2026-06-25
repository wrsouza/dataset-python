"""
Checagem de feriados fixos (lista estatica + logica)

O que este script demonstra: como representar feriados fixos (mesma data
todo ano) e feriados de data unica, e como checar se uma data e feriado ou
listar os proximos feriados a partir de hoje.
Quando usar: para bloquear agendamentos em feriados, calcular dias uteis
(combinado com calendario de dias uteis) ou exibir avisos em calendarios.
"""

from datetime import date

# Feriados fixos nacionais (Brasil) que se repetem todo ano: (mes, dia, nome)
FERIADOS_FIXOS_ANUAIS = [
    (1, 1, "Ano Novo"),
    (4, 21, "Tiradentes"),
    (5, 1, "Dia do Trabalho"),
    (9, 7, "Independencia"),
    (10, 12, "Nossa Senhora Aparecida"),
    (11, 2, "Finados"),
    (11, 15, "Proclamacao da Republica"),
    (12, 25, "Natal"),
]

# Feriados moveis/especificos de um ano (datas que mudam, ex: pontos facultativos
# ou feriados moveis ja calculados externamente) - aqui fixos por simplicidade
FERIADOS_ESPECIFICOS = {
    date(2026, 2, 16): "Carnaval (exemplo)",
}


def eh_feriado(dia: date) -> str | None:
    """Retorna o nome do feriado se `dia` for feriado, ou None caso contrario.

    Checamos primeiro feriados fixos anuais comparando apenas (mes, dia) -
    assim funcionam para qualquer ano - depois feriados especificos que tem
    ano fixo.
    """
    for mes, dia_do_mes, nome in FERIADOS_FIXOS_ANUAIS:
        if dia.month == mes and dia.day == dia_do_mes:
            return nome

    return FERIADOS_ESPECIFICOS.get(dia)


def listar_proximos_feriados(a_partir_de: date, quantidade: int = 5) -> list:
    """Lista os proximos `quantidade` feriados a partir de uma data, em ordem.

    Construimos a lista completa de feriados conhecidos (fixos expandidos
    para o ano atual e o seguinte, mais os especificos), ordenamos e
    filtramos os que ainda nao passaram.
    """
    candidatos = []
    for ano in (a_partir_de.year, a_partir_de.year + 1):
        for mes, dia_do_mes, nome in FERIADOS_FIXOS_ANUAIS:
            try:
                candidatos.append((date(ano, mes, dia_do_mes), nome))
            except ValueError:
                continue  # data invalida (nao deveria ocorrer para feriados fixos)

    for dia, nome in FERIADOS_ESPECIFICOS.items():
        candidatos.append((dia, nome))

    futuros = sorted(d for d in candidatos if d[0] >= a_partir_de)
    return futuros[:quantidade]


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    datas_teste = [date(2026, 1, 1), date(2026, 6, 25), date(2026, 9, 7), date(2026, 2, 16)]

    for d in datas_teste:
        resultado = eh_feriado(d)
        if resultado:
            print(f"{d} e feriado: {resultado}")
        else:
            print(f"{d} nao e feriado")

    print("\nProximos 5 feriados a partir de 2026-06-25:")
    for dia, nome in listar_proximos_feriados(date(2026, 6, 25), 5):
        print(f"  {dia}: {nome}")

    # sanity checks
    assert eh_feriado(date(2026, 1, 1)) == "Ano Novo"
    assert eh_feriado(date(2026, 6, 25)) is None
    proximos = listar_proximos_feriados(date(2026, 6, 25), 1)
    assert proximos[0][0] == date(2026, 9, 7)
    print("\nOK: sanity checks passaram.")
