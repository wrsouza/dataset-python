"""
Geracao de datas recorrentes (semanal/mensal)

O que este script demonstra: como gerar uma sequencia de datas recorrentes
(diaria, semanal, mensal) a partir de uma data inicial, sem bibliotecas
externas como dateutil.
Quando usar: para gerar ocorrencias de eventos recorrentes (assinaturas,
reunioes semanais, cobrancas mensais) em agendas ou sistemas de cobranca.
"""

from datetime import date, timedelta


def gerar_recorrencia_diaria(inicio: date, quantidade: int, intervalo_dias: int = 1) -> list:
    """Gera `quantidade` datas espacadas por `intervalo_dias` dias."""
    return [inicio + timedelta(days=intervalo_dias * i) for i in range(quantidade)]


def gerar_recorrencia_semanal(inicio: date, quantidade: int, intervalo_semanas: int = 1) -> list:
    """Gera datas recorrentes semanais (reutiliza a logica diaria com semanas)."""
    return gerar_recorrencia_diaria(inicio, quantidade, intervalo_dias=7 * intervalo_semanas)


def _ultimo_dia_do_mes(ano: int, mes: int) -> int:
    """Retorna o numero de dias do mes, tratando troca de ano em dezembro.

    Calculamos pegando o dia anterior ao primeiro dia do mes seguinte -
    evita ter que codificar manualmente anos bissextos.
    """
    if mes == 12:
        proximo_mes_ano, proximo_mes = ano + 1, 1
    else:
        proximo_mes_ano, proximo_mes = ano, mes + 1
    primeiro_dia_proximo_mes = date(proximo_mes_ano, proximo_mes, 1)
    return (primeiro_dia_proximo_mes - timedelta(days=1)).day


def gerar_recorrencia_mensal(inicio: date, quantidade: int) -> list:
    """Gera datas recorrentes mensais, mantendo o mesmo dia do mes quando possivel.

    Meses tem tamanhos diferentes, entao nao podemos simplesmente somar 30
    dias. Quando o dia original (ex: 31) nao existe no mes destino (ex:
    fevereiro), usamos o ultimo dia disponivel daquele mes.
    """
    datas = []
    ano, mes, dia_original = inicio.year, inicio.month, inicio.day

    for i in range(quantidade):
        mes_offset = mes - 1 + i
        ano_calculado = ano + mes_offset // 12
        mes_calculado = mes_offset % 12 + 1
        dia_ajustado = min(dia_original, _ultimo_dia_do_mes(ano_calculado, mes_calculado))
        datas.append(date(ano_calculado, mes_calculado, dia_ajustado))

    return datas


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    inicio = date(2026, 1, 31)

    print("Recorrencia diaria (5 ocorrencias, a cada 2 dias):")
    for d in gerar_recorrencia_diaria(date(2026, 6, 1), 5, intervalo_dias=2):
        print(f"  {d}")

    print("\nRecorrencia semanal (4 ocorrencias):")
    for d in gerar_recorrencia_semanal(date(2026, 6, 1), 4):
        print(f"  {d}")

    print(f"\nRecorrencia mensal a partir de {inicio} (6 ocorrencias):")
    mensais = gerar_recorrencia_mensal(inicio, 6)
    for d in mensais:
        print(f"  {d}")

    # sanity checks
    assert mensais[0] == date(2026, 1, 31)
    assert mensais[1] == date(2026, 2, 28)  # fevereiro 2026 nao tem dia 31, nem 29 (nao bissexto)
    assert mensais[2] == date(2026, 3, 31)
    print("\nOK: sanity checks passaram.")
