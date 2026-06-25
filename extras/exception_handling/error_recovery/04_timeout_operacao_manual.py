"""
Timeout manual de operação (multiplataforma)

O que este script demonstra: como limitar o tempo de execução de uma
operação usando threading (não usa signal.alarm/SIGALRM, que não existe no
Windows), executando a função em uma thread separada e aguardando com join.
Quando usar: quando é preciso impor um limite de tempo para uma chamada que
pode travar (ex.: I/O bloqueante) e o ambiente precisa funcionar em Windows,
onde sinais Unix não estão disponíveis.
"""

import threading
import time


class TimeoutOperacaoError(Exception):
    """Lançada quando a operação não termina dentro do tempo limite."""


def executar_com_timeout(func, timeout_segundos, *args, **kwargs):
    """
    Executa `func` em uma thread separada e espera até `timeout_segundos`.

    Observação importante: como não há forma segura/portável de "matar" uma
    thread no Python, a thread de trabalho pode continuar rodando em segundo
    plano (como daemon) mesmo após declararmos timeout. Para CPU-bound puro
    isso não é ideal, mas é a abordagem multiplataforma padrão sem depender
    de bibliotecas externas como multiprocessing com terminate().
    """
    resultado = {}
    erro = {}

    def alvo():
        try:
            resultado["valor"] = func(*args, **kwargs)
        except Exception as exc:  # captura para repassar à thread principal
            erro["excecao"] = exc

    thread = threading.Thread(target=alvo, daemon=True)
    thread.start()
    thread.join(timeout=timeout_segundos)

    if thread.is_alive():
        # A thread ainda está rodando após o tempo limite: consideramos a
        # operação como "estourada" e seguimos adiante sem esperar mais.
        raise TimeoutOperacaoError(
            f"operação excedeu o limite de {timeout_segundos}s"
        )

    if "excecao" in erro:
        raise erro["excecao"]

    return resultado.get("valor")


def operacao_lenta(duracao):
    """Simula uma operação bloqueante (ex.: chamada de rede travada)."""
    time.sleep(duracao)
    return f"concluído após {duracao}s"


if __name__ == "__main__":
    # Caso 1: operação rápida o suficiente -> deve retornar normalmente.
    resultado = executar_com_timeout(operacao_lenta, 1.0, 0.1)
    print(f"caso rápido: {resultado}")

    # Caso 2: dispara o timeout de propósito (operação mais lenta que o limite).
    try:
        executar_com_timeout(operacao_lenta, 0.3, 2.0)
    except TimeoutOperacaoError as exc:
        print(f"timeout disparado como esperado: {exc}")
        print("recuperação: seguindo a execução do programa normalmente")

    print("programa principal continua executando após o timeout")
