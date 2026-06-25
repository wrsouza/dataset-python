"""
Formatter customizado com contexto extra

O que este script demonstra: criar uma subclasse de `logging.Formatter` que injeta
campos extras (ex.: ambiente, versão) em toda mensagem, e usar `extra=` para
acrescentar dados específicos de um log individual (ex.: id da requisição).
Quando usar: quando se quer padronizar metadados de contexto (app, ambiente, versão)
sem repetir esses dados manualmente em cada chamada de log.
"""

import logging


class FormatterComContexto(logging.Formatter):
    """Formatter que adiciona campos fixos de contexto (não vêm do LogRecord por padrão)."""

    def __init__(self, ambiente: str, versao: str, fmt: str) -> None:
        super().__init__(fmt)
        self._ambiente = ambiente
        self._versao = versao

    def format(self, record: logging.LogRecord) -> str:
        # Anexamos os atributos customizados ao record ANTES de chamar o format() base,
        # pois o format() usa esses atributos para substituir os placeholders do fmt.
        record.ambiente = self._ambiente
        record.versao = self._versao
        # request_id é opcional: só existe quando o chamador passa extra={"request_id": ...}.
        # getattr com default evita AttributeError quando a chamada de log não fornece o campo.
        record.request_id = getattr(record, "request_id", "N/A")
        return super().format(record)


logger = logging.getLogger("app.formatacao_customizada")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(
    FormatterComContexto(
        ambiente="homologacao",
        versao="1.4.2",
        fmt="%(asctime)s | %(levelname)-8s | env=%(ambiente)s ver=%(versao)s req=%(request_id)s | %(message)s",
    )
)
logger.addHandler(handler)


def processar_pedido(pedido_id: int, request_id: str) -> None:
    """Processa um pedido fictício; falha propositalmente para pedido_id negativo."""
    # extra= injeta atributos no LogRecord que o Formatter customizado consome acima.
    logger.info("Iniciando processamento do pedido %s", pedido_id, extra={"request_id": request_id})
    if pedido_id < 0:
        # ValueError disparado propositalmente para exercitar o log de erro com contexto.
        raise ValueError(f"pedido_id inválido: {pedido_id}")
    logger.info("Pedido %s processado com sucesso", pedido_id, extra={"request_id": request_id})


if __name__ == "__main__":
    logger.debug("Log sem extra explícito: request_id usa o valor padrão 'N/A'")

    processar_pedido(101, request_id="req-abc-001")

    try:
        processar_pedido(-5, request_id="req-abc-002")  # dispara ValueError propositalmente
    except ValueError as exc:
        logger.error(
            "Falha ao processar pedido: %s",
            exc,
            extra={"request_id": "req-abc-002"},
            exc_info=True,
        )

    logger.info("Demonstração de formatter customizado concluída", extra={"request_id": "req-abc-003"})
