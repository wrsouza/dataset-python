"""
Context manager customizado com __enter__/__exit__

O que este script demonstra: como implementar uma classe que garante limpeza de
recursos (ex.: fechar algo) mesmo quando uma exceção ocorre dentro do bloco `with`.
Quando usar: quando se precisa de um recurso "RAII" customizado (conexão, lock,
arquivo temporário) e a lógica de abertura/fechamento é mais complexa que um simples
arquivo, justificando uma classe própria em vez de `@contextmanager`.
"""


class RecursoControlado:
    """Simula um recurso (ex.: conexão) que precisa ser liberado sempre."""

    def __init__(self, nome: str):
        self.nome = nome
        self.aberto = False

    def __enter__(self):
        print(f"Abrindo recurso '{self.nome}'...")
        self.aberto = True
        return self  # o que for retornado aqui vira o `as recurso` do with

    def __exit__(self, exc_type, exc_value, traceback):
        # __exit__ é chamado mesmo se o bloco `with` lançar exceção.
        print(f"Fechando recurso '{self.nome}' (aberto={self.aberto})...")
        self.aberto = False
        # Retornar False (ou None) propaga a exceção para fora do `with`;
        # retornar True a suprimiria — aqui escolhemos NÃO suprimir, só limpar.
        return False

    def usar(self, divisor: int) -> float:
        if not self.aberto:
            raise RuntimeError("Recurso não está aberto")
        return 100 / divisor  # pode disparar ZeroDivisionError


if __name__ == "__main__":
    print("--- Uso normal ---")
    with RecursoControlado("conexao-1") as recurso:
        print(recurso.usar(5))

    print("\n--- Uso que dispara erro dentro do with ---")
    try:
        with RecursoControlado("conexao-2") as recurso:
            # divisor 0 dispara ZeroDivisionError propositalmente;
            # mesmo assim o __exit__ deve imprimir a mensagem de fechamento.
            print(recurso.usar(0))
    except ZeroDivisionError as exc:
        print(f"Erro capturado fora do with, após limpeza garantida: {exc}")
