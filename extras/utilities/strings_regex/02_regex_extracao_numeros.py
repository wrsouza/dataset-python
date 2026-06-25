"""
Extracao de numeros e telefones de texto livre

O que este script demonstra: como usar re.findall para extrair sequencias
numericas e padroes de telefone (BR) embutidos em um texto qualquer.
Quando usar: ao precisar minerar dados estruturados (numeros, telefones) de texto nao estruturado.
"""

import re

# Numeros inteiros ou decimais (com ponto ou virgula)
NUMERO_REGEX = re.compile(r"\d+(?:[.,]\d+)?")

# Telefones BR: aceita formatos como (11) 91234-5678, 11 91234-5678, 1191234-5678
TELEFONE_REGEX = re.compile(
    r"(?:\(?\d{2}\)?\s?)?"   # DDD opcional, com ou sem parenteses
    r"9?\d{4}-?\d{4}"        # numero com 8 ou 9 digitos, com ou sem hifen
)


def extrair_numeros(texto: str) -> list[str]:
    """Extrai todas as sequencias numericas (inteiras ou decimais) do texto."""
    return NUMERO_REGEX.findall(texto)


def extrair_telefones(texto: str) -> list[str]:
    """Extrai padroes que parecem telefones brasileiros do texto."""
    # findall retorna apenas o que casa; strip remove espacos residuais
    return [t.strip() for t in TELEFONE_REGEX.findall(texto)]


if __name__ == "__main__":
    texto_exemplo = (
        "Meu pedido #4521 custou R$ 199,90 e chegou em 3.5 dias. "
        "Ligue para (11) 91234-5678 ou para o fixo 11 3456-7890 "
        "para mais informacoes sobre o item 7."
    )

    numeros = extrair_numeros(texto_exemplo)
    telefones = extrair_telefones(texto_exemplo)

    print("Texto original:")
    print(texto_exemplo)
    print("\nNumeros encontrados:", numeros)
    print("Telefones encontrados:", telefones)

    # sanity check
    assert "4521" in numeros
    assert "199,90" in numeros
    assert any("91234-5678" in t for t in telefones)
    print("\nOK: sanity checks passaram.")
