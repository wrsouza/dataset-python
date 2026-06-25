"""
Validacao de Tipo de Arquivo (Extensao + Magic Bytes)

O que este script demonstra: validar o tipo real de um arquivo combinando a
checagem da extensao com a leitura dos primeiros bytes (assinatura/"magic
bytes"), para evitar confiar apenas no nome do arquivo.
Quando usar: validar uploads de usuario (ex.: aceitar so imagens) detectando
arquivos com extensao trocada ou forjada.
"""

import io

# assinaturas conhecidas (magic bytes) de alguns formatos comuns
ASSINATURAS = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"%PDF-": "pdf",
}

EXTENSOES_PERMITIDAS = {"jpg", "jpeg", "png", "gif", "pdf"}


def detectar_tipo_por_assinatura(conteudo: bytes) -> str:
    """Retorna o tipo detectado pelos magic bytes, ou 'desconhecido'."""
    for assinatura, tipo in ASSINATURAS.items():
        if conteudo.startswith(assinatura):
            return tipo
    return "desconhecido"


def validar_arquivo(nome_arquivo: str, conteudo: bytes) -> list:
    """Retorna lista de erros comparando extensao do nome com a assinatura real."""
    erros = []

    extensao = nome_arquivo.rsplit(".", 1)[-1].lower() if "." in nome_arquivo else ""
    if extensao not in EXTENSOES_PERMITIDAS:
        erros.append(f"Extensao '.{extensao}' nao permitida")

    tipo_real = detectar_tipo_por_assinatura(conteudo)
    if tipo_real == "desconhecido":
        erros.append("Assinatura de arquivo (magic bytes) nao reconhecida")
    elif extensao in ("jpg", "jpeg") and tipo_real != "jpg":
        erros.append(f"Extensao diz JPG mas conteudo e '{tipo_real}'")
    elif extensao not in ("jpg", "jpeg") and tipo_real != extensao:
        erros.append(f"Extensao diz '{extensao}' mas conteudo real e '{tipo_real}'")

    return erros


if __name__ == "__main__":
    # bytes reais de cabecalho de PNG (assinatura completa)
    conteudo_png_valido = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

    # arquivo .jpg "forjado": extensao diz jpg, mas o conteudo e na verdade PDF
    conteudo_pdf = b"%PDF-1.4\n" + b"\x00" * 20

    # extensao nao permitida
    conteudo_exe = b"MZ" + b"\x00" * 20

    casos = [
        ("foto.png", conteudo_png_valido),
        ("foto_forjada.jpg", conteudo_pdf),
        ("programa.exe", conteudo_exe),
    ]

    for nome, conteudo in casos:
        erros = validar_arquivo(nome, conteudo)
        status = "VALIDO" if not erros else f"INVALIDO: {erros}"
        print(f"{nome} -> {status}")

    assert validar_arquivo("foto.png", conteudo_png_valido) == []
    assert validar_arquivo("foto_forjada.jpg", conteudo_pdf) != []
    assert validar_arquivo("programa.exe", conteudo_exe) != []
    print("Sanity check OK.")
