"""
Circuit breaker simples

O que este script demonstra: uma implementação mínima do padrão circuit
breaker com os estados CLOSED, OPEN e HALF_OPEN, que "abre o circuito" após
um número de falhas consecutivas, bloqueando chamadas até um tempo de
recuperação passar.
Quando usar: para evitar sobrecarregar um serviço já com problemas, falhando
rápido em vez de continuar tentando chamadas que provavelmente vão falhar.
"""

import time
from enum import Enum


class EstadoCircuito(Enum):
    CLOSED = "closed"        # operando normalmente
    OPEN = "open"             # bloqueando chamadas (serviço considerado fora do ar)
    HALF_OPEN = "half_open"   # testando se o serviço já se recuperou


class CircuitoAbertoError(Exception):
    """Lançada quando uma chamada é bloqueada porque o circuito está aberto."""


class CircuitBreaker:
    def __init__(self, limite_falhas=3, tempo_recuperacao=1.0):
        self.limite_falhas = limite_falhas
        self.tempo_recuperacao = tempo_recuperacao
        self.falhas_consecutivas = 0
        self.estado = EstadoCircuito.CLOSED
        self.abriu_em = None

    def _atualizar_para_half_open_se_pronto(self):
        # Decorrido o tempo de recuperação, damos uma chance ao serviço
        # (HALF_OPEN) em vez de continuar bloqueando para sempre.
        if self.estado is EstadoCircuito.OPEN:
            if time.monotonic() - self.abriu_em >= self.tempo_recuperacao:
                self.estado = EstadoCircuito.HALF_OPEN

    def chamar(self, func, *args, **kwargs):
        self._atualizar_para_half_open_se_pronto()

        if self.estado is EstadoCircuito.OPEN:
            raise CircuitoAbertoError("circuito aberto: chamada bloqueada")

        try:
            resultado = func(*args, **kwargs)
        except Exception:
            self.falhas_consecutivas += 1
            if self.estado is EstadoCircuito.HALF_OPEN or self.falhas_consecutivas >= self.limite_falhas:
                # Falhou no teste HALF_OPEN, ou atingiu o limite em CLOSED:
                # volta (ou permanece) a abrir o circuito.
                self.estado = EstadoCircuito.OPEN
                self.abriu_em = time.monotonic()
            raise
        else:
            # Sucesso reseta o contador e fecha o circuito.
            self.falhas_consecutivas = 0
            self.estado = EstadoCircuito.CLOSED
            return resultado


def servico_externo(estado={"chamadas": 0}):
    """Simula um serviço que falha sempre, até a chamada de número 5."""
    estado["chamadas"] += 1
    if estado["chamadas"] < 5:
        raise ConnectionError(f"serviço fora do ar (chamada {estado['chamadas']})")
    return "resposta ok"


if __name__ == "__main__":
    breaker = CircuitBreaker(limite_falhas=3, tempo_recuperacao=0.3)

    # Dispara falhas consecutivas reais até o circuito abrir de propósito.
    for i in range(3):
        try:
            breaker.chamar(servico_externo)
        except ConnectionError as exc:
            print(f"chamada {i + 1}: falhou como esperado ({exc}); estado={breaker.estado.value}")

    # Agora o circuito deve estar OPEN: a chamada nem chega a executar a função.
    try:
        breaker.chamar(servico_externo)
    except CircuitoAbertoError as exc:
        print(f"bloqueado pelo circuit breaker: {exc}; estado={breaker.estado.value}")

    # Espera o tempo de recuperação passar para permitir o teste HALF_OPEN.
    time.sleep(0.35)

    # Nessa fase o serviço ainda falha (chamada 4), então o teste em
    # HALF_OPEN falha e o circuito reabre imediatamente.
    try:
        breaker.chamar(servico_externo)
    except ConnectionError as exc:
        print(f"teste half-open falhou, reabrindo: {exc}; estado={breaker.estado.value}")

    time.sleep(0.35)
    # Na chamada 5 o serviço finalmente responde, fechando o circuito.
    resultado = breaker.chamar(servico_externo)
    print(f"circuito recuperado, resultado={resultado}; estado={breaker.estado.value}")
