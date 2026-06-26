"""
Rate limiter simples (token bucket simplificado)

Cenario: proteger uma API propria contra abuso, ou respeitar o limite de
chamadas por segundo de uma API de terceiros (ex.: "max 5 requisicoes/s")
para evitar erros HTTP 429 (Too Many Requests).
O que este script demonstra: implementacao de token bucket -- tokens sao
repostos ao longo do tempo e cada chamada consome um token.
"""

import time


class TokenBucketRateLimiter:
    """Permite no maximo 'capacidade' chamadas, repondo tokens a uma taxa fixa.

    Diferente de um contador fixo por janela de tempo, o token bucket
    suaviza picos: se o cliente nao usou a capacidade total, os tokens
    acumulam (até o limite) e podem ser "gastos" em rajada depois.
    """

    def __init__(self, capacidade: int, tokens_por_segundo: float):
        self._capacidade = capacidade
        self._tokens_por_segundo = tokens_por_segundo
        self._tokens_disponiveis = float(capacidade)
        self._ultima_atualizacao = time.monotonic()

    def _repor_tokens(self) -> None:
        agora = time.monotonic()
        tempo_passado = agora - self._ultima_atualizacao
        novos_tokens = tempo_passado * self._tokens_por_segundo
        # nunca passa da capacidade maxima do balde
        self._tokens_disponiveis = min(self._capacidade, self._tokens_disponiveis + novos_tokens)
        self._ultima_atualizacao = agora

    def permitir_chamada(self) -> bool:
        """Retorna True e consome 1 token se houver disponivel, senao False."""
        self._repor_tokens()
        if self._tokens_disponiveis >= 1:
            self._tokens_disponiveis -= 1
            return True
        return False


if __name__ == "__main__":
    # Simula um limite de 3 chamadas, repondo 1 token a cada 0.5s
    limiter = TokenBucketRateLimiter(capacidade=3, tokens_por_segundo=2)

    print("Disparando 6 chamadas rapidas (limite de 3 simultaneas):")
    for tentativa in range(1, 7):
        # Em uma app real, esta seria a chamada de API protegida pelo limiter
        permitido = limiter.permitir_chamada()
        status = "OK" if permitido else "BLOQUEADO (rate limit excedido)"
        print(f"  Tentativa {tentativa}: {status}")

    print("\nAguardando 1s para os tokens serem repostos...")
    time.sleep(1)
    permitido = limiter.permitir_chamada()
    print("Nova tentativa apos espera:", "OK" if permitido else "BLOQUEADO")
