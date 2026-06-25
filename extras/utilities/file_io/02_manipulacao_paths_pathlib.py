"""
Manipulacao de paths com pathlib

O que este script demonstra: uso de pathlib.Path para navegar, juntar e inspecionar
caminhos de forma orientada a objetos, em vez de manipular strings manualmente.
Quando usar: em qualquer código novo que lide com caminhos de arquivo/diretório multiplataforma.
"""

import tempfile
from pathlib import Path

def montar_estrutura(base: Path):
    # Path / "subpasta" junta caminhos de forma independente de SO (sem "/" ou "\" hardcoded)
    pasta_dados = base / "dados" / "2024"
    pasta_dados.mkdir(parents=True, exist_ok=True)
    arquivo = pasta_dados / "relatorio.txt"
    arquivo.write_text("conteudo do relatorio", encoding="utf-8")
    return arquivo

def inspecionar_path(caminho: Path):
    info = {
        "nome": caminho.name,           # "relatorio.txt"
        "stem": caminho.stem,           # "relatorio"
        "sufixo": caminho.suffix,       # ".txt"
        "pai": caminho.parent.name,     # "2024"
        "absoluto": caminho.is_absolute(),
        "existe": caminho.exists(),
    }
    return info


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)

        arquivo = montar_estrutura(base)
        print("Arquivo criado em:", arquivo)

        info = inspecionar_path(arquivo)
        print("Informacoes do path:", info)

        assert info["nome"] == "relatorio.txt"
        assert info["stem"] == "relatorio"
        assert info["sufixo"] == ".txt"
        assert info["pai"] == "2024"
        assert info["existe"] is True

        # with_suffix troca a extensão sem alterar o resto do caminho
        arquivo_md = arquivo.with_suffix(".md")
        print("Mesmo caminho com outra extensao:", arquivo_md)
        assert arquivo_md.name == "relatorio.md"

        # relative_to calcula caminho relativo entre dois Paths
        relativo = arquivo.relative_to(base)
        print("Caminho relativo a base:", relativo)
        assert str(relativo).replace("\\", "/") == "dados/2024/relatorio.txt"

        print("Todos os testes de sanity check passaram.")
