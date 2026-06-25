"""
Validação de resultado parcial em lote

O que este script demonstra: como processar uma coleção de itens tolerando
falhas individuais, registrando sucesso/erro de cada item e produzindo um
resumo final (parcialmente bem-sucedido) em vez de abortar o lote inteiro
na primeira falha.
Quando usar: importação/validação de dados em massa onde itens inválidos
isolados não devem impedir o processamento dos itens válidos.
"""

from dataclasses import dataclass, field


@dataclass
class ResumoLote:
    sucessos: list = field(default_factory=list)
    falhas: list = field(default_factory=list)

    @property
    def total(self):
        return len(self.sucessos) + len(self.falhas)

    @property
    def taxa_sucesso(self):
        return len(self.sucessos) / self.total if self.total else 0.0


def validar_registro(registro):
    """
    Valida um registro de cadastro simples. Lança ValueError para dados
    inválidos, simulando regras de negócio reais (campo obrigatório, tipo).
    """
    if "nome" not in registro or not registro["nome"].strip():
        raise ValueError("campo 'nome' é obrigatório")
    if "idade" not in registro:
        raise ValueError("campo 'idade' é obrigatório")
    if not isinstance(registro["idade"], int):
        raise ValueError(f"'idade' deve ser inteiro, recebido {type(registro['idade']).__name__}")
    if registro["idade"] < 0:
        raise ValueError("'idade' não pode ser negativa")
    return {"nome": registro["nome"].strip(), "idade": registro["idade"]}


def processar_lote(registros):
    """
    Processa cada registro individualmente; uma falha em um item não
    interrompe o processamento dos demais (isolamento de falhas por item).
    """
    resumo = ResumoLote()
    for indice, registro in enumerate(registros):
        try:
            validado = validar_registro(registro)
        except ValueError as exc:
            # Guardamos o índice e o motivo para permitir diagnóstico/correção
            # posterior, sem perder o restante do lote.
            resumo.falhas.append({"indice": indice, "registro": registro, "motivo": str(exc)})
        else:
            resumo.sucessos.append(validado)
    return resumo


if __name__ == "__main__":
    # Lote com registros válidos e inválidos de propósito, para forçar
    # falhas item a item (nome vazio, idade ausente, idade como string,
    # idade negativa) misturadas com registros válidos.
    lote = [
        {"nome": "Alice", "idade": 30},
        {"nome": "", "idade": 25},
        {"nome": "Bob", "idade": "vinte"},
        {"nome": "Carla"},
        {"nome": "Daniel", "idade": -5},
        {"nome": "Eduarda", "idade": 40},
    ]

    resumo = processar_lote(lote)

    print(f"total processado: {resumo.total}")
    print(f"sucessos: {len(resumo.sucessos)} | falhas: {len(resumo.falhas)}")
    print(f"taxa de sucesso: {resumo.taxa_sucesso:.0%}")

    print("\nregistros válidos:")
    for item in resumo.sucessos:
        print(f"  - {item}")

    print("\nregistros com falha:")
    for falha in resumo.falhas:
        print(f"  - índice {falha['indice']}: {falha['registro']} -> {falha['motivo']}")

    # Garante que o script comprova a tolerância a falhas: mesmo havendo
    # erros, o lote inteiro foi processado (nenhuma exceção sobe até aqui).
    assert resumo.total == len(lote)
    assert len(resumo.falhas) > 0
    print("\nlote concluído com sucesso parcial, conforme esperado.")
