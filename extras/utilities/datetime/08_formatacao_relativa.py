"""
Formatacao de tempo relativo ("ha 2 dias", "em 3 horas")

O que este script demonstra: como converter a diferenca entre dois datetimes
em uma frase legivel de tempo relativo, no passado ou no futuro.
Quando usar: em feeds de atividade, notificacoes ou logs onde e mais
natural mostrar "ha 5 minutos" do que um timestamp completo.
"""

from datetime import datetime, timedelta

# Limites em segundos para escolher a unidade mais adequada, do menor pro maior
UNIDADES = (
    ("segundo", 60),
    ("minuto", 60 * 60),
    ("hora", 60 * 60 * 24),
    ("dia", 60 * 60 * 24 * 30),
    ("mes", 60 * 60 * 24 * 365),
)


def _escolher_unidade(segundos_totais: float):
    """Escolhe a unidade (segundo/minuto/hora/dia/mes/ano) e a quantidade.

    Percorremos as unidades da menor pra maior e paramos na primeira cujo
    limite ainda nao foi atingido - assim "90 segundos" cai em minutos,
    e "25 horas" cai em dias.
    """
    limite_anterior = 1
    for nome, limite_segundos in UNIDADES:
        if segundos_totais < limite_segundos:
            quantidade = int(segundos_totais // limite_anterior)
            return max(quantidade, 1), nome
        limite_anterior = limite_segundos

    # Caso extremo: mais de um ano
    anos = int(segundos_totais // (60 * 60 * 24 * 365))
    return anos, "ano"


def tempo_relativo(momento: datetime, referencia: datetime = None) -> str:
    """Retorna uma string de tempo relativo tipo 'ha 2 dias' ou 'em 3 horas'."""
    if referencia is None:
        referencia = datetime.now()

    delta = referencia - momento
    segundos_totais = delta.total_seconds()
    no_passado = segundos_totais >= 0

    if abs(segundos_totais) < 1:
        return "agora mesmo"

    quantidade, unidade = _escolher_unidade(abs(segundos_totais))
    plural = "s" if quantidade != 1 else ""

    if no_passado:
        return f"ha {quantidade} {unidade}{plural}"
    return f"em {quantidade} {unidade}{plural}"


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    referencia = datetime(2026, 6, 25, 12, 0, 0)

    casos = [
        referencia - timedelta(seconds=30),
        referencia - timedelta(minutes=15),
        referencia - timedelta(hours=3),
        referencia - timedelta(days=2),
        referencia + timedelta(hours=5),
        referencia + timedelta(days=10),
        referencia,
    ]

    for momento in casos:
        print(f"{momento} -> {tempo_relativo(momento, referencia)}")

    # sanity checks
    assert tempo_relativo(referencia, referencia) == "agora mesmo"
    assert tempo_relativo(referencia - timedelta(hours=3), referencia) == "ha 3 horas"
    assert tempo_relativo(referencia + timedelta(days=10), referencia).startswith("em")
    print("\nOK: sanity checks passaram.")
