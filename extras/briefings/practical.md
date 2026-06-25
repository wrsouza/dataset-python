# Briefing — Categoria: Practical Code

> Sessão independente. Não depende de nenhuma outra conversa. Leia este arquivo inteiro antes de começar.

## Contexto do Projeto

Repositório `dataset-python` é um dataset educacional. A pasta `extras/` contém scripts **simples e independentes** (1 arquivo cada), diferente das pastas `creational/structural/behavioral` (projetos completos de design patterns com Docker/tests/SOLID). Não copie aquele padrão aqui.

Leia `extras/PLAN_EXTRAS.md` para visão geral (padrão de script, convenções de nome, regras de dependências).

## Sua Tarefa

Criar **30 scripts Python** na pasta `extras/practical/`, divididos em 4 subpastas. Cada script é um arquivo único, executável, comentado. Pode usar stdlib + `requests` (mockado/comentado, sem chamada de rede real) quando fizer sentido para o cenário — evite dependências de rede real para manter o script executável offline.

### Template obrigatório por script

```python
"""
<Título curto>

Cenário: <onde isso apareceria num trabalho real>
O que este script demonstra: <1-2 frases>
"""

# código comentado nos pontos não-óbvios

if __name__ == "__main__":
    # exemplo de uso executável com dados/cenário simulado
    ...
```

### Lista de scripts

**`extras/practical/real_world_snippets/` (10 scripts)**
1. `01_dedupe_lista_mantendo_ordem.py` — remover duplicados de uma lista preservando ordem
2. `02_flatten_lista_aninhada.py` — achatar listas aninhadas de profundidade arbitrária
3. `03_chunking_lista_em_lotes.py` — dividir lista grande em lotes de tamanho N
4. `04_merge_dicts_profundo.py` — merge recursivo de dicionários aninhados
5. `05_contador_frequencia_palavras.py` — contar frequência de palavras em texto (`Counter`)
6. `06_paginacao_manual_lista.py` — implementar paginação sobre uma lista em memória
7. `07_cache_simples_lru.py` — cache com `functools.lru_cache` e cache manual com TTL
8. `08_rate_limiter_simples.py` — limitador de taxa de chamadas (token bucket simplificado)
9. `09_gerador_dados_fake_para_teste.py` — gerar dados fake (nomes, emails, datas) sem lib externa
10. `10_comparador_versoes_semver.py` — comparar versões no estilo semver (string → tupla)

**`extras/practical/problem_solving/` (8 scripts)**
1. `01_anagrama_verificacao.py` — verificar se duas strings são anagramas
2. `02_balanceamento_parenteses.py` — validar balanceamento de parênteses/chaves/colchetes
3. `03_palindromo_verificacao.py` — verificar palíndromo (string e número)
4. `04_maior_subarray_soma_maxima.py` — algoritmo de Kadane para soma máxima de subarray
5. `05_intervalo_merge_sobrepostos.py` — mesclar intervalos sobrepostos (ex: agenda)
6. `06_two_sum_pares_soma.py` — encontrar par de números que somam um valor alvo
7. `07_top_k_elementos_frequentes.py` — encontrar os K elementos mais frequentes
8. `08_matriz_rotacao_transposicao.py` — rotacionar/transpor matriz em-place

**`extras/practical/edge_cases/` (6 scripts)**
1. `01_divisao_por_zero_tratamento.py` — tratar divisão por zero em cálculos em lote
2. `02_unicode_emoji_em_strings.py` — lidar com emojis/caracteres multi-byte em processamento de texto
3. `03_lista_vazia_vs_none.py` — diferenciar e tratar corretamente lista vazia vs `None`
4. `04_overflow_precisao_float.py` — problemas de precisão de float e uso de `Decimal`
5. `05_recursao_limite_profundidade.py` — lidar com `RecursionError` e conversão para iterativo
6. `06_concorrencia_condicao_de_corrida_simples.py` — demonstrar race condition simples com threading e a correção com lock

**`extras/practical/performance/` (6 scripts)**
1. `01_comparacao_list_comprehension_vs_loop.py` — benchmark list comprehension vs loop explícito
2. `02_generator_vs_lista_memoria.py` — comparar uso de memória entre generator e lista materializada
3. `03_profiling_basico_cprofile.py` — uso de `cProfile`/`timeit` para medir hotspots
4. `04_memoization_vs_recalculo.py` — comparar custo com/sem memoization
5. `05_otimizacao_busca_set_vs_list.py` — comparar custo de `in` em `set` vs `list`
6. `06_lazy_evaluation_generators.py` — pipeline de processamento com generators encadeados (lazy)

## Regras de Qualidade
- Sem chamadas de rede reais. Se o cenário envolve API/serviço externo, simule com dados em memória e comente que numa aplicação real seria uma chamada de rede.
- Cada script roda standalone e imprime resultado de um caso de exemplo.
- Comentários explicam o porquê, não o óbvio.
- Pode usar subagentes internos (1 por subpasta) se preferir paralelizar dentro desta sessão.

## Ao Terminar
Atualize `extras/STATUS_EXTRAS.md`, marcando os 30 itens da seção "Practical Code" como `[x]`.
