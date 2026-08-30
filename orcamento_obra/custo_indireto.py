"""Camada 3 — Custo Indireto Total.

    CI = custo_mensal_indireto · prazo_meses

``custo_mensal_indireto`` = (equipe técnica + infraestrutura de canteiro) ajustado
pelo fator de logística (mobilização, restrição de horário, distância).
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Mapping

from .coeficientes import EquipeTecnicaMensal, InfraCanteiroMensal
from .entradas import EntradaProjeto


@dataclass(frozen=True)
class CustoIndireto:
    detalhe_equipe: Mapping[str, float]
    detalhe_canteiro: Mapping[str, float]
    custo_equipe_mensal: float
    custo_canteiro_mensal: float
    fator_logistica: float
    custo_mensal_indireto: float  # já com o fator de logística
    prazo_meses: int
    custo_indireto_total: float


def _detalhar(obj: EquipeTecnicaMensal | InfraCanteiroMensal) -> dict[str, float]:
    return {f.name: float(getattr(obj, f.name)) for f in fields(obj)}


def calcular_custo_indireto(entrada: EntradaProjeto) -> CustoIndireto:
    equipe = _detalhar(entrada.equipe_tecnica)
    canteiro = _detalhar(entrada.infra_canteiro)

    soma_equipe = sum(equipe.values())
    soma_canteiro = sum(canteiro.values())
    f_log = entrada.fator_logistica

    mensal = (soma_equipe + soma_canteiro) * f_log
    total = mensal * entrada.prazo_meses

    return CustoIndireto(
        detalhe_equipe=equipe,
        detalhe_canteiro=canteiro,
        custo_equipe_mensal=soma_equipe,
        custo_canteiro_mensal=soma_canteiro,
        fator_logistica=f_log,
        custo_mensal_indireto=mensal,
        prazo_meses=entrada.prazo_meses,
        custo_indireto_total=total,
    )
