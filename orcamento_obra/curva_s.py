"""Curva de desembolso (Curva S) — cronograma físico-financeiro preliminar.

O avanço acumulado no mês ``m`` segue uma sigmoide normalizada:

    p(t) = t^a / ( t^a + (1 - t)^a ),   t = m / prazo,   a = parâmetro de forma

``a = 1`` gera desembolso linear; ``a > 1`` concentra o desembolso no miolo da
obra (comportamento típico). O desembolso do mês é a diferença dos acumulados.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PontoCurvaS:
    mes: int
    percentual_periodo: float
    percentual_acumulado: float
    desembolso_periodo: float
    desembolso_acumulado: float


@dataclass(frozen=True)
class CurvaS:
    base_financeira: str  # "custo_total" ou "preco_venda"
    valor_base: float
    forma: float
    pontos: tuple[PontoCurvaS, ...]


def _acumulado_sigmoide(t: float, forma: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    ta = t**forma
    return ta / (ta + (1.0 - t) ** forma)


def gerar_curva_s(
    valor_base: float,
    prazo_meses: int,
    forma: float = 2.2,
    base_financeira: str = "custo_total",
) -> CurvaS:
    if prazo_meses <= 0:
        raise ValueError("prazo_meses deve ser > 0.")
    if forma <= 0:
        raise ValueError("forma deve ser > 0.")

    pontos: list[PontoCurvaS] = []
    acumulado_anterior = 0.0
    for mes in range(1, prazo_meses + 1):
        t = mes / prazo_meses
        acumulado = _acumulado_sigmoide(t, forma)
        periodo = acumulado - acumulado_anterior
        pontos.append(
            PontoCurvaS(
                mes=mes,
                percentual_periodo=periodo,
                percentual_acumulado=acumulado,
                desembolso_periodo=periodo * valor_base,
                desembolso_acumulado=acumulado * valor_base,
            )
        )
        acumulado_anterior = acumulado

    return CurvaS(
        base_financeira=base_financeira,
        valor_base=valor_base,
        forma=forma,
        pontos=tuple(pontos),
    )
