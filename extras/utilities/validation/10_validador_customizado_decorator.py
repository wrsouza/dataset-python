"""
Validador Customizado com Decorator

O que este script demonstra: criar um decorator generico que valida os
argumentos de uma funcao contra regras (funcoes de checagem) declaradas via
anotacoes simples, usando apenas functools/inspect da stdlib.
Quando usar: validar parametros de funcoes de negocio (ex.: APIs internas)
de forma declarativa, sem repetir ifs de validacao em cada funcao.
"""

import functools
import inspect


def validar_args(**regras):
    """Decorator-factory: recebe regras como nome_param=funcao_de_checagem.

    A funcao de checagem deve retornar True/False ou levantar excecao.
    """
    def decorator(func):
        assinatura = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # bind_partial permite validar mesmo se nem todos os args foram
            # passados ainda (default values continuam funcionando normalmente)
            valores = assinatura.bind(*args, **kwargs)
            valores.apply_defaults()

            erros = []
            for nome_param, checagem in regras.items():
                if nome_param not in valores.arguments:
                    continue
                valor = valores.arguments[nome_param]
                try:
                    if not checagem(valor):
                        erros.append(f"{nome_param}={valor!r} falhou na validacao")
                except Exception as exc:  # checagem pode levantar excecao propria
                    erros.append(f"{nome_param}={valor!r} -> {exc}")

            if erros:
                raise ValueError(f"Argumentos invalidos para '{func.__name__}': " + "; ".join(erros))

            return func(*args, **kwargs)

        return wrapper

    return decorator


# regras reutilizaveis, podem ser combinadas em diferentes funcoes
def eh_positivo(valor):
    return isinstance(valor, (int, float)) and valor > 0


def eh_string_nao_vazia(valor):
    return isinstance(valor, str) and len(valor.strip()) > 0


@validar_args(preco=eh_positivo, nome=eh_string_nao_vazia)
def criar_item_catalogo(nome: str, preco: float):
    return {"nome": nome, "preco": preco}


if __name__ == "__main__":
    item_ok = criar_item_catalogo("Teclado", 199.90)
    print("Item criado com sucesso:", item_ok)

    erro_capturado = None
    try:
        criar_item_catalogo("", -10)
    except ValueError as exc:
        erro_capturado = str(exc)
        print("Erro esperado capturado:", erro_capturado)

    assert item_ok == {"nome": "Teclado", "preco": 199.90}
    assert erro_capturado is not None
    assert "nome" in erro_capturado and "preco" in erro_capturado
    print("Sanity check OK.")
