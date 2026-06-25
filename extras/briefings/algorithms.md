# Briefing — Categoria: Algoritmos Básicos

> Sessão independente. Não depende de nenhuma outra conversa. Leia este arquivo inteiro antes de começar.

## Contexto do Projeto

Repositório `dataset-python` é um dataset educacional. A pasta `extras/` contém scripts **simples e independentes** (1 arquivo cada), diferente das pastas `creational/structural/behavioral` (projetos completos de design patterns com Docker/tests/SOLID). Não copie aquele padrão aqui.

Leia `extras/PLAN_EXTRAS.md` para visão geral (padrão de script, convenções de nome, regras de dependências).

## Sua Tarefa

Criar **40 scripts Python** na pasta `extras/algorithms/`, divididos em 5 subpastas. Cada script é um arquivo único, executável, comentado, usando apenas **stdlib**. Foco em clareza didática + complexidade (Big-O) comentada.

### Template obrigatório por script

```python
"""
<Título curto>

O que este script demonstra: <1-2 frases>
Complexidade: O(...) tempo, O(...) espaço
"""

# código comentado nos pontos não-óbvios

if __name__ == "__main__":
    # exemplo de uso executável + comparação com caso trivial, se fizer sentido
    ...
```

### Lista de scripts

**`extras/algorithms/sorting/` (8 scripts)**
1. `01_bubble_sort.py`
2. `02_insertion_sort.py`
3. `03_selection_sort.py`
4. `04_merge_sort.py`
5. `05_quick_sort.py`
6. `06_heap_sort.py`
7. `07_counting_sort.py`
8. `08_comparacao_sorts_benchmark.py` — benchmark comparando os 7 anteriores em tamanhos crescentes

**`extras/algorithms/searching/` (8 scripts)**
1. `01_busca_linear.py`
2. `02_busca_binaria.py`
3. `03_busca_binaria_recursiva.py`
4. `04_busca_em_matriz_ordenada.py`
5. `05_busca_primeiro_ultimo_elemento.py` — encontrar primeira/última ocorrência (variação de binária)
6. `06_busca_interpolada.py`
7. `07_busca_em_lista_rotacionada.py`
8. `08_comparacao_busca_linear_vs_binaria.py` — benchmark comparativo

**`extras/algorithms/graphs/` (10 scripts)**
1. `01_representacao_grafo_lista_adjacencia.py`
2. `02_bfs_busca_em_largura.py`
3. `03_dfs_busca_em_profundidade.py`
4. `04_dfs_recursiva_vs_iterativa.py`
5. `05_deteccao_ciclo_grafo.py`
6. `06_ordenacao_topologica.py`
7. `07_dijkstra_caminho_minimo.py`
8. `08_componentes_conexos.py`
9. `09_grafo_bipartido_check.py`
10. `10_caminho_mais_curto_bfs_grafo_nao_ponderado.py`

**`extras/algorithms/dynamic_programming/` (8 scripts)**
1. `01_fibonacci_memoization.py`
2. `02_problema_mochila_knapsack.py`
3. `03_subsequencia_comum_maxima_lcs.py`
4. `04_distancia_edicao_levenshtein.py`
5. `05_soma_subconjunto.py`
6. `06_caminho_minimo_grade_matriz.py`
7. `07_quebra_moedas_coin_change.py`
8. `08_subsequencia_crescente_maxima.py`

**`extras/algorithms/trees/` (6 scripts)**
1. `01_arvore_binaria_busca_bst.py`
2. `02_travessia_in_pre_pos_ordem.py`
3. `03_arvore_balanceada_altura.py`
4. `04_lowest_common_ancestor.py`
5. `05_arvore_para_lista_serializacao.py`
6. `06_trie_prefixo_busca.py`

## Regras de Qualidade
- Apenas stdlib. Implementações didáticas (não use libs prontas tipo `heapq` para "reinventar" o algoritmo central, exceto onde fizer sentido como ferramenta auxiliar, ex.: Dijkstra pode usar `heapq` para a fila de prioridade).
- Cada script roda standalone e imprime o resultado de um caso de exemplo.
- Comente a complexidade (Big-O) no topo do arquivo.
- Pode usar subagentes internos (1 por subpasta) se preferir paralelizar dentro desta sessão.

## Ao Terminar
Atualize `extras/STATUS_EXTRAS.md`, marcando os 40 itens da seção "Algoritmos" como `[x]`.
