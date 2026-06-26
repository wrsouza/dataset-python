"""
Verificação de Palíndromo (string e número)

Cenário: validação de entradas em sistemas que aceitam códigos/identificadores
simétricos (ex: alguns formatos de número de série), ou em testes/quizzes de
lógica de programação que pedem verificação de strings e números palíndromos.
O que este script demonstra: checagem de palíndromo para strings (ignorando
pontuação/caixa) e para números, sem converter o número para string quando
queremos uma versão puramente matemática.
"""


def eh_palindromo_string(texto: str) -> bool:
    # Mantém apenas caracteres alfanuméricos e normaliza a caixa antes de comparar,
    # para frases como "Socorram-me, subi no ônibus em Marrocos" funcionarem.
    limpo = [c.lower() for c in texto if c.isalnum()]
    return limpo == limpo[::-1]


def eh_palindromo_numero(n: int) -> bool:
    """Verifica palíndromo sem converter para string, usando reversão matemática."""
    if n < 0:
        return False  # números negativos não são considerados palíndromos por convenção
    original = n
    reverso = 0
    while n > 0:
        digito = n % 10
        reverso = reverso * 10 + digito
        n //= 10
    return original == reverso


if __name__ == "__main__":
    frases = [
        "arara",
        "Socorram-me, subi no onibus em Marrocos",
        "Python",
        "A man, a plan, a canal: Panama",
    ]
    for frase in frases:
        print(f"{frase!r:45} -> palíndromo? {eh_palindromo_string(frase)}")

    print()
    numeros = [121, 12321, 123, -121, 0]
    for num in numeros:
        print(f"{num:>8} -> palíndromo? {eh_palindromo_numero(num)}")
