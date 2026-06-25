"""
Deteccao e correcao de encoding de um CSV por tentativa de multiplos encodings

O que este script demonstra: tentar decodificar os bytes de um arquivo com uma lista
de encodings candidatos (em ordem de probabilidade) ate encontrar um que funcione,
sem depender de bibliotecas externas como chardet.
Quando usar: ao receber arquivos de origem desconhecida/legada (ex: exportados de
Windows em Latin-1) onde o encoding declarado nao e confiavel ou esta ausente.
"""

import os
import tempfile

# ordem importa: utf-8 primeiro (mais comum hoje), depois variantes latinas comuns
# no Brasil, e cp1252 (Windows) como fallback antes do "ultimo recurso" permissivo.
ENCODINGS_CANDIDATOS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]


def detectar_encoding(caminho: str) -> str:
    """
    Tenta decodificar o arquivo inteiro com cada encoding candidato, na ordem.
    O primeiro que decodificar sem UnicodeDecodeError "ganha". Note que latin-1
    pratically nunca falha (decodifica qualquer byte), por isso fica perto do fim
    da lista - caso contrario ele "venceria" sempre e mascararia o encoding real.
    """
    with open(caminho, "rb") as f:
        conteudo_bytes = f.read()

    for encoding in ENCODINGS_CANDIDATOS:
        try:
            conteudo_bytes.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue

    # ultimo recurso: forca utf-8 substituindo caracteres invalidos
    return "utf-8"  # com errors="replace" no momento da leitura real


def ler_com_encoding_detectado(caminho: str) -> tuple[str, str]:
    """Retorna (encoding_usado, conteudo_decodificado)."""
    encoding = detectar_encoding(caminho)
    try:
        with open(caminho, "r", encoding=encoding, newline="") as f:
            return encoding, f.read()
    except UnicodeDecodeError:
        # fallback final, substitui bytes problematicos em vez de quebrar o pipeline
        with open(caminho, "r", encoding="utf-8", errors="replace", newline="") as f:
            return "utf-8 (com replace)", f.read()


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    caminho_csv = os.path.join(tmp_dir, "legado_latin1.csv")

    try:
        # gera um CSV com acentuacao tipica do PT-BR, salvo em latin-1 (comum em
        # exports antigos de sistemas Windows/legados)
        conteudo = "nome,cidade\nJoão,São Paulo\nMaría,Brasília\n"
        with open(caminho_csv, "w", encoding="latin-1") as f:
            f.write(conteudo)

        encoding_detectado = detectar_encoding(caminho_csv)
        print(f"Encoding detectado: {encoding_detectado}")

        encoding_usado, texto = ler_com_encoding_detectado(caminho_csv)
        print(f"Encoding usado na leitura: {encoding_usado}")
        print(texto)

        # utf-8 deve falhar para esses bytes acentuados em latin-1, entao o
        # detector deve cair para latin-1 (proximo candidato compativel)
        assert encoding_detectado in ("latin-1", "cp1252", "iso-8859-1")
        assert "João" in texto
        assert "Brasília" in texto
        print("OK: encoding detectado e conteudo decodificado corretamente.")
    finally:
        if os.path.exists(caminho_csv):
            os.remove(caminho_csv)
        os.rmdir(tmp_dir)
