"""
Busca fuzzy simples com difflib

O que este script demonstra: como usar difflib.SequenceMatcher e get_close_matches
para encontrar similaridade entre strings e sugerir correcoes/aproximacoes ("voce quis dizer...?").
Quando usar: autocomplete tolerante a erro de digitacao, deduplicacao aproximada de
registros, ou sugestao de correcao quando uma busca exata nao encontra resultado.
"""

import difflib


def calcular_similaridade(a: str, b: str) -> float:
    """Retorna um score de 0.0 a 1.0 indicando o quao parecidas duas strings sao."""
    # ratio() usa o algoritmo de Ratcliff/Obershelp (blocos comuns mais longos)
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def sugerir_correcao(palavra: str, vocabulario: list[str], n: int = 3, limite: float = 0.6) -> list[str]:
    """Sugere as 'n' palavras do vocabulario mais parecidas com a palavra digitada."""
    # get_close_matches usa o mesmo SequenceMatcher por baixo, mas ja devolve top-N ordenado
    return difflib.get_close_matches(palavra.lower(), vocabulario, n=n, cutoff=limite)


def encontrar_mais_proximo(consulta: str, candidatos: list[str]) -> tuple[str, float]:
    """Retorna o candidato com maior similaridade e o respectivo score."""
    melhor_candidato = max(candidatos, key=lambda c: calcular_similaridade(consulta, c))
    melhor_score = calcular_similaridade(consulta, melhor_candidato)
    return melhor_candidato, melhor_score


if __name__ == "__main__":
    vocabulario_frutas = ["abacaxi", "banana", "laranja", "maca", "melancia", "manga", "morango"]

    digitadas = ["bananaa", "melanci", "laranj", "uva"]

    print("Sugestoes de correcao (busca fuzzy):")
    for palavra in digitadas:
        sugestoes = sugerir_correcao(palavra, vocabulario_frutas)
        print(f"  {palavra!r:12} -> {sugestoes if sugestoes else 'nenhuma sugestao'}")

    print("\nSimilaridade par a par:")
    pares = [("python", "phyton"), ("javascript", "java"), ("teste", "teste")]
    for a, b in pares:
        score = calcular_similaridade(a, b)
        print(f"  {a!r:12} vs {b!r:12} -> {score:.2f}")

    candidato, score = encontrar_mais_proximo("bananaa", vocabulario_frutas)
    print(f"\nMais proximo de 'bananaa': {candidato!r} (score={score:.2f})")

    # sanity check
    assert "banana" in sugerir_correcao("bananaa", vocabulario_frutas)
    assert calcular_similaridade("teste", "teste") == 1.0
    assert candidato == "banana"
    print("\nOK: sanity checks passaram.")
