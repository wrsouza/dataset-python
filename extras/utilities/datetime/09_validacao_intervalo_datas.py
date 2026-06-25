"""
Validacao de intervalo de datas

O que este script demonstra: como verificar se uma data esta dentro de um
intervalo [inicio, fim], e como validar que um intervalo informado pelo
usuario e logicamente consistente (inicio <= fim).
Quando usar: para validar formularios de reserva, filtros de relatorio por
periodo, ou regras de negocio que dependem de janelas de tempo.
"""

from datetime import date


class IntervaloInvalidoError(ValueError):
    """Erro especifico para quando o intervalo tem inicio posterior ao fim."""


def validar_intervalo(inicio: date, fim: date) -> None:
    """Garante que o intervalo e logicamente valido (inicio <= fim).

    Levantar uma excecao especifica em vez de retornar bool deixa explicito
    no chamador que um intervalo invalido e um erro de entrada, nao um
    resultado de negocio normal.
    """
    if inicio > fim:
        raise IntervaloInvalidoError(
            f"Data de inicio ({inicio}) e posterior a data de fim ({fim})"
        )


def data_esta_no_intervalo(data_alvo: date, inicio: date, fim: date, inclusivo: bool = True) -> bool:
    """Verifica se data_alvo esta dentro de [inicio, fim].

    inclusivo=True (padrao) inclui as bordas do intervalo; inclusivo=False
    exige que a data esteja estritamente entre inicio e fim.
    """
    validar_intervalo(inicio, fim)
    if inclusivo:
        return inicio <= data_alvo <= fim
    return inicio < data_alvo < fim


def intervalos_se_sobrepoem(inicio_a: date, fim_a: date, inicio_b: date, fim_b: date) -> bool:
    """Verifica se dois intervalos de datas se sobrepoem em algum ponto.

    Dois intervalos NAO se sobrepoem se um termina antes do outro comecar;
    a negacao dessa condicao da a regra de sobreposicao.
    """
    validar_intervalo(inicio_a, fim_a)
    validar_intervalo(inicio_b, fim_b)
    sem_sobreposicao = fim_a < inicio_b or fim_b < inicio_a
    return not sem_sobreposicao


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    inicio_reserva = date(2026, 7, 1)
    fim_reserva = date(2026, 7, 10)

    datas_teste = [date(2026, 6, 30), date(2026, 7, 1), date(2026, 7, 5), date(2026, 7, 10), date(2026, 7, 11)]
    for d in datas_teste:
        dentro = data_esta_no_intervalo(d, inicio_reserva, fim_reserva)
        print(f"{d} esta no intervalo [{inicio_reserva}, {fim_reserva}]? {dentro}")

    print()
    nova_reserva_inicio = date(2026, 7, 8)
    nova_reserva_fim = date(2026, 7, 15)
    sobrepoe = intervalos_se_sobrepoem(inicio_reserva, fim_reserva, nova_reserva_inicio, nova_reserva_fim)
    print(f"Reserva [{inicio_reserva}, {fim_reserva}] sobrepoe "
          f"[{nova_reserva_inicio}, {nova_reserva_fim}]? {sobrepoe}")

    print("\nTentando validar um intervalo invalido (inicio > fim):")
    try:
        validar_intervalo(date(2026, 7, 10), date(2026, 7, 1))
    except IntervaloInvalidoError as erro:
        print(f"  Erro capturado como esperado: {erro}")

    # sanity checks
    assert data_esta_no_intervalo(date(2026, 7, 1), inicio_reserva, fim_reserva) is True
    assert data_esta_no_intervalo(date(2026, 7, 1), inicio_reserva, fim_reserva, inclusivo=False) is False
    assert sobrepoe is True
    assert intervalos_se_sobrepoem(date(2026, 1, 1), date(2026, 1, 5), date(2026, 2, 1), date(2026, 2, 5)) is False
    print("\nOK: sanity checks passaram.")
