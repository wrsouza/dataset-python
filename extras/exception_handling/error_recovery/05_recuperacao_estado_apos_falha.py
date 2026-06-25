"""
Recuperação de estado após falha

O que este script demonstra: como salvar progresso parcial (checkpoint) em
disco durante uma operação longa e retomar a partir do último ponto salvo
caso ocorra uma falha, em vez de recomeçar do zero.
Quando usar: processamento em lote ou tarefas longas onde recomeçar do
início após uma falha seria caro (ex.: importação de muitos registros).
"""

import json
import os
import tempfile


class FalhaProcessamentoError(Exception):
    """Erro simulado ocorrendo no meio do processamento do lote."""


def carregar_checkpoint(caminho):
    """Lê o índice do último item processado com sucesso; 0 se não existir."""
    if not os.path.exists(caminho):
        return 0
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados.get("proximo_indice", 0)


def salvar_checkpoint(caminho, proximo_indice):
    """Persiste o progresso em disco para sobreviver a uma falha/reinício."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"proximo_indice": proximo_indice}, f)


def processar_item(item):
    """Simula falha ao processar um item específico (índice 3)."""
    if item == "item-3":
        raise FalhaProcessamentoError(f"falha simulada ao processar {item}")
    return item.upper()


def processar_lote_com_checkpoint(itens, caminho_checkpoint):
    """
    Processa `itens` a partir do ponto salvo no checkpoint. Se uma exceção
    ocorrer, o checkpoint já reflete os itens processados com sucesso até
    aquele momento, permitindo retomar exatamente do item que falhou.
    """
    inicio = carregar_checkpoint(caminho_checkpoint)
    processados = []
    for indice in range(inicio, len(itens)):
        resultado = processar_item(itens[indice])  # pode lançar exceção
        processados.append(resultado)
        # Só avançamos o checkpoint DEPOIS do processamento ter sucesso,
        # garantindo que uma retomada nunca pule um item não processado.
        salvar_checkpoint(caminho_checkpoint, indice + 1)
    return processados


if __name__ == "__main__":
    itens = [f"item-{i}" for i in range(6)]

    with tempfile.TemporaryDirectory() as tmp:
        caminho_checkpoint = os.path.join(tmp, "checkpoint.json")

        # Primeira tentativa: dispara a falha de propósito no item-3.
        try:
            processar_lote_com_checkpoint(itens, caminho_checkpoint)
        except FalhaProcessamentoError as exc:
            indice_salvo = carregar_checkpoint(caminho_checkpoint)
            print(f"falha durante o processamento: {exc}")
            print(f"checkpoint salvo no índice {indice_salvo} (itens 0..{indice_salvo - 1} já concluídos)")

        # Simula a "correção do problema" (ex.: item-3 era inválido e foi
        # substituído por um valor processável) e retoma a partir do checkpoint.
        itens_corrigidos = list(itens)
        itens_corrigidos[3] = "item-3-corrigido"

        resultado_final = processar_lote_com_checkpoint(itens_corrigidos, caminho_checkpoint)
        print(f"processamento retomado e concluído: {resultado_final}")
