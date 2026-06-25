# Model Audit Trail (Memento) — P3

API Django que mantém uma trilha de auditoria completa de cada edição
de um `Product`: cada `PUT` cria um snapshot imutável (memento) antes
de aplicar a mudança, permitindo desfazer (`undo`) ou consultar o
histórico completo de versões.

> **Nota de ambiente:** o PLAN.md especifica SQL Server; este projeto usa
> SQLite como stand-in (mesmo precedente de outros projetos do dataset,
> ver `docs/decisions/`), já que não há driver ODBC de SQL Server
> disponível neste ambiente. Troque o `ENGINE`/`OPTIONS` em
> `config/settings.py` por `mssql` (django-mssql-backend) para apontar
> para uma instância real.

## Objetivo pedagógico

Demonstrar o pattern **Memento**: `Product` (Originator) sabe criar e
restaurar seu próprio estado a partir de um `ProductSnapshot` imutável,
mas não sabe onde nem como esses snapshots são guardados.
`DjangoAuditTrailCaretaker` (Caretaker) persiste cada snapshot na tabela
`AuditRecordModel`, separada da tabela `ProductModel` que guarda apenas
o estado atual — sem nunca interpretar a semântica dos campos do produto.

Elementos do pattern:
- **Originator:** `Product` (`domain/entities.py`)
- **Memento:** `ProductSnapshot`, `@dataclass(frozen=True)` — imutável após criado
- **Caretaker:** `DjangoAuditTrailCaretaker` (`infrastructure/caretaker.py`)

## Diagrama (ASCII)

```
Client
  │
  ▼
UpdateProductUseCase ──apply_edit()──► Product (Originator, versão++)
  │                                         │
  │                                         ▼ create_snapshot()
  │                                  ProductSnapshot (imutável)
  ▼                                         │
DjangoProductRepository.save()    DjangoAuditTrailCaretaker.save()
(estado atual)                    (tabela audit_record, por versão)

UndoProductUseCase ──undo()──► Caretaker descarta a última versão
                                e retorna a anterior; Product.restore()
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                              | Descrição                                  |
|--------|------------------------------------|---------------------------------------------|
| POST   | `/products/`                       | Cria um produto e seu primeiro snapshot     |
| PUT    | `/products/<product_id>/`          | Edita um produto, salvando um novo snapshot |
| POST   | `/products/<product_id>/undo/`     | Desfaz, voltando à versão anterior          |
| GET    | `/products/<product_id>/history/`  | Lista todos os snapshots (trilha de auditoria) |

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10, "changed_by": "ana"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** `Product` só manipula seu próprio estado em memória; `DjangoAuditTrailCaretaker` só persiste/recupera snapshots; `DjangoProductRepository` só persiste o estado atual.
- **OCP:** um novo backend de auditoria (ex.: tabela em outro banco, S3) implementa `AuditTrailCaretaker` sem alterar `Product` nem os use cases.
- **LSP:** qualquer implementação de `AuditTrailCaretaker`/`ProductRepository` pode substituir as concretas Django nos use cases sem quebrar o contrato.
- **ISP:** `AuditTrailCaretaker` e `ProductRepository` expõem só os métodos que o Originator/use cases realmente precisam.
- **DIP:** os use cases dependem de `AuditTrailCaretaker`/`ProductRepository` (abstrações), nunca das classes concretas Django diretamente — injeção via construtor nas views.
