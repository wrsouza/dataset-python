"""
Encode/Decode Base64

O que este script demonstra: como converter dados binarios/texto em uma
representacao ASCII segura usando Base64, e como reverter essa conversao.
Quando usar: ao transmitir dados binarios (imagens, arquivos) em canais
que so aceitam texto, como JSON, XML, URLs ou cabecalhos HTTP.
"""

import base64
import sys

# Garante saida em UTF-8 mesmo em terminais Windows configurados com cp1252,
# que nao conseguem imprimir diretamente certos caracteres acentuados/emoji
sys.stdout.reconfigure(encoding="utf-8")


def encode_texto(texto: str) -> str:
    # Base64 trabalha sobre bytes, entao precisamos primeiro
    # converter a string para bytes usando uma codificacao definida (utf-8)
    dados_bytes = texto.encode("utf-8")
    dados_codificados = base64.b64encode(dados_bytes)
    # b64encode retorna bytes; decode("ascii") devolve uma str legivel
    return dados_codificados.decode("ascii")


def decode_texto(texto_base64: str) -> str:
    dados_bytes = base64.b64decode(texto_base64)
    return dados_bytes.decode("utf-8")


def encode_url_safe(texto: str) -> str:
    # variante "urlsafe" troca '+' e '/' por '-' e '_', evitando
    # problemas ao colocar o resultado dentro de uma URL
    return base64.urlsafe_b64encode(texto.encode("utf-8")).decode("ascii")


if __name__ == "__main__":
    mensagem_original = "Python e ótimo para automação!"

    codificado = encode_texto(mensagem_original)
    print(f"Original:    {mensagem_original}")
    print(f"Codificado:  {codificado}")

    decodificado = decode_texto(codificado)
    print(f"Decodificado: {decodificado}")

    # sanity check: o ciclo encode -> decode deve ser perfeitamente reversivel
    assert decodificado == mensagem_original, "Falha no round-trip Base64"

    # exemplo de variante url-safe, util para tokens em querystrings
    url_safe = encode_url_safe("dados/com+caracteres especiais")
    print(f"URL-safe:    {url_safe}")

    print("\nTodos os testes passaram com sucesso.")
