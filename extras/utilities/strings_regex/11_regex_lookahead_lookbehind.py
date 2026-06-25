"""
Lookahead e lookbehind em regex

O que este script demonstra: como usar asserts de largura zero (?=...), (?!...),
(?<=...) e (?<!...) para casar padroes com base no contexto, sem consumir esse contexto no resultado.
Quando usar: quando a condicao de casamento depende do que vem antes/depois, mas esse
trecho nao deve fazer parte do texto extraido/substituido (ex: separar numero de moeda).
"""

import re


def extrair_valor_apos_simbolo(texto: str, simbolo: str = r"R\$") -> list[str]:
    """Extrai numeros que vem IMEDIATAMENTE depois de um simbolo de moeda (lookbehind)."""
    # (?<=R\$) exige que "R$" exista antes, mas nao inclui "R$" no resultado
    padrao = re.compile(rf"(?<={simbolo})\s?\d+(?:[.,]\d+)?")
    return [m.strip() for m in padrao.findall(texto)]


def senha_valida(senha: str) -> bool:
    """
    Valida senha usando varios lookaheads encadeados:
    - pelo menos 1 letra minuscula
    - pelo menos 1 letra maiuscula
    - pelo menos 1 digito
    - tamanho minimo de 8
    """
    # cada (?=...) verifica uma condicao sem consumir caracteres, permitindo combinar
    # multiplos requisitos independentes no inicio da string.
    padrao = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
    return bool(padrao.match(senha))


def palavra_sem_sufixo_plural(texto: str) -> list[str]:
    """Encontra palavras que NAO sao seguidas por 's' (negative lookahead), ou seja, no singular."""
    # \b\w+\b(?!s\b) casa uma palavra que nao tem 's' colado no final dela
    padrao = re.compile(r"\b\w+(?!s)\b")
    return padrao.findall(texto)


if __name__ == "__main__":
    texto_precos = "O produto custa R$199,90 e o frete R$15,00 a mais."
    senhas_teste = ["abc12345", "Abc12345", "Abcdefgh", "Ab1!"]
    texto_plural = "gato gatos casa casas livro"

    print("Valores apos R$:", extrair_valor_apos_simbolo(texto_precos))

    for senha in senhas_teste:
        print(f"Senha {senha!r:12} valida: {senha_valida(senha)}")

    print("Palavras (heuristica singular):", palavra_sem_sufixo_plural(texto_plural))

    # sanity check
    assert extrair_valor_apos_simbolo(texto_precos) == ["199,90", "15,00"]
    assert senha_valida("Abc12345") is True
    assert senha_valida("abc12345") is False  # falta maiuscula
    print("\nOK: sanity checks passaram.")
