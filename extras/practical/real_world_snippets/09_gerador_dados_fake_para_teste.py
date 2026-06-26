"""
Gerador de dados fake para testes (sem bibliotecas externas)

Cenario: popular um banco de testes, gerar massa de dados para uma demo
ou criar fixtures para testes automatizados sem depender de pacotes como
'Faker', seja por restricao de ambiente ou para manter o script standalone.
O que este script demonstra: geracao pseudo-aleatoria (mas reprodutivel
via seed) de nomes, emails e datas usando apenas a stdlib (random, datetime).
"""

import random
from datetime import date, timedelta
from typing import List, NamedTuple

PRIMEIROS_NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela"]
SOBRENOMES = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa"]
DOMINIOS_EMAIL = ["exemplo.com", "teste.dev", "mail.fake"]


class PessoaFake(NamedTuple):
    nome_completo: str
    email: str
    data_nascimento: date


def gerar_email(nome: str, sobrenome: str, rng: random.Random) -> str:
    # Padrao comum em sistemas reais: primeiro_nome.sobrenome@dominio
    dominio = rng.choice(DOMINIOS_EMAIL)
    return f"{nome.lower()}.{sobrenome.lower()}@{dominio}"


def gerar_data_nascimento(rng: random.Random, idade_min: int = 18, idade_max: int = 65) -> date:
    hoje = date.today()
    idade_sorteada = rng.randint(idade_min, idade_max)
    dias_extra = rng.randint(0, 364)  # varia o dia/mes dentro do ano sorteado
    return hoje.replace(year=hoje.year - idade_sorteada) - timedelta(days=dias_extra)


def gerar_pessoas_fake(quantidade: int, seed: int = 42) -> List[PessoaFake]:
    """Gera uma lista de pessoas fake de forma reprodutivel.

    Usar uma instancia propria de random.Random(seed) -- em vez do modulo
    'random' global -- evita interferir no estado aleatorio global do
    processo e garante que o mesmo seed sempre produza os mesmos dados,
    o que e essencial para testes deterministicos.
    """
    rng = random.Random(seed)
    pessoas = []
    for _ in range(quantidade):
        nome = rng.choice(PRIMEIROS_NOMES)
        sobrenome = rng.choice(SOBRENOMES)
        pessoas.append(
            PessoaFake(
                nome_completo=f"{nome} {sobrenome}",
                email=gerar_email(nome, sobrenome, rng),
                data_nascimento=gerar_data_nascimento(rng),
            )
        )
    return pessoas


if __name__ == "__main__":
    pessoas_teste = gerar_pessoas_fake(quantidade=5, seed=42)
    print("Dados fake gerados (seed=42, reproduzivel):")
    for pessoa in pessoas_teste:
        print(f"  {pessoa.nome_completo} | {pessoa.email} | nascido em {pessoa.data_nascimento}")
