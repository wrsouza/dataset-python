# Guia Clean Code — Design Patterns Dataset
> Aplicar em todos os 110 projetos sem exceção.

---

## Nomenclatura

- Nomes revelam **intenção**: `calculate_order_total()` não `calc()`.
- Evite prefixos desnecessários: `User` não `UserModel` ou `UserObject`.
- Booleanos usam prefixos `is_`, `has_`, `can_`: `is_active`, `has_permission`.
- Coleções no plural: `orders`, `payment_gateways`.
- Classes concretas incluem o conceito: `StripePaymentGateway`, `S3FileStorage`.

## Funções

- Uma função = uma responsabilidade.
- Máximo ~20 linhas; se precisar de mais, extraia funções auxiliares.
- Parâmetros: no máximo 3; se precisar de mais, use dataclass como parâmetro.
- Evite flags booleanas como parâmetro — prefira duas funções distintas.
- Retorne cedo (`early return`) para evitar aninhamento profundo.

```python
# Ruim
def process(data, send_email=False):
    if data:
        result = transform(data)
        if send_email:
            notify(result)
    return result

# Bom
def process_and_notify(data: OrderData) -> ProcessedOrder:
    order = transform(data)
    notify_order_processed(order)
    return order

def process_silently(data: OrderData) -> ProcessedOrder:
    return transform(data)
```

## Comentários

- Comente o **PORQUÊ**, nunca o **O QUÊ** (o código já diz o quê).
- Remova código comentado — use git para histórico.
- Docstrings obrigatórias apenas em: ABCs, módulos públicos, funções de API.

```python
# Ruim: comenta o óbvio
# Incrementa o contador
counter += 1

# Bom: explica o porquê não-óbvio
# AWS SDK exige retry com backoff exponencial em ThrottlingException
time.sleep(2 ** attempt)
```

## Tratamento de Erros

- Use exceções específicas do domínio.
- Nunca silencie exceções (`except: pass`).
- Logue antes de re-lançar se precisar de contexto.

```python
# Domínio define suas exceções
class PaymentDeclinedError(Exception):
    def __init__(self, reason: str, transaction_id: str) -> None:
        self.reason = reason
        self.transaction_id = transaction_id
        super().__init__(f"Payment declined: {reason}")
```

## Type Hints

- Obrigatórios em **toda** assinatura de função.
- Usar `from __future__ import annotations` para forward references.
- Preferir `Protocol` a importações cíclicas.
- Usar `TypeAlias` para tipos complexos recorrentes.

```python
from __future__ import annotations
from typing import Protocol, TypeAlias

OrderId: TypeAlias = str

class PaymentGateway(Protocol):
    def charge(self, amount: float, order_id: OrderId) -> bool: ...
```

## Organização de Módulos

- Imports: stdlib → third-party → local (Ruff/isort enforça isso).
- Evite importações circulares usando a arquitetura de camadas.
- `__all__` em módulos públicos para controlar o que é exportado.
