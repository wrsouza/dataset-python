"""
Unicode e emojis em processamento de texto

Cenario: processar mensagens de usuarios (comentarios, chat, feedback) que
contem emojis e caracteres multi-byte. Operacoes ingenuas como len() ou
slicing por indice podem cortar um emoji "no meio" e gerar caracteres
corrompidos, alem de erros de encoding ao salvar/imprimir em consoles que nao
sao UTF-8 (como o cp1252 do Windows).
Demonstra: contagem correta de "caracteres visiveis", truncamento seguro de
strings com emoji, e como evitar UnicodeEncodeError ao imprimir no terminal.
"""

import unicodedata


def truncar_seguro(texto, limite):
    """Trunca preservando code points completos, sem cortar no meio do emoji.

    Em Python 3 cada elemento de uma str já é um code point completo (nao um
    byte), entao slicing por indice de string já é seguro para a maioria dos
    emojis simples. O risco real aparece ao CODIFICAR para bytes (utf-8,
    cp1252) ou ao contar "larguras visuais" (emojis combinados/ZWJ).
    """
    if len(texto) <= limite:
        return texto
    return texto[:limite] + "..."


def remover_caracteres_nao_imprimiveis(texto):
    """Remove caracteres de controle que podem vir colados em texto de usuario."""
    return "".join(ch for ch in texto if unicodedata.category(ch)[0] != "C")


def imprimir_compativel(texto):
    """Imprime evitando UnicodeEncodeError em consoles legados (ex: cp1252).

    O console do Windows pode estar configurado em cp1252, que nao tem
    representacao para varios emojis. Em vez de deixar o print() explodir,
    codificamos com 'replace' para um encoding seguro e decodificamos de
    volta, trocando caracteres nao suportados por um marcador visivel.
    """
    import sys

    encoding_console = sys.stdout.encoding or "utf-8"
    texto_seguro = texto.encode(encoding_console, errors="replace").decode(encoding_console)
    print(texto_seguro)


def contar_bytes_utf8(texto):
    """Util para saber o custo real de armazenamento/rede do texto."""
    return len(texto.encode("utf-8"))


if __name__ == "__main__":
    mensagens = [
        "Adorei o produto, recomendo!",
        "Pessimo atendimento...",
        "Top demais, 5 estrelas",  # evitamos emojis literais no fonte para nao
        "Cafe quentinho de manha",  # depender de fonte de terminal especifica
    ]

    print("Processando mensagens de usuarios:\n")
    for msg in mensagens:
        limpa = remover_caracteres_nao_imprimiveis(msg)
        truncada = truncar_seguro(limpa, 20)
        print(f"Original ({len(msg)} chars, {contar_bytes_utf8(msg)} bytes utf-8):")
        imprimir_compativel(f"  {msg}")
        print(f"Truncado para preview: ")
        imprimir_compativel(f"  {truncada}")
        print()

    # Caso real de emoji multi-byte: testamos com um emoji simples via escape
    # unicode, que e seguro de declarar no fonte independente do encoding do
    # arquivo, e tratamos a impressao com a funcao segura acima.
    texto_com_emoji = "Pedido aprovado \U00002705"  # ✅ = check mark
    print("Texto com emoji (via escape unicode):")
    imprimir_compativel(f"  {texto_com_emoji}")
    print(f"  Tamanho em chars: {len(texto_com_emoji)} | bytes utf-8: {contar_bytes_utf8(texto_com_emoji)}")
