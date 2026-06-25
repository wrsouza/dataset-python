"""
Copia e movimentacao de arquivos com shutil

O que este script demonstra: shutil.copy, shutil.copytree e shutil.move, incluindo
tratamento de erros comuns (arquivo inexistente, destino já existente).
Quando usar: ao automatizar organização/backup de arquivos e diretórios.
"""

import shutil
import tempfile
from pathlib import Path

def copiar_arquivo(origem: Path, destino: Path):
    try:
        # shutil.copy preserva o conteúdo mas não todos os metadados (use copy2 para isso)
        caminho_resultante = shutil.copy(origem, destino)
        return caminho_resultante
    except FileNotFoundError as e:
        print(f"Erro: arquivo de origem nao encontrado: {e}")
        return None
    except shutil.SameFileError as e:
        print(f"Erro: origem e destino sao o mesmo arquivo: {e}")
        return None

def mover_arquivo(origem: Path, destino: Path):
    try:
        # move funciona tanto para renomear quanto para mover entre diretórios
        return shutil.move(str(origem), str(destino))
    except FileNotFoundError as e:
        print(f"Erro: nao foi possivel mover, origem nao existe: {e}")
        return None

def copiar_diretorio(origem: Path, destino: Path):
    try:
        # copytree exige que o destino NAO exista (a menos que dirs_exist_ok=True)
        return shutil.copytree(origem, destino, dirs_exist_ok=True)
    except FileNotFoundError as e:
        print(f"Erro: diretorio de origem nao encontrado: {e}")
        return None


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        pasta_origem = base / "origem"
        pasta_destino = base / "destino"
        pasta_origem.mkdir()
        pasta_destino.mkdir()

        arquivo_original = pasta_origem / "dados.txt"
        arquivo_original.write_text("dados importantes", encoding="utf-8")

        # copia simples de arquivo
        resultado = copiar_arquivo(arquivo_original, pasta_destino / "dados_copia.txt")
        assert resultado is not None
        assert (pasta_destino / "dados_copia.txt").read_text(encoding="utf-8") == "dados importantes"
        # original ainda deve existir após copiar
        assert arquivo_original.exists()
        print("Copia de arquivo OK.")

        # tentativa de copiar arquivo inexistente -> tratado sem crashar
        resultado_erro = copiar_arquivo(pasta_origem / "nao_existe.txt", pasta_destino)
        assert resultado_erro is None
        print("Tratamento de erro (arquivo inexistente) OK.")

        # mover arquivo (renomeando no processo)
        novo_caminho = mover_arquivo(arquivo_original, pasta_destino / "dados_movido.txt")
        assert novo_caminho is not None
        assert not arquivo_original.exists()  # original não existe mais após mover
        assert (pasta_destino / "dados_movido.txt").exists()
        print("Movimentacao de arquivo OK.")

        # copiar diretório inteiro recursivamente
        subpasta = pasta_origem / "subpasta"
        subpasta.mkdir()
        (subpasta / "extra.txt").write_text("arquivo extra", encoding="utf-8")
        copiar_diretorio(pasta_origem, pasta_destino / "origem_copiada")
        assert (pasta_destino / "origem_copiada" / "subpasta" / "extra.txt").exists()
        print("Copia recursiva de diretorio OK.")

        print("Todos os testes de sanity check passaram.")
