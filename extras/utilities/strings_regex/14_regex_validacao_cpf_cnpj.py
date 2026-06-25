"""
Validacao de CPF/CNPJ (formato + digito verificador)

O que este script demonstra: como usar regex para validar o FORMATO de CPF/CNPJ
e, em seguida, aplicar o algoritmo de digito verificador (modulo 11) para confirmar validade real.
Quando usar: validacao de documentos brasileiros em formularios, antes de qualquer chamada a API externa.
"""

import re

CPF_REGEX = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
CNPJ_REGEX = re.compile(r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$")


def _somente_digitos(documento: str) -> str:
    return re.sub(r"\D", "", documento)


def _calcular_digito(sequencia: list[int], pesos: list[int]) -> int:
    """Calcula um digito verificador pelo algoritmo padrao modulo 11 usado em CPF/CNPJ."""
    soma = sum(d * p for d, p in zip(sequencia, pesos))
    resto = soma % 11
    # regra do modulo 11: resto < 2 -> digito 0; senao digito = 11 - resto
    return 0 if resto < 2 else 11 - resto


def validar_cpf(cpf: str) -> bool:
    """Valida formato com regex e depois confere os 2 digitos verificadores do CPF."""
    if not CPF_REGEX.match(cpf.strip()):
        return False

    digitos = _somente_digitos(cpf)
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        # sequencias repetidas (ex: 111.111.111-11) passam no formato mas sao invalidas
        return False

    numeros = [int(d) for d in digitos]

    primeiro_dv = _calcular_digito(numeros[:9], list(range(10, 1, -1)))
    segundo_dv = _calcular_digito(numeros[:9] + [primeiro_dv], list(range(11, 1, -1)))

    return numeros[9] == primeiro_dv and numeros[10] == segundo_dv


def validar_cnpj(cnpj: str) -> bool:
    """Valida formato com regex e depois confere os 2 digitos verificadores do CNPJ."""
    if not CNPJ_REGEX.match(cnpj.strip()):
        return False

    digitos = _somente_digitos(cnpj)
    if len(digitos) != 14 or digitos == digitos[0] * 14:
        return False

    numeros = [int(d) for d in digitos]

    # pesos especificos do CNPJ (nao sao sequenciais como no CPF)
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    primeiro_dv = _calcular_digito(numeros[:12], pesos_1)
    segundo_dv = _calcular_digito(numeros[:12] + [primeiro_dv], pesos_2)

    return numeros[12] == primeiro_dv and numeros[13] == segundo_dv


if __name__ == "__main__":
    cpfs_teste = ["529.982.247-25", "111.111.111-11", "000.000.000-00", "123.456.789-00"]
    cnpjs_teste = ["11.222.333/0001-81", "00.000.000/0000-00", "11.444.777/0001-61"]

    print("Validacao de CPF:")
    for cpf in cpfs_teste:
        print(f"  {cpf:20} -> {'valido' if validar_cpf(cpf) else 'invalido'}")

    print("\nValidacao de CNPJ:")
    for cnpj in cnpjs_teste:
        print(f"  {cnpj:20} -> {'valido' if validar_cnpj(cnpj) else 'invalido'}")

    # sanity check (529.982.247-25 e um CPF de teste matematicamente valido e bem conhecido)
    assert validar_cpf("529.982.247-25") is True
    assert validar_cpf("111.111.111-11") is False
    assert validar_cnpj("11.222.333/0001-81") is True
    print("\nOK: sanity checks passaram.")
