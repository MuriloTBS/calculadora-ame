"""Orquestrador — encadeia as 4 camadas e produz o resultado completo.

    A_eq  -> CD  -> CI  -> CT = (CD + CI)·(1 + contingência)  -> PV = CT·(1 + BDI)
"""

from __future__ import annotations

from dataclasses import dataclass

from .areas import QuadroAreas, calcular_quadro_areas
from .bdi import ResultadoBDI, calcular_bdi
from .curva_s import CurvaS, gerar_curva_s
from .custo_direto import CustoDireto, calcular_custo_direto
from .custo_indireto import CustoIndireto, calcular_custo_indireto
from .entradas import EntradaProjeto, validar_entrada


@dataclass(frozen=True)
class IndicadoresUnitarios:
    custo_direto_por_m2_equivalente: float
    custo_indireto_por_m2_equivalente: float
    custo_total_por_m2_real: float
    custo_total_por_m2_equivalente: float
    preco_venda_por_m2_real: float
    preco_venda_por_m2_equivalente: float


@dataclass(frozen=True)
class DemonstrativoFinanceiro:
    custo_direto_total: float                 # CD
    custo_indireto_total: float               # CI
    subtotal_custos: float                    # CD + CI
    taxa_contingencia: float
    valor_contingencia: float
    custo_total_obra: float                   # CT
    taxa_bdi: float
    valor_bdi: float                          # PV - CT
    valor_global_proposta: float             # PV
    margem_lucro_bruta_estimada: float        # L · PV (informativo)
    participacao_custo_direto: float          # CD / PV
    participacao_custo_indireto: float        # CI / PV
    participacao_contingencia: float          # contingência / PV
    participacao_bdi: float                   # BDI / PV


@dataclass(frozen=True)
class ResultadoOrcamento:
    entrada: EntradaProjeto
    avisos: tuple[str, ...]
    quadro_areas: QuadroAreas
    custo_direto: CustoDireto
    custo_indireto: CustoIndireto
    bdi: ResultadoBDI
    indicadores: IndicadoresUnitarios
    demonstrativo: DemonstrativoFinanceiro
    curva_s: CurvaS


def calcular_orcamento(
    entrada: EntradaProjeto,
    forma_curva_s: float = 2.2,
    base_curva_s: str = "custo_total",
) -> ResultadoOrcamento:
    if base_curva_s not in ("custo_total", "preco_venda"):
        raise ValueError("base_curva_s deve ser 'custo_total' ou 'preco_venda'.")

    avisos = validar_entrada(entrada)

    quadro = calcular_quadro_areas(entrada.areas, entrada.coef_area)
    if quadro.area_equivalente_total <= 0:
        raise ValueError(
            "Área equivalente total é zero — informe ao menos uma área > 0."
        )

    cd = calcular_custo_direto(entrada, quadro)
    ci = calcular_custo_indireto(entrada)
    bdi = calcular_bdi(entrada.bdi)

    subtotal = cd.custo_direto_total + ci.custo_indireto_total
    valor_contingencia = subtotal * entrada.taxa_contingencia
    ct = subtotal + valor_contingencia
    pv = ct * bdi.multiplicador
    valor_bdi = pv - ct

    a_eq = quadro.area_equivalente_total
    a_real = quadro.area_real_total

    indicadores = IndicadoresUnitarios(
        custo_direto_por_m2_equivalente=cd.custo_direto_total / a_eq,
        custo_indireto_por_m2_equivalente=ci.custo_indireto_total / a_eq,
        custo_total_por_m2_real=ct / a_real,
        custo_total_por_m2_equivalente=ct / a_eq,
        preco_venda_por_m2_real=pv / a_real,
        preco_venda_por_m2_equivalente=pv / a_eq,
    )

    demonstrativo = DemonstrativoFinanceiro(
        custo_direto_total=cd.custo_direto_total,
        custo_indireto_total=ci.custo_indireto_total,
        subtotal_custos=subtotal,
        taxa_contingencia=entrada.taxa_contingencia,
        valor_contingencia=valor_contingencia,
        custo_total_obra=ct,
        taxa_bdi=bdi.taxa_bdi,
        valor_bdi=valor_bdi,
        valor_global_proposta=pv,
        margem_lucro_bruta_estimada=entrada.bdi.lucro * pv,
        participacao_custo_direto=cd.custo_direto_total / pv,
        participacao_custo_indireto=ci.custo_indireto_total / pv,
        participacao_contingencia=valor_contingencia / pv,
        participacao_bdi=valor_bdi / pv,
    )

    valor_base_curva = pv if base_curva_s == "preco_venda" else ct
    curva = gerar_curva_s(
        valor_base_curva, entrada.prazo_meses, forma_curva_s, base_curva_s
    )

    return ResultadoOrcamento(
        entrada=entrada,
        avisos=tuple(avisos),
        quadro_areas=quadro,
        custo_direto=cd,
        custo_indireto=ci,
        bdi=bdi,
        indicadores=indicadores,
        demonstrativo=demonstrativo,
        curva_s=curva,
    )
