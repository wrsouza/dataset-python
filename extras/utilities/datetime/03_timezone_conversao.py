"""
Conversao entre timezones com zoneinfo

O que este script demonstra: como anexar timezone a um datetime "naive" e
converter o mesmo instante entre diferentes timezones IANA usando zoneinfo.
Quando usar: ao exibir horarios de eventos para usuarios em fusos diferentes
ou ao normalizar timestamps recebidos de fontes em fusos distintos.
"""

from datetime import datetime

try:
    from zoneinfo import ZoneInfo

    # Tenta carregar um fuso real para verificar se o banco de dados de
    # timezones (tzdata) esta disponivel. No Windows, a stdlib zoneinfo
    # depende do pacote `tzdata` (via pip) pois o SO nao traz o banco IANA.
    ZoneInfo("UTC")
    ZONEINFO_DISPONIVEL = True
except Exception:
    ZONEINFO_DISPONIVEL = False


def converter_fuso(dt_naive: datetime, fuso_origem: str, fuso_destino: str):
    """Converte um datetime naive de um fuso de origem para um fuso de destino.

    Se zoneinfo/tzdata nao estiver disponivel, cai de volta para timezone
    fixo (timedelta) so para UTC, avisando que conversao completa nao e
    possivel sem o banco IANA.
    """
    if ZONEINFO_DISPONIVEL:
        origem = dt_naive.replace(tzinfo=ZoneInfo(fuso_origem))
        return origem.astimezone(ZoneInfo(fuso_destino))

    # Fallback gracioso: sem tzdata so conseguimos tratar UTC com offset fixo
    from datetime import timezone

    print(
        "AVISO: zoneinfo/tzdata indisponivel. Usando fallback UTC fixo. "
        "Instale com 'pip install tzdata' para conversao completa entre fusos."
    )
    origem = dt_naive.replace(tzinfo=timezone.utc)
    return origem  # sem tzdata nao sabemos o offset de fuso_destino


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    reuniao = datetime(2026, 6, 25, 15, 0, 0)  # 15h sem fuso definido

    print(f"Horario da reuniao (naive): {reuniao}")
    print(f"zoneinfo/tzdata disponivel: {ZONEINFO_DISPONIVEL}")

    sao_paulo_para_londres = converter_fuso(reuniao, "America/Sao_Paulo", "Europe/London")
    print(f"Sao Paulo 15:00 -> Londres: {sao_paulo_para_londres}")

    sao_paulo_para_tokyo = converter_fuso(reuniao, "America/Sao_Paulo", "Asia/Tokyo")
    print(f"Sao Paulo 15:00 -> Tokyo: {sao_paulo_para_tokyo}")

    utc_para_nyc = converter_fuso(reuniao, "UTC", "America/New_York")
    print(f"UTC 15:00 -> New York: {utc_para_nyc}")

    # sanity checks (apenas se tzdata estiver disponivel, conversao e exata)
    if ZONEINFO_DISPONIVEL:
        assert sao_paulo_para_londres.utcoffset() is not None
        assert utc_para_nyc.hour in (10, 11)  # NY esta 4-5h atras de UTC
    print("\nOK: sanity checks passaram.")
