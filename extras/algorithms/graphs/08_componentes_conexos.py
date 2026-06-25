"""
Componentes conexos em grafo nao-direcionado

O que este script demonstra: identificar grupos de nos onde existe
caminho entre qualquer par dentro do grupo, mas nenhum caminho para nos
de outros grupos. Usa BFS a partir de cada no ainda nao visitado.
Complexidade: O(V+E) tempo, O(V) espaco
"""

from collections import defaultdict, deque


def construir_grafo_com_componentes_separados():
    """Grafo com 3 componentes conexos distintos."""
    adj = defaultdict(list)
    arestas = [
        # componente 1
        ("A", "B"), ("B", "C"), ("A", "C"),
        # componente 2
        ("D", "E"),
        # componente 3 (resto isolado)
        # F fica sozinho
    ]
    for o, d in arestas:
        adj[o].append(d)
        adj[d].append(o)
    adj["F"]  # no isolado, terceiro componente
    return adj


def bfs_marcar_componente(adj, inicio, visitados):
    """BFS que marca todos os nos alcancaveis a partir de 'inicio'."""
    componente = []
    fila = deque([inicio])
    visitados.add(inicio)

    while fila:
        atual = fila.popleft()
        componente.append(atual)
        for vizinho in adj[atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

    return componente


def encontrar_componentes_conexos(adj):
    """Retorna lista de listas, cada uma um componente conexo."""
    visitados = set()
    componentes = []

    for no in adj:
        if no not in visitados:
            # toda vez que achamos um no "fresco", e a raiz de um novo componente
            componente = bfs_marcar_componente(adj, no, visitados)
            componentes.append(componente)

    return componentes


if __name__ == "__main__":
    grafo = construir_grafo_com_componentes_separados()

    print("=== Componentes conexos ===")
    componentes = encontrar_componentes_conexos(grafo)
    for i, comp in enumerate(componentes, start=1):
        print(f"  Componente {i}: {sorted(comp)}")

    # Caso trivial: grafo totalmente conexo (1 unico componente)
    grafo_unico = defaultdict(list)
    arestas_unicas = [("X", "Y"), ("Y", "Z")]
    for o, d in arestas_unicas:
        grafo_unico[o].append(d)
        grafo_unico[d].append(o)

    print("\n=== Caso trivial (tudo conectado) ===")
    componentes_unico = encontrar_componentes_conexos(grafo_unico)
    print(f"  Numero de componentes: {len(componentes_unico)}")

    # Sanity checks
    assert len(componentes) == 3
    tamanhos = sorted(len(c) for c in componentes)
    assert tamanhos == [1, 2, 3]  # F isolado, D-E, A-B-C
    assert len(componentes_unico) == 1
    print("\nOK: todos os asserts passaram.")
