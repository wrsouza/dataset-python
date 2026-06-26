"""
Cache simples: functools.lru_cache e cache manual com TTL

Cenario: evitar recalcular/reconsultar algo caro repetidamente (ex.: uma
consulta a banco de dados ou chamada de API para buscar dados de um
cliente que raramente mudam dentro de uma janela curta de tempo).
O que este script demonstra: uso de lru_cache (memoria, sem expiracao) e
um cache manual com TTL (time-to-live) para quando o dado pode "envelhecer".
"""

import time
from functools import lru_cache
from typing import Any, Dict, Tuple


@lru_cache(maxsize=128)
def calculo_caro(n: int) -> int:
    """Simula um calculo custoso (ex.: consulta pesada, algoritmo lento).

    lru_cache memoriza por argumentos -- chamadas repetidas com o mesmo
    'n' retornam instantaneamente do cache, sem reexecutar o corpo.
    """
    time.sleep(0.05)  # simula custo de processamento/IO
    return n * n


class CacheComTTL:
    """Cache manual onde cada entrada expira apos 'ttl_segundos'.

    lru_cache nao tem nocao de tempo -- uma vez guardado, o valor fica
    valido para sempre (ou até sair do maxsize). Quando o dado pode ficar
    desatualizado (ex.: cotacao, status de pedido), precisamos de TTL.
    """

    def __init__(self, ttl_segundos: float):
        self._ttl = ttl_segundos
        self._armazenamento: Dict[Any, Tuple[float, Any]] = {}

    def get_ou_calcular(self, chave: Any, funcao_calculo):
        agora = time.monotonic()
        if chave in self._armazenamento:
            timestamp, valor = self._armazenamento[chave]
            if agora - timestamp < self._ttl:
                return valor, True  # hit
        # cache miss ou expirado: recalcula (na vida real, seria uma chamada de API)
        valor = funcao_calculo()
        self._armazenamento[chave] = (agora, valor)
        return valor, False  # miss


if __name__ == "__main__":
    print("lru_cache:")
    print(" calculo_caro(10) ->", calculo_caro(10))
    print(" calculo_caro(10) novamente (cache hit, instantaneo) ->", calculo_caro(10))
    print(" cache info:", calculo_caro.cache_info())

    print("\nCache com TTL:")
    cache_ttl = CacheComTTL(ttl_segundos=0.2)

    def consultar_perfil_cliente():
        # Em uma app real, isto seria uma chamada de rede a uma API de clientes
        return {"id": 42, "nome": "Cliente Exemplo"}

    valor1, era_hit1 = cache_ttl.get_ou_calcular("cliente_42", consultar_perfil_cliente)
    print(" 1a chamada:", valor1, "hit?" , era_hit1)

    valor2, era_hit2 = cache_ttl.get_ou_calcular("cliente_42", consultar_perfil_cliente)
    print(" 2a chamada (dentro do TTL):", valor2, "hit?", era_hit2)

    time.sleep(0.25)  # espera o TTL expirar
    valor3, era_hit3 = cache_ttl.get_ou_calcular("cliente_42", consultar_perfil_cliente)
    print(" 3a chamada (apos expirar TTL):", valor3, "hit?", era_hit3)
