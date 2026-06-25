"""
Organizador de arquivos por extensao

O que este script demonstra: como percorrer um diretório e mover cada arquivo para uma
subpasta correspondente à sua extensão (ex.: .txt -> pasta "txt", .jpg -> pasta "jpg").
Quando usar: para organizar automaticamente pastas com arquivos desorganizados (ex.: Downloads).
"""

import shutil
import tempfile
from pathlib import Path

def organizar_por_extensao(diretorio: Path, pasta_sem_extensao="sem_extensao"):
    movidos = {}  # mapa extensao -> lista de nomes movidos, util para relatorio/log

    # lista primeiro, pois vamos modificar o diretório durante a iteração
    arquivos = [p for p in diretorio.iterdir() if p.is_file()]

    for arquivo in arquivos:
        # suffix inclui o ponto (".txt"); removemos para nome de pasta mais limpo
        extensao = arquivo.suffix.lower().lstrip(".")
        nome_pasta = extensao if extensao else pasta_sem_extensao

        pasta_destino = diretorio / nome_pasta
        pasta_destino.mkdir(exist_ok=True)

        destino_final = pasta_destino / arquivo.name
        shutil.move(str(arquivo), str(destino_final))

        movidos.setdefault(nome_pasta, []).append(arquivo.name)

    return movidos


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        diretorio = Path(tmp_dir)

        # cria uma bagunça de arquivos com extensões variadas, incluindo um sem extensão
        nomes_exemplo = [
            "foto1.jpg", "foto2.jpg", "documento.pdf",
            "notas.txt", "script.py", "LICENCA",
        ]
        for nome in nomes_exemplo:
            (diretorio / nome).write_text("conteudo de exemplo", encoding="utf-8")

        print("Arquivos antes de organizar:", sorted(p.name for p in diretorio.iterdir()))

        resultado = organizar_por_extensao(diretorio)
        print("Resultado da organizacao:", resultado)

        # validações: cada extensão deve ter sua própria subpasta com os arquivos certos
        assert (diretorio / "jpg").is_dir()
        assert {p.name for p in (diretorio / "jpg").iterdir()} == {"foto1.jpg", "foto2.jpg"}
        assert {p.name for p in (diretorio / "pdf").iterdir()} == {"documento.pdf"}
        assert {p.name for p in (diretorio / "txt").iterdir()} == {"notas.txt"}
        assert {p.name for p in (diretorio / "py").iterdir()} == {"script.py"}
        assert {p.name for p in (diretorio / "sem_extensao").iterdir()} == {"LICENCA"}

        # diretório raiz não deve ter mais arquivos sueltos, só as subpastas criadas
        arquivos_restantes_na_raiz = [p for p in diretorio.iterdir() if p.is_file()]
        assert arquivos_restantes_na_raiz == []

        print("Todos os testes de sanity check passaram.")
