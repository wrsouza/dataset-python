# Briefing — Categoria: Exception Handling

> Sessão independente. Não depende de nenhuma outra conversa. Leia este arquivo inteiro antes de começar.

## Contexto do Projeto

Repositório `dataset-python` é um dataset educacional. A pasta `extras/` contém scripts **simples e independentes** (1 arquivo cada), diferente das pastas `creational/structural/behavioral` (projetos completos de design patterns com Docker/tests/SOLID). Não copie aquele padrão aqui.

Leia `extras/PLAN_EXTRAS.md` para visão geral (padrão de script, convenções de nome, regras de dependências).

## Sua Tarefa

Criar **30 scripts Python** na pasta `extras/exception_handling/`, divididos em 4 subpastas. Cada script é um arquivo único, executável, comentado, usando apenas **stdlib**.

### Template obrigatório por script

```python
"""
<Título curto>

O que este script demonstra: <1-2 frases>
Quando usar: <1 frase>
"""

# código comentado nos pontos não-óbvios

if __name__ == "__main__":
    # exemplo de uso executável que dispara o cenário de erro propositalmente
    ...
```

### Lista de scripts

**`extras/exception_handling/custom_exceptions/` (8 scripts)**
1. `01_exception_customizada_basica.py` — criar exceção própria herdando de `Exception`
2. `02_hierarquia_exceptions_dominio.py` — hierarquia de exceções para um domínio (ex: erros de pagamento)
3. `03_exception_com_contexto_extra.py` — exceção que carrega atributos extras (código, payload)
4. `04_exception_chaining_raise_from.py` — `raise ... from ...` para preservar causa original
5. `05_exception_groups_python311.py` — `ExceptionGroup`/`except*` (Python 3.11+)
6. `06_exception_para_api_erros.py` — exceções mapeadas para códigos de erro tipo HTTP (sem framework)
7. `07_exception_serializavel.py` — exceção customizada que pode ser convertida para dict/JSON
8. `08_exception_com_codigo_recuperacao.py` — exceção que sugere ação de recuperação (retry/abort)

**`extras/exception_handling/try_except_patterns/` (8 scripts)**
1. `01_try_except_multiplos_tipos.py` — capturar múltiplos tipos de exceção numa cláusula
2. `02_try_except_else_finally.py` — uso correto de `else`/`finally`
3. `03_context_manager_customizado.py` — `__enter__`/`__exit__` para garantir limpeza
4. `04_contextlib_contextmanager.py` — `@contextmanager` para simplificar context managers
5. `05_suppress_exceptions.py` — `contextlib.suppress` para ignorar exceções esperadas
6. `06_try_except_em_loop.py` — tratamento de erro item a item sem interromper o loop
7. `07_validacao_precondicoes_vs_exception.py` — quando validar antes vs deixar a exceção estourar
8. `08_exception_em_list_comprehension.py` — lidar com erros dentro de comprehensions (padrão alternativo)

**`extras/exception_handling/logging_patterns/` (8 scripts)**
1. `01_logging_basico_niveis.py` — configuração básica de `logging` e níveis
2. `02_logging_exception_traceback.py` — `logger.exception` vs `logger.error` com traceback
3. `03_logging_handlers_multiplos.py` — múltiplos handlers (console + arquivo)
4. `04_logging_formatacao_customizada.py` — `Formatter` customizado com contexto extra
5. `05_logging_rotacao_arquivos.py` — `RotatingFileHandler` para rotação de logs
6. `06_logging_structured_json.py` — logging estruturado em formato JSON
7. `07_logging_contexto_correlacao.py` — adicionar ID de correlação/contexto via `LoggerAdapter`
8. `08_logging_supressao_ruido_terceiros.py` — silenciar logs verbosos de bibliotecas terceiras

**`extras/exception_handling/error_recovery/` (6 scripts)**
1. `01_retry_com_backoff_exponencial.py` — retry manual com backoff exponencial
2. `02_circuit_breaker_simples.py` — implementação simples de circuit breaker
3. `03_fallback_valor_padrao.py` — padrão de fallback para valor default em caso de erro
4. `04_timeout_operacao_manual.py` — limitar tempo de execução de uma operação (signal/threading)
5. `05_recuperacao_estado_apos_falha.py` — salvar/restaurar estado parcial após falha
6. `06_validacao_resultado_parcial.py` — processar lote tolerando falhas item a item e reportando resumo

## Regras de Qualidade
- Apenas stdlib. Sem framework/banco/cloud.
- Cada script deve **disparar de fato** o cenário de erro/exceção no `__main__` e mostrar o tratamento funcionando.
- Comentários explicam o porquê, não o óbvio.
- Pode usar subagentes internos (1 por subpasta) se preferir paralelizar dentro desta sessão.

## Ao Terminar
Atualize `extras/STATUS_EXTRAS.md`, marcando os 30 itens da seção "Exception Handling" como `[x]`.
