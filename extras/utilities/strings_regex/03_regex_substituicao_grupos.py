"""
re.sub com grupos de captura

O que este script demonstra: como usar grupos de captura em re.sub para
reorganizar/transformar partes especificas de um texto (datas, nomes, etc.).
Quando usar: quando a substituicao precisa reaproveitar pedacos do que foi casado, nao so apagar/trocar tudo.
"""

import re

# Grupos nomeados deixam o backreference no replacement mais legivel
DATA_BR_REGEX = re.compile(r"(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<ano>\d{4})")


def data_br_para_iso(texto: str) -> str:
    """Converte datas dd/mm/aaaa para o formato ISO aaaa-mm-dd dentro do texto."""
    # \g<nome> evita ambiguidade que \1\2 teria se houvesse digitos colados
    return DATA_BR_REGEX.sub(r"\g<ano>-\g<mes>-\g<dia>", texto)


def mascarar_cartao(texto: str) -> str:
    """Mascara numeros de cartao de credito (16 digitos) mantendo so os 4 ultimos."""
    padrao = re.compile(r"(\d{4})[ -]?(\d{4})[ -]?(\d{4})[ -]?(\d{4})")
    # grupos 1,2,3 sao trocados por asteriscos; grupo 4 (ultimos 4 digitos) e preservado
    return padrao.sub(r"**** **** **** \4", texto)


def usar_funcao_callback(texto: str) -> str:
    """Demonstra re.sub com uma funcao callback em vez de string de substituicao."""
    # callback e util quando a transformacao exige logica (ex: maiusculizar)
    return re.sub(r"\b(palavra)\b", lambda m: m.group(1).upper(), texto)


if __name__ == "__main__":
    texto_datas = "A reuniao foi em 25/06/2026 e o prazo final e 01/12/2026."
    texto_cartao = "Cartao: 1234 5678 9012 3456 foi usado na compra."
    texto_callback = "Essa palavra e importante, repita: palavra."

    print("Datas convertidas:", data_br_para_iso(texto_datas))
    print("Cartao mascarado:", mascarar_cartao(texto_cartao))
    print("Callback aplicado:", usar_funcao_callback(texto_callback))

    # sanity check
    assert "2026-06-25" in data_br_para_iso(texto_datas)
    assert "**** **** **** 3456" in mascarar_cartao(texto_cartao)
    assert "PALAVRA" in usar_funcao_callback(texto_callback)
    print("\nOK: sanity checks passaram.")
