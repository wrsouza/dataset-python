"""
Mesclagem de Intervalos Sobrepostos

Cenário: consolidação de uma agenda de reuniões com horários que se
sobrepõem, unificação de faixas de IP/portas reservadas, ou compactação de
períodos de promoção em um sistema de e-commerce.
O que este script demonstra: ordenar intervalos pelo início e percorrer
linearmente, mesclando quando o intervalo atual começa antes (ou no momento)
do fim do último intervalo já mesclado.
"""


def mesclar_intervalos(intervalos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervalos:
        return []

    # Ordenar por início é o que torna possível decidir com um único passe
    # se o próximo intervalo se sobrepõe ao último já mesclado.
    ordenados = sorted(intervalos, key=lambda par: par[0])

    mesclados = [ordenados[0]]
    for inicio, fim in ordenados[1:]:
        ultimo_inicio, ultimo_fim = mesclados[-1]
        if inicio <= ultimo_fim:
            # Sobreposição (ou contiguidade exata): estende o fim se necessário.
            mesclados[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            mesclados.append((inicio, fim))

    return mesclados


if __name__ == "__main__":
    # Horários de reuniões representados em minutos desde 00:00.
    reunioes = [(540, 600), (570, 630), (650, 700), (710, 720), (715, 750)]

    resultado = mesclar_intervalos(reunioes)
    print(f"Reuniões originais: {reunioes}")
    print(f"Agenda consolidada: {resultado}")
