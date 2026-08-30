"""Camada 2 — Custo Direto Total, decomposto por macroetapa.

    CD = ( Σ_j  peso_j · custo_base · F_padrão · F_região · F_solo_j ) · A_eq

``F_solo_j`` vale ``F_solo`` apenas nas macroetapas 01 (Preliminares) e 02
(Fundações) e 1.0 nas demais — assim solo/topografia desfavoráveis elevam o CD
e aumentam a participação relativa dessas etapas (regra de negócio 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .areas import QuadroAreas
from .coeficientes import (
    ETAPAS_SENSIVEIS_SOLO,
    MACROETAPAS,
    ROTULOS_MACROETAPA,
)
from .entradas import EntradaProjeto


@dataclass(frozen=True)
class ItemMacroetapa:
    chave: str
    rotulo: str
    peso_base: float          # peso normalizado, antes do ajuste de solo
    fator_solo_aplicado: float
    peso_aplicado: float      # peso_base · fator_solo_aplicado
    custo_total: float        # R$
    custo_por_m2_real: float
    custo_por_m2_equivalente: float
    percentual: float         # custo_total / CD


@dataclass(frozen=True)
class CustoDireto:
    custo_base_m2: float
    fator_padrao: float
    fator_regiao: float
    fator_solo: float
    custo_base_ajustado_m2: float  # custo_base · F_padrão · F_região (sem solo)
    custo_direto_total: float
    custo_direto_por_m2_equivalente: float
    custo_direto_por_m2_real: float
    itens: tuple[ItemMacroetapa, ...]


def _pesos_normalizados(
    pesos: Mapping[str, float], normalizar: bool
) -> dict[str, float]:
    bruto = {etapa: float(pesos.get(etapa, 0.0)) for etapa in MACROETAPAS}
    total = sum(bruto.values())
    if normalizar and total > 0:
        return {etapa: valor / total for etapa, valor in bruto.items()}
    return bruto


def calcular_custo_direto(
    entrada: EntradaProjeto, quadro_areas: QuadroAreas
) -> CustoDireto:
    f_padrao = entrada.fator_padrao
    f_regiao = entrada.fator_regiao
    f_solo = entrada.fator_solo

    a_eq = quadro_areas.area_equivalente_total
    a_real = quadro_areas.area_real_total

    base_ajustada = entrada.custo_base_m2 * f_padrao * f_regiao
    pesos = _pesos_normalizados(entrada.pesos_macroetapa, entrada.normalizar_pesos)

    aplicados: list[tuple[str, float, float, float]] = []
    for etapa in MACROETAPAS:
        peso_base = pesos[etapa]
        fator = f_solo if etapa in ETAPAS_SENSIVEIS_SOLO else 1.0
        aplicados.append((etapa, peso_base, fator, peso_base * fator))

    soma_aplicada = sum(p for _, _, _, p in aplicados)
    cd_total = base_ajustada * a_eq * soma_aplicada

    itens: list[ItemMacroetapa] = []
    for etapa, peso_base, fator, peso_aplicado in aplicados:
        custo = base_ajustada * a_eq * peso_aplicado
        itens.append(
            ItemMacroetapa(
                chave=etapa,
                rotulo=ROTULOS_MACROETAPA[etapa],
                peso_base=peso_base,
                fator_solo_aplicado=fator,
                peso_aplicado=peso_aplicado,
                custo_total=custo,
                custo_por_m2_real=custo / a_real if a_real else 0.0,
                custo_por_m2_equivalente=custo / a_eq if a_eq else 0.0,
                percentual=custo / cd_total if cd_total else 0.0,
            )
        )

    return CustoDireto(
        custo_base_m2=entrada.custo_base_m2,
        fator_padrao=f_padrao,
        fator_regiao=f_regiao,
        fator_solo=f_solo,
        custo_base_ajustado_m2=base_ajustada,
        custo_direto_total=cd_total,
        custo_direto_por_m2_equivalente=cd_total / a_eq if a_eq else 0.0,
        custo_direto_por_m2_real=cd_total / a_real if a_real else 0.0,
        itens=tuple(itens),
    )
