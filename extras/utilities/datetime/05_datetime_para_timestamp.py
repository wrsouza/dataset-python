"""
Conversao entre datetime e timestamp (epoch)

O que este script demonstra: como converter um objeto datetime para um
timestamp Unix (segundos desde 1970-01-01 UTC) e vice-versa.
Quando usar: ao trocar dados de tempo com APIs/bancos que armazenam epoch,
ou ao serializar/desserializar datas em JSON.
"""

from datetime import datetime, timezone


def datetime_para_epoch(dt: datetime) -> float:
    """Converte um datetime para timestamp epoch (segundos desde 1970 UTC).

    Se o datetime for naive (sem tzinfo), assumimos que representa horario
    local do sistema - timestamp() faz essa interpretacao automaticamente.
    Para evitar ambiguidade, e mais seguro sempre trabalhar com datetimes
    "aware" (com tzinfo) quando precisao entre maquinas/fusos importa.
    """
    return dt.timestamp()


def epoch_para_datetime(timestamp: float, em_utc: bool = True) -> datetime:
    """Converte um timestamp epoch para datetime.

    em_utc=True retorna um datetime aware em UTC (recomendado para
    armazenamento e comparacao); em_utc=False retorna o horario local naive.
    """
    if em_utc:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return datetime.fromtimestamp(timestamp)


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    dt_aware_utc = datetime(2026, 6, 25, 12, 0, 0, tzinfo=timezone.utc)
    epoch = datetime_para_epoch(dt_aware_utc)
    print(f"datetime UTC {dt_aware_utc} -> epoch: {epoch}")

    de_volta = epoch_para_datetime(epoch, em_utc=True)
    print(f"epoch {epoch} -> datetime UTC: {de_volta}")

    # timestamp conhecido: 0 representa exatamente a epoch (1970-01-01 00:00:00 UTC)
    origem_epoch = epoch_para_datetime(0, em_utc=True)
    print(f"\nTimestamp 0 -> {origem_epoch}")

    # exemplo com timestamp "agora" simulado (valor fixo para reprodutibilidade)
    timestamp_exemplo = 1_800_000_000  # data fixa hipotetica
    data_exemplo = epoch_para_datetime(timestamp_exemplo, em_utc=True)
    print(f"Timestamp {timestamp_exemplo} -> {data_exemplo}")

    # sanity checks
    assert origem_epoch == datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert datetime_para_epoch(de_volta) == epoch
    print("\nOK: sanity checks passaram.")
