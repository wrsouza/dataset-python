"""
Verificacao de grafo bipartido (coloracao via BFS)

O que este script demonstra: testar se um grafo pode ser dividido em
dois conjuntos de nos tal que toda aresta liga nos de conjuntos
diferentes. Usa BFS atribuindo cores alternadas (0/1) aos vizinhos.
Complexidade: O(V+E) tempo, O(V) espaco
"""

from collections import defaultdict, deque


def construir_grafo_bipartido():
    """Grafo bipartido classico (ex: like um grafo bipartido pessoas/tarefas)."""
    adj = defaultdict(list)
    arestas = [("A", "1"), ("A", "2"), ("B", "2"), ("B", "3"), ("C", "1"), ("C", "3")]
    for o, d in arestas:
        adj[o].append(d)
        adj[d].append(o)
    return adj


def construir_grafo_nao_bipartido():
    """Triangulo (ciclo de tamanho impar) nunca e bipartido."""
    adj = defaultdict(list)
    arestas = [("A", "B"), ("B", "C"), ("C", "A")]
    for o, d in arestas:
        adj[o].append(d)
        adj[d].append(o)
    return adj


def eh_bipartido(adj):
    """Tenta colorir o grafo com 2 cores via BFS. Se algum vizinho tiver
    a mesma cor do no atual, o grafo nao e bipartido."""
    cor = {}

    for inicio in adj:
        if inicio in cor:
            continue  # ja processado em uma BFS anterior (outro componente)

        cor[inicio] = 0  # cor arbitraria para iniciar este componente
        fila = deque([inicio])

        while fila:
            atual = fila.popleft()
            for vizinho in adj[atual]:
                if vizinho not in cor:
                    cor[vizinho] = 1 - cor[atual]  # alterna a cor (0<->1)
                    fila.append(vizinho)
                elif cor[vizinho] == cor[atual]:
                    # vizinho com mesma cor do no atual = conflito = nao bipartido
                    return False, cor

    return True, cor


if __name__ == "__main__":
    grafo_bip = construir_grafo_bipartido()
    grafo_nao_bip = construir_grafo_nao_bipartido()

    print("=== Grafo bipartido ===")
    resultado, cores = eh_bipartido(grafo_bip)
    print("E bipartido?", resultado)
    print("Cores:", cores)

    print("\n=== Grafo com triangulo (nao bipartido) ===")
    resultado2, cores2 = eh_bipartido(grafo_nao_bip)
    print("E bipartido?", resultado2)

    # Caso trivial: no isolado (sempre bipartido)
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    resultado3, _ = eh_bipartido(grafo_trivial)
    print("E bipartido?", resultado3)

    # Sanity checks
    assert resultado is True
    assert resultado2 is False
    assert resultado3 is True
    # toda aresta deve ligar cores diferentes no grafo bipartido
    for origem, vizinhos in grafo_bip.items():
        for destino in vizinhos:
            assert cores[origem] != cores[destino]
    print("\nOK: todos os asserts passaram.")
