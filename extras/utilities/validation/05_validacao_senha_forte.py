"""
Validacao de Forca de Senha

O que este script demonstra: aplicar um checklist de regras combinadas
(tamanho, maiuscula, minuscula, digito, caractere especial, espacos) para
classificar a forca de uma senha usando apenas string/re da stdlib.
Quando usar: validar senhas no cadastro de usuarios antes de armazena-las
(sempre com hash, claro - este script so avalia a forca do texto).
"""

import re

REGRAS = {
    "tamanho_minimo": (lambda s: len(s) >= 8, "deve ter ao menos 8 caracteres"),
    "tem_maiuscula": (lambda s: re.search(r"[A-Z]", s) is not None, "deve ter ao menos 1 letra maiuscula"),
    "tem_minuscula": (lambda s: re.search(r"[a-z]", s) is not None, "deve ter ao menos 1 letra minuscula"),
    "tem_digito": (lambda s: re.search(r"\d", s) is not None, "deve ter ao menos 1 digito"),
    "tem_especial": (lambda s: re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", s) is not None, "deve ter ao menos 1 caractere especial"),
    "sem_espacos": (lambda s: " " not in s, "nao pode conter espacos"),
}


def avaliar_senha(senha: str) -> dict:
    """Retorna dict com regras atendidas, erros e uma pontuacao de 0 a len(REGRAS)."""
    erros = []
    pontuacao = 0
    for nome_regra, (checagem, mensagem) in REGRAS.items():
        if checagem(senha):
            pontuacao += 1
        else:
            erros.append(mensagem)

    if pontuacao == len(REGRAS):
        classificacao = "forte"
    elif pontuacao >= len(REGRAS) - 2:
        classificacao = "media"
    else:
        classificacao = "fraca"

    return {"pontuacao": pontuacao, "total": len(REGRAS), "classificacao": classificacao, "erros": erros}


if __name__ == "__main__":
    senhas_teste = [
        "abc123",            # fraca
        "Senha forte 1",     # tem espaco -> nao forte
        "Sup3rSegura!2024",  # forte
        "minuscula",         # fraca
    ]

    for senha in senhas_teste:
        resultado = avaliar_senha(senha)
        print(f"'{senha}' -> {resultado['classificacao']} ({resultado['pontuacao']}/{resultado['total']})")
        if resultado["erros"]:
            for erro in resultado["erros"]:
                print("   -", erro)

    forte = avaliar_senha("Sup3rSegura!2024")
    fraca = avaliar_senha("abc123")

    assert forte["classificacao"] == "forte"
    assert fraca["classificacao"] == "fraca"
    print("Sanity check OK.")
