# Infrastructure Profile Cloner (Prototype)

> **Design Pattern:** Prototype | **Categoria:** Creational
> **Framework:** CLI Typer | **Serviços:** Nenhum (persistência em arquivo JSON local)

## Objetivo Pedagógico

Demonstrar o pattern Prototype clonando "perfis de infraestrutura" (tipo de
instância, região, tags, regras de firewall, variáveis de ambiente, storage)
a partir de templates pré-configurados. O aluno deve aprender por que um
clone superficial (`copy.copy`) seria perigoso aqui — os campos `tags`,
`firewall_rules` e `env_vars` são dicts/listas mutáveis, e compartilhar essas
estruturas entre o original e o clone faria uma edição no clone "vazar" de
volta para o template. O clone profundo (`copy.deepcopy`) resolve isso.

## O Pattern Aplicado

- **Prototype** (`src/infra_profile/domain/interfaces.py`): ABC com o método
  abstrato `clone()`.
- **ConcretePrototype** (`InfrastructureProfile`, em
  `src/infra_profile/domain/entities.py`): implementa `clone()` retornando
  `copy.deepcopy(self)`, com um `__deepcopy__` explícito que deixa visível,
  campo a campo, que `tags`, `firewall_rules`, `env_vars` e `storage` são
  todos copiados profundamente — nunca compartilhados por referência.
- **Prototype Registry** (`ProfileRegistry`, em
  `src/infra_profile/infrastructure/registry.py`): guarda templates
  nomeados (`prod-api-template`, `staging-db-template`) disponíveis para
  clonagem via `get_template(name)`.

Fluxo típico: o usuário pede para clonar `prod-api-template` como
`staging-api-template` mudando a região — o caso de uso busca o template no
registry, chama `clone()` (deep copy), aplica os overrides apenas no clone, e
salva o resultado. O template original nunca é tocado.

## Diagrama UML (ASCII)

```
        <<ABC>>
        Prototype
   -----------------------
   + clone(): Prototype
            ^
            | implementa
            |
      InfrastructureProfile
   -----------------------------------
   - name: str
   - instance_type: str
   - region: str
   - tags: dict[str, str]
   - firewall_rules: list[str]
   - env_vars: dict[str, str]
   - storage: StorageConfig
   -----------------------------------
   + clone(): InfrastructureProfile      (deep copy)
   + apply_overrides(**fields): None

      ProfileRegistry  (Prototype Registry)
   -----------------------------------
   - _templates: dict[str, InfrastructureProfile]
   -----------------------------------
   + register(profile): None             (extensível, sem if/elif)
   + get_template(name): InfrastructureProfile
   + list_template_names(): list[str]
            |
            | usado por
            v
      CloneProfileUseCase
   -----------------------------------
   + execute(template_name, new_name, **overrides)
       -> registry.get_template(name).clone() + overrides
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** a entidade (`entities.py`), a lógica de
  clonagem/registry (`registry.py`), a persistência
  (`json_repository.py`) e a apresentação (`cli.py`) vivem em arquivos e
  classes separadas — cada um com um único motivo para mudar.
- **O (Open/Closed):** `ProfileRegistry.register()` aceita qualquer
  `InfrastructureProfile`; adicionar um novo template (ou, futuramente, um
  novo tipo de recurso clonável) nunca exige modificar `ProfileRegistry`
  nem `CloneProfileUseCase` — apenas chamar `register()` com a nova
  instância (ver `build_default_registry()`).
- **D (Dependency Inversion):** todos os use cases em
  `src/infra_profile/application/use_cases.py` recebem `ProfileRepository`
  (um `Protocol`, ver `domain/interfaces.py`) via construtor. Nenhum deles
  importa `JsonProfileRepository` diretamente — os testes unitários usam um
  `FakeProfileRepository` em memória sem precisar de arquivo no disco.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

### Exemplos de uso da CLI

```bash
# Listar templates disponíveis no registry
python -m src.infra_profile list-templates

# Clonar um template para um novo perfil, ajustando região e instance_type
python -m src.infra_profile clone prod-api-template staging-api-template \
    --region us-west-2 --instance-type m5.large

# Criar um perfil do zero (sem clonar nenhum template)
python -m src.infra_profile create dev-box --instance-type t3.micro --region us-east-1

# Mostrar um perfil salvo
python -m src.infra_profile show staging-api-template

# Listar perfis salvos no repositório
python -m src.infra_profile list

# Exportar um perfil salvo para um arquivo JSON independente
python -m src.infra_profile export staging-api-template --output staging.json
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (com o venv do projeto):

```bash
.venv/Scripts/python -m pytest
```
