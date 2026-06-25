"""
Validar precondições vs deixar a exceção estourar (LBYL vs EAFP)

O que este script demonstra: a diferença entre "Look Before You Leap" (validar antes
de agir) e "Easier to Ask Forgiveness than Permission" (agir e tratar a exceção se
ocorrer), com um exemplo de cada um aplicado ao mesmo problema.
Quando usar: prefira validar antes (LBYL) quando o erro é esperado/comum e a validação
é barata e sem condição de corrida; prefira deixar estourar (EAFP) quando o erro é
raro/excepcional ou quando validar exigiria duplicar o trabalho que a operação já faz.
"""


def dividir_lbyl(a: float, b: float) -> float:
    """Estilo LBYL: valida a precondição (b != 0) antes de operar."""
    # Aqui a validação é barata (uma comparação) e a condição é comum o suficiente
    # para justificar checar antes, evitando o custo de lançar/capturar exceção.
    if b == 0:
        raise ValueError("divisor não pode ser zero (validado antes da operação)")
    return a / b


def obter_item_eafp(dados: dict, chave: str) -> int:
    """Estilo EAFP: tenta acessar direto e trata a exceção se a chave não existir."""
    # Validar com "if chave in dados" antes faria o dict ser percorrido/hashado duas
    # vezes (uma para checar, outra para acessar). Para o caso comum (chave existe),
    # deixar a exceção estourar só no caso raro é mais eficiente e mais "pythonico".
    try:
        return dados[chave]
    except KeyError as exc:
        raise KeyError(f"chave {chave!r} não encontrada (tratada via exceção)") from exc


if __name__ == "__main__":
    print("--- LBYL: validação prévia dispara ValueError controlado ---")
    try:
        dividir_lbyl(10, 0)
    except ValueError as exc:
        print(f"Erro esperado e validado antes: {exc}")

    print("\n--- EAFP: deixa a exceção estourar e trata depois ---")
    dados = {"x": 1, "y": 2}
    try:
        obter_item_eafp(dados, "z")  # "z" não existe, dispara KeyError propositalmente
    except KeyError as exc:
        print(f"Erro esperado e tratado via except: {exc}")
