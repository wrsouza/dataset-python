"""
Parser manual de linha delimitada (sem o modulo csv)

O que este script demonstra: como implementar manualmente um parser de linha
estilo CSV, tratando aspas e delimitadores escapados, sem usar o modulo csv da stdlib.
Quando usar: exercicio didatico para entender como um parser CSV funciona por dentro,
ou quando se precisa de um formato customizado que o modulo csv padrao nao cobre bem.
"""


def parsear_linha_csv(linha: str, delimitador: str = ",") -> list[str]:
    """
    Parser manual: percorre caractere por caractere, respeitando campos entre aspas
    (onde o delimitador deve ser ignorado) e aspas duplicadas como escape de aspas literais.
    """
    campos = []
    campo_atual = []
    dentro_de_aspas = False
    i = 0
    n = len(linha)

    while i < n:
        char = linha[i]

        if dentro_de_aspas:
            if char == '"':
                # aspas duplicadas ("") dentro de um campo citado = aspas literal escapada
                if i + 1 < n and linha[i + 1] == '"':
                    campo_atual.append('"')
                    i += 2
                    continue
                # aspas simples fecham o campo citado
                dentro_de_aspas = False
                i += 1
                continue
            campo_atual.append(char)
            i += 1
            continue

        if char == '"':
            # abre um campo citado (permite delimitador literal dentro do campo)
            dentro_de_aspas = True
            i += 1
            continue

        if char == delimitador:
            campos.append("".join(campo_atual))
            campo_atual = []
            i += 1
            continue

        campo_atual.append(char)
        i += 1

    campos.append("".join(campo_atual))
    return campos


if __name__ == "__main__":
    linhas_exemplo = [
        "nome,idade,cidade",
        "Joao,28,Sao Paulo",
        '"Silva, Maria",34,"Rio de Janeiro"',
        '"Ela disse ""ola""",40,Curitiba',
    ]

    for linha in linhas_exemplo:
        campos = parsear_linha_csv(linha)
        print(f"{linha!r:45} -> {campos}")

    # sanity check
    assert parsear_linha_csv('"Silva, Maria",34,"Rio de Janeiro"') == ["Silva, Maria", "34", "Rio de Janeiro"]
    assert parsear_linha_csv('"Ela disse ""ola""",40,Curitiba') == ['Ela disse "ola"', "40", "Curitiba"]
    print("\nOK: sanity checks passaram.")
