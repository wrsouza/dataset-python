"""
Split avancado com multiplos delimitadores

O que este script demonstra: como usar re.split para dividir texto por varios
delimitadores diferentes ao mesmo tempo (virgula, ponto-e-virgula, pipe, espacos multiplos).
Quando usar: ao receber dados semi-estruturados onde o delimitador nao e sempre o mesmo caractere.
"""

import re


def split_multidelimitador(texto: str) -> list[str]:
    """Divide o texto por virgula, ponto-e-virgula ou pipe, ignorando vazios."""
    # o conjunto [,;|] define a classe de delimitadores aceitos
    partes = re.split(r"[,;|]+", texto)
    # strip remove espacos residuais e filtramos strings vazias resultantes de delimitadores colados
    return [p.strip() for p in partes if p.strip()]


def split_mantendo_delimitador(texto: str) -> list[str]:
    """Divide o texto mas mantem o delimitador como item separado, usando grupo de captura."""
    # quando o padrao tem um grupo de captura, re.split inclui o delimitador no resultado
    return [p for p in re.split(r"(\d+)", texto) if p]


def split_espacos_multiplos(texto: str) -> list[str]:
    """Divide por qualquer sequencia de espacos em branco (1 ou mais)."""
    return re.split(r"\s+", texto.strip())


if __name__ == "__main__":
    linha_csv_like = "maca, banana; uva|melao,  ,abacaxi"
    texto_com_numeros = "item1quantidade5preco10"
    texto_espacado = "  isso   tem    espacos   irregulares  "

    print("Multi-delimitador:", split_multidelimitador(linha_csv_like))
    print("Mantendo delimitador:", split_mantendo_delimitador(texto_com_numeros))
    print("Espacos multiplos:", split_espacos_multiplos(texto_espacado))

    # sanity check
    assert split_multidelimitador(linha_csv_like) == ["maca", "banana", "uva", "melao", "abacaxi"]
    assert split_espacos_multiplos(texto_espacado) == ["isso", "tem", "espacos", "irregulares"]
    print("\nOK: sanity checks passaram.")
