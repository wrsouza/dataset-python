"""
Validacao de URL

O que este script demonstra: validar formato basico de URLs usando
urllib.parse, checando esquema, host e estrutura geral sem usar regex
complexo nem libs externas.
Quando usar: validar URLs informadas pelo usuario (links, webhooks, redirects)
antes de armazenar ou fazer requisicoes.
"""

from urllib.parse import urlparse

ESQUEMAS_PERMITIDOS = {"http", "https"}


def validar_url(url: str, exigir_https=False) -> list:
    """Retorna lista de erros (vazia se a URL for valida)."""
    erros = []

    if not isinstance(url, str) or not url.strip():
        return ["URL vazia ou nao e string"]

    resultado = urlparse(url)

    # scheme e netloc sao os indicadores mais confiaveis de uma URL bem formada;
    # path sozinho (ex.: "/home") nao e considerado URL absoluta aqui.
    if not resultado.scheme:
        erros.append("URL sem esquema (ex.: 'https://')")
    elif resultado.scheme not in ESQUEMAS_PERMITIDOS:
        erros.append(f"Esquema '{resultado.scheme}' nao permitido (use {ESQUEMAS_PERMITIDOS})")

    if not resultado.netloc:
        erros.append("URL sem host (netloc vazio)")
    elif "." not in resultado.netloc and resultado.netloc != "localhost":
        # heuristica simples: host deve ter um dominio com ponto, exceto localhost
        erros.append(f"Host '{resultado.netloc}' parece invalido (sem dominio)")

    if exigir_https and resultado.scheme != "https":
        erros.append("HTTPS e obrigatorio para esta operacao")

    return erros


if __name__ == "__main__":
    urls_teste = [
        "https://www.exemplo.com/pagina?busca=python",
        "http://localhost:8000/api",
        "ftp://servidor.com/arquivo",  # esquema nao permitido
        "exemplo.com/sem-esquema",      # sem scheme
        "https://",                     # sem host
    ]

    for url in urls_teste:
        erros = validar_url(url)
        status = "VALIDA" if not erros else f"INVALIDA: {erros}"
        print(f"{url!r} -> {status}")

    assert validar_url("https://www.exemplo.com") == []
    assert validar_url("ftp://servidor.com/arquivo") != []
    assert validar_url("exemplo.com/sem-esquema") != []
    assert validar_url("http://exemplo.com", exigir_https=True) != []
    print("Sanity check OK.")
