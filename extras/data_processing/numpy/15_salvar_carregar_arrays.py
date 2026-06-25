"""
Salvar e carregar arrays: .npy (binario) e .csv/.txt (texto)

O que este script demonstra: como persistir arrays em disco com np.save/np.load
(formato binario nativo) e com np.savetxt/np.loadtxt (formato texto legivel).
Quando usar: .npy para performance e fidelidade total de tipos; texto/csv quando o
arquivo precisa ser lido por humanos ou por outras ferramentas (Excel, etc).
"""

import os
import tempfile
import numpy as np

if __name__ == "__main__":
    dados = np.array([[1.5, 2.5, 3.5], [4.0, 5.0, 6.0]])

    # cria um diretorio temporario isolado -- garante que nada fica residual no
    # projeto, mesmo se o script falhar no meio (usamos try/finally para limpar)
    pasta_temp = tempfile.mkdtemp(prefix="numpy_demo_")
    caminho_npy = os.path.join(pasta_temp, "dados.npy")
    caminho_csv = os.path.join(pasta_temp, "dados.csv")

    try:
        # .npy: formato binario que preserva shape e dtype exatamente
        np.save(caminho_npy, dados)
        dados_carregados_npy = np.load(caminho_npy)

        # .csv/.txt: formato texto, precisa especificar delimitador; perde dtype
        # original (sempre volta como float ao recarregar, por isso comparamos com
        # tolerancia via allclose em vez de igualdade exata de tipo)
        np.savetxt(caminho_csv, dados, delimiter=",", fmt="%.2f")
        dados_carregados_csv = np.loadtxt(caminho_csv, delimiter=",")

        print("dados originais:\n", dados)
        print("arquivo .npy salvo em:", caminho_npy)
        print("dados carregados do .npy:\n", dados_carregados_npy)
        print("arquivo .csv salvo em:", caminho_csv)
        print("dados carregados do .csv:\n", dados_carregados_csv)

        # sanity checks
        assert np.array_equal(dados, dados_carregados_npy)  # .npy e exato (binario)
        assert np.allclose(dados, dados_carregados_csv, atol=1e-2)  # texto tem arredondamento
        assert os.path.exists(caminho_npy)
        assert os.path.exists(caminho_csv)
        print("OK: todos os asserts passaram.")
    finally:
        # limpeza: remove os arquivos e a pasta temporaria, nao deixando residuos
        for caminho in (caminho_npy, caminho_csv):
            if os.path.exists(caminho):
                os.remove(caminho)
        os.rmdir(pasta_temp)
