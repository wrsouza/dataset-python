"""
Generator vs lista materializada: consumo de memoria

Cenario: ao processar arquivos grandes (logs, CSVs, respostas de API paginadas),
a escolha entre retornar uma lista completa em memoria ou um generator que produz
itens sob demanda pode ser a diferenca entre um script que funciona e um que
estoura a memoria disponivel.
O que este script demonstra: usar sys.getsizeof para comparar o tamanho em bytes
de uma lista materializada versus um objeto generator equivalente, evidenciando
que o generator ocupa memoria constante independente do "tamanho" da sequencia
que ele pode produzir.
"""

import sys

TAMANHO = 1_000_000  # quantidade "logica" de itens que a sequencia representaria


def gerar_lista(n):
    """Materializa todos os n itens em memoria de uma vez."""
    return [i * i for i in range(n)]


def gerar_generator(n):
    """Cria um generator: nao calcula nada até ser iterado."""
    return (i * i for i in range(n))


if __name__ == "__main__":
    lista = gerar_lista(TAMANHO)
    generator = gerar_generator(TAMANHO)

    tamanho_lista = sys.getsizeof(lista)
    tamanho_generator = sys.getsizeof(generator)

    print(f"Sequencia logica de {TAMANHO:,} itens (quadrados de 0 a {TAMANHO - 1})")
    print(f"Tamanho da lista materializada:  {tamanho_lista:,} bytes (~{tamanho_lista / 1024 / 1024:.2f} MB)")
    print(f"Tamanho do objeto generator:     {tamanho_generator:,} bytes")

    proporcao = tamanho_lista / tamanho_generator
    print(f"A lista ocupa aproximadamente {proporcao:,.0f}x mais memoria que o generator.")

    # importante: getsizeof no generator mede so o objeto generator em si
    # (estado da funcao + frame), nao os itens que ele ainda vai produzir.
    # O "custo" do generator e pago item a item, durante a iteracao, e descartado
    # depois -- por isso ele permanece com tamanho fixo mesmo se TAMANHO crescer.

    # prova de que o generator ainda produz os mesmos valores que a lista
    primeiros_da_lista = lista[:5]
    primeiros_do_generator = [next(gerar_generator(TAMANHO)) for _ in range(0)]  # placeholder, ver abaixo
    novo_generator = gerar_generator(TAMANHO)
    primeiros_do_generator = [next(novo_generator) for _ in range(5)]
    print(f"Primeiros 5 valores (lista):     {primeiros_da_lista}")
    print(f"Primeiros 5 valores (generator): {primeiros_do_generator}")
    assert primeiros_da_lista == primeiros_do_generator
    print("Valores equivalentes confirmados (sanity check).")
