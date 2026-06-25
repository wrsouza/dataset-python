"""
Try/except com múltiplos tipos de exceção

O que este script demonstra: como capturar mais de um tipo de exceção na mesma
cláusula `except`, usando uma tupla de tipos, quando o tratamento é igual para todos.
Quando usar: quando diferentes erros levam à mesma ação de recuperação (ex.: logar e
seguir), evitando duplicar blocos `except` idênticos.
"""


def converter_e_dividir(valor: str, divisor: str) -> float:
    """Converte duas strings para número e divide a primeira pela segunda."""
    # ValueError pode vir do int()/float(); ZeroDivisionError, da divisão.
    # Tratamos juntos pois a ação (avisar e retornar None) é idêntica nos dois casos.
    try:
        numero = float(valor)
        div = float(divisor)
        return numero / div
    except (ValueError, ZeroDivisionError) as exc:
        # type(exc).__name__ evita precisar de um except por tipo só para logar.
        print(f"Falha ao processar ({valor!r}, {divisor!r}): {type(exc).__name__}: {exc}")
        return None


if __name__ == "__main__":
    casos = [
        ("10", "2"),       # caso normal, sem erro
        ("abc", "2"),      # dispara ValueError na conversão
        ("10", "0"),       # dispara ZeroDivisionError na divisão
    ]

    for valor, divisor in casos:
        resultado = converter_e_dividir(valor, divisor)
        print(f"Resultado para {valor}/{divisor}: {resultado}")
