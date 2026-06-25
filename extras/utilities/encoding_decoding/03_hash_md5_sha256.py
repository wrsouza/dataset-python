"""
Hashes com hashlib (MD5 e SHA-256)

O que este script demonstra: como gerar digests (hashes) de strings e
arquivos usando os algoritmos MD5 e SHA-256, e como comparar hashes
para verificar integridade de dados.
Quando usar: para verificar integridade de arquivos (checksums), gerar
identificadores deterministicos de conteudo, ou (com cautela) compor
fluxos de armazenamento de senhas — nunca use MD5/SHA-256 puros para
senhas em producao, prefira bcrypt/scrypt/argon2.
"""

import hashlib


def gerar_md5(texto: str) -> str:
    # MD5 e rapido mas criptograficamente quebrado para uso de seguranca;
    # ainda e aceitavel para checksums simples de integridade, nao para senhas
    return hashlib.md5(texto.encode("utf-8")).hexdigest()


def gerar_sha256(texto: str) -> str:
    # SHA-256 e o padrao atual para verificacao de integridade e
    # assinaturas; muito mais resistente a colisoes que MD5
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def gerar_sha256_em_blocos(dados_bytes: bytes, tamanho_bloco: int = 4096) -> str:
    # Para arquivos grandes, processar em blocos evita carregar
    # tudo na memoria de uma vez (aqui simulamos com bytes em memoria)
    hasher = hashlib.sha256()
    for inicio in range(0, len(dados_bytes), tamanho_bloco):
        hasher.update(dados_bytes[inicio:inicio + tamanho_bloco])
    return hasher.hexdigest()


if __name__ == "__main__":
    texto = "Integridade de dados com Python"

    md5_hash = gerar_md5(texto)
    sha256_hash = gerar_sha256(texto)

    print(f"Texto:  {texto}")
    print(f"MD5:    {md5_hash}")
    print(f"SHA256: {sha256_hash}")

    # sanity check: o mesmo texto deve sempre gerar o mesmo hash (determinismo)
    assert gerar_md5(texto) == md5_hash, "MD5 nao e deterministico!"
    assert gerar_sha256(texto) == sha256_hash, "SHA256 nao e deterministico!"

    # um texto diferente deve (com altissima probabilidade) gerar hash diferente
    outro_hash = gerar_sha256("Integridade de dados com python")  # 'p' minusculo
    assert outro_hash != sha256_hash, "Hashes colidiram inesperadamente"

    # hash em blocos deve produzir o mesmo resultado que hash direto
    dados_grandes = (texto * 1000).encode("utf-8")
    hash_direto = hashlib.sha256(dados_grandes).hexdigest()
    hash_em_blocos = gerar_sha256_em_blocos(dados_grandes)
    assert hash_direto == hash_em_blocos, "Hash em blocos divergiu do hash direto"

    print(f"\nHash em blocos (dados grandes): {hash_em_blocos}")
    print("Todos os testes passaram com sucesso.")
