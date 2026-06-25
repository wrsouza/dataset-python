"""
ExceptionGroup e except* (Python 3.11+)

O que este script demonstra: como agrupar múltiplas exceções independentes em
um único ExceptionGroup e tratá-las seletivamente com a sintaxe `except*`,
útil quando várias operações falham simultaneamente (ex: validações em lote).
Quando usar: quando múltiplos erros independentes podem ocorrer na mesma
operação e você quer reportar/tratar todos, não só o primeiro.
"""

import sys


class ValidacaoCampoError(ValueError):
    """Erro de validação de um campo específico de um formulário."""
    pass


class RegraNegocioError(Exception):
    """Erro de violação de regra de negócio (não é simples validação de campo)."""
    pass


def validar_formulario(dados: dict) -> None:
    erros = []

    if not dados.get("nome"):
        erros.append(ValidacaoCampoError("Campo 'nome' é obrigatório"))
    if dados.get("idade", 0) < 0:
        erros.append(ValidacaoCampoError("Campo 'idade' não pode ser negativo"))
    if dados.get("idade", 0) > 0 and dados.get("idade") < 18 and dados.get("autoriza_menor") is not True:
        erros.append(RegraNegocioError("Menor de idade requer autorização explícita"))

    if erros:
        # ExceptionGroup permite carregar várias exceções não relacionadas
        # entre si (mas relacionadas a um mesmo evento) em um único objeto
        # lançável, sem perder informação de cada uma.
        raise ExceptionGroup("Falhas na validação do formulário", erros)


if __name__ == "__main__":
    if sys.version_info < (3, 11):
        print("Este script requer Python 3.11+ (ExceptionGroup/except*).")
        sys.exit(0)

    dados_invalidos = {"nome": "", "idade": 15}

    try:
        # Disparamos o cenário propositalmente: nome vazio + menor sem autorização.
        validar_formulario(dados_invalidos)
    except* ValidacaoCampoError as grupo_validacao:
        # except* captura apenas as exceções do grupo que casam com o tipo
        # informado; grupo_validacao.exceptions contém só essas.
        for erro in grupo_validacao.exceptions:
            print(f"Erro de validação de campo: {erro}")
    except* RegraNegocioError as grupo_regras:
        for erro in grupo_regras.exceptions:
            print(f"Erro de regra de negócio: {erro}")

    dados_validos = {"nome": "Ana", "idade": 20}
    validar_formulario(dados_validos)
    print("Formulário válido, nenhum erro encontrado.")
