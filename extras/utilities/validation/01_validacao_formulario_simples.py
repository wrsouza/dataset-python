"""
Validacao de Formulario Simples

O que este script demonstra: validar um dicionario de dados de formulario,
checando campos obrigatorios e tipos esperados sem usar bibliotecas externas.
Quando usar: validar payloads simples (ex.: formularios web) antes de processa-los.
"""


def validar_formulario(dados: dict, esquema: dict) -> list:
    """Retorna lista de erros encontrados (vazia se tudo ok).

    esquema = {"campo": (tipo, obrigatorio_bool)}
    """
    erros = []

    for campo, (tipo_esperado, obrigatorio) in esquema.items():
        if campo not in dados or dados[campo] in (None, ""):
            # campo ausente ou vazio: so e erro se for obrigatorio
            if obrigatorio:
                erros.append(f"Campo obrigatorio ausente: '{campo}'")
            continue

        valor = dados[campo]
        if not isinstance(valor, tipo_esperado):
            erros.append(
                f"Campo '{campo}' deveria ser {tipo_esperado.__name__}, "
                f"recebeu {type(valor).__name__}"
            )

    # campos extras nao previstos no esquema (apenas aviso, nao bloqueante)
    extras = set(dados) - set(esquema)
    if extras:
        erros.append(f"Campos nao reconhecidos (ignorados): {sorted(extras)}")

    return erros


if __name__ == "__main__":
    esquema_cadastro = {
        "nome": (str, True),
        "idade": (int, True),
        "email": (str, True),
        "newsletter": (bool, False),
    }

    formulario_valido = {
        "nome": "Ana Silva",
        "idade": 30,
        "email": "ana@example.com",
        "newsletter": True,
    }

    formulario_invalido = {
        "nome": "",
        "idade": "trinta",  # tipo errado
        "telefone": "123",  # campo extra nao previsto
    }

    erros_ok = validar_formulario(formulario_valido, esquema_cadastro)
    erros_falho = validar_formulario(formulario_invalido, esquema_cadastro)

    print("Formulario valido -> erros:", erros_ok)
    print("Formulario invalido -> erros:", erros_falho)

    assert erros_ok == []
    assert any("obrigatorio ausente" in e for e in erros_falho)
    assert any("deveria ser int" in e for e in erros_falho)
    print("Sanity check OK.")
