"""
Profiling basico com cProfile

Cenario: antes de otimizar qualquer codigo em producao (uma rota lenta de API,
um job batch demorado), e preciso medir ONDE o tempo esta sendo gasto em vez de
"otimizar no escuro" baseado em suposicao.
O que este script demonstra: usar cProfile.Profile para coletar estatisticas de
chamadas de funcao de uma rotina com multiplos hotspots, e usar pstats para
imprimir um relatorio ordenado por tempo cumulativo, revelando qual funcao
realmente consome mais tempo de execucao.
"""

import cProfile
import pstats
import io
import time


def tarefa_rapida():
    """Simula uma operacao leve (ex: validacao simples)."""
    total = 0
    for i in range(1_000):
        total += i
    return total


def tarefa_lenta_cpu():
    """Simula uma operacao cara de CPU (ex: calculo numerico ineficiente)."""
    total = 0
    for i in range(500_000):
        total += i * i
    return total


def tarefa_com_io_simulado():
    """Simula uma chamada de I/O (ex: request de rede) usando sleep."""
    time.sleep(0.05)
    return "ok"


def pipeline_principal():
    """Funcao "de negocio" que chama as outras -- e o que normalmente seria
    investigado quando alguem reclama que 'a rotina X esta lenta'."""
    resultados = []
    for _ in range(3):
        resultados.append(tarefa_rapida())
        resultados.append(tarefa_lenta_cpu())
    resultados.append(tarefa_com_io_simulado())
    return resultados


if __name__ == "__main__":
    profiler = cProfile.Profile()

    profiler.enable()
    pipeline_principal()
    profiler.disable()

    # pstats permite ordenar e formatar as estatisticas coletadas.
    # Ordenamos por "cumulative" (tempo total dentro da funcao + chamadas filhas),
    # que e geralmente o criterio mais util para achar o hotspot real.
    buffer_saida = io.StringIO()
    estatisticas = pstats.Stats(profiler, stream=buffer_saida).sort_stats("cumulative")
    estatisticas.print_stats(8)  # top 8 linhas mais relevantes

    print("Relatorio de profiling (top funcoes por tempo cumulativo):")
    print(buffer_saida.getvalue())

    print("Dica de leitura: 'tarefa_lenta_cpu' deve aparecer com tottime alto")
    print("(tempo gasto dentro dela mesma), enquanto 'tarefa_com_io_simulado'")
    print("aparece com tempo proporcional ao sleep, mas baixo uso de CPU real.")
