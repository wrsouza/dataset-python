"""
Supressao de logs verbosos de bibliotecas terceiras

O que este script demonstra: como elevar o nivel de log de loggers de
bibliotecas externas (ex: urllib3, requests) sem afetar o logging da
aplicacao, usando logging.getLogger("nome.da.lib").setLevel(...).
Quando usar: quando uma dependencia poluiu o stdout/arquivo de log com
mensagens DEBUG/INFO irrelevantes para o diagnostico do seu proprio codigo.
"""

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Simula uma biblioteca terceira que loga muito em DEBUG.
biblioteca_externa = logging.getLogger("biblioteca_terceira.http")


def operacao_da_biblioteca_externa():
    biblioteca_externa.debug("conectando ao host (detalhe interno irrelevante)")
    biblioteca_externa.debug("enviando headers (detalhe interno irrelevante)")
    biblioteca_externa.info("conexao estabelecida")


app_logger = logging.getLogger("minha_app")


def processar():
    app_logger.info("iniciando processamento")
    operacao_da_biblioteca_externa()
    try:
        1 / 0
    except ZeroDivisionError:
        app_logger.exception("falha durante o processamento")
    app_logger.info("processamento finalizado")


if __name__ == "__main__":
    print("--- Antes da supressao (ruido da lib externa aparece) ---")
    processar()

    # Eleva o nivel apenas do logger da "biblioteca", silenciando DEBUG/INFO
    # dela, sem alterar o nivel global nem o do app_logger.
    logging.getLogger("biblioteca_terceira").setLevel(logging.WARNING)

    print("\n--- Depois da supressao (so WARNING+ da lib aparece) ---")
    processar()

    assert biblioteca_externa.getEffectiveLevel() == logging.WARNING
    print("\nOK: ruido da biblioteca terceira suprimido com sucesso.")
