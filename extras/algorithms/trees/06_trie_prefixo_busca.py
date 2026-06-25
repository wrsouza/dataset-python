"""
Trie (Arvore de Prefixos)

O que este script demonstra: implementacao manual de uma Trie para
armazenar palavras de forma compartilhando prefixos comuns, com
operacoes de insert, search (busca exata) e starts_with (busca por
prefixo).
Complexidade: O(L) tempo por operacao, onde L e o tamanho da palavra
(ou prefixo) processada. Espaco: O(ALFABETO * N * L) no pior caso,
onde N e o numero de palavras, mas na pratica e bem menor gracas ao
compartilhamento de prefixos.
"""


class NoTrie:
    def __init__(self):
        # mapa caractere -> NoTrie filho; cresce sob demanda
        self.filhos = {}
        # marca se uma palavra completa termina exatamente neste no
        self.fim_de_palavra = False


class Trie:
    def __init__(self):
        self.raiz = NoTrie()

    def inserir(self, palavra):
        no = self.raiz
        for caractere in palavra:
            if caractere not in no.filhos:
                no.filhos[caractere] = NoTrie()
            no = no.filhos[caractere]
        no.fim_de_palavra = True

    def buscar(self, palavra):
        """Retorna True somente se 'palavra' foi inserida exatamente (nao apenas como prefixo)."""
        no = self._navegar_até(palavra)
        return no is not None and no.fim_de_palavra

    def comeca_com(self, prefixo):
        """Retorna True se existe alguma palavra inserida que comeca com 'prefixo'."""
        return self._navegar_até(prefixo) is not None

    def _navegar_até(self, texto):
        no = self.raiz
        for caractere in texto:
            if caractere not in no.filhos:
                return None
            no = no.filhos[caractere]
        return no


if __name__ == "__main__":
    trie = Trie()
    palavras = ["casa", "casaco", "caso", "carro", "carta"]
    for palavra in palavras:
        trie.inserir(palavra)

    print("Palavras inseridas:", palavras)

    print("\nBuscas exatas (search):")
    for termo in ["casa", "casaco", "cas", "carro", "carruagem"]:
        print(f"  buscar({termo!r}) -> {trie.buscar(termo)}")

    print("\nBuscas por prefixo (starts_with):")
    for prefixo in ["cas", "car", "z", ""]:
        print(f"  comeca_com({prefixo!r}) -> {trie.comeca_com(prefixo)}")

    print("\nCaso trivial: Trie vazia")
    trie_vazia = Trie()
    print("  buscar('qualquer') ->", trie_vazia.buscar("qualquer"))
    print("  comeca_com('') ->", trie_vazia.comeca_com(""))

    assert trie.buscar("casa") is True
    assert trie.buscar("cas") is False          # prefixo, mas nao foi inserido como palavra
    assert trie.comeca_com("cas") is True        # existe palavra com esse prefixo
    assert trie.comeca_com("z") is False
    assert trie_vazia.buscar("qualquer") is False
    print("\nSanity checks OK.")
