"""
Deteccao de ciclo em grafo direcionado (cores/estados)

O que este script demonstra: detectar ciclos em um grafo direcionado
usando DFS com tres estados por no (branco/cinza/preto), o equivalente
ao algoritmo classico de deteccao de ciclo via "coloracao" de DFS.
Complexidade: O(V+E) tempo, O(V) espaco

Nota sobre grafo nao-direcionado: la, basta verificar se durante a DFS
visitamos um vizinho ja visitado que NAO seja o pai direto do no atual
(toda aresta de volta nao-trivial indica ciclo). Nao precisamos do estado
"cinza" porque, em grafo nao-direcionado, nao existe "aresta de avanco para
ancestral em processamento" sem ser tambem uma aresta de retorno simples.
"""

from collections import defaultdict

BRANCO, CINZA, PRETO = 0, 1, 2
# BRANCO = nunca visitado
# CINZA  = em processamento (esta na pilha de recursao atual)
# PRETO  = totalmente processado (ele e todos os seus descendentes)


def construir_grafo_com_ciclo():
    adj = defaultdict(list)
    arestas = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E")]
    for o, d in arestas:
        adj[o].append(d)
        adj[d]  # garante que destino exista no dict
    return adj


def construir_grafo_sem_ciclo():
    adj = defaultdict(list)
    arestas = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("E", "F")]
    for o, d in arestas:
        adj[o].append(d)
        adj[d]
    return adj


def tem_ciclo_direcionado(adj):
    """Retorna True se existir pelo menos um ciclo no grafo direcionado."""
    estado = {no: BRANCO for no in adj}

    def visitar(no):
        estado[no] = CINZA  # entra na pilha de recursao
        for vizinho in adj[no]:
            if estado[vizinho] == CINZA:
                # vizinho esta "em processamento" -> aresta de retorno -> ciclo!
                return True
            if estado[vizinho] == BRANCO and visitar(vizinho):
                return True
        estado[no] = PRETO  # terminou de processar esse no e seus descendentes
        return False

    for no in adj:
        if estado[no] == BRANCO:
            if visitar(no):
                return True
    return False


if __name__ == "__main__":
    grafo_ciclico = construir_grafo_com_ciclo()
    grafo_acmclico = construir_grafo_sem_ciclo()

    print("=== Grafo com ciclo (B -> C -> D -> B) ===")
    print("Tem ciclo?", tem_ciclo_direcionado(grafo_ciclico))

    print("\n=== Grafo sem ciclo (DAG) ===")
    print("Tem ciclo?", tem_ciclo_direcionado(grafo_acmclico))

    # Caso trivial: no isolado, sem arestas
    grafo_trivial = defaultdict(list)
    grafo_trivial["X"]
    print("\n=== Caso trivial (no isolado) ===")
    print("Tem ciclo?", tem_ciclo_direcionado(grafo_trivial))

    # Caso trivial: auto-loop (no aponta para si mesmo) tambem e ciclo
    grafo_autoloop = defaultdict(list)
    grafo_autoloop["Y"].append("Y")
    print("\n=== Caso trivial (auto-loop) ===")
    print("Tem ciclo?", tem_ciclo_direcionado(grafo_autoloop))

    # Sanity checks
    assert tem_ciclo_direcionado(grafo_ciclico) is True
    assert tem_ciclo_direcionado(grafo_acmclico) is False
    assert tem_ciclo_direcionado(grafo_trivial) is False
    assert tem_ciclo_direcionado(grafo_autoloop) is True
    print("\nOK: todos os asserts passaram.")
