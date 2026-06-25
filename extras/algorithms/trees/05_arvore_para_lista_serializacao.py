"""
Serializacao e Desserializacao de Arvore Binaria

O que este script demonstra: como converter uma arvore binaria qualquer
em uma lista/string (serializar) e reconstrui-la de volta (desserializar)
usando travessia pre-order com um marcador explicito para filhos
ausentes (None). Essa tecnica preserva a estrutura exata da arvore.
Complexidade: O(n) tempo para serializar e O(n) para desserializar,
O(n) espaco para a representacao serializada e O(h) de pilha de recursao.
"""

MARCADOR_NULO = "#"


class No:
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita


def serializar(raiz):
    """
    Pre-order: raiz, depois esquerda, depois direita. Cada filho ausente
    e marcado explicitamente com MARCADOR_NULO para que a desserializacao
    saiba exatamente onde parar de descer em cada ramo.
    Retorna uma string com valores separados por virgula.
    """
    partes = []

    def percorrer(no):
        if no is None:
            partes.append(MARCADOR_NULO)
            return
        partes.append(str(no.valor))
        percorrer(no.esquerda)
        percorrer(no.direita)

    percorrer(raiz)
    return ",".join(partes)


def desserializar(dados):
    """
    Consome a string token por token na mesma ordem (pre-order) em que
    foi produzida, reconstruindo a arvore recursivamente. Um iterador
    compartilhado garante que a posicao de leitura avance de forma
    consistente entre as chamadas recursivas.
    """
    valores = iter(dados.split(","))

    def construir():
        token = next(valores)
        if token == MARCADOR_NULO:
            return None
        no = No(int(token))
        no.esquerda = construir()
        no.direita = construir()
        return no

    return construir()


def em_ordem(no, resultado=None):
    if resultado is None:
        resultado = []
    if no is not None:
        em_ordem(no.esquerda, resultado)
        resultado.append(no.valor)
        em_ordem(no.direita, resultado)
    return resultado


if __name__ == "__main__":
    # Arvore original:
    #        1
    #       / \
    #      2   3
    #         / \
    #        4   5
    original = No(1, No(2), No(3, No(4), No(5)))

    serializada = serializar(original)
    print("Arvore serializada:", serializada)

    reconstruida = desserializar(serializada)
    print("Em-ordem da arvore original:    ", em_ordem(original))
    print("Em-ordem da arvore reconstruida:", em_ordem(reconstruida))

    print("\nCaso trivial: arvore vazia")
    serializada_vazia = serializar(None)
    print("  serializar(None) ->", serializada_vazia)
    print("  desserializar(...) ->", desserializar(serializada_vazia))

    print("\nCaso trivial: um unico no")
    unico = No(99)
    serializada_unico = serializar(unico)
    print("  serializado:", serializada_unico)
    reconstruido_unico = desserializar(serializada_unico)
    print("  valor reconstruido:", reconstruido_unico.valor)

    assert em_ordem(original) == em_ordem(reconstruida)
    assert serializar(original) == serializar(reconstruida)
    assert desserializar(serializar(None)) is None
    print("\nSanity checks OK.")
