"""
Chunking: dividir lista grande em lotes de tamanho N

Cenario: ao inserir milhares de registros num banco, enviar emails em
massa ou chamar uma API com limite de itens por requisicao, e necessario
processar os dados em lotes (batches) menores.
O que este script demonstra: gerador de chunks eficiente em memoria
(nao duplica a lista inteira) e seu uso tipico em um loop de processamento.
"""

from typing import Iterator, List, Sequence, TypeVar

T = TypeVar("T")


def em_lotes(itens: Sequence[T], tamanho: int) -> Iterator[List[T]]:
    """Gera fatias da sequencia original sem copiar tudo de uma vez.

    Usar um gerador (yield) em vez de retornar uma lista de listas evita
    manter duas copias completas dos dados na memoria simultaneamente --
    relevante quando 'itens' tem milhoes de elementos.
    """
    if tamanho <= 0:
        raise ValueError("tamanho do lote deve ser positivo")
    for inicio in range(0, len(itens), tamanho):
        yield list(itens[inicio: inicio + tamanho])


def processar_em_lotes(itens: Sequence[T], tamanho: int) -> None:
    """Simula o padrao real: enviar cada lote para uma 'API' externa.

    Em uma aplicacao real, a chamada abaixo seria algo como
    requests.post(url, json=lote) -- aqui apenas simulamos o efeito.
    """
    for numero, lote in enumerate(em_lotes(itens, tamanho), start=1):
        # Chamada de rede simulada: na vida real seria uma requisicao HTTP
        print(f"Lote {numero}: enviando {len(lote)} itens -> {lote}")


if __name__ == "__main__":
    ids_clientes = list(range(1, 23))  # 22 IDs para enviar a uma API fictícia
    print("Total de itens:", len(ids_clientes))
    processar_em_lotes(ids_clientes, tamanho=5)
