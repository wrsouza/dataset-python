# Briefing — Categoria: Utilities & Helpers

> Sessão independente. Não depende de nenhuma outra conversa. Leia este arquivo inteiro antes de começar.

## Contexto do Projeto

Repositório `dataset-python` é um dataset educacional. A pasta `extras/` contém scripts **simples e independentes** (1 arquivo cada), diferente das pastas `creational/structural/behavioral` (projetos completos de design patterns com Docker/tests/SOLID). Não copie aquele padrão aqui.

Leia `extras/PLAN_EXTRAS.md` para visão geral (padrão de script, convenções de nome, regras de dependências).

## Sua Tarefa

Criar **50 scripts Python** na pasta `extras/utilities/`, divididos em 5 subpastas. Cada script é um arquivo único, executável, comentado, usando apenas **stdlib** (sem pandas/numpy/frameworks).

### Template obrigatório por script

```python
"""
<Título curto>

O que este script demonstra: <1-2 frases>
Quando usar: <1 frase>
"""

# código comentado nos pontos não-óbvios

if __name__ == "__main__":
    # exemplo de uso executável com dados embutidos
    ...
```

### Lista de scripts

**`extras/utilities/strings_regex/` (15 scripts)**
1. `01_regex_validacao_email.py` — validar formato de e-mail com regex
2. `02_regex_extracao_numeros.py` — extrair números/telefones de texto livre
3. `03_regex_substituicao_grupos.py` — `re.sub` com grupos de captura
4. `04_parsing_log_lines.py` — parsear linhas de log com regex nomeado
5. `05_string_formatacao_avancada.py` — f-strings, `format`, alinhamento/padding
6. `06_string_slugify.py` — gerar slugs (remover acentos, espaços, etc.)
7. `07_string_template_simples.py` — `string.Template` para templates de texto
8. `08_regex_split_avancado.py` — split com múltiplos delimitadores
9. `09_string_normalizacao_unicode.py` — `unicodedata.normalize` para acentos
10. `10_csv_like_parsing_manual.py` — parser manual de linha delimitada (sem lib csv)
11. `11_regex_lookahead_lookbehind.py` — uso de lookahead/lookbehind
12. `12_string_wrap_textwrap.py` — `textwrap` para quebra de linha/parágrafos
13. `13_string_case_conversions.py` — snake_case ↔ camelCase ↔ PascalCase
14. `14_regex_validacao_cpf_cnpj.py` — validação de CPF/CNPJ (formato + dígito verificador)
15. `15_string_busca_fuzzy_simples.py` — comparação de similaridade com `difflib`

**`extras/utilities/file_io/` (10 scripts)**
1. `01_leitura_escrita_arquivo_texto.py` — `open`, context manager, modos de abertura
2. `02_manipulacao_paths_pathlib.py` — `pathlib.Path` para navegação/joins
3. `03_busca_recursiva_arquivos.py` — `glob`/`rglob` para buscar arquivos por padrão
4. `04_copia_movimentacao_arquivos.py` — `shutil.copy`/`move` com tratamento de erro
5. `05_compactacao_zip.py` — criar/extrair arquivos `.zip`
6. `06_leitura_arquivo_grande_streaming.py` — ler arquivo grande linha a linha sem carregar tudo
7. `07_watcher_diretorio_simples.py` — detectar mudanças num diretório (polling simples)
8. `08_arquivos_temporarios.py` — `tempfile` para arquivos/diretórios temporários
9. `09_leitura_escrita_binaria.py` — manipulação de arquivos binários (bytes)
10. `10_organizador_arquivos_por_extensao.py` — script que organiza arquivos em pastas por tipo

**`extras/utilities/datetime/` (10 scripts)**
1. `01_parsing_formatacao_datas.py` — `strptime`/`strftime` em formatos variados
2. `02_calculo_diferenca_datas.py` — `timedelta`, diferença entre datas
3. `03_timezone_conversao.py` — conversão entre timezones com `zoneinfo`
4. `04_calendario_dias_uteis.py` — calcular dias úteis entre duas datas
5. `05_datetime_para_timestamp.py` — conversão epoch ↔ datetime
6. `06_recorrencia_datas.py` — gerar datas recorrentes (semanal/mensal)
7. `07_idade_calculo.py` — calcular idade exata a partir de data de nascimento
8. `08_formatacao_relativa.py` — "há 2 dias", "em 3 horas" (tempo relativo)
9. `09_validacao_intervalo_datas.py` — validar se data está dentro de um intervalo
10. `10_feriados_simples.py` — checagem de feriados fixos (lista estática + lógica)

**`extras/utilities/validation/` (10 scripts)**
1. `01_validacao_formulario_simples.py` — validar dict de formulário (campos obrigatórios/tipos)
2. `02_validacao_tipos_dataclass.py` — validação de tipos usando `dataclasses` + checagem manual
3. `03_validacao_schema_json.py` — validar estrutura de JSON contra schema simples (dict)
4. `04_validacao_faixa_numerica.py` — validar números dentro de faixas/limites
5. `05_validacao_senha_forte.py` — checklist de força de senha (regras combinadas)
6. `06_validacao_url.py` — validar formato de URL com `urllib.parse`
7. `07_sanitizacao_input_usuario.py` — sanitizar strings de input (remover/escapar caracteres)
8. `08_validacao_arquivo_tipo_mime.py` — checar extensão/assinatura de arquivo (magic bytes simples)
9. `09_validacao_dados_duplicados.py` — detectar registros duplicados num dataset em memória
10. `10_validador_customizado_decorator.py` — decorator que valida argumentos de função

**`extras/utilities/encoding_decoding/` (5 scripts)**
1. `01_base64_encode_decode.py` — encode/decode Base64
2. `02_url_encoding.py` — `urllib.parse.quote`/`unquote`
3. `03_hash_md5_sha256.py` — gerar hashes com `hashlib`
4. `04_serializacao_pickle_vs_json.py` — comparar `pickle` e `json` (quando usar cada)
5. `05_encoding_caracteres_especiais.py` — lidar com encoding/decoding utf-8/latin-1

## Regras de Qualidade
- Apenas stdlib. Sem pandas/numpy/frameworks/banco de dados.
- Script roda standalone: `python <arquivo>.py` não deve dar erro.
- Comentários explicam o porquê, não o óbvio.
- Dados de exemplo embutidos/gerados no próprio script.
- Pode usar subagentes internos (1 por subpasta) se preferir paralelizar dentro desta sessão.

## Ao Terminar
Atualize `extras/STATUS_EXTRAS.md`, marcando os 50 itens da seção "Utilities & Helpers" como `[x]`.
