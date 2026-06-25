"""
Retry com backoff exponencial

O que este script demonstra: como tentar novamente uma operação que falha
de forma transitória, aumentando o tempo de espera entre tentativas
exponencialmente (com jitter) até um número máximo de tentativas.
Quando usar: chamadas a recursos instáveis (rede, disco, serviços externos)
onde a falha pode ser temporária e uma nova tentativa tem chance de sucesso.
"""

import random
import time


class FalhaTransitoria(Exception):
    """Representa uma falha que pode se resolver sozinha com o tempo."""


def retry_com_backoff(func, tentativas=5, base=0.2, fator=2.0, jitter=0.1):
    """
    Executa `func` repetidamente até ter sucesso ou esgotar as tentativas.

    O tempo de espera crebsce exponencialmente: base * fator^(tentativa-1).
    O jitter evita que múltiplos clientes retomem exatamente no mesmo
    instante (efeito "thundering herd").
    """
    ultima_excecao = None
    for tentativa in range(1, tentativas + 1):
        try:
            return func()
        except FalhaTransitoria as exc:
            ultima_excecao = exc
            if tentativa == tentativas:
                # Esgotou as tentativas: propaga o erro original para quem chamou.
                break
            espera = base * (fator ** (tentativa - 1))
            espera += random.uniform(0, jitter)
            print(f"[tentativa {tentativa}] falhou ({exc}); aguardando {espera:.2f}s")
            time.sleep(espera)
    raise ultima_excecao


def operacao_instavel(estado={"chamadas": 0}):
    """Simula uma operação que falha nas duas primeiras chamadas e depois funciona."""
    estado["chamadas"] += 1
    if estado["chamadas"] < 3:
        raise FalhaTransitoria(f"indisponível (chamada {estado['chamadas']})")
    return "sucesso"


if __name__ == "__main__":
    # Dispara o cenário: a operação falha de propósito nas duas primeiras
    # chamadas, forçando o mecanismo de retry/backoff a atuar antes de
    # finalmente obter sucesso na terceira tentativa.
    resultado = retry_com_backoff(operacao_instavel, tentativas=5, base=0.1)
    print(f"Resultado final: {resultado}")

    # Caso extremo: operação que nunca se recupera -> deve propagar a exceção
    # depois de esgotar as tentativas, comprovando que o retry não mascara
    # falhas permanentes indefinidamente.
    def sempre_falha():
        raise FalhaTransitoria("recurso permanentemente indisponível")

    try:
        retry_com_backoff(sempre_falha, tentativas=3, base=0.05)
    except FalhaTransitoria as exc:
        print(f"Esgotadas as tentativas, erro propagado corretamente: {exc}")
