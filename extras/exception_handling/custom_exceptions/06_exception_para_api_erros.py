"""
Exceptions mapeadas para códigos de erro tipo HTTP (sem framework)

O que este script demonstra: como modelar exceções de domínio que carregam um
"status code" inspirado em HTTP, permitindo que uma camada de borda (ex: um
handler manual de requisições) traduza erros internos em respostas
padronizadas, sem depender de nenhum framework web.
Quando usar: ao construir uma API simples (ou simular uma) onde se quer
desacoplar a lógica de negócio do protocolo de transporte.
"""


class ApiError(Exception):
    """Base para erros que devem ser traduzidos em uma resposta de API."""

    status_code = 500  # valor padrão, sobrescrito pelas subclasses

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontradoError(ApiError):
    status_code = 404


class NaoAutorizadoError(ApiError):
    status_code = 401


class RequisicaoInvalidaError(ApiError):
    status_code = 400


def montar_resposta_erro(erro: ApiError) -> dict:
    # Função que simula a camada de borda: transforma a exceção em algo
    # que poderia ser serializado como resposta HTTP (status + corpo).
    return {"status": erro.status_code, "body": {"erro": erro.mensagem}}


def buscar_usuario(usuarios: dict, user_id: int) -> dict:
    if user_id <= 0:
        raise RequisicaoInvalidaError("ID de usuário deve ser positivo")
    if user_id not in usuarios:
        raise RecursoNaoEncontradoError(f"Usuário {user_id} não encontrado")
    return usuarios[user_id]


if __name__ == "__main__":
    base_usuarios = {1: {"nome": "Carlos"}, 2: {"nome": "Bea"}}

    for user_id_teste in (-1, 99, 1):
        try:
            # Disparamos cenários propositalmente: id inválido e id inexistente,
            # além de um caso de sucesso para contraste.
            usuario = buscar_usuario(base_usuarios, user_id_teste)
            print(f"200 OK -> {usuario}")
        except ApiError as erro:
            # Qualquer subclasse de ApiError sabe se "auto-traduzir" em resposta,
            # então o handler genérico não precisa de um if/elif por tipo.
            resposta = montar_resposta_erro(erro)
            print(f"{resposta['status']} -> {resposta['body']}")
