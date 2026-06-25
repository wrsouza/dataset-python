"""CLI Typer: ponto de entrada para processar pedidos instrumentados."""

from __future__ import annotations

import typer

from observability.domain.entities import OrderRequest
from observability.domain.exceptions import InvalidOrderError
from observability.infrastructure.factory import build_instrumented_order_processor
from observability.infrastructure.settings import Settings

app = typer.Typer(
    name="observability-decorator",
    help="Processa pedidos com observabilidade (métricas/tracing/erros) via CloudWatch.",  # noqa: E501
)


@app.command()
def process_order(
    customer_id: str = typer.Option(..., help="Identificador do cliente."),
    item_sku: str = typer.Option(..., help="SKU do item do pedido."),
    quantity: int = typer.Option(..., min=1, help="Quantidade de itens."),
    unit_price: float = typer.Option(..., min=0.01, help="Preço unitário do item."),
) -> None:
    """Processa um pedido através da cadeia de decoradores de observabilidade."""
    request = OrderRequest(
        customer_id=customer_id,
        item_sku=item_sku,
        quantity=quantity,
        unit_price=unit_price,
    )
    processor = build_instrumented_order_processor(Settings.from_env())

    try:
        result = processor.process(request)
    except InvalidOrderError as error:
        typer.secho(f"Pedido inválido: {error.reason}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from error

    typer.secho(
        f"Pedido {result.order_id} processado: status={result.status.value} "
        f"total={result.total_amount}",
        fg=typer.colors.GREEN,
    )


def main() -> None:
    """Executa a aplicação CLI."""
    app()


if __name__ == "__main__":
    main()
