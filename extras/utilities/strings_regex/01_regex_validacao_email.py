"""
Validacao de formato de e-mail com regex

O que este script demonstra: como usar uma expressao regular pragmatica para
validar o formato sintatico de enderecos de e-mail, sem tentar cobrir 100% da RFC 5322.
Quando usar: validacao de entrada de formularios onde uma checagem "boa o suficiente" basta.
"""

import re

# Regex pragmatica: nao cobre toda a RFC 5322 (que e enorme e pouco pratica),
# mas cobre a grande maioria dos casos reais de uso.
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+"      # parte local: letras, numeros e alguns simbolos comuns
    r"@"                       # arroba obrigatoria
    r"[a-zA-Z0-9-]+"           # dominio (sem ponto na primeira parte)
    r"(\.[a-zA-Z0-9-]+)*"      # subdominios opcionais
    r"\.[a-zA-Z]{2,}$"         # TLD com pelo menos 2 letras
)


def validar_email(endereco: str) -> bool:
    """Retorna True se o endereco casa com o padrao basico de e-mail."""
    # strip() evita falso-negativo por espacos acidentais ao colar texto
    return bool(EMAIL_REGEX.match(endereco.strip()))


if __name__ == "__main__":
    candidatos = [
        "usuario@example.com",
        "nome.sobrenome@empresa.com.br",
        "invalido@",
        "@invalido.com",
        "sem-arroba.com",
        "com.numeros123@dominio99.io",
        "espaco no meio@dominio.com",
    ]

    for email in candidatos:
        resultado = "valido" if validar_email(email) else "invalido"
        print(f"{email!r:40} -> {resultado}")

    # sanity check
    assert validar_email("teste@dominio.com") is True
    assert validar_email("invalido") is False
    print("\nOK: sanity checks passaram.")
