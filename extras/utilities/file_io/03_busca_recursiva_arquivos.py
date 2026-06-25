"""
Busca recursiva de arquivos com glob/rglob

O que este script demonstra: como localizar arquivos por padrão de nome usando
Path.glob (não recursivo) e Path.rglob (recursivo, equivalente a "**/padrao").
Quando usar: quando precisar encontrar todos os arquivos de um tipo dentro de uma árvore de diretórios.
"""

import tempfile
from pathlib import Path

def criar_estrutura_exemplo(base: Path):
    # cria uma árvore de diretórios com arquivos de tipos diferentes para testar a busca
    (base / "src").mkdir()
    (base / "src" / "modulo_a.py").write_text("# modulo a", encoding="utf-8")
    (base / "src" / "modulo_b.py").write_text("# modulo b", encoding="utf-8")
    (base / "src" / "sub").mkdir()
    (base / "src" / "sub" / "modulo_c.py").write_text("# modulo c", encoding="utf-8")
    (base / "docs").mkdir()
    (base / "docs" / "leia.txt").write_text("documentacao", encoding="utf-8")
    (base / "README.md").write_text("# readme", encoding="utf-8")

def buscar_nao_recursivo(base: Path, padrao):
    # glob só olha o nível indicado no padrão, não desce em subpastas automaticamente
    return sorted(base.glob(padrao))

def buscar_recursivo(base: Path, padrao):
    # rglob é equivalente a glob("**/" + padrao): percorre todas as subpastas
    return sorted(base.rglob(padrao))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        criar_estrutura_exemplo(base)

        # busca não recursiva direto na pasta "src" encontra só os 2 arquivos daquele nível
        py_diretos = buscar_nao_recursivo(base / "src", "*.py")
        print("Arquivos .py direto em src/:", [p.name for p in py_diretos])
        assert len(py_diretos) == 2

        # busca recursiva a partir da base encontra todos os .py, incluindo os de subpastas
        todos_py = buscar_recursivo(base, "*.py")
        print("Todos os arquivos .py (recursivo):", [p.name for p in todos_py])
        assert len(todos_py) == 3

        # busca recursiva por extensão diferente
        todos_txt = buscar_recursivo(base, "*.txt")
        print("Todos os arquivos .txt (recursivo):", [p.name for p in todos_txt])
        assert len(todos_txt) == 1

        # padrão pode combinar prefixo + wildcard
        modulos_a_e_b = buscar_recursivo(base, "modulo_[ab].py")
        print("Modulos a/b via classe de caracteres:", [p.name for p in modulos_a_e_b])
        assert len(modulos_a_e_b) == 2

        print("Todos os testes de sanity check passaram.")
