"""
BFS - Busca em Largura (Breadth-First Search)

O que este script demonstra: percorrer um grafo "em camadas", visitando
todos os vizinhos de distancia 1 antes dos de distancia 2, usando uma
fila (collections.deque) para garantir a ordem FIFO.
Complexidade: O(V+E) tempo, O(V) espaco
"""

from collections import deque, defaultdict


def construir_grafo_exemplo():
    """Grafo nao-direcionado simples para os exemplos deste arquivo."""
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


def bfs(adj, inicio):
    """Retorna a ordem de visitacao dos nos a partir de 'inicio'."""
    visitados = {inicio}
    fila = deque([inicio])  # deque.popleft() e O(1); list.pop(0) seria O(n)
    ordem = []

    while fila:
        atual = fila.popleft()
        ordem.append(atual)
        # percorre vizinhos em ordem para resultado deterministico
        for vizinho in adj[atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)  # marca ao enfileirar, nao ao desenfileirar,
                fila.append(vizinho)    # evita enfileirar o mesmo no duas vezes
    return ordem


if __name__ == "__main__":
    grafo = construir_grafo_exemplo()

    print("=== BFS a partir de A ===")
    resultado = bfs(grafo, "A")
    print(" -> ".join(resultado))

    print("\n=== BFS a partir de F ===")
    resultado_f = bfs(grafo, "F")
    print(" -> ".join(resultado_f))

    # Caso trivial: grafo com um unico no, sem arestas
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print(bfs(grafo_trivial, "X"))

    # Sanity checks
    assert resultado[0] == "A"
    assert set(resultado) == set(grafo.keys())  # visita todos os nos alcancaveis
    assert bfs(grafo_trivial, "X") == ["X"]
    print("\nOK: todos os asserts passaram.")
