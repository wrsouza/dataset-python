"""
Calculo de diferenca entre datas

O que este script demonstra: como usar timedelta para calcular a diferenca
entre duas datas em dias, horas, semanas, e tambem como somar/subtrair
intervalos de tempo de uma data.
Quando usar: para calcular prazos, duracoes de eventos, ou tempo restante
até uma data alvo.
"""

from datetime import datetime, timedelta


def diferenca_detalhada(inicio: datetime, fim: datetime) -> dict:
    """Retorna a diferenca entre duas datas decomposta em varias unidades.

    timedelta so armazena dias/segundos/microsegundos internamente, entao
    para "anos" e "meses" aproximados precisamos calcular manualmente -
    nao existe conversao exata pois meses tem tamanhos diferentes.
    """
    delta = fim - inicio
    total_segundos = delta.total_seconds()
    return {
        "dias": delta.days,
        "semanas": delta.days / 7,
        "horas_totais": total_segundos / 3600,
        "segundos_totais": total_segundos,
    }


def somar_intervalo(base: datetime, dias: int = 0, horas: int = 0, semanas: int = 0) -> datetime:
    """Soma um intervalo de tempo a uma data base."""
    return base + timedelta(days=dias, hours=horas, weeks=semanas)


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    data_inicio = datetime(2026, 1, 1, 9, 0, 0)
    data_fim = datetime(2026, 6, 25, 18, 30, 0)

    resultado = diferenca_detalhada(data_inicio, data_fim)
    print(f"Diferenca entre {data_inicio} e {data_fim}:")
    for unidade, valor in resultado.items():
        print(f"  {unidade}: {valor}")

    # exemplo de soma de intervalo: prazo de entrega 15 dias apos hoje
    prazo = somar_intervalo(data_fim, dias=15)
    print(f"\nPrazo de 15 dias apos {data_fim.date()}: {prazo.date()}")

    # exemplo de subtracao usando timedelta negativo
    uma_semana_antes = data_fim - timedelta(weeks=1)
    print(f"Uma semana antes de {data_fim.date()}: {uma_semana_antes.date()}")

    # sanity checks
    assert resultado["dias"] == (data_fim - data_inicio).days
    assert somar_intervalo(datetime(2026, 1, 1), dias=1) == datetime(2026, 1, 2)
    print("\nOK: sanity checks passaram.")
