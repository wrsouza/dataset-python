"""
Tratamento de divisao por zero em calculos em lote

Cenario: processar uma planilha/lista de pedidos calculando media de preco por
unidade, onde algum registro pode ter quantidade igual a zero (erro de
digitacao, produto cancelado, etc). Um unico ZeroDivisionError nao deve
interromper o processamento dos demais registros.
Demonstra: try/except direcionado, valores sentinela e relatorio de erros
acumulados ao final do lote.
"""

from dataclasses import dataclass, field


@dataclass
class ResultadoLote:
    # Guardamos sucesso e falha juntos para nao perder rastreabilidade do lote
    sucesso: dict = field(default_factory=dict)
    falhas: dict = field(default_factory=dict)


def calcular_preco_unitario(pedido_id, valor_total, quantidade):
    """Calcula valor_total / quantidade, isolando o erro por registro."""
    try:
        return valor_total / quantidade
    except ZeroDivisionError:
        # Nao propagamos o erro: quantidade zero e um dado invalido esperado,
        # nao uma falha de programa. Registramos e seguimos o lote.
        return None


def processar_lote(pedidos):
    resultado = ResultadoLote()
    for pedido_id, valor_total, quantidade in pedidos:
        preco = calcular_preco_unitario(pedido_id, valor_total, quantidade)
        if preco is None:
            resultado.falhas[pedido_id] = "quantidade zero - revisar pedido"
        else:
            resultado.sucesso[pedido_id] = round(preco, 2)
    return resultado


if __name__ == "__main__":
    pedidos_exemplo = [
        ("PED-001", 150.00, 3),
        ("PED-002", 89.90, 0),   # quantidade zero -> deve cair em falhas
        ("PED-003", 320.00, 4),
        ("PED-004", 10.00, -0),  # -0 tambem dispara ZeroDivisionError em int/float
    ]

    resultado = processar_lote(pedidos_exemplo)

    print("Precos unitarios calculados com sucesso:")
    for pedido_id, preco in resultado.sucesso.items():
        print(f"  {pedido_id}: R$ {preco:.2f}")

    print("\nPedidos com falha (quantidade invalida):")
    for pedido_id, motivo in resultado.falhas.items():
        print(f"  {pedido_id}: {motivo}")

    total_processados = len(resultado.sucesso) + len(resultado.falhas)
    print(f"\nResumo: {len(resultado.sucesso)}/{total_processados} pedidos calculados, "
          f"{len(resultado.falhas)} com erro de divisao por zero.")
