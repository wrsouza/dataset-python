"""
Uso de arquivos e diretorios temporarios com tempfile

O que este script demonstra: tempfile.NamedTemporaryFile, tempfile.TemporaryDirectory
e tempfile.mkstemp para criar recursos temporários que são limpos automaticamente (ou manualmente).
Quando usar: para arquivos intermediários de processamento que não devem poluir o disco permanentemente.
"""

import os
import tempfile

def usar_arquivo_temporario_com_contexto():
    # delete=True (padrão) remove o arquivo automaticamente ao saída do bloco "with"
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write("conteudo temporario")
        caminho = tmp.name
    # delete=False permite reabrir o arquivo depois de fechado (necessario no Windows
    # para reabrir o mesmo arquivo em outro "open" enquanto o handle original existe)
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    os.remove(caminho)  # limpeza manual já que usamos delete=False
    return conteudo

def usar_diretorio_temporario():
    caminhos_criados = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        # tudo dentro de tmp_dir é removido automaticamente ao saída do "with",
        # mesmo que vários arquivos tenham sido criados dentro dele
        for i in range(3):
            caminho = os.path.join(tmp_dir, f"arquivo_{i}.txt")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(f"dados {i}")
            caminhos_criados.append(caminho)
        existiam_durante_o_with = all(os.path.exists(p) for p in caminhos_criados)
    existem_apos_o_with = any(os.path.exists(p) for p in caminhos_criados)
    return existiam_durante_o_with, existem_apos_o_with

def usar_mkstemp():
    # mkstemp retorna um descritor de baixo nivel (fd) + caminho; quem chama é responsavel pela limpeza
    fd, caminho = tempfile.mkstemp(suffix=".bin")
    try:
        os.write(fd, b"dados binarios temporarios")
    finally:
        os.close(fd)  # fechar o fd explicitamente é obrigatorio com mkstemp
    with open(caminho, "rb") as f:
        conteudo = f.read()
    os.remove(caminho)
    return conteudo


if __name__ == "__main__":
    conteudo_lido = usar_arquivo_temporario_com_contexto()
    print("Conteudo lido do NamedTemporaryFile:", conteudo_lido)
    assert conteudo_lido == "conteudo temporario"

    existiam, existem_depois = usar_diretorio_temporario()
    print("Arquivos existiam durante o 'with'?", existiam)
    print("Arquivos existem depois do 'with'?", existem_depois)
    assert existiam is True
    assert existem_depois is False

    conteudo_binario = usar_mkstemp()
    print("Conteudo binario lido via mkstemp:", conteudo_binario)
    assert conteudo_binario == b"dados binarios temporarios"

    print("Todos os testes de sanity check passaram.")
