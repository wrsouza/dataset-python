# Checklist SOLID — Design Patterns Dataset
> Use este checklist para validar cada projeto antes de marcar como [x] no STATUS.md.

---

## S — Single Responsibility Principle

**Regra:** Uma classe tem apenas um motivo para mudar.

### Checklist
- [ ] Cada classe encapsula um único conceito de negócio
- [ ] Não há classes que "salvam E enviam e-mail"
- [ ] Repositórios não contêm lógica de negócio
- [ ] Use cases não acessam banco diretamente (usam interface)

### Sinais de violação
- Classe com `and` na descrição do que faz
- Método `save_and_notify()` em vez de `save()` + `notify()`
- Mais de 2 razões para alterar uma classe

### Exemplo correto
```python
# Separado: cada classe uma responsabilidade
class OrderRepository:
    def save(self, order: Order) -> None: ...

class OrderNotifier:
    def notify_created(self, order: Order) -> None: ...

class CreateOrderUseCase:
    def __init__(self, repo: OrderRepository, notifier: OrderNotifier) -> None: ...
    def execute(self, data: OrderData) -> Order: ...
```

---

## O — Open/Closed Principle

**Regra:** Aberto para extensão, fechado para modificação.

### Checklist
- [ ] Adicionar novo tipo/estratégia não exige alterar código existente
- [ ] Sem `if isinstance(obj, ConcreteType)` para decidir comportamento
- [ ] Sem `if type == "stripe": ... elif type == "paypal": ...`
- [ ] Extensão via herança de ABC ou injeção de nova implementação

### Sinais de violação
- Toda adição de novo provedor exige alterar a classe principal
- Switch/if-elif encadeado baseado em tipo de objeto

### Exemplo correto
```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool: ...

class StripeGateway(PaymentGateway):      # extensão: novo arquivo, sem alterar base
    def charge(self, amount: float) -> bool: ...

class PayPalGateway(PaymentGateway):      # extensão: novo arquivo, sem alterar base
    def charge(self, amount: float) -> bool: ...
```

---

## L — Liskov Substitution Principle

**Regra:** Subclasses devem ser substituíveis pela superclasse.

### Checklist
- [ ] Subclasse não lança exceções que a base não lança
- [ ] Subclasse não restringe pré-condições da base
- [ ] Subclasse não enfraquece pós-condições da base
- [ ] Nenhum `if isinstance(obj, SubClass)` para tratamento especial

### Sinais de violação
- Método sobrescrito que lança `NotImplementedError`
- Subclasse que ignora ou invalida o comportamento da base
- Código cliente que verifica o tipo concreto

### Exemplo correto
```python
class FileStorage(ABC):
    def upload(self, key: str, data: bytes) -> str:
        """Returns public URL. Never raises IOError (wraps internally)."""
        ...

class S3Storage(FileStorage):
    def upload(self, key: str, data: bytes) -> str:
        # Mesma contrato: retorna URL, nunca propaga IOError para fora
        try:
            self._client.put_object(...)
            return self._build_url(key)
        except ClientError as e:
            raise StorageUploadError(str(e)) from e  # exceção do domínio, não boto3
```

---

## I — Interface Segregation Principle

**Regra:** Clientes não devem depender de interfaces que não usam.

### Checklist
- [ ] ABCs têm poucos métodos (idealmente 1-3)
- [ ] Não há métodos `raise NotImplementedError` espalhados
- [ ] Diferentes clientes têm interfaces diferentes e enxutas
- [ ] Uso de `Protocol` para interfaces implícitas quando adequado

### Sinais de violação
- ABC com 10+ métodos abstratos
- Implementações concretas com `def method(self): pass` (método vazio)
- Uma interface serve N propósitos diferentes

### Exemplo correto
```python
from typing import Protocol

class Readable(Protocol):
    def read(self, key: str) -> bytes: ...

class Writable(Protocol):
    def write(self, key: str, data: bytes) -> None: ...

class Deletable(Protocol):
    def delete(self, key: str) -> None: ...

# Cliente que só lê não precisa depender de Writable/Deletable
class FileViewer:
    def __init__(self, storage: Readable) -> None: ...
```

---

## D — Dependency Inversion Principle

**Regra:** Módulos de alto nível dependem de abstrações, não de implementações.

### Checklist
- [ ] Use cases recebem dependências via construtor (não instanciam internamente)
- [ ] Use cases dependem de `Protocol` ou `ABC`, não de classes concretas
- [ ] Implementações concretas são injetadas na composição root (main.py / factory)
- [ ] Testes unitários injetam mocks/fakes sem alterar o código de produção

### Sinais de violação
- `self.db = PostgreSQLConnection(...)` dentro de um use case
- `import boto3; s3 = boto3.client(...)` dentro de lógica de negócio
- Impossível testar sem banco de dados real

### Exemplo correto
```python
# domain/interfaces.py — abstração de alto nível
class OrderRepository(Protocol):
    def find_by_id(self, order_id: str) -> Order | None: ...
    def save(self, order: Order) -> None: ...

# application/use_cases.py — depende da abstração
class CancelOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository  # injeção via construtor

    def execute(self, order_id: str) -> None:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        order.cancel()
        self._repository.save(order)

# infrastructure/postgres_order_repository.py — implementação concreta
class PostgresOrderRepository:
    def find_by_id(self, order_id: str) -> Order | None: ...
    def save(self, order: Order) -> None: ...

# main.py — composição root (único lugar com dependência concreta)
repo = PostgresOrderRepository(connection_string=settings.DATABASE_URL)
use_case = CancelOrderUseCase(repository=repo)
```

---

## Validação Final por Projeto

Antes de marcar `[x]`:

| Princípio | Verificado? | Onde aparece no código |
|-----------|-------------|------------------------|
| S — SRP   | [ ]         | `src/.../domain/` e `application/` |
| O — OCP   | [ ]         | ABCs em `domain/interfaces.py` |
| L — LSP   | [ ]         | Subclasses em `infrastructure/` |
| I — ISP   | [ ]         | Protocols em `domain/interfaces.py` |
| D — DIP   | [ ]         | Injeção em `application/use_cases.py` |
