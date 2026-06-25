"""
Exception com contexto extra (código e payload)

O que este script demonstra: uma exceção customizada que carrega atributos
adicionais (código de erro e payload) além da mensagem, úteis para logging,
telemetria ou decisões automatizadas no handler.
Quando usar: quando o chamador precisa de dados estruturados sobre o erro,
não apenas uma string descritiva.
"""


class RequisicaoInvalidaError(Exception):
    """Erro com metadados extras: código de erro e payload que causou a falha."""

    def __init__(self, mensagem: str, codigo: str, payload: dict):
        # Chamamos o __init__ da base para manter compatibilidade com
        # str(exc) e repr(exc) tradicionais.
        super().__init__(mensagem)
        self.codigo = codigo
        self.payload = payload

    def __str__(self) -> str:
        # Customizamos a representação textual para já incluir o código,
        # facilitando a leitura em logs sem precisar acessar atributos.
        return f"[{self.codigo}] {super().__str__()} | payload={self.payload}"


def validar_pedido(pedido: dict) -> None:
    if "item" not in pedido or not pedido["item"]:
        raise RequisicaoInvalidaError(
            mensagem="Campo 'item' é obrigatório",
            codigo="PEDIDO_SEM_ITEM",
            payload=pedido,
        )
    if pedido.get("quantidade", 0) <= 0:
        raise RequisicaoInvalidaError(
            mensagem="Quantidade deve ser maior que zero",
            codigo="QUANTIDADE_INVALIDA",
            payload=pedido,
        )


if __name__ == "__main__":
    pedido_invalido = {"item": "", "quantidade": 2}

    try:
        # Disparamos o erro propositalmente com um pedido sem item.
        validar_pedido(pedido_invalido)
    except RequisicaoInvalidaError as erro:
        # Aqui aproveitamos os atributos extras para uma decisão programática,
        # algo que não seria possível só com a mensagem de texto.
        print(f"Erro capturado: {erro}")
        print(f"Código estruturado: {erro.codigo}")
        print(f"Payload original para reprocessamento/log: {erro.payload}")

    pedido_valido = {"item": "Teclado", "quantidade": 1}
    validar_pedido(pedido_valido)
    print("Pedido válido processado com sucesso.")
