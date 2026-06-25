"""
string.Template para templates de texto

O que este script demonstra: como usar string.Template (mais seguro e simples que
f-strings quando o template vem de fonte externa, ex: arquivo ou input de usuario) para
substituir placeholders $nome em um texto.
Quando usar: ao gerar texto a partir de templates definidos por usuarios finais (nao desenvolvedores),
onde nao se quer expor a sintaxe completa de f-strings/eval.
"""

from string import Template


def renderizar_email(template_texto: str, dados: dict) -> str:
    """Substitui os placeholders $variavel pelos valores do dict de dados."""
    template = Template(template_texto)
    # substitute() lanca KeyError se faltar alguma variavel - sinal de bug no template
    return template.substitute(dados)


def renderizar_seguro(template_texto: str, dados: dict) -> str:
    """Versao tolerante a variaveis faltantes, usando safe_substitute."""
    # safe_substitute mantem o placeholder original ($var) se a chave nao existir,
    # em vez de lancar excecao - util quando os dados podem ser incompletos.
    template = Template(template_texto)
    return template.safe_substitute(dados)


if __name__ == "__main__":
    template_completo = "Ola $nome, seu pedido #$pedido foi enviado para $cidade."
    template_incompleto = "Ola $nome, seu codigo de rastreio e $rastreio."

    dados_cliente = {"nome": "Maria", "pedido": "4521", "cidade": "Sao Paulo"}
    dados_parciais = {"nome": "Joao"}  # falta 'rastreio' de proposito

    print(renderizar_email(template_completo, dados_cliente))
    print(renderizar_seguro(template_incompleto, dados_parciais))

    # sanity check
    assert renderizar_email(template_completo, dados_cliente) == (
        "Ola Maria, seu pedido #4521 foi enviado para Sao Paulo."
    )
    assert "$rastreio" in renderizar_seguro(template_incompleto, dados_parciais)
    print("\nOK: sanity checks passaram.")
