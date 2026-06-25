"""
Leitura e escrita de arquivos de texto

O que este script demonstra: como abrir arquivos de texto usando context manager (with),
e as diferenças entre os principais modos de abertura (w, r, a, x).
Quando usar: sempre que precisar ler ou escrever arquivos de texto simples (logs, configs, CSV cru, etc.).
"""

import os
import tempfile

def escrever_arquivo(caminho, conteudo, modo="w"):
    # context manager garante que o arquivo seja fechado mesmo se ocorrer exceção
    with open(caminho, mode=modo, encoding="utf-8") as f:
        f.write(conteudo)

def ler_arquivo_completo(caminho):
    with open(caminho, mode="r", encoding="utf-8") as f:
        return f.read()

def ler_linhas(caminho):
    with open(caminho, mode="r", encoding="utf-8") as f:
        # readlines() carrega tudo em memória; ok para arquivos pequenos
        return f.readlines()

def adicionar_ao_arquivo(caminho, conteudo):
    # modo "a" (append) escreve no final sem truncar o conteúdo existente
    with open(caminho, mode="a", encoding="utf-8") as f:
        f.write(conteudo)


if __name__ == "__main__":
    # usa diretório temporário para não deixar lixo no repositório
    with tempfile.TemporaryDirectory() as tmp_dir:
        caminho = os.path.join(tmp_dir, "exemplo.txt")

        # modo "w" (write): cria o arquivo do zero, sobrescrevendo se já existir
        escrever_arquivo(caminho, "linha 1\nlinha 2\n", modo="w")
        conteudo = ler_arquivo_completo(caminho)
        print("Conteudo apos escrita:")
        print(conteudo)
        assert conteudo == "linha 1\nlinha 2\n"

        # modo "a" (append): adiciona sem apagar o que já existe
        adicionar_ao_arquivo(caminho, "linha 3\n")
        linhas = ler_linhas(caminho)
        print("Linhas apos append:", linhas)
        assert len(linhas) == 3
        assert linhas[2] == "linha 3\n"

        # modo "x" (exclusive create): falha se o arquivo já existir
        caminho_novo = os.path.join(tmp_dir, "novo.txt")
        escrever_arquivo(caminho_novo, "criado com modo x\n", modo="x")
        try:
            escrever_arquivo(caminho_novo, "tentando de novo", modo="x")
            raise AssertionError("deveria ter levantado FileExistsError")
        except FileExistsError:
            print("Modo 'x' corretamente impediu sobrescrita de arquivo existente.")

        print("Todos os testes de sanity check passaram.")
