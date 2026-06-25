"""
URL Encoding com urllib.parse

O que este script demonstra: como escapar (quote) e desescapar (unquote)
caracteres especiais para que possam ser usados com seguranca em URLs,
incluindo a codificacao de parametros de query string completos.
Quando usar: ao montar URLs manualmente com valores dinamicos (parametros
de busca, nomes de arquivos, emails) que podem conter espacos ou simbolos.
"""

from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode


def codificar_parametro(valor: str) -> str:
    # quote() escapa caracteres reservados de URL (espaco -> %20, etc.)
    # mas mantem '/' intacto por padrao (util em paths)
    return quote(valor)


def codificar_query_string(valor: str) -> str:
    # quote_plus() e o formato esperado em query strings (espaco -> '+'),
    # que e o padrao usado por formularios HTML application/x-www-form-urlencoded
    return quote_plus(valor)


if __name__ == "__main__":
    texto = "café com leite & açúcar/canela"

    codificado_path = codificar_parametro(texto)
    print(f"Original:        {texto}")
    print(f"Quote (path):    {codificado_path}")

    decodificado = unquote(codificado_path)
    assert decodificado == texto, "Falha no round-trip quote/unquote"

    codificado_query = codificar_query_string(texto)
    print(f"Quote_plus(query): {codificado_query}")

    decodificado_query = unquote_plus(codificado_query)
    assert decodificado_query == texto, "Falha no round-trip quote_plus/unquote_plus"

    # urlencode monta uma query string completa a partir de um dict,
    # cuidando da codificacao de cada chave/valor automaticamente
    params = {"busca": "café & bolo", "pagina": 2}
    query_string = urlencode(params)
    print(f"Query string completa: ?{query_string}")

    url_final = f"https://exemplo.com/produtos?{query_string}"
    print(f"URL final: {url_final}")

    print("\nTodos os testes passaram com sucesso.")
