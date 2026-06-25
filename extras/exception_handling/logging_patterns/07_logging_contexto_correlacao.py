"""
ID de correlação/contexto via LoggerAdapter

O que este script demonstra: usar `logging.LoggerAdapter` para injetar
automaticamente um `correlation_id` em toda mensagem logada através dele,
sem precisar passar `extra=` manualmente em cada chamada.
Quando usar: rastrear todas as mensagens de uma mesma requisição/transação
através de múltiplas funções/módulos, sem propagar o id explicitamente em
cada log.
"""

import logging
import uuid

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | corr_id=%(correlation_id)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger_base = logging.getLogger("app.contexto_correlacao")


class CorrelationAdapter(logging.LoggerAdapter):
    """Adapter que injeta correlation_id em todo log feito através dele."""

    def process(self, msg, kwargs):
        # O LoggerAdapter mescla self.extra no kwargs["extra"] de cada chamada,
        # então o Formatter (que referencia %(correlation_id)s) sempre encontra o campo.
        kwargs.setdefault("extra", {})
        kwargs["extra"].update(self.extra)
        return msg, kwargs


def criar_logger_requisicao(correlation_id: str) -> CorrelationAdapter:
    """Fábrica de adapter: cada requisição/transação recebe seu próprio id de correlação."""
    return CorrelationAdapter(logger_base, {"correlation_id": correlation_id})


def buscar_usuario(log, usuario_id: int, banco_simulado: dict) -> str:
    """Busca um usuário simulado; propaga KeyError propositalmente se não existir."""
    log.debug("Buscando usuário id=%s no 'banco' simulado", usuario_id)
    try:
        return banco_simulado[usuario_id]
    except KeyError:
        log.error("Usuário id=%s não encontrado", usuario_id, exc_info=True)
        raise


def processar_requisicao(correlation_id: str, usuario_id: int, banco_simulado: dict) -> None:
    """Simula o processamento de uma requisição completa, todo log carrega o mesmo correlation_id."""
    log = criar_logger_requisicao(correlation_id)
    log.info("Requisição iniciada para usuario_id=%s", usuario_id)
    try:
        nome = buscar_usuario(log, usuario_id, banco_simulado)
        log.info("Usuário encontrado: %s", nome)
    except KeyError:
        log.warning("Requisição finalizada com erro tratado")


if __name__ == "__main__":
    banco = {1: "Maria", 2: "João"}

    # Cada chamada simula uma requisição independente, com seu próprio correlation_id,
    # permitindo distinguir os logs de uma chamada das de outra ao filtrar por corr_id.
    processar_requisicao(correlation_id=str(uuid.uuid4())[:8], usuario_id=1, banco_simulado=banco)

    # Esta segunda requisição dispara o cenário de erro propositalmente (usuario_id ausente).
    processar_requisicao(correlation_id=str(uuid.uuid4())[:8], usuario_id=999, banco_simulado=banco)

    logger_base.info("Observe que cada bloco de log tem um corr_id diferente e consistente entre si")
