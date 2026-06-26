"""
Validação de Balanceamento de Parênteses/Chaves/Colchetes

Cenário: parsers de código, validadores de JSON/expressões matemáticas, ou
linters que precisam garantir que delimitadores estão corretamente abertos e
fechados antes de seguir com análises mais profundas.
O que este script demonstra: uso de uma pilha (stack) para validar
balanceamento e correspondência correta entre tipos de delimitadores.
"""

PARES = {")": "(", "]": "[", "}": "{"}
ABERTURAS = set(PARES.values())
FECHAMENTOS = set(PARES.keys())


def esta_balanceado(expressao: str) -> bool:
    pilha = []
    for char in expressao:
        if char in ABERTURAS:
            pilha.append(char)
        elif char in FECHAMENTOS:
            # Pilha vazia significa fechamento sem abertura correspondente.
            if not pilha:
                return False
            topo = pilha.pop()
            # O fechamento atual deve corresponder exatamente à última abertura aberta.
            if topo != PARES[char]:
                return False
        # outros caracteres (letras, números, operadores) são ignorados de propósito
    # Se sobrou algo na pilha, há aberturas sem fechamento.
    return len(pilha) == 0


if __name__ == "__main__":
    casos = [
        "(a + b) * [c - d]",
        "{[()]}",
        "([)]",
        "(a + b",
        "func(x, y) { return [x, y]; }",
    ]

    for expr in casos:
        print(f"{expr!r:35} -> balanceado? {esta_balanceado(expr)}")
