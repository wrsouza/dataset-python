# ML Model Registry — Singleton Pattern

> **Design Pattern:** Singleton | **Categoria:** Creational
> **Framework:** Streamlit | **Serviços:** Nenhum (registry em memória, por processo)

## Objetivo Pedagógico

Demonstrar o padrão **Singleton** em um domínio de MLOps: um único
`ModelRegistry` compartilhado por toda a aplicação mantém metadados de
versões de modelo e instâncias de modelo "carregadas" (simuladas) em
memória, evitando recarregar o mesmo modelo pesado múltiplas vezes. O
aluno deve identificar:

- a implementação do Singleton via **metaclass** com double-checked locking;
- o registry guardando metadados (`ModelVersion`/`ModelMetrics`) separados
  da lógica de promoção e do cache de modelos carregados;
- a UI Streamlit provando visualmente que múltiplos reruns acessam a
  **mesma instância** (mesmo `id(registry)`).

## O Pattern Aplicado

`SingletonMeta` é a metaclasse que garante, para qualquer classe que a use,
que `Classe(...)` sempre devolve o mesmo objeto. `ModelRegistry` usa essa
metaclasse e concentra toda a lógica de negócio: registrar versões,
promover uma versão para `PRODUCTION` (arquivando a anterior) e cachear
modelos já carregados (`get_loaded_model`), para que `loader.load()` —
operação cara em produção real — só execute uma vez por
`(model_name, version)`.

A UI (`infrastructure/app.py`) instancia `ModelRegistry(loader=...)` em
**toda** execução do script (Streamlit reexecuta o arquivo inteiro a cada
interação), mas como `SingletonMeta` intercepta a construção, o objeto
devolvido é sempre o mesmo — visível porque `id(registry)` nunca muda entre
reruns, mesmo registrando novos modelos ou promovendo versões.

## Diagrama UML (ASCII)

```
SingletonMeta (metaclass)
+ _instances: dict[type, Any]        <-- registro global de instâncias
+ _lock: threading.Lock              <-- double-checked locking
+ __call__(cls, *args, **kwargs)
        |
        v instancia exatamente uma vez por classe
ModelRegistry
- _loader: ModelLoader                 <-- injetado (DIP)
- _versions: dict[str, ModelVersion]   <-- metadados em memória
- _loaded_models: dict[str, LoadedModel] <-- cache de modelos "carregados"
- _rlock: threading.RLock              <-- protege leituras/escritas
+ register_version(model_version): None
+ promote_to_production(name, version): ModelVersion
+ list_versions(name=None): list[ModelVersion]
+ get_production_version(name): ModelVersion
+ get_loaded_model(name, version): LoadedModel
+ instance_id() -> int                 <-- prova visual do singleton

        ^                          ^
        | depende de               | depende de
        |                          |
ModelLoader (Protocol)       LoadedModel (Protocol)
- load(name, version)        - predict(payload) -> float
        ^
        | implementa
   MockModelLoader
   (simula carregamento pesado; load_count conta chamadas reais)

        <<entities>>
ModelVersion (dataclass)          ModelMetrics (frozen dataclass)
- model_name, version             - accuracy, f1_score, latency_ms
- status: ModelStatus             - validação no __post_init__
- metrics: ModelMetrics
- promote() / archive()

Streamlit app.py (infrastructure/app.py)
  -> ModelRegistry(loader=MockModelLoader())  # SEMPRE o mesmo objeto
  -> RegisterModelVersionUseCase / PromoteModelVersionUseCase /
     ListModelVersionsUseCase / GetActiveModelUseCase
```

## Por que Metaclass + Double-Checked Locking é Thread-Safe

```python
class SingletonMeta(type):
    _instances: dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:        # leitura rápida, sem lock
            with cls._lock:                  # entra na seção crítica
                if cls not in cls._instances:  # reverifica DENTRO do lock
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
```

