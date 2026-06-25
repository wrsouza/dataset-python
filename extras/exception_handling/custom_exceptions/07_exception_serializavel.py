"""
Exception serializável (conversível para dict/JSON)

O que este script demonstra: uma exceção customizada com método `to_dict`
(e, por consequência, serializável via `json.dumps`), útil para logging
estruturado ou para enviar detalhes do erro em uma resposta de API.
Quando usar: quando o erro precisa atravessar uma fronteira que só entende
dados serializáveis (logs JSON, filas de mensagens, respostas HTTP).
"""

import json
import time


class ErroSerializavel(Exception):
    """Exceção que sabe se descrever como dict/JSON, preservando estrutura."""

    def __init__(self, mensagem: str, tipo_erro: str, detalhes: dict | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.tipo_erro = tipo_erro
        self.detalhes = detalhes or {}
        # Carimbamos o momento da criação da exceção; em sistemas reais isso
        # ajuda a correlacionar o erro com logs/traces de outros serviços.
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "tipo_erro": self.tipo_erro,
            "mensagem": self.mensagem,
            "detalhes": self.detalhes,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        # Reaproveita to_dict para não duplicar a lógica de montagem da estrutura.
        return json.dumps(self.to_dict(), ensure_ascii=False)


def processar_arquivo(caminho: str) -> str:
    if not caminho.endswith(".csv"):
        raise ErroSerializavel(
            mensagem="Formato de arquivo não suportado",
            tipo_erro="FORMATO_INVALIDO",
            detalhes={"caminho": caminho, "extensao_esperada": ".csv"},
        )
    return f"Arquivo {caminho} processado"


if __name__ == "__main__":
    try:
        # Disparamos o erro propositalmente com extensão incorreta.
        processar_arquivo("relatorio.txt")
    except ErroSerializavel as erro:
        # Em vez de só logar a mensagem, logamos a estrutura completa em JSON,
        # como faríamos em um sistema de logging estruturado real.
        print("Erro capturado, representação JSON para log estruturado:")
        print(erro.to_json())

    resultado = processar_arquivo("dados.csv")
    print(f"Sucesso: {resultado}")
