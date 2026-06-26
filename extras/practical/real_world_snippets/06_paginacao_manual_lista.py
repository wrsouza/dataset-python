"""
Paginacao manual sobre uma lista em memoria

Cenario: implementar paginacao de resultados (ex.: endpoint REST "GET
/produtos?pagina=2&tamanho=10") quando os dados ja estao todos carregados
em memoria, sem usar um ORM ou framework que faca isso automaticamente.
O que este script demonstra: calculo de slices, metadados de paginacao
(total de paginas, has_next/has_prev) e validacao de limites.
"""

import math
from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginaResultado(Generic[T]):
    itens: List[T]
    pagina_atual: int
    total_paginas: int
    total_itens: int
    tem_proxima: bool
    tem_anterior: bool


def paginar(itens: List[T], pagina: int, tamanho_pagina: int) -> PaginaResultado:
    """Retorna a pagina solicitada (1-indexed, como em APIs REST comuns).

    Paginas fora do intervalo sao "clampadas" em vez de lancar erro --
    decisao deliberada para tornar a funcao tolerante a entradas como
    pagina=0 ou pagina=999 vindas de parametros de URL nao confiaveis.
    """
    total_itens = len(itens)
    total_paginas = max(1, math.ceil(total_itens / tamanho_pagina))
    pagina = max(1, min(pagina, total_paginas))  # clamp dentro do intervalo valido

    inicio = (pagina - 1) * tamanho_pagina
    fim = inicio + tamanho_pagina

    return PaginaResultado(
        itens=itens[inicio:fim],
        pagina_atual=pagina,
        total_paginas=total_paginas,
        total_itens=total_itens,
        tem_proxima=pagina < total_paginas,
        tem_anterior=pagina > 1,
    )


if __name__ == "__main__":
    produtos = [f"Produto-{i:02d}" for i in range(1, 24)]  # 23 produtos fictícios

    for numero_pagina in (1, 2, 5, 99):  # 99 testa o clamp para a ultima pagina valida
        resultado = paginar(produtos, pagina=numero_pagina, tamanho_pagina=10)
        print(
            f"Pagina solicitada={numero_pagina} -> "
            f"pagina_atual={resultado.pagina_atual}/{resultado.total_paginas} "
            f"itens={resultado.itens} "
            f"tem_proxima={resultado.tem_proxima} tem_anterior={resultado.tem_anterior}"
        )
