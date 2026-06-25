"""
Validacao de Faixa Numerica

O que este script demonstra: validar se valores numericos estao dentro de
limites minimos/maximos definidos, incluindo limites abertos/fechados e
mensagens de erro descritivas.
Quando usar: validar entradas como idade, percentual, nota, temperatura, etc.,
antes de salva-las ou processa-las.
"""


def validar_faixa(valor, minimo=None, maximo=None, inclusivo=True, nome="valor"):
    """Levanta ValueError se valor estiver fora da faixa; retorna o valor se ok."""
    if not isinstance(valor, (int, float)):
        raise TypeError(f"{nome} deve ser numerico, recebido {type(valor).__name__}")

    if minimo is not None:
        # inclusivo controla se o limite em si conta como valido (<=) ou nao (<)
        dentro = valor >= minimo if inclusivo else valor > minimo
        if not dentro:
            simbolo = ">=" if inclusivo else ">"
            raise ValueError(f"{nome}={valor} deve ser {simbolo} {minimo}")

    if maximo is not None:
        dentro = valor <= maximo if inclusivo else valor < maximo
        if not dentro:
            simbolo = "<=" if inclusivo else "<"
            raise ValueError(f"{nome}={valor} deve ser {simbolo} {maximo}")

    return valor


def validar_lote(valores: dict, minimo=None, maximo=None, inclusivo=True) -> dict:
    """Valida varios valores de uma vez; retorna {nome: erro_ou_None}."""
    resultado = {}
    for nome, valor in valores.items():
        try:
            validar_faixa(valor, minimo, maximo, inclusivo, nome)
            resultado[nome] = None
        except (ValueError, TypeError) as exc:
            resultado[nome] = str(exc)
    return resultado


if __name__ == "__main__":
    notas = {
        "Ana": 8.5,
        "Bruno": 10.0,
        "Carla": -1.0,   # invalida
        "Diego": 11.5,   # invalida
        "Eva": "dez",    # tipo invalido
    }

    relatorio = validar_lote(notas, minimo=0, maximo=10, inclusivo=True)

    for nome, erro in relatorio.items():
        status = "OK" if erro is None else f"ERRO: {erro}"
        print(f"{nome}: {status}")

    assert relatorio["Ana"] is None
    assert relatorio["Bruno"] is None
    assert relatorio["Carla"] is not None
    assert relatorio["Diego"] is not None
    assert relatorio["Eva"] is not None
    print("Sanity check OK.")
