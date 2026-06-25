"""
Caminho mais curto em grafo nao ponderado (BFS + reconstrucao de caminho)

O que este script demonstra: como BFS, alem de dar a distancia minima
(em numero de arestas) em um grafo sem pesos, tambem permite reconstruir
o caminho exato guardando um dict de predecessores durante a busca.
Complexidade: O(V+E) tempo, O(V) espaco
"""

from collections import defaultdict, deque


def construir_grafo_exemplo():
    adj = defaultdict(list)
    arestas = [
        ("A", "B"), ("A", "C"),
        ("B", "D"), ("C", "D"),
        ("D", "E"), ("C", "F"), ("F", "E"),
    ]
    for o, d in arestas:
        adj[o].append(d)
        adj[d].append(o)
    return adj


def caminho_mais_curto_bfs(adj, origem, destino):
    """Retorna (caminho, distancia) usando BFS + dict de predecessores.
    Se nao houver caminho, retorna (None, -1)."""
    if origem == destino:
        return [origem], 0

    visitados = {origem}
    predecessor = {origem: None}
    fila = deque([origem])

    while fila:
        atual = fila.popleft()

        for vizinho in adj[atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                predecessor[vizinho] = atual  # guarda de onde viemos
                if vizinho == destino:
                    # achou o destino: reconstroi o caminho andando para tras
                    return _reconstruir(predecessor, origem, destino)
                fila.append(vizinho)

    return None, -1  # destino inalcancavel a partir da origem


def _reconstruir(predecessor, origem, destino):
    caminho = []
    no = destino
    while no is not None:
        caminho.append(no)
        no = predecessor[no]
    caminho.reverse()
    assert caminho[0] == origem
    return caminho, len(caminho) - 1  # distancia = numero de arestas


if __name__ == "__main__":
    grafo = construir_grafo_exemplo()

    print("=== Caminho mais curto de A para E ===")
    caminho, dist = caminho_mais_curto_bfs(grafo, "A", "E")
    print(f"Caminho: {' -> '.join(caminho)} (distancia = {dist} arestas)")

    print("\n=== Caminho mais curto de B para F ===")
    caminho2, dist2 = caminho_mais_curto_bfs(grafo, "B", "F")
    print(f"Caminho: {' -> '.join(caminho2)} (distancia = {dist2} arestas)")

    # Caso trivial: origem == destino
    print("\n=== Caso trivial (origem == destino) ===")
    caminho_trivial, dist_trivial = caminho_mais_curto_bfs(grafo, "A", "A")
    print(f"Caminho: {caminho_trivial} (distancia = {dist_trivial})")

    # Caso sem caminho possivel (no isolado)
    grafo_desconexo = defaultdict(list)
    grafo_desconexo["A"].append("B")
    grafo_desconexo["B"].append("A")
    grafo_desconexo["Z"]  # isolado
    print("\n=== Caso sem caminho (no isolado) ===")
    resultado_none = caminho_mais_curto_bfs(grafo_desconexo, "A", "Z")
    print(f"Resultado: {resultado_none}")

    # Sanity checks
    assert dist == len(caminho) - 1  # distancia deve ser consistente com o caminho
    assert dist <= 3  # BFS garante o menor numero possivel de arestas
    assert caminho_trivial == ["A"] and dist_trivial == 0
    assert resultado_none == (None, -1)
    assert caminho[0] == "A" and caminho[-1] == "E"
    print("\nOK: todos os asserts passaram.")
