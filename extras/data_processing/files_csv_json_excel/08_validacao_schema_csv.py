"""
Validacao de schema de um CSV antes de processar

O que este script demonstra: verificar se um CSV possui as colunas esperadas e se os
valores respeitam os tipos/regras definidos, coletando erros antes de processar os dados.
Quando usar: como uma etapa de "gate" antes de ETL/ingestao, para falhar rapido e com
mensagens claras quando o arquivo de entrada esta fora do formato esperado.
"""

import csv
import io
from dataclasses import dataclass, field


@dataclass
class RegraColuna:
    nome: str
    tipo: type  # int, float ou str
    obrigatoria: bool = True


@dataclass
class ResultadoValidacao:
    valido: bool
    erros: list[str] = field(default_factory=list)


SCHEMA_ESPERADO = [
    RegraColuna("id", int),
    RegraColuna("nome", str),
    RegraColuna("idade", int),
    RegraColuna("email", str, obrigatoria=False),
]


def validar_csv(texto_csv: str, schema: list[RegraColuna]) -> ResultadoValidacao:
    erros: list[str] = []
    leitor = csv.DictReader(io.StringIO(texto_csv))

    colunas_presentes = set(leitor.fieldnames or [])
    colunas_esperadas = {regra.nome for regra in schema}

    faltantes = colunas_esperadas - colunas_presentes
    if faltantes:
        erros.append(f"Colunas faltantes: {sorted(faltantes)}")

    extras = colunas_presentes - colunas_esperadas
    if extras:
        erros.append(f"Colunas inesperadas (ignoradas no processamento): {sorted(extras)}")

    # se faltam colunas obrigatorias nao ha como validar linha a linha de forma confiavel
    if any(r.nome not in colunas_presentes and r.obrigatoria for r in schema):
        return ResultadoValidacao(valido=False, erros=erros)

    for num_linha, linha in enumerate(leitor, start=2):  # linha 1 e o cabecalho
        for regra in schema:
            valor = linha.get(regra.nome)
            if valor is None or valor == "":
                if regra.obrigatoria:
                    erros.append(f"Linha {num_linha}: campo obrigatorio '{regra.nome}' vazio")
                continue
            if regra.tipo in (int, float):
                try:
                    regra.tipo(valor)
                except ValueError:
                    erros.append(
                        f"Linha {num_linha}: campo '{regra.nome}' deveria ser "
                        f"{regra.tipo.__name__}, recebeu {valor!r}"
                    )

    return ResultadoValidacao(valido=len(erros) == 0, erros=erros)


if __name__ == "__main__":
    csv_valido = (
        "id,nome,idade,email\n"
        "1,Ana,30,ana@exemplo.com\n"
        "2,Bruno,25,\n"
    )

    csv_invalido = (
        "id,nome,idade\n"  # falta a coluna 'email' (mas ela e opcional, ok)
        "1,Ana,trinta\n"  # idade nao e int
        ",Bruno,25\n"  # id vazio (obrigatorio)
    )

    resultado_valido = validar_csv(csv_valido, SCHEMA_ESPERADO)
    print("Resultado CSV valido:", resultado_valido)

    resultado_invalido = validar_csv(csv_invalido, SCHEMA_ESPERADO)
    print("Resultado CSV invalido:", resultado_invalido)

    assert resultado_valido.valido is True
    assert resultado_invalido.valido is False
    assert any("idade" in erro for erro in resultado_invalido.erros)
    assert any("id" in erro for erro in resultado_invalido.erros)
    print("OK: validacao de schema detectou corretamente o CSV invalido.")
