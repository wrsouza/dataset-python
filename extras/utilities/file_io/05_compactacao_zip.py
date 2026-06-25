"""
Compactacao e extracao de arquivos ZIP

O que este script demonstra: como criar um arquivo .zip a partir de vários arquivos
usando zipfile, listar seu conteúdo e extraí-lo novamente.
Quando usar: para empacotar/desempacotar conjuntos de arquivos (backups, distribuição, uploads).
"""

import tempfile
import zipfile
from pathlib import Path

def criar_zip(arquivos, caminho_zip):
    # ZIP_DEFLATED aplica compressão real (o padrão ZIP_STORED apenas empacota sem compactar)
    with zipfile.ZipFile(caminho_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for caminho_arquivo in arquivos:
            # arcname define o nome dentro do zip, evitando vazar o caminho absoluto do disco
            zf.write(caminho_arquivo, arcname=caminho_arquivo.name)
    return caminho_zip

def listar_conteudo_zip(caminho_zip):
    with zipfile.ZipFile(caminho_zip, mode="r") as zf:
        return zf.namelist()

def extrair_zip(caminho_zip, destino):
    with zipfile.ZipFile(caminho_zip, mode="r") as zf:
        # testzip() retorna None se nenhum membro estiver corrompido
        nome_corrompido = zf.testzip()
        if nome_corrompido is not None:
            raise ValueError(f"Arquivo corrompido dentro do zip: {nome_corrompido}")
        zf.extractall(destino)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        pasta_arquivos = base / "arquivos"
        pasta_arquivos.mkdir()

        arquivo1 = pasta_arquivos / "a.txt"
        arquivo2 = pasta_arquivos / "b.txt"
        arquivo1.write_text("conteudo do arquivo A", encoding="utf-8")
        arquivo2.write_text("conteudo do arquivo B" * 100, encoding="utf-8")  # maior, para ver compressão

        caminho_zip = base / "pacote.zip"
        criar_zip([arquivo1, arquivo2], caminho_zip)
        print("Zip criado em:", caminho_zip, "- tamanho:", caminho_zip.stat().st_size, "bytes")
        assert caminho_zip.exists()

        conteudo = listar_conteudo_zip(caminho_zip)
        print("Conteudo do zip:", conteudo)
        assert set(conteudo) == {"a.txt", "b.txt"}

        pasta_extraida = base / "extraido"
        extrair_zip(caminho_zip, pasta_extraida)
        assert (pasta_extraida / "a.txt").read_text(encoding="utf-8") == "conteudo do arquivo A"
        assert (pasta_extraida / "b.txt").read_text(encoding="utf-8") == "conteudo do arquivo B" * 100
        print("Extracao verificada com sucesso.")

        print("Todos os testes de sanity check passaram.")
