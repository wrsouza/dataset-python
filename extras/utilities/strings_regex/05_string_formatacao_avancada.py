"""
F-strings, format e alinhamento/padding

O que este script demonstra: recursos de formatacao de strings (f-strings,
str.format, alinhamento, padding, precisao numerica) para gerar saidas tabulares legiveis.
Quando usar: ao montar relatorios de texto, tabelas em console ou logs formatados sem libs externas.
"""


def formatar_tabela(dados: list[tuple[str, float, int]]) -> str:
    """Monta uma tabela alinhada usando especificadores de formatacao."""
    linhas = []
    # cabecalho: < esquerda, > direita, ^ centralizado; numeros fixam largura de coluna
    linhas.append(f"{'Produto':<15}{'Preco':>10}{'Qtd':^8}")
    linhas.append("-" * 33)

    for nome, preco, qtd in dados:
        # :.2f arredonda para 2 casas decimais; >10 alinha a direita em 10 colunas
        linhas.append(f"{nome:<15}{preco:>10.2f}{qtd:^8}")

    return "\n".join(linhas)


def exemplos_padding() -> list[str]:
    """Demonstra padding com zeros, alinhamento e formatos numericos diversos."""
    exemplos = [
        f"{42:05d}",          # zero-padding: 00042
        f"{3.14159:+.2f}",    # forca sinal: +3.14
        f"{255:#x}",          # hexadecimal com prefixo: 0xff
        f"{0.4567:.1%}",      # percentual: 45.7%
        f"{1234567:,}",       # separador de milhar: 1,234,567
        "{:*^20}".format("titulo"),  # centralizado com * de preenchimento (str.format)
    ]
    return exemplos


if __name__ == "__main__":
    produtos = [
        ("Teclado", 199.9, 3),
        ("Mouse", 59.5, 10),
        ("Monitor 24pol", 899.99, 1),
    ]

    print(formatar_tabela(produtos))
    print()

    for exemplo in exemplos_padding():
        print(exemplo)

    # sanity check
    assert f"{42:05d}" == "00042"
    assert "0xff" == f"{255:#x}"
    print("\nOK: sanity checks passaram.")
