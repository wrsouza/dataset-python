"""
Conversoes entre snake_case, camelCase e PascalCase

O que este script demonstra: como converter identificadores entre as convencoes
de nomenclatura mais comuns (snake_case, camelCase, PascalCase) usando regex e str.
Quando usar: ao integrar APIs/dados que usam convencoes de nomenclatura diferentes
(ex: JSON em camelCase consumido por codigo Python em snake_case).
"""

import re

# Detecta limites de palavra em camelCase/PascalCase: uma minuscula seguida de
# maiuscula, ou uma sequencia de maiusculas seguida de minuscula (ex: "HTTPServer" -> "HTTP", "Server")
LIMITE_CAMEL_REGEX = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def snake_para_camel(texto: str) -> str:
    """Converte snake_case para camelCase (primeira palavra minuscula, demais capitalizadas)."""
    partes = texto.split("_")
    primeira, *resto = partes
    # capitalize() so na primeira letra; o resto da palavra fica como veio
    return primeira + "".join(p.capitalize() for p in resto)


def snake_para_pascal(texto: str) -> str:
    """Converte snake_case para PascalCase (todas as palavras capitalizadas)."""
    return "".join(p.capitalize() for p in texto.split("_"))


def camel_para_snake(texto: str) -> str:
    """Converte camelCase ou PascalCase para snake_case usando os limites de palavra detectados."""
    # insere "_" exatamente nos limites encontrados, depois tudo para minusculo
    partes = LIMITE_CAMEL_REGEX.split(texto)
    return "_".join(p.lower() for p in partes)


if __name__ == "__main__":
    casos_snake = ["nome_do_usuario", "valor_total_pedido", "id"]
    casos_camel = ["nomeDoUsuario", "valorTotalPedido", "httpServerError", "id"]

    print("snake -> camel:")
    for caso in casos_snake:
        print(f"  {caso:25} -> {snake_para_camel(caso)}")

    print("\nsnake -> Pascal:")
    for caso in casos_snake:
        print(f"  {caso:25} -> {snake_para_pascal(caso)}")

    print("\ncamel/Pascal -> snake:")
    for caso in casos_camel:
        print(f"  {caso:25} -> {camel_para_snake(caso)}")

    # sanity check
    assert snake_para_camel("nome_do_usuario") == "nomeDoUsuario"
    assert snake_para_pascal("nome_do_usuario") == "NomeDoUsuario"
    assert camel_para_snake("nomeDoUsuario") == "nome_do_usuario"
    assert camel_para_snake("httpServerError") == "http_server_error"
    print("\nOK: sanity checks passaram.")
