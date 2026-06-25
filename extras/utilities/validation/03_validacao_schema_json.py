"""
Validacao de Schema JSON Simples

O que este script demonstra: validar a estrutura de um objeto JSON (carregado
como dict) contra um schema simples descrito tambem como dict, de forma
recursiva, sem usar jsonschema.
Quando usar: validar payloads de API ou arquivos de config antes de
processa-los, quando um schema completo (jsonschema) seria excessivo.
"""

import json


def validar_schema(dados, schema, caminho="raiz"):
    """Schema simplificado:
    {"tipo": str|int|float|bool|list|dict, "campos": {...} (se dict),
     "item": {...} (se list), "obrigatorio": bool}
    Retorna lista de erros.
    """
    erros = []
    tipo_esperado = schema.get("tipo")

    if tipo_esperado and not isinstance(dados, tipo_esperado):
        erros.append(f"{caminho}: esperado {tipo_esperado.__name__}, recebido {type(dados).__name__}")
        return erros  # sem o tipo certo, nao vale a pena validar mais fundo

    if tipo_esperado is dict:
        campos = schema.get("campos", {})
        for nome_campo, sub_schema in campos.items():
            if nome_campo not in dados:
                if sub_schema.get("obrigatorio", True):
                    erros.append(f"{caminho}.{nome_campo}: campo obrigatorio ausente")
                continue
            erros.extend(validar_schema(dados[nome_campo], sub_schema, f"{caminho}.{nome_campo}"))

    elif tipo_esperado is list:
        item_schema = schema.get("item")
        if item_schema:
            for i, item in enumerate(dados):
                erros.extend(validar_schema(item, item_schema, f"{caminho}[{i}]"))

    return erros


if __name__ == "__main__":
    schema_pedido = {
        "tipo": dict,
        "campos": {
            "id": {"tipo": int, "obrigatorio": True},
            "cliente": {"tipo": str, "obrigatorio": True},
            "itens": {
                "tipo": list,
                "obrigatorio": True,
                "item": {
                    "tipo": dict,
                    "campos": {
                        "produto": {"tipo": str, "obrigatorio": True},
                        "qtd": {"tipo": int, "obrigatorio": True},
                    },
                },
            },
        },
    }

    pedido_json_valido = json.loads(
        '{"id": 1, "cliente": "Joao", "itens": [{"produto": "Mouse", "qtd": 2}]}'
    )

    pedido_json_invalido = json.loads(
        '{"id": "um", "itens": [{"produto": "Mouse", "qtd": "dois"}]}'
    )

    erros_validos = validar_schema(pedido_json_valido, schema_pedido)
    erros_invalidos = validar_schema(pedido_json_invalido, schema_pedido)

    print("Pedido valido -> erros:", erros_validos)
    print("Pedido invalido -> erros:")
    for e in erros_invalidos:
        print(" -", e)

    assert erros_validos == []
    assert any("cliente" in e and "ausente" in e for e in erros_invalidos)
    assert any("qtd" in e for e in erros_invalidos)
    print("Sanity check OK.")
