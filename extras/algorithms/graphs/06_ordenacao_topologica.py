"""
Ordenacao topologica (algoritmo de Kahn)

O que este script demonstra: ordenar os nos de um DAG (grafo direcionado
acmclico) de forma que toda aresta u->v apareca com u antes de v na
ordem final. Usa o algoritmo de Kahn, baseado em graus de entrada (BFS).
Complexidade: O(V+E) tempo, O(V) espaco
"""

from collections import defaultdict, deque


def construir_dag_exemplo():
    """DAG representando dependencias de tarefas (ex: build de um projeto)."""
    adj = defaultdict(list)
    arestas = [
        ("vestir_meia", "vestir_sapato"),
        ("vestir_cueca", "vestir_calca"),
        ("vestir_calca", "vestir_sapato"),
        ("vestir_camisa", "vestir_casaco"),
        ("vestir_calca", "vestir_casaco"),
    ]
    for o, d in arestas:
        adj[o].append(d)
        adj[d]  # garante existencia no dict mesmo sem saidas
    return adj


def ordenacao_topologica_kahn(adj):
    """Algoritmo de Kahn: repetidamente remove nos com grau de entrada 0."""
    grau_entrada = {no: 0 for no in adj}
    for no in adj:
        for vizinho in adj[no]:
            grau_entrada[vizinho] += 1

    # fila inicial com todos os nos sem dependencias (grau de entrada 0)
    fila = deque(no for no, grau in grau_entrada.items() if grau == 0)
    ordem = []

    while fila:
        atual = fila.popleft()
        ordem.append(atual)
        for vizinho in adj[atual]:
            grau_entrada[vizinho] -= 1
            if grau_entrada[vizinho] == 0:
                fila.append(vizinho)

    if len(ordem) != len(adj):
        # se nem todos os nos foram processados, ha um ciclo (nao e DAG)
        raise ValueError("Grafo possui ciclo: ordenacao topologica nao existe")

    return ordem


if __name__ == "__main__":
    dag = construir_dag_exemplo()

    print("=== Ordenacao topologica (vestir roupas) ===")
    ordem = ordenacao_topologica_kahn(dag)
    print(" -> ".join(ordem))

    # Caso trivial: no isolado
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print(ordenacao_topologica_kahn(grafo_trivial))

    # Caso com ciclo deve falhar
    print("\n=== Caso com ciclo (deve lancar erro) ===")
    grafo_ciclico = defaultdict(list)
    grafo_ciclico["A"].append("B")
    grafo_ciclico["B"].append("A")
    try:
        ordenacao_topologica_kahn(grafo_ciclico)
    except ValueError as erro:
        print(f"Erro esperado: {erro}")

    # Sanity checks: toda aresta deve respeitar a ordem (origem antes do destino)
    posicao = {no: i for i, no in enumerate(ordem)}
    for origem, vizinhos in dag.items():
        for destino in vizinhos:
            assert posicao[origem] < posicao[destino]
    assert ordenacao_topologica_kahn(grafo_trivial) == ["X"]
    print("\nOK: todos os asserts passaram.")
