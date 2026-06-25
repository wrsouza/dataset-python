"""
Fallback para valor padrão

O que este script demonstra: como capturar uma exceção em uma operação que
pode falhar e retornar um valor padrão (ou de uma fonte secundária) em vez
de propagar o erro, mantendo o fluxo do programa.
Quando usar: quando existe um valor "razoável" para seguir adiante mesmo
quando a fonte primária de dados falha (ex.: configuração, cache, parsing).
"""

import json


VALOR_PADRAO_CONFIG = {"timeout": 30, "modo": "padrao"}


def obter_config(texto_json):
    """Tenta interpretar uma configuração em JSON; usa valor padrão se falhar."""
    try:
        return json.loads(texto_json)
    except json.JSONDecodeError as exc:
        # JSON malformado é um erro esperado vindo de entrada externa (arquivo,
        # variável de ambiente, resposta de rede) — não é motivo para
        # interromper a aplicação, só para usar uma configuração segura.
        print(f"aviso: configuração inválida ({exc}); usando valores padrão")
        return dict(VALOR_PADRAO_CONFIG)


def converter_para_inteiro(valor, padrao=0):
    """Converte `valor` para int, retornando `padrao` em caso de erro."""
    try:
        return int(valor)
    except (TypeError, ValueError) as exc:
        print(f"aviso: não foi possível converter {valor!r} ({exc}); usando {padrao}")
        return padrao


def buscar_em_cache_com_fallback(chave, cache, fonte_alternativa):
    """
    Busca `chave` no `cache`; se não existir, busca na fonte alternativa
    (ex.: banco de dados, arquivo). Demonstra fallback em cadeia.
    """
    try:
        return cache[chave]
    except KeyError:
        print(f"aviso: chave {chave!r} ausente no cache; buscando na fonte alternativa")
        try:
            return fonte_alternativa[chave]
        except KeyError:
            # Nenhuma das fontes tem o dado: aqui o fallback final é None,
            # que é um valor padrão explícito e seguro para o chamador tratar.
            print(f"aviso: chave {chave!r} ausente em todas as fontes; retornando None")
            return None


if __name__ == "__main__":
    # 1) Dispara um erro de parsing JSON de propósito (texto malformado).
    config = obter_config("{invalido: sem aspas}")
    print(f"configuração final: {config}")

    # 2) Dispara um ValueError de conversão de propósito.
    porta = converter_para_inteiro("nao-e-um-numero", padrao=8080)
    print(f"porta final: {porta}")

    # 3) Dispara um KeyError em ambas as fontes de propósito.
    cache = {"usuario:1": "Alice"}
    banco = {"usuario:2": "Bob"}
    usuario = buscar_em_cache_com_fallback("usuario:999", cache, banco)
    print(f"usuário final: {usuario}")
