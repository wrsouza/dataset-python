# Structured Logger (Singleton)

> **Design Pattern:** Singleton | **Categoria:** Creational
> **Framework:** CLI Typer | **Serviços:** Nenhum (sem dependências externas)

## Objetivo Pedagógico

Demonstrar o pattern Singleton em um logger estruturado que produz registros
JSON. O aluno deve aprender a garantir uma única instância compartilhada por
todo o processo, mesmo sob concorrência de múltiplas threads, usando uma
metaclasse com lock — a forma idiomática e thread-safe de implementar
Singleton em Python.

## O Pattern Aplicado

`StructuredLogger` é a classe cujo ciclo de vida é controlado pelo Singleton.
Toda chamada `StructuredLogger(...)` passa primeiro pela metaclasse
`SingletonMeta`, que verifica (com lock de double-checked locking) se já
existe uma instância para aquela classe. Se existir, retorna a mesma
instância — ignorando até os argumentos passados em chamadas subsequentes.
Isso garante que:

- Handlers registrados, contexto global e contadores (`LoggerStats`) sejam
  compartilhados por toda a aplicação (CLI, use cases, etc.).
- Múltiplas threads chamando `StructuredLogger()` simultaneamente nunca
  criam instâncias duplicadas.

## Diagrama UML (ASCII)

```
        <<metaclass>>
        SingletonMeta
   ---------------------------
   - _instances: dict
   - _lock: Lock
   ---------------------------
   + __call__(cls, ...): Any
            |
            | controla instanciação de
            v
       StructuredLogger  (metaclass=SingletonMeta)
   ---------------------------
   - _min_level: LogLevel
   - _handlers: list[LogHandlerProtocol]
   - _global_context: dict
   - _stats: LoggerStats
   ---------------------------
   + log(level, message, **ctx): LogRecord
   + set_context(**ctx): None
   + add_handler(handler): None
            |
            | implementa
            v
       AbstractLogger (ABC)
   ---------------------------
   + log(level, message, **ctx)
   + set_context(**ctx)
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** `StructuredLogger` só constrói e despacha
  `LogRecord`s; serialização para JSON fica em `StdoutJsonHandler`
  (`src/logger/handlers/stdout_handler.py`); orquestração de alto nível fica
  nos use cases (`src/logger/application/use_cases.py`).
- **D (Dependency Inversion):** `EmitLogMessageUseCase` e
  `SetLoggerContextUseCase` dependem da abstração `AbstractLogger`
  (`src/logger/domain/interfaces.py`), não da classe concreta
  `StructuredLogger` — testáveis com um fake logger sem nenhuma instância
  real (ver `tests/unit/test_use_cases.py`).
- **I (Interface Segregation):** `LogHandlerProtocol` expõe apenas
  `emit()`; handlers não são forçados a implementar métodos que não usam.
- **O (Open/Closed):** novos handlers (arquivo, rede, etc.) podem ser
  adicionados implementando `LogHandlerProtocol` sem alterar
  `StructuredLogger`.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

### Exemplos de uso da CLI

```bash
# Logar uma mensagem em INFO
python -m src.cli log "payment processed" --level INFO --tag order_id=42

# Definir contexto global persistente
python -m src.cli context service=billing region=us-east-1

# Ver estatísticas agregadas do logger singleton
python -m src.cli stats
```

Saída de exemplo (`log`):

```json
{"timestamp": "2026-06-22T12:00:00+00:00", "level": "INFO", "message": "payment processed", "module": "...", "context": {"service": "billing", "order_id": "42"}}
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```
