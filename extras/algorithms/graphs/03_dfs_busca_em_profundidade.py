"""
DFS - Busca em Profundidade (Depth-First Search), versao recursiva

O que este script demonstra: percorrer um grafo indo o mais "fundo"
possivel em cada ramo antes de retroceder (backtrack), usando recursao
e a pilha de chamadas do Python como estrutura implicita.
Complexidade: O(V+E) tempo, O(V) espaco (pilha de recursao + visitados)
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


def dfs_recursiva(adj, atual, visitados=None, ordem=None):
    """DFS recursiva classica. Os parametros mutaveis sao inicializados
    apenas na primeira chamada (evita o pitfall de default mutavel)."""
    if visitados is None:
        visitados = set()
        ordem = []

    visitados.add(atual)
    ordem.append(atual)

    for vizinho in adj[atual]:
        if vizinho not in visitados:
            dfs_recursiva(adj, vizinho, visitados, ordem)

    return ordem


if __name__ == "__main__":
    grafo = construir_grafo_exemplo()

    print("=== DFS recursiva a partir de A ===")
    resultado = dfs_recursiva(grafo, "A")
    print(" -> ".join(resultado))

    print("\n=== DFS recursiva a partir de F ===")
    resultado_f = dfs_recursiva(grafo, "F")
    print(" -> ".join(resultado_f))

    # Caso trivial: no isolado
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print(dfs_recursiva(grafo_trivial, "X"))

    # Sanity checks
    assert resultado[0] == "A"
    assert set(resultado) == set(grafo.keys())
    assert dfs_recursiva(grafo_trivial, "X") == ["X"]
    print("\nOK: todos os asserts passaram.")
