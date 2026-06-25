"""
Parsing de linhas de log com regex nomeado (named groups)

O que este script demonstra: como usar grupos nomeados (?P<nome>...) para
extrair campos estruturados (timestamp, nivel, mensagem) de linhas de log em texto livre.
Quando usar: ao processar arquivos de log que nao tem um parser dedicado (ex: logs customizados de app).
"""

import re

# Formato esperado: "2026-06-25 14:32:10 [INFO] Mensagem qualquer aqui"
LOG_REGEX = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<nivel>\w+)\]\s+"
    r"(?P<mensagem>.+)$"
)


def parsear_linha(linha: str) -> dict | None:
    """Retorna um dict com os campos extraidos, ou None se a linha nao casar."""
    m = LOG_REGEX.match(linha.strip())
    if not m:
        return None
    # groupdict() ja devolve um dict pronto, usando os nomes definidos na regex
    return m.groupdict()


def parsear_logs(linhas: list[str]) -> list[dict]:
    """Parseia uma lista de linhas, ignorando silenciosamente as que nao casam."""
    resultados = []
    for linha in linhas:
        registro = parsear_linha(linha)
        if registro is not None:
            resultados.append(registro)
        # linhas invalidas (ex: linha em branco, stacktrace continuado) sao ignoradas
    return resultados


if __name__ == "__main__":
    log_bruto = [
        "2026-06-25 14:32:10 [INFO] Servidor iniciado na porta 8080",
        "2026-06-25 14:32:15 [WARNING] Conexao lenta detectada",
        "2026-06-25 14:33:01 [ERROR] Falha ao conectar no banco de dados",
        "",  # linha vazia, deve ser ignorada
        "    continuacao de stacktrace sem timestamp",  # nao casa, ignorada
    ]

    registros = parsear_logs(log_bruto)

    for registro in registros:
        print(f"{registro['timestamp']} | {registro['nivel']:8} | {registro['mensagem']}")

    # sanity check
    assert len(registros) == 3
    assert registros[2]["nivel"] == "ERROR"
    assert registros[0]["mensagem"] == "Servidor iniciado na porta 8080"
    print("\nOK: sanity checks passaram.")