A primeira verificação é uma leitura sem lock (caminho rápido, já existe na
maioria das chamadas). Se a classe ainda não foi instanciada, a thread
adquire `_lock` e **verifica novamente** dentro da seção crítica — sem essa
segunda verificação, duas threads poderiam passar a primeira checagem e
construir dois objetos distintos antes que qualquer uma alcançasse o lock.
Apenas a thread que "ganha" a corrida constrói o objeto; todas as demais
(inclusive as que perderam a corrida original) recebem a mesma instância
em cache.

### Por que metaclass, e não módulo ou `__new__` + lock?

- **Módulo (singleton implícito por import):** funciona, mas mistura a
  responsabilidade de "garantir uma instância" com efeitos colaterais de
  import, frágil a `importlib.reload` ou a importar o módulo por dois
  caminhos diferentes.
- **`__new__` + lock dentro da própria classe:** funciona, mas obriga
  `ModelRegistry` a carregar tanto a lógica de negócio quanto a lógica de
  singleton, violando SRP.
- **Metaclass (escolhida):** separa completamente o mecanismo de
  singleton (`SingletonMeta`) da lógica de domínio (`ModelRegistry`),
  segue a mesma convenção já usada no projeto irmão `singleton/p3`
  (consistência no dataset), e permite reutilizar `SingletonMeta` para
  qualquer outra classe sem duplicar código.

Além do `SingletonMeta._lock`, `ModelRegistry` usa `threading.RLock` para
proteger `_versions` e `_loaded_models`, pois o Streamlit pode disparar
chamadas concorrentes a partir de múltiplas sessões/reruns. RLock (em vez
de Lock simples) é usado porque alguns métodos internos chamam outros
métodos protegidos pelo mesmo lock na mesma thread (ex.:
`promote_to_production` chama `_get_version`).

## Prova Visual do Singleton na UI

A seção "Estado único do Registry" em `app.py` exibe três métricas a cada
rerun:

- `id(registry)` — nunca muda entre interações, mesmo registrando ou
  promovendo modelos, provando que a mesma instância está sendo reutilizada;
- número de versões registradas;
- número de modelos efetivamente carregados em cache
  (`registry.loaded_model_count()`), provando que `loader.load()` não é
  chamado de novo a cada inferência.

## Princípios SOLID Demonstrados

- **S — SRP:** `ModelVersion`/`ModelMetrics` (domain/entities.py) descrevem
  apenas dados; `ModelRegistry` (infrastructure/registry.py) cuida apenas
  de armazenamento, regras de promoção e cache de modelos carregados;
  `app.py` cuida apenas de apresentação Streamlit.
- **O — OCP:** `ModelLoader` é um `Protocol` (domain/interfaces.py). Novas
  estratégias de carregamento (ex.: ler de S3, de um arquivo pickle local,
  de um runtime ONNX) bastam implementar `load(model_name, version)` —
  nenhuma mudança em `ModelRegistry` ou nos use cases é necessária.
- **D — DIP:** `ModelRegistry.__init__` recebe um `ModelLoader` injetado;
  os use cases em `application/use_cases.py` dependem apenas de
  `ModelRegistry` e nunca de `MockModelLoader` diretamente. A implementação
  concreta é escolhida apenas na composition root (`app.py`).

## Estrutura do Projeto

```
p5/
├── src/
│   └── model_registry/
│       ├── domain/
│       │   ├── entities.py        <- ModelVersion, ModelMetrics, exceptions
│       │   └── interfaces.py      <- ModelLoader, LoadedModel (Protocol)
│       ├── application/
│       │   └── use_cases.py       <- Register/Promote/List/GetActiveModel
│       └── infrastructure/
│           ├── registry.py        <- SingletonMeta + ModelRegistry
│           ├── loaders.py         <- MockModelLoader
│           └── app.py             <- Streamlit UI (composition root)
├── tests/
│   ├── unit/
│   │   ├── test_entities.py
│   │   ├── test_loaders.py
│   │   └── test_registry.py       <- identidade do singleton + thread-safety
│   └── integration/
│       └── test_model_lifecycle_workflow.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

### Localmente com Streamlit

```bash
pip install -e ".[dev]"
streamlit run src/model_registry/infrastructure/app.py
```

Acesse `http://localhost:8501`.

### Via Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Ou localmente:

```bash
pytest --cov=src --cov-report=term-missing
```
