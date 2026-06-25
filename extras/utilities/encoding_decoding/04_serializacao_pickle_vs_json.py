"""
Serializacao: Pickle vs JSON

O que este script demonstra: como serializar/desserializar objetos Python
com pickle (formato binario, especifico do Python) e com json (formato
texto, interoperavel), destacando as diferencas de capacidade e seguranca.
Quando usar: use JSON para troca de dados entre sistemas/linguagens
diferentes ou APIs web; use pickle apenas para persistir objetos Python
complexos internamente, em ambiente confiavel (nunca desserialize pickle
de fontes nao confiaveis, pois pode executar codigo arbitrario).
"""

import json
import pickle
from datetime import datetime


def serializar_json(dados: dict) -> str:
    # JSON so suporta tipos basicos: dict, list, str, int, float, bool, None
    # objetos como datetime precisam ser convertidos manualmente (default=str)
    return json.dumps(dados, default=str, ensure_ascii=False, indent=2)


def desserializar_json(texto_json: str) -> dict:
    return json.loads(texto_json)


def serializar_pickle(objeto) -> bytes:
    # pickle suporta praticamente qualquer objeto Python (incluindo
    # instancias de classes customizadas, datetime nativo, sets, etc.)
    return pickle.dumps(objeto)


def desserializar_pickle(dados_bytes: bytes):
    return pickle.loads(dados_bytes)


if __name__ == "__main__":
    registro = {
        "usuario": "maria",
        "ativo": True,
        "tags": {"admin", "beta_tester"},  # set: NAO suportado nativamente em JSON
        "criado_em": datetime(2024, 1, 15, 10, 30),  # datetime: NAO suportado em JSON
        "pontuacao": 98.5,
    }

    print("=== JSON ===")
    # para JSON, precisamos adaptar o set (vira list) antes de serializar,
    # pois json.dumps com default=str so chama default para tipos NAO serializaveis
    registro_compativel_json = dict(registro)
    registro_compativel_json["tags"] = sorted(registro["tags"])
    json_texto = serializar_json(registro_compativel_json)
    print(json_texto)

    registro_json_volta = desserializar_json(json_texto)
    # nota: datetime virou string apos o round-trip — JSON nao preserva o tipo original
    assert isinstance(registro_json_volta["criado_em"], str)
    print(f"Tipo de 'criado_em' apos JSON: {type(registro_json_volta['criado_em'])}")

    print("\n=== Pickle ===")
    pickle_bytes = serializar_pickle(registro)
    print(f"Tamanho em bytes: {len(pickle_bytes)} (formato binario, ilegivel como texto)")

    registro_pickle_volta = desserializar_pickle(pickle_bytes)
    # pickle preserva os tipos originais perfeitamente: set continua set, datetime continua datetime
    assert isinstance(registro_pickle_volta["tags"], set)
    assert isinstance(registro_pickle_volta["criado_em"], datetime)
    assert registro_pickle_volta == registro, "Pickle nao preservou os dados originais"

    print(f"Tipo de 'tags' apos Pickle: {type(registro_pickle_volta['tags'])}")
    print(f"Tipo de 'criado_em' apos Pickle: {type(registro_pickle_volta['criado_em'])}")

    print("\nResumo: JSON e legivel/interoperavel mas perde tipos complexos.")
    print("Pickle preserva tipos Python fielmente mas e binario e especifico do Python.")
    print("\nTodos os testes passaram com sucesso.")
