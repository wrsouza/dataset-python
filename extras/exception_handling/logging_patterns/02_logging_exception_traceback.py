"""
logger.exception vs logger.error com traceback

O que este script demonstra: a diferença entre `logger.error(...)` (sem stack trace
por padrão) e `logger.exception(...)` / `logger.error(..., exc_info=True)` (que
anexam o traceback completo da exceção atual ao log).
Quando usar: dentro de blocos `except`, quando se quer preservar o traceback original
para diagnóstico, sem precisar montar a mensagem manualmente.
"""

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def carregar_config(chave: str, config: dict) -> str:
    """Busca uma chave de configuração, deixando a exceção se propagar se ausente."""
    return config[chave]  # KeyError propositalmente não tratado aqui


def processar_com_error_simples(config: dict) -> None:
    """Loga com logger.error SEM exc_info: não inclui traceback."""
    try:
        carregar_config("usuario", config)
    except KeyError as exc:
        # logger.error por si só não grava o traceback, apenas a mensagem;
        # quem ler o log perde a localização exata da falha.
        logger.error("Falha ao carregar configuração (sem traceback): %s", exc)


def processar_com_error_exc_info(config: dict) -> None:
    """Loga com logger.error mas passando exc_info=True: inclui traceback."""
    try:
        carregar_config("usuario", config)
    except KeyError:
        # exc_info=True instrui o logging a capturar sys.exc_info() automaticamente.
        logger.error("Falha ao carregar configuração (com exc_info=True)", exc_info=True)


def processar_com_exception(config: dict) -> None:
    """Loga com logger.exception: equivalente a error(..., exc_info=True), mas mais idiomático."""
    try:
        carregar_config("usuario", config)
    except KeyError:
        # logger.exception SÓ deve ser chamado dentro de um bloco except ativo,
        # pois depende do estado de exceção corrente (sys.exc_info()).
        logger.exception("Falha ao carregar configuração (via logger.exception)")


if __name__ == "__main__":
    config_incompleta = {"host": "localhost", "porta": 8080}  # sem a chave "usuario" de propósito

    logger.info("--- 1) logger.error sem traceback ---")
    processar_com_error_simples(config_incompleta)

    logger.info("--- 2) logger.error com exc_info=True ---")
    processar_com_error_exc_info(config_incompleta)

    logger.info("--- 3) logger.exception (forma idiomática) ---")
    processar_com_exception(config_incompleta)

    logger.info("Demonstração concluída: compare os 3 blocos de log acima")
