"""
Logging básico e níveis

O que este script demonstra: configuração mínima do módulo `logging` (basicConfig)
e o uso dos cinco níveis padrão (DEBUG, INFO, WARNING, ERROR, CRITICAL).
Quando usar: ponto de partida para qualquer script/serviço que precise registrar
eventos em vez de usar `print`.
"""

import logging

# basicConfig só tem efeito na primeira chamada por processo (a menos que force=True);
# por isso centralizamos a configuração aqui, no topo do módulo.
logging.basicConfig(
    level=logging.DEBUG,  # nível mínimo que será processado pelo logger raiz
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# Boa prática: usar um logger nomeado por módulo (__name__) em vez do logger raiz
# diretamente, para permitir granularidade de configuração por origem.
logger = logging.getLogger(__name__)


def dividir(a: float, b: float) -> float:
    """Divide dois números, logando cada etapa em um nível apropriado."""
    logger.debug("Iniciando divisão: a=%s, b=%s", a, b)  # detalhe técnico, só para depuração
    if b == 0:
        # WARNING: situação anômala mas que o chamador pode decidir tratar.
        logger.warning("Tentativa de divisão por zero detectada (a=%s)", a)
    try:
        resultado = a / b
    except ZeroDivisionError:
        # ERROR: a operação falhou de fato.
        logger.error("Falha ao dividir %s por %s", a, b)
        raise
    logger.info("Divisão concluída: resultado=%s", resultado)
    return resultado


if __name__ == "__main__":
    logger.info("=== Demonstração dos níveis de logging ===")

    logger.debug("Mensagem DEBUG: detalhes internos, normalmente desligados em produção")
    logger.info("Mensagem INFO: fluxo normal da aplicação")
    logger.warning("Mensagem WARNING: algo inesperado, mas não fatal")

    try:
        dividir(10, 0)  # dispara propositalmente ZeroDivisionError para exercitar logger.error
    except ZeroDivisionError:
        # CRITICAL: usado aqui só para ilustrar o nível mais alto, indicando que
        # o programa não pode continuar com segurança nesse ponto hipotético.
        logger.critical("Encerrando fluxo crítico após divisão inválida")

    logger.info("=== Fim da demonstração ===")
