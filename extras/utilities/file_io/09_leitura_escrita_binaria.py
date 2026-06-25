"""
Leitura e escrita de arquivos binarios

O que este script demonstra: manipulação de bytes crus com modos "rb"/"wb", uso do
módulo struct para empacotar/desempacotar dados binários estruturados.
Quando usar: ao lidar com formatos binários (imagens, arquivos proprietários, protocolos de rede).
"""

import struct
import tempfile
from pathlib import Path

def escrever_bytes(caminho: Path, dados: bytes):
    # "wb" escreve bytes crus, sem nenhuma codificação/decodificação de texto envolvida
    with open(caminho, mode="wb") as f:
        f.write(dados)

def ler_bytes(caminho: Path) -> bytes:
    with open(caminho, mode="rb") as f:
        return f.read()

def empacotar_registro(id_registro: int, valor: float, ativo: bool) -> bytes:
    # struct.pack converte valores Python em uma sequência fixa de bytes
    # ">" = big-endian, "I" = unsigned int (4 bytes), "f" = float (4 bytes), "?" = bool (1 byte)
    return struct.pack(">If?", id_registro, valor, ativo)

def desempacotar_registro(dados: bytes):
    return struct.unpack(">If?", dados)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        caminho = Path(tmp_dir) / "dados.bin"

        # escrita/leitura de bytes simples
        dados_originais = bytes([0x00, 0xFF, 0x10, 0x20, 0xAB])
        escrever_bytes(caminho, dados_originais)
        dados_lidos = ler_bytes(caminho)
        print("Bytes lidos:", dados_lidos)
        assert dados_lidos == dados_originais

        # empacotamento estruturado com struct (registro de tamanho fixo)
        registro = empacotar_registro(id_registro=42, valor=3.5, ativo=True)
        print("Registro empacotado (bytes):", registro, "- tamanho:", len(registro))
        assert len(registro) == struct.calcsize(">If?")

        caminho_registro = Path(tmp_dir) / "registro.bin"
        escrever_bytes(caminho_registro, registro)
        registro_lido = ler_bytes(caminho_registro)
        id_lido, valor_lido, ativo_lido = desempacotar_registro(registro_lido)
        print(f"Registro desempacotado: id={id_lido}, valor={valor_lido}, ativo={ativo_lido}")
        assert id_lido == 42
        assert abs(valor_lido - 3.5) < 1e-6
        assert ativo_lido is True

        # leitura parcial em chunks (util para arquivos binarios grandes)
        with open(caminho, "rb") as f:
            primeiro_chunk = f.read(2)
            segundo_chunk = f.read(2)
        print("Chunks lidos separadamente:", primeiro_chunk, segundo_chunk)
        assert primeiro_chunk == bytes([0x00, 0xFF])
        assert segundo_chunk == bytes([0x10, 0x20])

        print("Todos os testes de sanity check passaram.")
