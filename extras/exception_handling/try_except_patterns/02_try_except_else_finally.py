"""
Try/except com else e finally

O que este script demonstra: a diferença entre código que só deve rodar se NÃO houve
exceção (`else`) e código que deve rodar sempre, com ou sem erro (`finally`).
Quando usar: quando há uma etapa de "sucesso" que não deve ser confundida com o corpo
do `try` (para não mascarar exceções dela) e uma etapa de limpeza obrigatória.
"""


def processar_lista(indices: list, dados: list) -> list:
    """Acessa posições de `dados` pelos índices em `indices`, registrando o que ocorreu."""
    resultados = []
    for indice in indices:
        try:
            valor = dados[indice]
        except IndexError as exc:
            print(f"Índice {indice} inválido: {exc}")
        else:
            # `else` só executa se o `try` não lançou exceção.
            # Colocar `resultados.append` aqui (e não dentro do try) evita que um
            # eventual erro do próprio append seja confundido com erro de acesso à lista.
            resultados.append(valor)
            print(f"Índice {indice} processado com sucesso: {valor}")
        finally:
            # `finally` roda sempre, sucesso ou falha — útil para logging/contadores.
            print(f"-- fim da tentativa para índice {indice} --")
    return resultados


if __name__ == "__main__":
    dados = ["a", "b", "c"]
    indices = [0, 5, 2]  # índice 5 não existe, dispara IndexError propositalmente

    resultado = processar_lista(indices, dados)
    print(f"Resultados coletados: {resultado}")
