"""
Dijkstra - caminho minimo em grafo com pesos nao-negativos

O que este script demonstra: encontrar a menor distancia de um no de
origem para todos os outros nos, usando uma fila de prioridade (heap)
para sempre processar o no com menor distancia conhecida ate o momento.
Complexidade: O((V+E) log V) tempo, O(V+E) espaco
"""

import heapq
from collections import defaultdict

INFINITO = float("inf")


def construir_grafo_ponderado():
    """Grafo nao-direcionado com pesos (ex: distancias entre cidades)."""
    adj = defaultdict(list)
    arestas = [
        ("A", "B", 4), ("A", "C", 1),
        ("C", "B", 2), ("B", "D", 5),
        ("C", "D", 8), ("D", "E", 3),
        ("C", "E", 10), ("E", "F", 2),
    ]
    for o, d, peso in arestas:
        adj[o].append((d, peso))
        adj[d].append((o, peso))  # nao-direcionado: aresta nos dois sentidos
    return adj


def dijkstra(adj, origem):
    """Retorna dict {no: menor_distancia_a_partir_da_origem}."""
    distancias = {no: INFINITO for no in adj}
    distancias[origem] = 0
    # heap de tuplas (distancia, no): heapq ordena automaticamente pelo 1o item
    heap = [(0, origem)]
    visitados = set()

    while heap:
        dist_atual, atual = heapq.heappop(heap)

        if atual in visitados:
            # pode haver entradas obsoletas no heap (nao removemos ao atualizar,
            # so inserimos nova); ignoramos se ja fechamos esse no
            continue
        visitados.add(atual)

        for vizinho, peso in adj[atual]:
            nova_dist = dist_atual + peso
            if nova_dist < distancias[vizinho]:
                distancias[vizinho] = nova_dist
                heapq.heappush(heap, (nova_dist, vizinho))

    return distancias


def reconstruir_caminho(adj, origem, destino):
    """Versao auxiliar que tambem devolve o caminho, guardando predecessores."""
    distancias = {no: INFINITO for no in adj}
    distancias[origem] = 0
    predecessor = {origem: None}
    heap = [(0, origem)]
    visitados = set()

    while heap:
        dist_atual, atual = heapq.heappop(heap)
        if atual in visitados:
            continue
        visitados.add(atual)

        for vizinho, peso in adj[atual]:
            nova_dist = dist_atual + peso
            if nova_dist < distancias[vizinho]:
                distancias[vizinho] = nova_dist
                predecessor[vizinho] = atual
                heapq.heappush(heap, (nova_dist, vizinho))

    if distancias[destino] == INFINITO:
        return None, INFINITO

    caminho = []
    no = destino
    while no is not None:
        caminho.append(no)
        no = predecessor.get(no)
    caminho.reverse()
    return caminho, distancias[destino]


if __name__ == "__main__":
    grafo = construir_grafo_ponderado()

    print("=== Distancias minimas a partir de A ===")
    distancias = dijkstra(grafo, "A")
    for no, dist in sorted(distancias.items()):
        print(f"  A -> {no}: {dist}")

    print("\n=== Caminho minimo de A para F ===")
    caminho, dist_total = reconstruir_caminho(grafo, "A", "F")
    print(f"Caminho: {' -> '.join(caminho)} (distancia total = {dist_total})")

    # Caso trivial: grafo com um unico no
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print(dijkstra(grafo_trivial, "X"))

    # Sanity checks
    assert distancias["A"] == 0
    assert distancias["C"] == 1  # aresta direta A-C
    assert distancias["B"] == 3  # A->C->B = 1+2, melhor que A->B direto (4)
    assert dist_total == distancias["F"]
    assert dijkstra(grafo_trivial, "X") == {"X": 0}
    print("\nOK: todos os asserts passaram.")
