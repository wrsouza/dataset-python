"""
Exception chaining com `raise ... from ...`

O que este script demonstra: como preservar a causa original de um erro ao
relançar uma exceção de nível mais alto, mantendo o traceback completo
encadeado (__cause__) para diagnóstico.
Quando usar: quando você captura um erro de baixo nível (ex: parsing, I/O) e
precisa relançar um erro de domínio sem perder a causa raiz.
"""


class ConfiguracaoInvalidaError(Exception):
    """Erro de domínio: configuração da aplicação não pôde ser carregada."""
    pass


def carregar_porta(valor_bruto: str) -> int:
    try:
        # Conversão que pode falhar com um ValueError "de baixo nível".
        porta = int(valor_bruto)
    except ValueError as erro_origem:
        # "raise ... from erro_origem" encadeia a exceção original em
        # __cause__, em vez de simplesmente perdê-la (o que aconteceria
        # se apenas relançássemos um novo erro sem o "from").
        raise ConfiguracaoInvalidaError(
            f"Valor de porta inválido: {valor_bruto!r}"
        ) from erro_origem
    if not (0 < porta <= 65535):
        raise ConfiguracaoInvalidaError(f"Porta fora do intervalo válido: {porta}")
    return porta


if __name__ == "__main__":
    try:
        # Disparamos o erro propositalmente com um valor não numérico.
        carregar_porta("oitenta")
    except ConfiguracaoInvalidaError as erro:
        print(f"Erro de configuração: {erro}")
        # __cause__ guarda a exceção original (o ValueError do int()),
        # permitindo inspecionar a causa raiz sem precisar re-parsear nada.
        print(f"Causa original: {erro.__cause__!r}")

    porta_valida = carregar_porta("8080")
    print(f"Porta carregada com sucesso: {porta_valida}")
