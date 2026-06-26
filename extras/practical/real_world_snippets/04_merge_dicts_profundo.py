"""
Merge recursivo (deep merge) de dicionarios aninhados

Cenario: combinar configuracoes em camadas (defaults + config do ambiente
+ overrides da linha de comando) ou mesclar respostas parciais de uma API
que retorna o mesmo recurso em fragmentos.
O que este script demonstra: merge profundo que combina dicts aninhados
em vez de simplesmente sobrescrever (como dict.update faria).
"""

from copy import deepcopy
from typing import Any, Dict


def deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Mescla 'overrides' em 'base' recursivamente, sem mutar os originais.

    dict.update() comum sobrescreveria chaves inteiras (ex.: o sub-dict
    'database' inteiro), perdendo chaves que so existiam em 'base'.
    Aqui, quando ambos os valores na mesma chave sao dicts, mesclamos
    neles tambem -- senao, o valor de 'overrides' simplesmente vence.
    """
    resultado = deepcopy(base)
    for chave, valor_override in overrides.items():
        valor_base = resultado.get(chave)
        if isinstance(valor_base, dict) and isinstance(valor_override, dict):
            resultado[chave] = deep_merge(valor_base, valor_override)
        else:
            resultado[chave] = deepcopy(valor_override)
    return resultado


if __name__ == "__main__":
    config_default = {
        "database": {"host": "localhost", "port": 5432, "timeout": 30},
        "feature_flags": {"novo_checkout": False},
        "debug": False,
    }

    config_producao = {
        "database": {"host": "db.producao.exemplo.com"},  # so sobrescreve o host
        "feature_flags": {"novo_checkout": True},
    }

    config_final = deep_merge(config_default, config_producao)

    print("Config default :", config_default)
    print("Config producao:", config_producao)
    print("Config final   :", config_final)
    # 'port' e 'timeout' continuam vindo do default, pois nao foram sobrescritos
    assert config_final["database"]["port"] == 5432
    assert config_final["database"]["host"] == "db.producao.exemplo.com"
