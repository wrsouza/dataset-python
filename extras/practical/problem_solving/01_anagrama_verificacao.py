"""
Verificação de Anagramas

Cenário: validação de jogos de palavras, deduplicação de strings equivalentes
(ex: "roma" e "amor"), ou checagem de integridade em sistemas que comparam
nomes/tokens ignorando ordem dos caracteres.
O que este script demonstra: duas formas de checar se duas strings são
anagramas - por contagem de caracteres (Counter) e por ordenação - e discute
o trade-off de complexidade entre elas.
"""

from collections import Counter


def sao_anagramas_ordenacao(a: str, b: str) -> bool:
    """O(n log n): normaliza removendo espaços/caixa e compara as strings ordenadas."""
    norm_a = a.replace(" ", "").lower()
    norm_b = b.replace(" ", "").lower()
    # Anagramas têm a mesma "assinatura" quando ordenados character a character.
    return sorted(norm_a) == sorted(norm_b)


def sao_anagramas_contagem(a: str, b: str) -> bool:
    """O(n): usa multiset de caracteres (Counter) em vez de ordenar - mais rápido para strings longas."""
    norm_a = a.replace(" ", "").lower()
    norm_b = b.replace(" ", "").lower()
    # Counter compara igualdade de frequências, equivalente a comparar multisets.
    return Counter(norm_a) == Counter(norm_b)


if __name__ == "__main__":
    casos = [
        ("roma", "amor"),
        ("listen", "silten"),
        ("dataset", "python"),
        ("Dormitory", "Dirty Room"),
    ]

    for x, y in casos:
        r1 = sao_anagramas_ordenacao(x, y)
        r2 = sao_anagramas_contagem(x, y)
        assert r1 == r2, "As duas implementações divergiram - bug!"
        print(f"'{x}' vs '{y}': anagrama? {r1}")
