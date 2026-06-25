"""
Try/except dentro de um loop, item a item

O que este script demonstra: como colocar o try/except DENTRO do loop (e não em volta
dele) para que um item com erro não interrompa o processamento dos demais.
Quando usar: em processamento em lote (ex.: importação de linhas de um arquivo) onde
um item inválido deve ser registrado/pulado, mas não deve abortar o lote inteiro.
"""


def processar_linhas(linhas: list) -> tuple:
    """Converte cada linha em inteiro, separando sucessos de falhas."""
    sucesso = []
    falhas = []

    for indice, linha in enumerate(linhas):
        try:
            # Cada iteração tem seu próprio try: um erro aqui não aborta as próximas.
            numero = int(linha)
        except ValueError as exc:
            # Guardamos o erro em vez de só "passar", para podermos reportar no final.
            falhas.append((indice, linha, str(exc)))
            continue  # pula para o próximo item do loop
        sucesso.append(numero)

    return sucesso, falhas


if __name__ == "__main__":
    linhas = ["10", "20", "abc", "30", "", "40"]  # "abc" e "" disparam ValueError

    sucesso, falhas = processar_linhas(linhas)

    print(f"Processados com sucesso: {sucesso}")
    print(f"Falhas encontradas ({len(falhas)}):")
    for indice, linha, motivo in falhas:
        print(f"  linha {indice} ({linha!r}): {motivo}")

    # O loop terminou normalmente mesmo com erros no meio — é o ponto central do padrão.
    assert sucesso == [10, 20, 30, 40], "loop deveria ter continuado após os erros"
    print("Loop concluído sem interrupção, apesar dos erros.")
