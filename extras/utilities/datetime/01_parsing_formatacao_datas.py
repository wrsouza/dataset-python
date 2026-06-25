"""
Parsing e formatacao de datas

O que este script demonstra: como converter strings em objetos datetime (strptime)
e como converter objetos datetime em strings em formatos variados (strftime).
Quando usar: ao ler datas de arquivos/APIs em formatos diversos ou ao exibir
datas para o usuario em um formato legivel especifico.
"""

from datetime import datetime

# Formatos de entrada comuns que aparecem em arquivos CSV, logs e APIs
FORMATOS_ENTRADA = {
    "iso": "%Y-%m-%d",
    "br": "%d/%m/%Y",
    "us": "%m/%d/%Y",
    "log": "%Y-%m-%d %H:%M:%S",
    "extenso_en": "%B %d, %Y",  # ex: "June 25, 2026"
}


def parsear_data(texto: str, formato_chave: str) -> datetime:
    """Converte uma string em datetime usando uma chave de FORMATOS_ENTRADA.

    Usamos um dicionario de formatos nomeados em vez de strptime direto
    para deixar explicito qual formato cada fonte de dados usa.
    """
    formato = FORMATOS_ENTRADA[formato_chave]
    return datetime.strptime(texto, formato)


def formatar_data(dt: datetime, estilo: str) -> str:
    """Formata um datetime para exibicao em diferentes estilos."""
    estilos = {
        "curto": "%d/%m/%Y",
        "longo": "%A, %d de %B de %Y",  # nomes em ingles pois locale padrao nao e pt-BR
        "iso": "%Y-%m-%dT%H:%M:%S",
        "so_hora": "%H:%M:%S",
    }
    return dt.strftime(estilos[estilo])


if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    entradas = [
        ("2026-06-25", "iso"),
        ("25/06/2026", "br"),
        ("06/25/2026", "us"),
        ("2026-06-25 14:30:00", "log"),
        ("June 25, 2026", "extenso_en"),
    ]

    for texto, chave in entradas:
        dt = parsear_data(texto, chave)
        print(f"Entrada: {texto!r} ({chave}) -> datetime: {dt}")

    # Pegamos a primeira data parseada para demonstrar formatacao de saida
    dt_exemplo = parsear_data("2026-06-25 14:30:00", "log")
    print()
    print("Formatacoes de saida para", dt_exemplo)
    for estilo in ("curto", "longo", "iso", "so_hora"):
        print(f"  {estilo}: {formatar_data(dt_exemplo, estilo)}")

    # sanity checks
    assert parsear_data("2026-06-25", "iso") == datetime(2026, 6, 25)
    assert formatar_data(datetime(2026, 6, 25), "iso") == "2026-06-25T00:00:00"
    print("\nOK: sanity checks passaram.")
