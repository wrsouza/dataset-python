"""
Slugify: gerar slugs a partir de texto livre

O que este script demonstra: como remover acentos (via unicodedata), normalizar
espacos/caracteres especiais e gerar um slug amigavel para URLs, usando so a stdlib.
Quando usar: ao gerar identificadores de URL a partir de titulos digitados por usuarios.
"""

import re
import unicodedata


def remover_acentos(texto: str) -> str:
    """Remove diacriticos (acentos, cedilhas) decompondo e filtrando marcas combinantes."""
    # NFKD separa o caractere base do diacritico (ex: 'a' + acento agudo);
    # depois descartamos tudo que e categoria 'Mn' (mark, nonspacing).
    forma_decomposta = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in forma_decomposta if unicodedata.category(c) != "Mn")


def slugify(texto: str) -> str:
    """Converte um texto livre em um slug minusculo separado por hifens."""
    sem_acento = remover_acentos(texto).lower()
    # qualquer coisa que nao seja letra/numero vira hifen
    com_hifens = re.sub(r"[^a-z0-9]+", "-", sem_acento)
    # remove hifens redundantes nas pontas e duplicados no meio
    return re.sub(r"-{2,}", "-", com_hifens).strip("-")


if __name__ == "__main__":
    titulos = [
        "Programacao Funcional em Python!",
        "  Como usar REGEX (de verdade)?  ",
        "Codigo limpo: principios & praticas",
        "Sao Paulo - Cidade Maravilhosa?",
    ]

    for titulo in titulos:
        print(f"{titulo!r:45} -> {slugify(titulo)}")

    # sanity check
    assert slugify("Programacao Funcional em Python!") == "programacao-funcional-em-python"
    assert slugify("Sao Paulo - Cidade Maravilhosa?") == "sao-paulo-cidade-maravilhosa"
    print("\nOK: sanity checks passaram.")
