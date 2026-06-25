"""
Conversao CSV para JSON e vice-versa

O que este script demonstra: transformar um CSV (linhas/colunas) em uma lista de
objetos JSON e o caminho inverso, preservando tipos basicos (numeros, texto).
Quando usar: ao integrar sistemas onde um lado consome JSON (ex: API REST) e o
outro produz/consome CSV (ex: planilhas, exports de BI).
"""

import csv
import io
import json


def csv_para_json(texto_csv: str) -> str:
    """Converte uma string CSV em uma string JSON (lista de objetos)."""
    leitor = csv.DictReader(io.StringIO(texto_csv))
    registros = []
    for linha in leitor:
        registro = {}
        for chave, valor in linha.items():
            registro[chave] = _converter_tipo(valor)
        registros.append(registro)
    return json.dumps(registros, ensure_ascii=False, indent=2)


def _converter_tipo(valor: str):
    """CSV so guarda texto; tenta inferir int/float para nao gerar JSON so com strings."""
    if valor is None or valor == "":
        return None
    try:
        return int(valor)
    except ValueError:
        pass
    try:
        return float(valor)
    except ValueError:
        pass
    return valor


def json_para_csv(texto_json: str) -> str:
    """Converte uma string JSON (lista de objetos planos) em uma string CSV."""
    registros = json.loads(texto_json)
    if not registros:
        return ""

    saida = io.StringIO()
    # usa a uniao das chaves de todos os registros para nao perder colunas esparsas
    colunas = []
    vistas = set()
    for registro in registros:
        for chave in registro:
            if chave not in vistas:
                vistas.add(chave)
                colunas.append(chave)

    writer = csv.DictWriter(saida, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(registros)
    return saida.getvalue()


if __name__ == "__main__":
    csv_exemplo = "id,nome,preco\n1,Mouse,49.90\n2,Teclado,120\n3,Cabo,\n"

    json_gerado = csv_para_json(csv_exemplo)
    print("CSV -> JSON:")
    print(json_gerado)

    csv_de_volta = json_para_csv(json_gerado)
    print("\nJSON -> CSV:")
    print(csv_de_volta)

    registros = json.loads(json_gerado)
    assert registros[0]["preco"] == 49.90
    assert registros[1]["preco"] == 120  # int, pois "120" nao tem ponto decimal
    assert registros[2]["preco"] is None  # campo vazio no CSV original

    linhas_de_volta = list(csv.DictReader(io.StringIO(csv_de_volta)))
    assert linhas_de_volta[0]["nome"] == "Mouse"
    print("OK: conversao CSV <-> JSON preservou estrutura e tipos.")
