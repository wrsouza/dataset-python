"""
Contador de frequencia de palavras em texto

Cenario: analisar logs de busca, feedbacks de clientes ou textos livres
para descobrir termos mais citados (ex.: nuvem de palavras, deteccao de
reclamacoes recorrentes em um suporte).
O que este script demonstra: normalizacao simples de texto e contagem
de frequencia usando collections.Counter, incluindo remocao de stopwords.
"""

import re
from collections import Counter
from typing import List

STOPWORDS_PT = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para",
    "com", "nao", "uma", "os", "no", "se", "na", "por", "mais", "as",
}


def tokenizar(texto: str) -> List[str]:
    """Quebra o texto em palavras minusculas, ignorando pontuacao.

    O regex \\b\\w+\\b captura sequencias alfanumericas, descartando
    pontuacao e espacos sem precisar de um tokenizer mais pesado (NLTK etc.).
    """
    return re.findall(r"\b\w+\b", texto.lower())


def contar_frequencia(texto: str, remover_stopwords: bool = True, top_n: int = 5):
    palavras = tokenizar(texto)
    if remover_stopwords:
        palavras = [p for p in palavras if p not in STOPWORDS_PT]
    contagem = Counter(palavras)
    return contagem.most_common(top_n)


if __name__ == "__main__":
    feedback_clientes = """
    O atendimento foi rapido e o produto chegou no prazo.
    O produto e bom, mas a embalagem do produto chegou danificada.
    O atendimento poderia ser mais rapido em casos de troca do produto.
    """

    print("Texto analisado:")
    print(feedback_clientes.strip())
    print()
    top_palavras = contar_frequencia(feedback_clientes, top_n=3)
    print("Top 3 palavras mais citadas (sem stopwords):")
    for palavra, qtd in top_palavras:
        print(f"  {palavra!r}: {qtd}x")
