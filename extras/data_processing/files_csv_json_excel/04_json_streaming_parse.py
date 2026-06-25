"""
Parse incremental (streaming) de JSON grande sem bibliotecas externas

O que este script demonstra: usar json.JSONDecoder.raw_decode para extrair objetos
JSON um a um de um arquivo grande, sem carregar a estrutura completa em memoria
(simulando o que bibliotecas como ijson fazem, porem so com a stdlib).
Quando usar: quando o arquivo JSON e grande demais para um unico json.load(), mas
tem o formato de uma sequencia de objetos concatenados ou um array enorme.
"""

import json
import os
import tempfile


def gerar_jsonl_como_array_gigante(caminho: str, n_objetos: int = 5000) -> None:
    """
    Gera um arquivo contendo um JSON array gigante: [ {...}, {...}, ... ]
    Escrito objeto a objeto para nao precisar montar a lista inteira em memoria.
    """
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i in range(n_objetos):
            obj = {"id": i, "valor": i * 2}
            f.write(json.dumps(obj))
            if i < n_objetos - 1:
                f.write(",")
            f.write("\n")
        f.write("]\n")


def iterar_objetos_streaming(caminho: str, tamanho_buffer: int = 65536):
    """
    Le o arquivo em pedacos de texto e usa raw_decode para extrair um objeto
    completo por vez, mantendo no buffer apenas o restante nao decodificado.
    Isso evita ter o JSON inteiro como string na memoria de uma vez.
    """
    decoder = json.JSONDecoder()
    buffer = ""
    with open(caminho, "r", encoding="utf-8") as f:
        # pula o '[' inicial e espacos/quebras de linha
        while True:
            pedaco = f.read(tamanho_buffer)
            if not pedaco:
                break
            buffer += pedaco

            # consome o caractere de abertura do array, se ainda presente
            buffer = buffer.lstrip()
            if buffer.startswith("["):
                buffer = buffer[1:].lstrip()

            while True:
                buffer = buffer.lstrip(", \n\r\t")
                if not buffer or buffer.startswith("]"):
                    break
                try:
                    obj, idx = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    # objeto incompleto no buffer atual: busca mais dados do arquivo
                    break
                yield obj
                buffer = buffer[idx:]


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_json = os.path.join(tmp_dir, "grande.json")

    try:
        gerar_jsonl_como_array_gigante(caminho_json, n_objetos=5000)

        total = 0
        contagem = 0
        for obj in iterar_objetos_streaming(caminho_json):
            total += obj["valor"]
            contagem += 1

        print(f"Objetos processados em streaming: {contagem}")
        print(f"Soma dos valores: {total}")

        assert contagem == 5000, "Deveria processar todos os 5000 objetos"
        # soma de 0*2 + 1*2 + ... + 4999*2 = 2 * soma(0..4999)
        soma_esperada = 2 * sum(range(5000))
        assert total == soma_esperada, "Soma deveria bater com o calculo direto"
        print("OK: parse streaming de JSON funcionou corretamente.")
    finally:
        if os.path.exists(caminho_json):
            os.remove(caminho_json)
        os.rmdir(tmp_dir)
