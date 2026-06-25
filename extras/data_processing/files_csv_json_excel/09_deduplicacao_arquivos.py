"""
Deteccao e remocao de linhas duplicadas entre arquivos CSV

O que este script demonstra: identificar registros duplicados tanto dentro de um
unico CSV quanto duplicados entre dois arquivos diferentes, usando uma chave composta.
Quando usar: ao consolidar exports periodicos (ex: snapshots diarios) onde o mesmo
registro pode aparecer mais de uma vez e so a versao mais recente/unica deve ficar.
"""

import csv
import io


def ler_csv_como_dicts(texto_csv: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(texto_csv)))


def chave_registro(registro: dict, colunas_chave: list[str]) -> tuple:
    return tuple(registro[c] for c in colunas_chave)


def remover_duplicados_internos(registros: list[dict], colunas_chave: list[str]) -> list[dict]:
    """Mantem a primeira ocorrencia de cada chave; descarta as repeticoes seguintes."""
    vistos = set()
    resultado = []
    for registro in registros:
        chave = chave_registro(registro, colunas_chave)
        if chave not in vistos:
            vistos.add(chave)
            resultado.append(registro)
    return resultado


def diff_entre_arquivos(
    registros_a: list[dict], registros_b: list[dict], colunas_chave: list[str]
) -> dict:
    """
    Compara dois conjuntos de registros e retorna o que e exclusivo de cada lado
    e o que esta duplicado em ambos (mesma chave presente nos dois arquivos).
    """
    chaves_a = {chave_registro(r, colunas_chave) for r in registros_a}
    chaves_b = {chave_registro(r, colunas_chave) for r in registros_b}

    return {
        "somente_em_a": chaves_a - chaves_b,
        "somente_em_b": chaves_b - chaves_a,
        "em_ambos": chaves_a & chaves_b,
    }


if __name__ == "__main__":
    csv_a = (
        "id,nome\n"
        "1,Ana\n"
        "2,Bruno\n"
        "2,Bruno\n"  # duplicado interno
        "3,Carla\n"
    )

    csv_b = (
        "id,nome\n"
        "2,Bruno\n"  # presente tambem no arquivo A
        "4,Diego\n"
    )

    registros_a = ler_csv_como_dicts(csv_a)
    registros_b = ler_csv_como_dicts(csv_b)

    colunas_chave = ["id"]

    registros_a_sem_dup = remover_duplicados_internos(registros_a, colunas_chave)
    print(f"Registros A antes: {len(registros_a)}, depois de dedup: {len(registros_a_sem_dup)}")

    diff = diff_entre_arquivos(registros_a_sem_dup, registros_b, colunas_chave)
    print("Diff entre arquivos:", diff)

    assert len(registros_a_sem_dup) == 3, "Deveria remover o duplicado interno (id=2)"
    assert diff["em_ambos"] == {("2",)}
    assert diff["somente_em_a"] == {("1",), ("3",)}
    assert diff["somente_em_b"] == {("4",)}
    print("OK: deduplicacao interna e comparacao entre arquivos corretas.")
