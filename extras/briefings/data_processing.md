# Briefing — Categoria: Data Processing

> Sessão independente. Não depende de nenhuma outra conversa. Leia este arquivo inteiro antes de começar.

## Contexto do Projeto

Repositório `dataset-python` é um dataset educacional. A pasta `extras/` contém scripts **simples e independentes** (1 arquivo cada), diferente das pastas `creational/structural/behavioral` (que são projetos completos de design patterns com Docker/tests/SOLID). Não copie aquele padrão aqui.

Leia `extras/PLAN_EXTRAS.md` para visão geral (padrão de script, convenções de nome, regras de dependências).

## Sua Tarefa

Criar **50 scripts Python** na pasta `extras/data_processing/`, divididos em 3 subpastas. Cada script é um arquivo único, executável, comentado, sem dependências externas exceto `pandas`, `numpy`, `openpyxl` (quando necessário) e stdlib.

### Template obrigatório por script

```python
"""
<Título curto>

O que este script demonstra: <1-2 frases>
Quando usar: <1 frase>
"""

# código comentado nos pontos não-óbvios

if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos/gerados
    ...
```

### Lista de scripts

**`extras/data_processing/pandas/` (20 scripts)**
1. `01_read_write_csv_basico.py` — ler/escrever CSV com `read_csv`/`to_csv`, encoding e separador
2. `02_read_write_excel.py` — ler/escrever Excel multi-aba com `openpyxl`
3. `03_read_write_json.py` — `read_json`/`to_json`, orient e normalização
4. `04_groupby_agregacoes.py` — `groupby` com múltiplas agregações (`agg`)
5. `05_groupby_multiplas_colunas.py` — groupby por mais de uma coluna + `transform`
6. `06_merge_inner_outer.py` — merge com `inner`/`outer`/`left`/`right`
7. `07_merge_multiplas_chaves.py` — merge por múltiplas colunas-chave
8. `08_concat_dataframes.py` — `concat` por linha e por coluna
9. `09_pivot_table.py` — `pivot_table` com múltiplas métricas
10. `10_pivot_melt.py` — `melt` (wide→long) e o inverso
11. `11_filtragem_condicional.py` — filtros booleanos, `query()`, `isin()`
12. `12_tratamento_valores_nulos.py` — `fillna`, `dropna`, `interpolate`
13. `13_remocao_duplicatas.py` — `duplicated`/`drop_duplicates` com subset
14. `14_apply_map_lambda.py` — `apply`, `map`, `applymap` em colunas/linhas
15. `15_ordenacao_dataframe.py` — `sort_values` multi-coluna, `sort_index`
16. `16_indexacao_loc_iloc.py` — `loc`/`iloc`, slicing, `at`/`iat`
17. `17_tipos_dados_conversao.py` — `astype`, `to_datetime`, `to_numeric`
18. `18_window_functions_rolling.py` — `rolling`, `expanding`, médias móveis
19. `19_categorical_data.py` — tipo `category`, ordenação categórica
20. `20_multiindex_basico.py` — DataFrame com MultiIndex, `stack`/`unstack`

**`extras/data_processing/numpy/` (15 scripts)**
1. `01_criacao_arrays.py` — `array`, `zeros`, `ones`, `arange`, `linspace`
2. `02_indexacao_slicing.py` — slicing, indexação booleana, fancy indexing
3. `03_operacoes_elementwise.py` — operações vetorizadas vs loop Python
4. `04_broadcasting.py` — regras de broadcasting entre shapes diferentes
5. `05_reshape_flatten.py` — `reshape`, `ravel`, `flatten`, `transpose`
6. `06_agregacoes_axis.py` — `sum`/`mean`/`std` por eixo
7. `07_concatenacao_arrays.py` — `concatenate`, `stack`, `hstack`, `vstack`
8. `08_algebra_linear_basica.py` — produto matricial, `dot`, `linalg.inv`
9. `09_random_seeds.py` — `np.random.default_rng`, reprodutibilidade
10. `10_mascara_booleana.py` — máscaras booleanas para filtragem/edição
11. `11_where_select.py` — `np.where`, `np.select` para lógica condicional vetorizada
12. `12_funcoes_universais_ufunc.py` — ufuncs (`np.vectorize`, custom ufunc)
13. `13_ordenacao_arrays.py` — `sort`, `argsort`, `argmax`/`argmin`
14. `14_tratamento_nan.py` — `isnan`, `nan_to_num`, `nanmean`
15. `15_salvar_carregar_arrays.py` — `np.save`/`np.load`, `savetxt`/`loadtxt`

**`extras/data_processing/files_csv_json_excel/` (15 scripts)**
1. `01_csv_grandes_arquivos_chunks.py` — leitura em chunks com `csv` ou `pandas` (chunksize)
2. `02_csv_dialeto_customizado.py` — `csv.Sniffer`, delimitadores customizados
3. `03_json_nested_flatten.py` — achatar JSON aninhado para tabela
4. `04_json_streaming_parse.py` — parse incremental de JSON grande
5. `05_excel_multiplas_planilhas.py` — ler/escrever várias abas com `openpyxl`
6. `06_excel_formatacao_celulas.py` — formatação condicional/estilo com `openpyxl`
7. `07_csv_para_json.py` — conversão CSV → JSON e vice-versa
8. `08_validacao_schema_csv.py` — validar colunas/tipos esperados antes de processar
9. `09_deduplicacao_arquivos.py` — detectar/remover linhas duplicadas entre arquivos
10. `10_merge_multiplos_csvs.py` — combinar N arquivos CSV em um único dataset
11. `11_csv_compactado_gzip.py` — ler/escrever CSV compactado (`.csv.gz`)
12. `12_json_lines_jsonl.py` — leitura/escrita do formato JSON Lines
13. `13_csv_encoding_detection.py` — detectar/corrigir encoding (`chardet`-like via tentativa)
14. `14_excel_para_csv_batch.py` — converter várias planilhas Excel para CSV em lote
15. `15_relatorio_csv_para_excel_formatado.py` — gerar Excel formatado a partir de CSV

## Regras de Qualidade
- Sem framework, sem banco de dados, sem cloud. Apenas stdlib + pandas/numpy/openpyxl.
- Script roda standalone: `python <arquivo>.py` não deve dar erro.
- Comentários explicam o porquê, não o óbvio.
- Use dados de exemplo gerados em runtime (não dependa de arquivos externos pré-existentes) — se precisar de um CSV/Excel de entrada, gere-o no próprio script antes de processá-lo.
- Pode usar subagentes internos (1 por subpasta) se preferir paralelizar dentro desta sessão.

## Ao Terminar
Atualize `extras/STATUS_EXTRAS.md`, marcando os 50 itens da seção "Data Processing" como `[x]`.
