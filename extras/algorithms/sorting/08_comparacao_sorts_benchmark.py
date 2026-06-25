"""
Comparacao de algoritmos de ordenacao (benchmark)

O que este script demonstra: executa os 7 algoritmos de ordenacao
(bubble, insertion, selection, merge, quick, heap, counting sort) sobre
listas aleatorias de tamanhos crescentes e imprime uma tabela comparando
o tempo de execucao de cada um, usando time.perf_counter().
Complexidade: cada algoritmo mantem sua complexidade original (ver scripts
01 a 07); este script em si e O(1) espaco extra alem das copias das listas.

Nota: as 7 funcoes de ordenacao sao reimplementadas localmente (copiadas dos
scripts 01-07) em vez de importadas, pois os nomes dos arquivos comecam com
digitos e nao podem ser usados diretamente em 'import' (precisariam de
importlib.import_module, o que adicionaria complexidade desnecessaria aqui).
"""

import random
import time


# ---------------------------------------------------------------------------
# Implementacoes dos algoritmos (copiadas dos scripts 01 a 07)
# ---------------------------------------------------------------------------

def bubble_sort(items):
    items = list(items)
    n = len(items)
    for i in range(n):
        trocou = False
        for j in range(0, n - 1 - i):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                trocou = True
        if not trocou:
            break
    return items


def insertion_sort(items):
    items = list(items)
    for i in range(1, len(items)):
        chave = items[i]
        j = i - 1
        while j >= 0 and items[j] > chave:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = chave
    return items


def selection_sort(items):
    items = list(items)
    n = len(items)
    for i in range(n - 1):
        indice_menor = i
        for j in range(i + 1, n):
            if items[j] < items[indice_menor]:
                indice_menor = j
        if indice_menor != i:
            items[i], items[indice_menor] = items[indice_menor], items[i]
    return items


def merge_sort(items):
    if len(items) <= 1:
        return list(items)
    meio = len(items) // 2
    esquerda = merge_sort(items[:meio])
    direita = merge_sort(items[meio:])
    return _merge(esquerda, direita)


def _merge(esquerda, direita):
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


def quick_sort(items):
    items = list(items)
    _quick_sort(items, 0, len(items) - 1)
    return items


def _quick_sort(items, inicio, fim):
    if inicio >= fim:
        return
    indice_pivo = _particionar(items, inicio, fim)
    _quick_sort(items, inicio, indice_pivo - 1)
    _quick_sort(items, indice_pivo + 1, fim)


def _particionar(items, inicio, fim):
    meio = (inicio + fim) // 2
    items[meio], items[fim] = items[fim], items[meio]
    pivo = items[fim]
    fronteira = inicio
    for i in range(inicio, fim):
        if items[i] <= pivo:
            items[fronteira], items[i] = items[i], items[fronteira]
            fronteira += 1
    items[fronteira], items[fim] = items[fim], items[fronteira]
    return fronteira


def heap_sort(items):
    items = list(items)
    n = len(items)
    for i in range(n // 2 - 1, -1, -1):
        _afundar(items, n, i)
    for fim in range(n - 1, 0, -1):
        items[0], items[fim] = items[fim], items[0]
        _afundar(items, fim, 0)
    return items


def _afundar(items, tamanho_heap, raiz):
    maior = raiz
    esquerda = 2 * raiz + 1
    direita = 2 * raiz + 2
    if esquerda < tamanho_heap and items[esquerda] > items[maior]:
        maior = esquerda
    if direita < tamanho_heap and items[direita] > items[maior]:
        maior = direita
    if maior != raiz:
        items[raiz], items[maior] = items[maior], items[raiz]
        _afundar(items, tamanho_heap, maior)


def counting_sort(items):
    if not items:
        return []
    if any(x < 0 for x in items):
        raise ValueError("counting_sort so suporta inteiros nao-negativos")
    maior_valor = max(items)
    contagem = [0] * (maior_valor + 1)
    for valor in items:
        contagem[valor] += 1
    resultado = []
    for valor, qtd in enumerate(contagem):
        resultado.extend([valor] * qtd)
    return resultado


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

# bubble/insertion/selection sao O(n^2): pulamos tamanhos grandes para nao
# deixar o benchmark lento demais (sao marcados como None na tabela)
ALGORITMOS = {
    "bubble_sort": (bubble_sort, 5000),
    "insertion_sort": (insertion_sort, 5000),
    "selection_sort": (selection_sort, 5000),
    "merge_sort": (merge_sort, None),
    "quick_sort": (quick_sort, None),
    "heap_sort": (heap_sort, None),
    "counting_sort": (counting_sort, None),
}

TAMANHOS = [100, 1000, 5000]
LIMITE_VALOR_ALEATORIO = 100_000


def medir_tempo(func, dados):
    """Roda 'func' sobre uma copia de 'dados' e retorna o tempo em segundos."""
    copia = list(dados)
    inicio = time.perf_counter()
    func(copia)
    fim = time.perf_counter()
    return fim - inicio


def main():
    random.seed(42)  # reprodutibilidade entre execucoes

    print(f"{'Algoritmo':<16}", end="")
    for tamanho in TAMANHOS:
        print(f"n={tamanho:<10}", end="")
    print()
    print("-" * (16 + 12 * len(TAMANHOS)))

    for nome, (func, limite_n) in ALGORITMOS.items():
        print(f"{nome:<16}", end="")
        for tamanho in TAMANHOS:
            if limite_n is not None and tamanho > limite_n:
                print(f"{'pulado':<12}", end="")
                continue
            dados = [random.randint(0, LIMITE_VALOR_ALEATORIO) for _ in range(tamanho)]
            tempo_gasto = medir_tempo(func, dados)
            print(f"{tempo_gasto:<12.5f}", end="")
        print()


if __name__ == "__main__":
    main()

    # sanity check: todos os algoritmos devem produzir o mesmo resultado
    # que a ordenacao nativa, para uma lista pequena de exemplo
    exemplo = [5, 2, 9, 1, 5, 6, 0, 33, 12]
    esperado = sorted(exemplo)
    for nome, (func, _) in ALGORITMOS.items():
        assert func(exemplo) == esperado, f"{nome} produziu resultado incorreto"
    print("\nSanity check ok: todos os algoritmos concordam com sorted().")
