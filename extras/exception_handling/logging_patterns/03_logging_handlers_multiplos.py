"""
Múltiplos handlers (console + arquivo)

O que este script demonstra: como anexar mais de um Handler ao mesmo logger,
cada um com seu próprio nível e formato — console mostra só INFO+, arquivo grava
tudo a partir de DEBUG.
Quando usar: quando se quer um nível de detalhe diferente para o operador (console)
e para auditoria/depuração posterior (arquivo).
"""

import logging
from pathlib import Path

# Os logs de exemplo ficam dentro da própria pasta do script, em um subdiretório
# próprio, para não poluir o restante do projeto.
LOG_DIR = Path(__file__).parent / "_logs_exemplo"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "03_handlers_multiplos.log"

logger = logging.getLogger("app.handlers_multiplos")
logger.setLevel(logging.DEBUG)  # o logger precisa permitir o nível mais baixo que algum handler usará

# Evita duplicar handlers se o módulo for importado/executado mais de uma vez no mesmo processo.
logger.handlers.clear()

formato_console = logging.Formatter("%(levelname)-8s | %(message)s")
formato_arquivo = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)

# Handler de console: só mostra o que realmente interessa ao operador em tempo real.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formato_console)

# Handler de arquivo: grava tudo, incluindo DEBUG, para investigação posterior.
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formato_arquivo)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def acessar_recurso(recurso_id: int, recursos_disponiveis: dict) -> str:
    """Busca um recurso por id, logando em granularidades diferentes."""
    logger.debug("Consultando recurso id=%s (detalhe só vai para o arquivo)", recurso_id)
    try:
        return recursos_disponiveis[recurso_id]
    except KeyError as exc:
        logger.error("Recurso id=%s não encontrado", recurso_id, exc_info=True)
        raise LookupError(f"Recurso {recurso_id} inexistente") from exc


if __name__ == "__main__":
    recursos = {1: "relatorio.pdf", 2: "planilha.xlsx"}

    logger.info("Console mostra apenas INFO e acima; arquivo grava tudo a partir de DEBUG")
    acessar_recurso(1, recursos)

    try:
        acessar_recurso(99, recursos)  # id inexistente, dispara o cenário de erro propositalmente
    except LookupError as e:
        logger.warning("Tratamento concluído após falha esperada: %s", e)

    print(f"\nVerifique o conteúdo completo (incluindo DEBUG) em: {LOG_FILE}")
