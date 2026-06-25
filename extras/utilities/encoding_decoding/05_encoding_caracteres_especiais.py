"""
Encoding de Caracteres Especiais (UTF-8 vs Latin-1)

O que este script demonstra: como strings Python (sempre Unicode internamente)
sao convertidas para bytes usando diferentes codecs (utf-8, latin-1), e os
erros comuns que surgem ao misturar codificacoes incompativeis.
Quando usar: ao ler/escrever arquivos ou receber dados de sistemas legados
que usam codificacoes diferentes de UTF-8, evitando o classico erro
UnicodeDecodeError ou caracteres corrompidos ("mojibake").
"""

import sys

# Garante saida em UTF-8 mesmo em terminais Windows configurados com cp1252,
# que nao conseguem imprimir diretamente certos bytes/caracteres decodificados
sys.stdout.reconfigure(encoding="utf-8")


def comparar_codecs(texto: str) -> None:
    # UTF-8 usa de 1 a 4 bytes por caractere; caracteres acentuados
    # ocupam 2 bytes, enquanto Latin-1 (ISO-8859-1) usa sempre 1 byte
    # por caractere, mas so cobre o conjunto Europeu Ocidental
    bytes_utf8 = texto.encode("utf-8")
    bytes_latin1 = texto.encode("latin-1")

    print(f"Texto original: {texto!r}")
    print(f"UTF-8   ({len(bytes_utf8)} bytes): {bytes_utf8}")
    print(f"Latin-1 ({len(bytes_latin1)} bytes): {bytes_latin1}")


def demonstrar_erro_decode_incorreto() -> None:
    texto = "café"
    bytes_utf8 = texto.encode("utf-8")

    # decodificar bytes UTF-8 como se fossem Latin-1 NAO gera erro,
    # mas produz "mojibake": cada byte multi-byte e lido como 2 chars errados
    decodificado_errado = bytes_utf8.decode("latin-1")
    print(f"\nBytes UTF-8 decodificados incorretamente como Latin-1: {decodificado_errado!r}")
    assert decodificado_errado != texto, "Deveria ter gerado mojibake, nao o texto original"


def demonstrar_unicode_decode_error() -> None:
    # bytes que nao formam uma sequencia UTF-8 valida geram UnicodeDecodeError
    bytes_invalidos = b"\xff\xfe\x00caf\xe9"
    try:
        bytes_invalidos.decode("utf-8")
        assert False, "Deveria ter lancado UnicodeDecodeError"
    except UnicodeDecodeError as erro:
        print(f"\nErro esperado ao decodificar bytes invalidos como UTF-8: {erro}")

    # usando errors="replace" o decode nao falha, substitui bytes invalidos por '?'/'�'
    resultado_seguro = bytes_invalidos.decode("utf-8", errors="replace")
    print(f"Decode com errors='replace': {resultado_seguro!r}")

    # usando errors="ignore" os bytes invalidos sao simplesmente descartados
    resultado_ignorado = bytes_invalidos.decode("utf-8", errors="ignore")
    print(f"Decode com errors='ignore':  {resultado_ignorado!r}")


if __name__ == "__main__":
    comparar_codecs("café com açúcar e pão")

    demonstrar_erro_decode_incorreto()
    demonstrar_unicode_decode_error()

    # sanity check: round-trip correto (mesma codificacao no encode e no decode)
    texto_original = "São Paulo - município"
    bytes_corretos = texto_original.encode("utf-8")
    texto_restaurado = bytes_corretos.decode("utf-8")
    assert texto_restaurado == texto_original, "Round-trip UTF-8 falhou"

    # round-trip com latin-1 tambem deve funcionar, desde que os
    # caracteres estejam dentro do conjunto suportado por latin-1
    bytes_latin1 = texto_original.encode("latin-1")
    texto_restaurado_latin1 = bytes_latin1.decode("latin-1")
    assert texto_restaurado_latin1 == texto_original, "Round-trip Latin-1 falhou"

    print("\nTodos os testes passaram com sucesso.")
