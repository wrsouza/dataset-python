"""
Context manager simplificado com @contextmanager

O que este script demonstra: como usar `contextlib.contextmanager` para criar um
context manager a partir de uma função geradora, sem precisar escrever uma classe
com __enter__/__exit__.
Quando usar: quando a lógica de setup/teardown é simples e linear (um único recurso,
sem estado complexo), tornando a classe completa um exagero.
"""

from contextlib import contextmanager


@contextmanager
def arquivo_temporario_simulado(nome: str):
    """Simula abertura/fechamento de um arquivo, sem usar I/O real (apenas stdlib puro)."""
    print(f"[setup] Criando recurso simulado '{nome}'")
    estado = {"nome": nome, "fechado": False}
    try:
        # tudo antes do yield é o "__enter__"; o valor do yield é o `as` do with
        yield estado
    finally:
        # O finally garante que o teardown roda mesmo se o bloco `with` lançar exceção.
        # Usar try/finally (em vez de try/except) é o que faz o @contextmanager
        # propagar a exceção original para fora do `with`, igual ao __exit__ retornando False.
        estado["fechado"] = True
        print(f"[teardown] Liberando recurso simulado '{nome}'")


if __name__ == "__main__":
    print("--- Uso normal ---")
    with arquivo_temporario_simulado("dados.txt") as estado:
        print(f"Usando recurso: {estado}")

    print("\n--- Uso que dispara erro dentro do with ---")
    try:
        with arquivo_temporario_simulado("config.txt") as estado:
            # Acesso a chave inexistente dispara KeyError propositalmente.
            print(estado["chave_que_nao_existe"])
    except KeyError as exc:
        print(f"Erro capturado fora do with, teardown já executado: {exc}")
