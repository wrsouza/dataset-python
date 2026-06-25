"""
Ignorando exceções esperadas com contextlib.suppress

O que este script demonstra: como usar `contextlib.suppress` para ignorar
silenciosamente um tipo de exceção esperado, evitando um `try/except: pass` verboso.
Quando usar: quando a exceção é um caminho normal e aceitável do fluxo (ex.: remover
uma chave que pode não existir) e não há nada útil a fazer com ela.
"""

from contextlib import suppress


def remover_chave_se_existir(dicionario: dict, chave: str) -> None:
    """Remove uma chave de um dict, sem se importar se ela não existir."""
    # suppress(KeyError) é equivalente a:
    #   try:
    #       del dicionario[chave]
    #   except KeyError:
    #       pass
    # mas comunica a intenção de forma mais direta: "ignore essa exceção específica".
    with suppress(KeyError):
        del dicionario[chave]


if __name__ == "__main__":
    dados = {"a": 1, "b": 2}

    print(f"Antes: {dados}")

    remover_chave_se_existir(dados, "a")  # existe, remove normalmente
    print(f"Depois de remover 'a': {dados}")

    # 'c' não existe — sem suppress, isso dispararia KeyError não tratado.
    remover_chave_se_existir(dados, "c")
    print(f"Depois de tentar remover 'c' (inexistente, sem erro): {dados}")

    # Demonstrando que suppress só ignora o tipo declarado: ZeroDivisionError
    # continua se propagando normalmente, pois não está na lista de suprimidos.
    try:
        with suppress(KeyError):
            resultado = 1 / 0
    except ZeroDivisionError as exc:
        print(f"Erro NÃO suprimido (tipo diferente do declarado): {exc}")
