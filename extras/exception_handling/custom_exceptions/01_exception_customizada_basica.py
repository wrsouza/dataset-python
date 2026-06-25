"""
Exceção customizada básica

O que este script demonstra: como criar uma exceção própria herdando de
`Exception` e usá-la para sinalizar uma condição de erro específica do domínio.
Quando usar: quando exceções built-in (ValueError, TypeError etc.) não
comunicam claramente a intenção/semântica do erro no seu domínio.
"""


class SaldoInsuficienteError(Exception):
    """Erro de domínio: conta sem saldo suficiente para a operação."""
    # Herdar de Exception (e não de BaseException) é a prática recomendada,
    # pois BaseException inclui casos como SystemExit/KeyboardInterrupt,
    # que não devem ser capturados por engano em handlers genéricos.
    pass


def sacar(saldo: float, valor: float) -> float:
    if valor > saldo:
        # Lançamos nossa exceção customizada em vez de um ValueError genérico,
        # permitindo que quem chama distinga esse erro de outros erros de valor.
        raise SaldoInsuficienteError(
            f"Saldo de {saldo:.2f} é insuficiente para sacar {valor:.2f}"
        )
    return saldo - valor


if __name__ == "__main__":
    saldo_atual = 100.0

    try:
        # Disparamos o cenário de erro propositalmente: saque maior que o saldo.
        novo_saldo = sacar(saldo_atual, 500.0)
        print(f"Saque realizado. Novo saldo: {novo_saldo:.2f}")
    except SaldoInsuficienteError as erro:
        # Tratamento específico: capturamos apenas o erro de domínio esperado.
        print(f"Operação rejeitada: {erro}")

    # Demonstrando o caminho de sucesso, para contraste.
    saldo_final = sacar(saldo_atual, 30.0)
    print(f"Saque de 30.00 realizado com sucesso. Saldo final: {saldo_final:.2f}")
