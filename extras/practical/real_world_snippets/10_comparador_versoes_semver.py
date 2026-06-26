"""
Comparador de versoes estilo SemVer

Cenario: decidir se uma dependencia instalada satisfaz um requisito
minimo de versao, ou ordenar releases de um pacote (ex.: checar se a
versao do CLI do usuario é >= versao minima exigida por uma feature).
O que este script demonstra: parsing de strings "MAJOR.MINOR.PATCH" para
tuplas comparaveis e funcoes de comparacao/ordenacao sem libs externas.
"""

from typing import Tuple


def parse_versao(versao: str) -> Tuple[int, int, int]:
    """Converte '1.4.2' em (1, 4, 2) para permitir comparacao numerica correta.

    Comparar strings diretamente falha em casos como '1.10.0' < '1.2.0'
    (pois '1' > '0' lexicograficamente na 3a posicao do segundo numero,
    "10" vem antes de "2" como string) -- por isso convertemos para tupla
    de inteiros antes de comparar.
    """
    partes = versao.strip().split(".")
    if len(partes) != 3:
        raise ValueError(f"versao invalida (esperado MAJOR.MINOR.PATCH): {versao!r}")
    try:
        major, minor, patch = (int(parte) for parte in partes)
    except ValueError as erro:
        raise ValueError(f"versao invalida, partes devem ser numericas: {versao!r}") from erro
    return major, minor, patch


def comparar_versoes(versao_a: str, versao_b: str) -> int:
    """Retorna -1 se a < b, 0 se iguais, 1 se a > b (convencao tipo strcmp)."""
    tupla_a = parse_versao(versao_a)
    tupla_b = parse_versao(versao_b)
    if tupla_a < tupla_b:
        return -1
    if tupla_a > tupla_b:
        return 1
    return 0


def versao_satisfaz_minima(versao_atual: str, versao_minima: str) -> bool:
    return comparar_versoes(versao_atual, versao_minima) >= 0


if __name__ == "__main__":
    versoes_instaladas = ["1.2.0", "1.10.0", "2.0.1", "1.9.9"]

    print("Ordenando versoes corretamente (numerico, nao lexicografico):")
    ordenadas = sorted(versoes_instaladas, key=parse_versao)
    print(" ", ordenadas)

    versao_minima_exigida = "1.10.0"
    print(f"\nChecando quais versoes satisfazem >= {versao_minima_exigida}:")
    for versao in versoes_instaladas:
        ok = versao_satisfaz_minima(versao, versao_minima_exigida)
        print(f"  {versao}: {'OK' if ok else 'insuficiente'}")

    # Caso classico que comparacao de string pura erraria:
    assert comparar_versoes("1.2.0", "1.10.0") == -1
    print("\nVerificado: '1.2.0' < '1.10.0' numericamente (string compararia errado).")
