"""
DFS recursiva vs DFS iterativa (pilha explicita)

O que este script demonstra: duas implementacoes equivalentes de DFS -
uma usando recursao (pilha de chamadas implicita) e outra usando uma
pilha explicita (list), evidenciando o tradeoff de profundidade maxima
de recursao do Python (RecursionError em grafos muito "longos").
Complexidade: O(V+E) tempo, O(V) espaco em ambas as versoes
"""

from collections import defaultdict


def construir_grafo_exemplo():
    adj = defaultdict(list)
    arestas = [
        ("A", "B"), ("A", "C"),
        ("B", "D"), ("C", "D"),
        ("D", "E"), ("E", "F"), ("C", "F"),
    ]
    for o, d in arestas:
        adj[o].append(d)
        adj[d].append(o)
    return adj


def dfs_recursiva(adj, inicio):
    visitados = set()
    ordem = []

    def visitar(no):
        visitados.add(no)
        ordem.append(no)
        for vizinho in adj[no]:
            if vizinho not in visitados:
                visitar(vizinho)

    visitar(inicio)
    return ordem


def dfs_iterativa(adj, inicio):
    """Equivalente a recursiva, mas usando list como pilha (LIFO).
    Atencao: a ordem de visitacao pode diferir levemente da recursiva
    porque empilhamos os vizinhos e desempilhamos do final (LIFO),
    o que inverte a ordem de exploracao em comparacao ao 'for' direto."""
    visitados = set()
    ordem = []
    pilha = [inicio]

    while pilha:
        atual = pilha.pop()  # list.pop() sem indice = remove do topo, O(1)
        if atual in visitados:
            continue  # pode haver duplicatas na pilha; ignora se ja visitado
        visitados.add(atual)
        ordem.append(atual)

        # empilha em ordem reversa para tentar manter a ordem "natural"
        # de exploracao (vizinho mais a esquerda primeiro)
        for vizinho in reversed(adj[atual]):
            if vizinho not in visitados:
                pilha.append(vizinho)

    return ordem


if __name__ == "__main__":
    grafo = construir_grafo_exemplo()

    print("=== DFS recursiva a partir de A ===")
    ordem_rec = dfs_recursiva(grafo, "A")
    print(" -> ".join(ordem_rec))

    print("\n=== DFS iterativa a partir de A ===")
    ordem_iter = dfs_iterativa(grafo, "A")
    print(" -> ".join(ordem_iter))

    # Caso trivial
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print("recursiva:", dfs_recursiva(grafo_trivial, "X"))
    print("iterativa:", dfs_iterativa(grafo_trivial, "X"))

    # Demonstracao do limite de recursao: grafo "longo" (cadeia linear)
    grafo_cadeia = defaultdict(list)
    n = 500
    for i in range(n - 1):
        grafo_cadeia[i].append(i + 1)
        grafo_cadeia[i + 1].append(i)

    # A versao iterativa nao tem limite de profundidade de recursao do Python
    resultado_cadeia = dfs_iterativa(grafo_cadeia, 0)
    print(f"\nDFS iterativa em cadeia de {n} nos: visitou {len(resultado_cadeia)} nos sem RecursionError")

    # Sanity checks
    assert set(ordem_rec) == set(ordem_iter) == set(grafo.keys())
    assert ordem_rec[0] == ordem_iter[0] == "A"
    assert len(resultado_cadeia) == n
    print("\nOK: todos os asserts passaram.")
