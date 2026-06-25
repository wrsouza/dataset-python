"""
Validacao de Tipos com Dataclass

O que este script demonstra: usar dataclasses para modelar uma entidade e
validar manualmente os tipos dos campos no metodo __post_init__.
Quando usar: quando se quer um modelo de dados tipado com validacao basica,
sem depender de pydantic ou outra lib externa.
"""

from dataclasses import dataclass, fields


@dataclass
class Produto:
    nome: str
    preco: float
    quantidade: int

    def __post_init__(self):
        # __post_init__ roda automaticamente apos a criacao do objeto,
        # entao e o lugar natural para validar os campos sem reescrever
        # a logica de construcao do dataclass.
        erros = []
        for campo in fields(self):
            valor = getattr(self, campo.name)
            tipo_esperado = campo.type
            # dataclass guarda o tipo como string em alguns contextos;
            # aqui comparamos com os tipos reais ja importados no escopo.
            tipo_real = {"str": str, "float": float, "int": int}.get(tipo_esperado, tipo_esperado)
            if isinstance(tipo_real, type) and not isinstance(valor, tipo_real):
                erros.append(f"{campo.name}: esperado {tipo_esperado}, recebido {type(valor).__name__}")

        # so compara preco/quantidade se o tipo ja estiver correto, evitando
        # TypeError ao comparar string com int (ex.: "caro" < 0)
        if isinstance(self.preco, (int, float)) and self.preco < 0:
            erros.append("preco: nao pode ser negativo")
        if isinstance(self.quantidade, (int, float)) and self.quantidade < 0:
            erros.append("quantidade: nao pode ser negativa")

        if erros:
            raise ValueError("Produto invalido: " + "; ".join(erros))


def criar_produto_seguro(nome, preco, quantidade):
    """Tenta criar um Produto e retorna (produto, erro)."""
    try:
        return Produto(nome=nome, preco=preco, quantidade=quantidade), None
    except (ValueError, TypeError) as exc:
        return None, str(exc)


if __name__ == "__main__":
    produto_ok, erro_ok = criar_produto_seguro("Caderno", 12.5, 100)
    produto_falho, erro_falho = criar_produto_seguro("Caneta", -3.0, 50)
    produto_tipo_errado, erro_tipo = criar_produto_seguro("Lapis", "caro", 10)

    print("Produto valido:", produto_ok, "| erro:", erro_ok)
    print("Produto com preco negativo -> erro:", erro_falho)
    print("Produto com tipo errado -> erro:", erro_tipo)

    assert produto_ok is not None and erro_ok is None
    assert produto_falho is None and "negativo" in erro_falho
    assert produto_tipo_errado is None and "preco" in erro_tipo
    print("Sanity check OK.")
