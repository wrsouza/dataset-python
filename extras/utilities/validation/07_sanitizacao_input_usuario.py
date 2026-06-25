"""
Sanitizacao de Input do Usuario

O que este script demonstra: limpar e escapar strings de entrada do usuario
removendo caracteres de controle, normalizando espacos e escapando HTML
basico, usando apenas string/re/html da stdlib.
Quando usar: antes de exibir input do usuario em uma pagina (evitar XSS
basico) ou antes de gravar texto "sujo" em banco/arquivo.
"""

import html
import re
import unicodedata


def remover_caracteres_controle(texto: str) -> str:
    """Remove caracteres de controle (categoria Unicode 'Cc'), exceto \n e \t."""
    return "".join(
        ch for ch in texto
        if unicodedata.category(ch) != "Cc" or ch in ("\n", "\t")
    )


def normalizar_espacos(texto: str) -> str:
    """Colapsa multiplos espacos/tabs em um unico espaco e remove bordas."""
    return re.sub(r"[ \t]+", " ", texto).strip()


def escapar_html(texto: str) -> str:
    """Escapa caracteres especiais de HTML para evitar injecao basica de tags."""
    return html.escape(texto, quote=True)


def sanitizar_input(texto: str, max_len: int = 200) -> str:
    """Pipeline completo de sanitizacao: controle -> espacos -> truncagem -> escape."""
    if not isinstance(texto, str):
        texto = str(texto)

    texto = remover_caracteres_controle(texto)
    texto = normalizar_espacos(texto)
    texto = texto[:max_len]  # evita inputs absurdamente longos (DoS simples)
    texto = escapar_html(texto)
    return texto


if __name__ == "__main__":
    entradas_teste = [
        "Ola  mundo!   <script>alert('xss')</script>",
        "Texto\x00com\x07controle",
        "   espacos   nas   bordas   ",
        "x" * 300,  # texto muito longo
    ]

    for entrada in entradas_teste:
        limpo = sanitizar_input(entrada)
        print(f"original (repr): {entrada[:50]!r}...")
        print(f"sanitizado:       {limpo[:80]!r}")
        print()

    assert "<script>" not in sanitizar_input("<script>alert(1)</script>")
    assert sanitizar_input("  a   b  ") == "a b"
    assert len(sanitizar_input("x" * 300, max_len=10)) <= 10
    print("Sanity check OK.")
