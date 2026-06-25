"""
RotatingFileHandler para rotação de logs

O que este script demonstra: configurar um `RotatingFileHandler` com tamanho
máximo pequeno (maxBytes) para forçar, na prática, a criação de múltiplos
arquivos rotacionados (.log, .log.1, .log.2, ...) durante a própria execução.
Quando usar: serviços de longa duração que escrevem logs em arquivo e precisam
evitar que um único arquivo cresça indefinidamente e consuma todo o disco.
"""

import logging
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "_logs_exemplo"
# Começamos limpos para que a demonstração mostre claramente os arquivos gerados nesta execução.
if LOG_DIR.exists():
    shutil.rmtree(LOG_DIR)
LOG_DIR.mkdir()
LOG_FILE = LOG_DIR / "05_rotacao.log"

logger = logging.getLogger("app.rotacao_arquivos")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

# maxBytes bem pequeno (1 KB) e backupCount=3 são valores didáticos só para forçar
# rotação rapidamente nesta demo; em produção, valores típicos seriam MBs.
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024, backupCount=3, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
logger.addHandler(handler)


def gravar_muitas_linhas(quantidade: int) -> None:
    """Gera várias linhas de log para estourar o limite de tamanho e forçar rotação."""
    for i in range(quantidade):
        logger.info("Linha de log número %d - conteúdo de exemplo para ocupar espaço em disco", i)


def operacao_arriscada(indice: int) -> int:
    """Operação que falha propositalmente para indices negativos, logando o erro antes de propagar."""
    if indice < 0:
        try:
            raise IndexError(f"índice inválido para operação: {indice}")
        except IndexError:
            logger.exception("Erro durante operação arriscada (índice=%s)", indice)
            raise
    return indice * 2


if __name__ == "__main__":
    logger.info("Gerando volume de logs para forçar rotação de arquivos...")
    gravar_muitas_linhas(200)  # volume suficiente para estourar maxBytes=1024 várias vezes

    try:
        operacao_arriscada(-1)  # dispara IndexError propositalmente, já logado via logger.exception
    except IndexError:
        logger.warning("Operação arriscada falhou e foi tratada após o log do erro")

    arquivos_gerados = sorted(LOG_DIR.glob("05_rotacao.log*"))
    print(f"\nArquivos de log gerados pela rotação ({len(arquivos_gerados)}):")
    for arquivo in arquivos_gerados:
        print(f"  - {arquivo.name} ({arquivo.stat().st_size} bytes)")
