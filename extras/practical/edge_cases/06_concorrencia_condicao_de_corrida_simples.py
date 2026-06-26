"""
Race condition simples com threading e correcao com Lock

Cenario: varias threads de um servico web incrementando um contador
compartilhado em memoria (ex: contador de requisicoes processadas, saldo de
um carrinho/estoque). Sem sincronizacao, incrementos simultaneos podem se
perder porque "ler, somar, gravar" nao e uma operacao atomica - duas threads
podem ler o mesmo valor antes de qualquer uma escrever o resultado.
Demonstra: a race condition acontecendo de fato (contador final errado) e a
correcao usando threading.Lock para tornar a secao critica atomica.
"""

import threading
import time


class ContadorInseguro:
    """Contador sem nenhuma protecao contra acesso concorrente."""

    def __init__(self):
        self.valor = 0

    def incrementar(self):
        # Esta operacao parece uma linha so, mas internamente e
        # "ler self.valor -> calcular +1 -> escrever de volta". Entre o ler e
        # o escrever, o interpretador pode trocar para outra thread (GIL
        # libera o controle entre bytecodes), permitindo que duas threads
        # leiam o mesmo valor antes de qualquer uma salvar o resultado.
        valor_atual = self.valor
        # Um sleep minusculo aqui forca o escalonador a trocar de thread bem
        # no meio da secao critica (entre o "ler" e o "escrever"), tornando a
        # race condition visivel de forma confiavel. Sem ele, o bug ainda
        # existe na logica, mas pode nao se manifestar sempre, dependendo de
        # sorte no escalonamento das threads (e por isso bugs de concorrencia
        # sao notoriamente dificeis de reproduzir e debugar em produção).
        time.sleep(0)
        valor_atual += 1
        self.valor = valor_atual


class ContadorSeguro:
    """Mesmo contador, agora protegido por um Lock."""

    def __init__(self):
        self.valor = 0
        self._lock = threading.Lock()

    def incrementar(self):
        # O lock garante que so uma thread por vez execute o bloco "ler,
        # somar, gravar", eliminando a janela onde a race condition ocorria.
        with self._lock:
            valor_atual = self.valor
            valor_atual += 1
            self.valor = valor_atual


def executar_incrementos_concorrentes(contador, n_threads, incrementos_por_thread):
    def tarefa():
        for _ in range(incrementos_por_thread):
            contador.incrementar()

    threads = [threading.Thread(target=tarefa) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return contador.valor


if __name__ == "__main__":
    N_THREADS = 10
    INCREMENTOS_POR_THREAD = 500
    esperado = N_THREADS * INCREMENTOS_POR_THREAD

    print(f"Esperado apos {N_THREADS} threads x {INCREMENTOS_POR_THREAD} incrementos: {esperado}")

    contador_inseguro = ContadorInseguro()
    resultado_inseguro = executar_incrementos_concorrentes(
        contador_inseguro, N_THREADS, INCREMENTOS_POR_THREAD
    )
    print(f"\nSem Lock (ContadorInseguro): valor final = {resultado_inseguro}")
    if resultado_inseguro != esperado:
        print(f"  -> RACE CONDITION CONFIRMADA: perdeu {esperado - resultado_inseguro} incrementos")
    else:
        print("  -> Neste run especifico nao houve perda visivel (race condition e nao-deterministica,"
              " pode nao aparecer sempre, mas o risco existe)")

    contador_seguro = ContadorSeguro()
    resultado_seguro = executar_incrementos_concorrentes(
        contador_seguro, N_THREADS, INCREMENTOS_POR_THREAD
    )
    print(f"\nCom Lock (ContadorSeguro): valor final = {resultado_seguro}")
    print(f"  -> Resultado correto? {resultado_seguro == esperado}")
