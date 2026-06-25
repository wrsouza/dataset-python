"""
Normalizacao unicode com unicodedata

O que este script demonstra: como usar unicodedata.normalize para comparar e
limpar strings que representam o mesmo texto visualmente mas com codificacoes unicode diferentes.
Quando usar: ao comparar/deduplicar strings de usuarios onde acentos podem estar
compostos (NFC) ou decompostos (NFD), o que faz "==" falhar silenciosamente.
"""

import unicodedata


def comparar_formas_unicode(a: str, b: str) -> bool:
    """Compara duas strings normalizando ambas para a mesma forma (NFC) antes."""
    # sem normalizar, 'e' + acento combinante pode ser != do caractere acentuado pronto,
    # mesmo parecendo identico na tela.
    return unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)


def remover_acentos_nfkd(texto: str) -> str:
    """Remove acentos via decomposicao NFKD, descartando marcas combinantes (categoria Mn)."""
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def descrever_caracteres(texto: str) -> list[str]:
    """Retorna o nome unicode oficial de cada caractere - util para depurar encoding."""
    descricoes = []
    for c in texto:
        try:
            descricoes.append(f"{c!r}: {unicodedata.name(c)}")
        except ValueError:
            # nem todo codepoint tem nome (ex: caracteres de controle)
            descricoes.append(f"{c!r}: <sem nome>")
    return descricoes


if __name__ == "__main__":
    # Construimos as duas formas a partir de escapes \u explicitos, para nao
    # depender de como o editor/terminal grava acentos no arquivo-fonte.
    # 'e' agudo pre-composto = U+00E9 (forma NFC, um unico codepoint)
    e_agudo_composto = "é"
    # 'e' (U+0065) + acento agudo combinante (U+0301) = forma NFD (dois codepoints)
    e_agudo_decomposto = "é"

    forma_composta = "caf" + e_agudo_composto
    forma_decomposta = "caf" + e_agudo_decomposto

    print("Mesmo texto visual, == cru retorna:", forma_composta == forma_decomposta)
    print("Comparando com normalizacao:", comparar_formas_unicode(forma_composta, forma_decomposta))
    print("Sem acentos:", remover_acentos_nfkd(forma_composta))

    for desc in descrever_caracteres(e_agudo_composto):
        print(desc)

    # sanity check
    assert len(e_agudo_composto) == 1
    assert len(e_agudo_decomposto) == 2
    assert forma_composta != forma_decomposta  # comparacao "crua" falha, como esperado
    assert comparar_formas_unicode(forma_composta, forma_decomposta) is True
    assert remover_acentos_nfkd(forma_composta) == "cafe"
    print("\nOK: sanity checks passaram.")
