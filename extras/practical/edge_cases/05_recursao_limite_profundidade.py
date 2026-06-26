"""
RecursionError e conversao de recursao para iterativo

Cenario: percorrer uma estrutura hierarquica profunda (ex: arvore de
categorias de produtos, comentarios aninhados, estrutura de pastas) de forma
recursiva. Em produção, dados reais podem ter profundidade maior do que o
esperado (ex: import de dados malformado criando uma cadeia muito longa) e
estourar o limite de recursao do Python (RecursionError), derrubando o
processo.
Demonstra: como o RecursionError ocorre, como capturar e degradar com
seguranca, e como reescrever a mesma logica de forma iterativa (usando uma
pilha explicita) para suportar profundidade arbitraria sem o limite da call
stack do interpretador.
"""

import sys


def construir_cadeia_aninhada(profundidade):
    """Simula uma estrutura de dados aninhada tipo {"filho": {"filho": {...}}}."""
    no = {"valor": profundidade, "filho": None}
    atual = no
    for nivel in range(profundidade - 1, 0, -1):
        atual["filho"] = {"valor": nivel, "filho": None}
        atual = atual["filho"]
    return no


def contar_profundidade_recursivo(no):
    """Versao recursiva simples - falha com RecursionError em estruturas profundas."""
    if no is None:
        return 0
    return 1 + contar_profundidade_recursivo(no["filho"])


def contar_profundidade_recursivo_seguro(no):
    """Tenta a versao recursiva, mas degrada com aviso em vez de derrubar o processo."""
    try:
        return contar_profundidade_recursivo(no)
    except RecursionError:
        # Nao deixamos o erro propagar para o chamador sem contexto: avisamos
        # que a estrutura excedeu o limite seguro de recursao do interpretador.
        return None


def contar_profundidade_iterativo(no):
    """Mesma logica, sem usar a call stack do Python - suporta profundidade
    arbitraria (limitada apenas pela memoria disponivel, nao pelo recursion limit)."""
    contagem = 0
    atual = no
    while atual is not None:
        contagem += 1
        atual = atual["filho"]
    return contagem


if __name__ == "__main__":
    limite_atual = sys.getrecursionlimit()
    print(f"Limite de recursao do interpretador: {limite_atual}")

    # Caso normal: profundidade pequena, a versao recursiva funciona bem
    estrutura_pequena = construir_cadeia_aninhada(50)
    print(f"\nEstrutura pequena (50 niveis):")
    print(f"  Recursivo : {contar_profundidade_recursivo(estrutura_pequena)}")
    print(f"  Iterativo : {contar_profundidade_iterativo(estrutura_pequena)}")

    # Caso problematico: profundidade maior que o limite de recursao,
    # simulando dado real malformado/inesperado
    profundidade_grande = limite_atual + 2000
    estrutura_grande = construir_cadeia_aninhada(profundidade_grande)

    print(f"\nEstrutura grande ({profundidade_grande} niveis):")
    resultado_recursivo = contar_profundidade_recursivo_seguro(estrutura_grande)
    if resultado_recursivo is None:
        print("  Recursivo : RecursionError capturado - estrutura excede o limite seguro de recursao")
    else:
        print(f"  Recursivo : {resultado_recursivo}")

    resultado_iterativo = contar_profundidade_iterativo(estrutura_grande)
    print(f"  Iterativo : {resultado_iterativo} (funciona normalmente, sem limite de call stack)")
