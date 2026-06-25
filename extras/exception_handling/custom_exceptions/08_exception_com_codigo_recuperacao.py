"""
Exception com código de recuperação (retry/abort)

O que este script demonstra: uma exceção customizada que carrega uma sugestão
de ação de recuperação (ex: "retry", "abort", "fallback"), permitindo que o
código chamador automatize a decisão de o que fazer após o erro.
Quando usar: em operações que podem falhar de forma transitória (rede,
concorrência) e onde a própria exceção pode indicar se vale tentar novamente.
"""

import random


class OperacaoFalhouError(Exception):
    """Erro que sugere uma ação de recuperação ao chamador."""

    ACOES_VALIDAS = {"retry", "abort", "fallback"}

    def __init__(self, mensagem: str, acao_sugerida: str):
        if acao_sugerida not in self.ACOES_VALIDAS:
            # Validamos a própria ação sugerida para evitar que um erro de
            # digitação no código de quem lança a exceção passe despercebido.
            raise ValueError(f"Ação de recuperação inválida: {acao_sugerida!r}")
        super().__init__(mensagem)
        self.acao_sugerida = acao_sugerida


def chamar_servico_externo(tentativa: int) -> str:
    # Simulamos uma falha transitória de rede que se resolve em algumas tentativas,
    # típica de serviços externos instáveis.
    if tentativa < 3:
        raise OperacaoFalhouError(
            f"Timeout na tentativa {tentativa}", acao_sugerida="retry"
        )
    return "Resposta do serviço externo"


def executar_com_recuperacao(max_tentativas: int = 5) -> str:
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            return chamar_servico_externo(tentativa)
        except OperacaoFalhouError as erro:
            print(f"Falha: {erro} | ação sugerida: {erro.acao_sugerida}")
            if erro.acao_sugerida == "retry":
                # A própria exceção orienta o loop a tentar novamente,
                # sem que o chamador precise conhecer a causa específica.
                tentativa += 1
                continue
            if erro.acao_sugerida == "abort":
                raise
            # "fallback" e outros casos não tratados aqui simplesmente propagam.
            raise
    raise OperacaoFalhouError("Número máximo de tentativas excedido", acao_sugerida="abort")


if __name__ == "__main__":
    random.seed(42)  # determinismo apenas para reprodutibilidade do exemplo

    try:
        # Disparamos o cenário de falhas transitórias propositalmente: as duas
        # primeiras tentativas falham com "retry" antes do sucesso na 3ª.
        resultado = executar_com_recuperacao(max_tentativas=5)
        print(f"Sucesso após recuperação automática: {resultado}")
    except OperacaoFalhouError as erro_final:
        print(f"Falha definitiva, ação sugerida: {erro_final.acao_sugerida}")
