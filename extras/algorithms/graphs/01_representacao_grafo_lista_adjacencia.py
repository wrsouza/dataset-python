"""
Representacao de grafo com lista de adjacencia

O que este script demonstra: como representar grafos direcionados e
nao-direcionados usando um dict de listas (lista de adjacencia), a forma
mais comum e eficiente em memoria para grafos esparsos.
Complexidade: O(1) amortizado para adicionar aresta, O(V+E) espaco total
"""

from collections import defaultdict


class Grafo:
    """Grafo representado por lista de adjacencia (dict[no] -> list[vizinhos])."""

    def __init__(self, direcionado: bool = False):
        self.direcionado = direcionado
        # defaultdict evita checar "if no not in grafo" toda hora
        self.adj = defaultdict(list)

    def adicionar_no(self, no):
        # acessar a chave via defaultdict ja cria a lista vazia se nao existir
        _ = self.adj[no]

    def adicionar_aresta(self, origem, destino, peso=1):
        # guardamos tupla (vizinho, peso) para reaproveitar essa estrutura
        # em scripts futuros (ex: Dijkstra) sem mudar o formato
        self.adj[origem].append((destino, peso))
        if not self.direcionado:
            # grafo nao-direcionado: aresta "volta" tambem precisa existir
            self.adj[destino].append((origem, peso))
        else:
            # garante que o destino apareca no dict mesmo sem arestas saindo dele
            _ = self.adj[destino]

    def vizinhos(self, no):
        return self.adj[no]

    def nos(self):
        return list(self.adj.keys())

    def __str__(self):
        linhas = []
        tipo = "Direcionado" if self.direcionado else "Nao-direcionado"
        linhas.append(f"Grafo {tipo}:")
        for no in self.adj:
            vizinhos_str = ", ".join(f"{v}(peso={p})" for v, p in self.adj[no])
            linhas.append(f"  {no} -> [{vizinhos_str}]")
        return "\n".join(linhas)


if __name__ == "__main__":
    # Grafo nao-direcionado de exemplo (ex: rede de amizades)
    g_nao_direcionado = Grafo(direcionado=False)
    arestas = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("E", "F")]
    for o, d in arestas:
        g_nao_direcionado.adicionar_aresta(o, d)

    print("=== Grafo nao-direcionado ===")
    print(g_nao_direcionado)
    print()

    # Mesmo conjunto de arestas, mas direcionado (ex: dependencias, fluxo)
    g_direcionado = Grafo(direcionado=True)
    for o, d in arestas:
        g_direcionado.adicionar_aresta(o, d)

    print("=== Grafo direcionado ===")
    print(g_direcionado)
    print()

    # Caso trivial: grafo com um unico no isolado
    g_trivial = Grafo()
    g_trivial.adicionar_no("X")
    print("=== Caso trivial (no isolado) ===")
    print(g_trivial)

    # Sanity checks
    assert len(g_nao_direcionado.vizinhos("D")) == 3  # B, C, E
    assert len(g_direcionado.vizinhos("D")) == 1  # so E (direcionado)
    assert g_trivial.vizinhos("X") == []
    print("\nOK: todos os asserts passaram.")
