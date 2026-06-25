"""
Logging estruturado em formato JSON

O que este script demonstra: um Formatter customizado que serializa cada
LogRecord como uma linha JSON (incluindo traceback quando houver exceção),
em vez de texto livre — facilitando ingestão por ferramentas de log (ELK,
CloudWatch, etc.) sem depender de regex para parsing.
Quando usar: serviços que enviam logs para um agregador/observabilidade que
espera registros estruturados (um objeto JSON por linha).
"""

import json
import logging
import traceback
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Serializa o LogRecord como uma única linha JSON."""

    # Campos padrão do LogRecord que NÃO queremos repetir dentro de "extra",
    # pois já são representados explicitamente no dicionário base abaixo.
    _CAMPOS_PADRAO = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())

    def format(self, record: logging.LogRecord) -> str:
        registro = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),  # já aplica a interpolação de %s/%d etc.
            "module": record.module,
            "line": record.lineno,
        }

        # Qualquer atributo extra passado via extra={} aparece em record.__dict__
        # e não está em _CAMPOS_PADRAO; incluímos esses campos dinamicamente.
        for chave, valor in record.__dict__.items():
            if chave not in self._CAMPOS_PADRAO and chave not in registro:
                registro[chave] = valor

        if record.exc_info:
            # exc_info é a tupla (tipo, valor, traceback); formatamos como lista de linhas
            # para manter o JSON válido em uma única linha (sem quebras de linha cruas).
            registro["exception"] = "".join(traceback.format_exception(*record.exc_info)).splitlines()

        return json.dumps(registro, ensure_ascii=False)


logger = logging.getLogger("app.json_estruturado")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)


def validar_idade(idade: int) -> None:
    """Valida idade, levantando ValueError propositalmente para valores fora do intervalo."""
    if not 0 <= idade <= 130:
        raise ValueError(f"idade fora do intervalo permitido: {idade}")


if __name__ == "__main__":
    logger.info("Log estruturado simples", extra={"usuario_id": 42, "acao": "login"})

    try:
        validar_idade(999)  # dispara ValueError propositalmente
    except ValueError:
        logger.error(
            "Falha de validação capturada e registrada em JSON",
            extra={"usuario_id": 42, "campo": "idade", "valor_recebido": 999},
            exc_info=True,
        )

    logger.info("Cada linha acima é um objeto JSON independente, pronto para parsing automatizado")
