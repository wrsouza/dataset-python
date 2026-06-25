"""
Hierarquia de exceptions de domínio (pagamentos)

O que este script demonstra: como organizar uma árvore de exceções para um
domínio (pagamentos), com uma base comum e subclasses específicas, permitindo
capturar erros em diferentes níveis de granularidade.
Quando usar: quando o domínio tem múltiplos tipos de falha relacionados e o
código cliente precisa decidir o tratamento de forma genérica ou específica.
"""


class PagamentoError(Exception):
    """Classe base para todos os erros relacionados a pagamentos."""
    pass


class CartaoRecusadoError(PagamentoError):
    """Erro específico: operadora do cartão recusou a transação."""
    pass


class SaldoInsuficienteError(PagamentoError):
    """Erro específico: saldo/limite insuficiente para a transação."""
    pass


class GatewayIndisponivelError(PagamentoError):
    """Erro específico: gateway de pagamento fora do ar (infraestrutura)."""
    pass


def processar_pagamento(metodo: str, valor: float) -> str:
    # Simulação simples de regras de negócio que disparam erros distintos,
    # todos pertencentes à mesma família PagamentoError.
    if metodo == "cartao" and valor > 1000:
        raise CartaoRecusadoError("Operadora recusou: valor acima do limite do cartão")
    if metodo == "debito" and valor > 200:
        raise SaldoInsuficienteError("Saldo em conta corrente insuficiente")
    if metodo == "pix_offline":
        raise GatewayIndisponivelError("Gateway PIX está indisponível no momento")
    return f"Pagamento de {valor:.2f} via {metodo} aprovado"


if __name__ == "__main__":
    cenarios = [
        ("cartao", 1500.0),     # dispara CartaoRecusadoError
        ("debito", 300.0),      # dispara SaldoInsuficienteError
        ("pix_offline", 50.0),  # dispara GatewayIndisponivelError
        ("pix", 50.0),          # caminho de sucesso
    ]

    for metodo, valor in cenarios:
        try:
            resultado = processar_pagamento(metodo, valor)
            print(f"OK: {resultado}")
        except CartaoRecusadoError as erro:
            # Tratamento específico: poderia sugerir outro cartão.
            print(f"Cartão recusado -> {erro}")
        except PagamentoError as erro:
            # Tratamento genérico para qualquer outro erro de pagamento
            # (SaldoInsuficienteError, GatewayIndisponivelError, futuras subclasses).
            print(f"Falha no pagamento ({type(erro).__name__}) -> {erro}")
