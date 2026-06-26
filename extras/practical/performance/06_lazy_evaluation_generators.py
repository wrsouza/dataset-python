"""
Lazy evaluation com pipeline de generators encadeados

Cenario: pipelines de processamento de dados (leitura de arquivo linha a linha,
ETL, parsing de logs) frequentemente encadeiam varias etapas de transformacao
e filtro. Fazer isso com listas intermediarias materializa dados desnecessarios
na memoria a cada etapa.
O que este script demonstra: construir um pipeline de generators encadeados
(cada etapa consome o generator anterior e produz outro generator) para mostrar
avaliacao "lazy" -- nenhum dado e processado até que o consumidor final
(list(), for, sum(), etc.) efetivamente itere sobre o pipeline.
"""


def ler_linhas_simuladas(quantidade):
    """Simula a leitura de um arquivo grande, linha a linha, sob demanda.
    Em vez de abrir um arquivo real, geramos linhas sinteticas para o exemplo."""
    for i in range(quantidade):
        # nada e calculado ainda quando esta funcao e chamada -- e um generator
        yield f"linha_{i};valor={i * 3}"


def filtrar_linhas_validas(linhas):
    """Etapa 2: descarta linhas que nao atendem a um criterio (ex: valor par)."""
    for linha in linhas:
        valor = int(linha.split("valor=")[1])
        if valor % 2 == 0:
            yield linha


def extrair_valor(linhas):
    """Etapa 3: transforma cada linha textual no valor numerico que ela contem."""
    for linha in linhas:
        valor = int(linha.split("valor=")[1])
        yield valor


def montar_pipeline(quantidade):
    """Encadeia as tres etapas. Nenhuma delas executa codigo ainda --
    cada chamada apenas cria um objeto generator que referencia o anterior."""
    linhas = ler_linhas_simuladas(quantidade)
    linhas_validas = filtrar_linhas_validas(linhas)
    valores = extrair_valor(linhas_validas)
    return valores


if __name__ == "__main__":
    QUANTIDADE = 20

    pipeline = montar_pipeline(QUANTIDADE)
    print(f"Pipeline criado para {QUANTIDADE} linhas simuladas.")
    print(f"Tipo do objeto retornado: {type(pipeline).__name__} (nada foi processado ainda)")

    # so agora, ao iterar (via list()), o pipeline efetivamente "roda":
    # cada item passa pelas 3 etapas (ler -> filtrar -> extrair) sob demanda,
    # um por vez, sem nunca materializar a lista completa de linhas em memoria.
    resultados = list(pipeline)
    print(f"Resultados extraidos (apenas valores pares): {resultados}")
    print(f"Total de itens que passaram pelo filtro: {len(resultados)} de {QUANTIDADE} linhas lidas")

    # demonstracao extra: consumir parcialmente um pipeline com next()
    pipeline_parcial = montar_pipeline(1_000_000)  # "milhoes" de linhas, mas nada e gerado ainda
    primeiros_tres = [next(pipeline_parcial) for _ in range(3)]
    print(f"Mesmo com 1.000.000 de linhas 'declaradas', pegamos so os 3 primeiros valores: {primeiros_tres}")
    print("Isso e o poder do lazy evaluation: custo proporcional ao que de fato e consumido.")
