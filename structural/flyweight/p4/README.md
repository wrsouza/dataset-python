# Game Particle System — Flyweight Pattern

> **Design Pattern:** Flyweight | **Categoria:** Structural
> **Framework:** CLI Typer | **Serviços:** Nenhum (sem dependências externas)

## Objetivo Pedagógico

Demonstrar o padrão Flyweight em uma simulação de explosão/fogos de
artifício com milhares de partículas. Em vez de armazenar sprite, cor e
demais dados de configuração em cada `Particle`, o sistema compartilha um
único objeto `ParticleType` por tipo ("fire", "spark", "smoke") entre todas
as partículas daquele tipo — independentemente de existirem 10 ou 100.000
partículas em cena.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Flyweight (estado intrínseco, imutável) | `ParticleType` | `src/particle_system/domain/entities.py` |
| Context (estado extrínseco + referência ao Flyweight) | `Particle` | `src/particle_system/domain/entities.py` |
| FlyweightFactory | `ParticleTypeFactory` | `src/particle_system/infrastructure/factory.py` |
| Client | CLI Typer (`simulate`, `stats`, `export`) | `src/cli/main.py` |

`ParticleType` é um `@dataclass(frozen=True)` — name, sprite, color,
base_lifetime_seconds, drag_coefficient. É o **mesmo objeto** (mesmo `id()`)
para todas as partículas do mesmo tipo. `Particle` guarda apenas o que varia
por partícula: x, y, vx, vy, age_seconds, além da referência ao Flyweight
compartilhado.

## Diagrama UML (ASCII)

```
                     <<frozen dataclass>>
                     ParticleType (Flyweight)
                  name, sprite, color, lifetime, drag
                            ▲   ▲   ▲   ▲   ▲
                            │   │   │   │   │  (mesma referência)
            ┌───────────────┘   │   │   │   └───────────────┐
            │                   │   │   │                   │
       Particle#1           Particle#2  ...            Particle#N
   x,y,vx,vy,age        x,y,vx,vy,age              x,y,vx,vy,age
   (Context)             (Context)                  (Context)

      ParticleTypeFactory (FlyweightFactory)
      ─────────────────────────────────────
      _cache: dict[str, ParticleType]
      + get_or_create(name) -> ParticleType   (cache hit -> mesma instância)
      + register_type(particle_type)          (extensão sem modificar a classe)
```

N partículas (milhares) apontam para apenas 3 (ou poucos) objetos
`ParticleType` compartilhados via a factory — essa é a economia de memória
mensurável que o comando `stats` reporta.

## Estado Intrínseco vs. Extrínseco

| Estado | Onde vive | Exemplos | Compartilhado? |
|--------|-----------|----------|-----------------|
| **Intrínseco** | `ParticleType` (Flyweight) | sprite, color, base_lifetime_seconds, drag_coefficient | Sim — uma instância por tipo |
| **Extrínseco** | `Particle` (Context) | x, y, vx, vy, age_seconds | Não — único por partícula |

## Princípios SOLID Demonstrados

- **SRP (Single Responsibility):** `ParticleType`/`Particle` (estado),
  `ParticleTypeFactory` (cache de Flyweights), `SimpleGravityPhysics`/
  `WeightlessPhysics` (movimento) e a CLI (apresentação) vivem em módulos
  separados, cada um com um único motivo para mudar.
- **OCP (Open/Closed):** novos tipos de partícula (ex: `"magic_spark"`) são
  adicionados via `factory.register_type(ParticleType(...))` — nenhuma
  linha de `ParticleTypeFactory` precisa ser alterada. O método
  `get_or_create` também já tem um caminho de fallback genérico para tipos
  desconhecidos, sem `if/elif` por tipo.
- **DIP (Dependency Inversion):** `RunSimulationUseCase`
  (`src/particle_system/application/use_cases.py`) depende apenas do
  Protocol `PhysicsProtocol` (`src/particle_system/domain/interfaces.py`),
  nunca de `SimpleGravityPhysics` diretamente. A CLI decide qual física
  injetar (`--physics gravity` ou `--physics weightless`); o use case nunca
  muda.

## Relatório de Economia de Memória

O comando `stats` calcula:

- `unique_flyweights`: quantos objetos `ParticleType` distintos existem em
  memória (via `factory.get_flyweight_count()` — contagem real do cache,
  não uma estimativa).
- `estimated_bytes_without_flyweight`: estimativa do custo se cada
  partícula duplicasse seus próprios dados intrínsecos
  (`total_particles * (INTRINSIC_PER_PARTICLE + EXTRINSIC_PER_PARTICLE)`).
- `estimated_bytes_with_flyweight`: custo real com o Flyweight
  (`unique_flyweights * FLYWEIGHT_INTRINSIC_SIZE + total_particles * EXTRINSIC_PER_PARTICLE`)
  — a parcela intrínseca só é paga uma vez por tipo, não por partícula.
- `memory_saved_bytes` / `savings_percentage`: diferença entre os dois
  cenários acima.

Com 1.000 partículas e 3 tipos, a parcela intrínseca cai de "1.000× o custo
de um tipo" para apenas "3× o custo de um tipo" — o ganho cresce
linearmente com o número de partículas, sem nunca aumentar com o número de
tipos únicos.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

### Exemplos de uso da CLI

```bash
# Simular uma explosão com 1000 partículas e 20 passos de física (gravidade)
python -m cli.main simulate --particles 1000 --steps 20

# Simular sem gravidade (física alternativa via Strategy/DIP)
python -m cli.main simulate --particles 500 --steps 10 --physics weightless

# Relatório de economia de memória da última simulação
python -m cli.main stats

# Exportar o estado final das partículas como JSON
python -m cli.main export output.json
```

Saída de exemplo (`stats`):

```
Total particles:      842
Unique flyweights:    3 ('fire', 'spark', 'smoke')
Bytes without Flyweight: 269,440
Bytes with Flyweight:    81,600
Bytes saved:             187,840
Savings:                 69.72%
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (com Python 3.11+ e dependências instaladas):

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

O teste central do pattern é
`tests/unit/test_factory.py::test_get_or_create_returns_same_instance_for_same_type`,
que verifica via `is` que duas chamadas para o mesmo tipo retornam o
**mesmo objeto Python**, e não apenas objetos iguais.
