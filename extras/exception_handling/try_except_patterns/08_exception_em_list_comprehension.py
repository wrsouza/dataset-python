"""
Lidando com exceções dentro de list comprehensions

O que este script demonstra: list comprehensions não suportam try/except diretamente
no seu corpo, então mostramos o padrão alternativo de extrair a conversão para uma
função auxiliar que captura o erro e retorna um valor sentinela (ou None) a ser
filtrado depois.
Quando usar: quando se quer manter a expressividade de uma comprehension mas alguns
itens podem falhar na conversão/transformação, sem abortar a expressão inteira.
"""


def converter_ou_none(valor: str):
    """Função auxiliar: encapsula o try/except que a comprehension não pode conter."""
    try:
        return int(valor)
    except ValueError:
        # Retornar None (em vez de propagar) é o que permite usar isso dentro
        # de uma comprehension sem interromper a iteração nos demais itens.
        return None


if __name__ == "__main__":
    valores = ["1", "2", "x", "4", "", "6"]  # "x" e "" disparam ValueError na conversão

    # Comprehension não pode ter try/except embutido; por isso delegamos para a função.
    convertidos_com_none = [converter_ou_none(v) for v in valores]
    print(f"Resultado bruto (com None nos inválidos): {convertidos_com_none}")

    # Padrão alternativo: filtrar os None na mesma comprehension (dupla expressão).
    apenas_validos = [n for n in (converter_ou_none(v) for v in valores) if n is not None]
    print(f"Apenas valores convertidos com sucesso: {apenas_validos}")

    # Prova de que, sem a função auxiliar, a conversão direta dispararia ValueError
    # e abortaria a comprehension inteira — por isso o padrão acima é necessário.
    try:
        [int(v) for v in valores]
    except ValueError as exc:
        print(f"Comprehension direta (sem tratamento) falha como esperado: {exc}")
