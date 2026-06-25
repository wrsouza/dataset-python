"""
textwrap para quebra de linha e formatacao de paragrafos

O que este script demonstra: como usar o modulo textwrap da stdlib para quebrar
texto em linhas de largura fixa, indentar paragrafos e gerar versoes resumidas (shorten).
Quando usar: ao formatar texto para terminal, relatorios de largura fixa ou previews truncados.
"""

import textwrap

TEXTO_LONGO = (
    "Python e uma linguagem de programacao de alto nivel, interpretada, "
    "de proposito geral, criada por Guido van Rossum e lancada em 1991. "
    "Sua filosofia de design enfatiza a legibilidade do codigo, usando "
    "indentacao significativa para delimitar blocos."
)


def quebrar_em_linhas(texto: str, largura: int = 40) -> list[str]:
    """Quebra o texto em uma lista de linhas, cada uma com no maximo 'largura' caracteres."""
    # wrap() nao quebra palavras no meio por padrao, preservando legibilidade
    return textwrap.wrap(texto, width=largura)


def indentar_paragrafo(texto: str, prefixo: str = "    ") -> str:
    """Adiciona um prefixo (ex: indentacao) no inicio de cada linha do texto."""
    return textwrap.indent(texto, prefixo)


def resumir_texto(texto: str, largura: int = 50) -> str:
    """Trunca o texto para caber em 'largura' caracteres, adicionando [...] se cortar."""
    # shorten colapsa espacos extras e corta no limite de palavras, nao no meio de uma palavra
    return textwrap.shorten(texto, width=largura, placeholder=" [...]")


if __name__ == "__main__":
    linhas = quebrar_em_linhas(TEXTO_LONGO, largura=40)
    print("Texto quebrado em linhas de 40 caracteres:")
    for linha in linhas:
        print(linha)

    print("\nTexto indentado:")
    print(indentar_paragrafo("Linha um\nLinha dois\nLinha tres"))

    print("\nTexto resumido:")
    print(resumir_texto(TEXTO_LONGO, largura=60))

    # sanity check
    assert all(len(linha) <= 40 for linha in linhas)
    assert resumir_texto(TEXTO_LONGO, largura=60).endswith("[...]")
    print("\nOK: sanity checks passaram.")
