"""
Validacao de Dados Duplicados

O que este script demonstra: detectar registros duplicados em uma lista de
dicts em memoria, tanto duplicatas exatas quanto duplicatas baseadas em uma
chave especifica (ex.: mesmo email com nomes diferentes).
Quando usar: validar uma lista de registros (ex.: importacao de planilha)
antes de inserir no banco, encontrando duplicatas que quebrariam unicidade.
"""

from collections import Counter


def encontrar_duplicatas_exatas(registros: list) -> list:
    """Encontra registros (dicts) que aparecem mais de uma vez, identicos."""
    # dicts nao sao hashable, entao convertemos para tuplas ordenadas de itens
    # para poder contar ocorrencias com Counter.
    chaves = [tuple(sorted(r.items())) for r in registros]
    contagem = Counter(chaves)
    duplicados = [chave for chave, qtd in contagem.items() if qtd > 1]
    return [dict(chave) for chave in duplicados]


def encontrar_duplicatas_por_campo(registros: list, campo: str) -> dict:
    """Agrupa indices de registros que compartilham o mesmo valor em 'campo'.

    Retorna {valor_do_campo: [indices]} apenas para valores com mais de 1 ocorrencia.
    """
    grupos = {}
    for i, registro in enumerate(registros):
        valor = registro.get(campo)
        grupos.setdefault(valor, []).append(i)

    return {valor: indices for valor, indices in grupos.items() if len(indices) > 1}


if __name__ == "__main__":
    clientes = [
        {"id": 1, "nome": "Ana", "email": "ana@exemplo.com"},
        {"id": 2, "nome": "Bruno", "email": "bruno@exemplo.com"},
        {"id": 3, "nome": "Ana", "email": "ana@exemplo.com"},   # duplicata exata do id=1 (sem contar id)
        {"id": 4, "nome": "Ana Maria", "email": "bruno@exemplo.com"},  # email duplicado, nome diferente
    ]

    # comparacao exata ignorando o id (que e sempre unico por natureza)
    sem_id = [{"nome": c["nome"], "email": c["email"]} for c in clientes]
    duplicatas_exatas = encontrar_duplicatas_exatas(sem_id)

    duplicatas_por_email = encontrar_duplicatas_por_campo(clientes, "email")

    print("Duplicatas exatas (nome+email):", duplicatas_exatas)
    print("Duplicatas por email:")
    for email, indices in duplicatas_por_email.items():
        registros = [clientes[i]["nome"] for i in indices]
        print(f"  {email}: registros {indices} -> nomes {registros}")

    assert {"nome": "Ana", "email": "ana@exemplo.com"} in duplicatas_exatas
    assert "bruno@exemplo.com" in duplicatas_por_email
    assert duplicatas_por_email["bruno@exemplo.com"] == [1, 3]
    print("Sanity check OK.")
