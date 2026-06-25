"""
Watcher simples de diretorio (polling)

O que este script demonstra: como detectar mudancas (criação, remoção, modificação)
em um diretório usando polling simples — comparar snapshots do estado do diretório
ao longo do tempo, sem depender de bibliotecas externas (watchdog, inotify, etc.).
Quando usar: para detecção básica de mudanças quando não se pode/quer adicionar dependências externas.
"""

import tempfile
import time
from pathlib import Path

def tirar_snapshot(diretorio: Path):
    # mapeia nome -> mtime (momento da ultima modificacao) de cada arquivo presente
    snapshot = {}
    for caminho in diretorio.iterdir():
        if caminho.is_file():
            snapshot[caminho.name] = caminho.stat().st_mtime
    return snapshot

def comparar_snapshots(antigo, novo):
    nomes_antigos = set(antigo)
    nomes_novos = set(novo)

    criados = sorted(nomes_novos - nomes_antigos)
    removidos = sorted(nomes_antigos - nomes_novos)
    # modificados: presentes nos dois, mas com mtime diferente
    modificados = sorted(
        nome for nome in (nomes_antigos & nomes_novos)
        if antigo[nome] != novo[nome]
    )
    return {"criados": criados, "removidos": removidos, "modificados": modificados}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        diretorio = Path(tmp_dir)

        # estado inicial: um arquivo já existente antes do "monitoramento" começar
        (diretorio / "inicial.txt").write_text("estado inicial", encoding="utf-8")
        snapshot_anterior = tirar_snapshot(diretorio)
        print("Snapshot inicial:", list(snapshot_anterior))

        eventos_detectados = []

        # simula algumas iteracoes de polling (loop finito, nao infinito) ---
        acoes = [
            lambda: (diretorio / "novo_arquivo.txt").write_text("conteudo novo", encoding="utf-8"),
            lambda: (diretorio / "inicial.txt").write_text("conteudo alterado", encoding="utf-8"),
            lambda: (diretorio / "inicial.txt").unlink(),
        ]

        for i, acao in enumerate(acoes, start=1):
            time.sleep(0.05)  # pequena pausa para garantir mtime diferente entre iteracoes
            acao()
            snapshot_atual = tirar_snapshot(diretorio)
            mudancas = comparar_snapshots(snapshot_anterior, snapshot_atual)
            print(f"Iteracao {i} - mudancas detectadas:", mudancas)
            eventos_detectados.append(mudancas)
            snapshot_anterior = snapshot_atual

        # validações de sanity check sobre o que foi detectado em cada iteração
        assert eventos_detectados[0]["criados"] == ["novo_arquivo.txt"]
        assert eventos_detectados[1]["modificados"] == ["inicial.txt"]
        assert eventos_detectados[2]["removidos"] == ["inicial.txt"]

        print("Todos os testes de sanity check passaram.")
