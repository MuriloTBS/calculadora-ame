"""Camada 1 — Área Equivalente de Construção (NBR 12.721).

    A_eq = Σ (A_i · k_i)
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Mapping

from .coeficientes import CoeficientesArea
from .entradas import AreasProjeto


@dataclass(frozen=True)
class QuadroAreas:
    """Resultado do dimensionamento de áreas."""

    por_tipo_real: Mapping[str, float]
    por_tipo_equivalente: Mapping[str, float]
    coeficientes: Mapping[str, float]
    area_real_total: float
    area_equivalente_total: float
    fator_equivalencia_medio: float  # A_eq / A_real


def calcular_quadro_areas(
    areas: AreasProjeto, coef: CoeficientesArea
) -> QuadroAreas:
    nomes = [f.name for f in fields(areas)]

    real = {n: float(getattr(areas, n)) for n in nomes}
    ks = {n: float(getattr(coef, n)) for n in nomes}
    equivalente = {n: real[n] * ks[n] for n in nomes}

    area_real = sum(real.values())
    area_eq = sum(equivalente.values())
    fator = area_eq / area_real if area_real else 0.0

    return QuadroAreas(
        por_tipo_real=real,
        por_tipo_equivalente=equivalente,
        coeficientes=ks,
        area_real_total=area_real,
        area_equivalente_total=area_eq,
        fator_equivalencia_medio=fator,
    )
