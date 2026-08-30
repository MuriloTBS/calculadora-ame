"""Calculadora paramétrica de custo de obra por m² (NBR 12.721 / BDI TCU 2622/2013).

Uso mínimo::

    from orcamento_obra import AreasProjeto, EntradaProjeto, calcular_orcamento, formatar_relatorio

    entrada = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=1800, garagem_coberta_subsolo=600),
        custo_base_m2=2600.0,
        padrao_construtivo="medio",
        solo_topografia="aclive_declive_medio",
        prazo_meses=18,
    )
    resultado = calcular_orcamento(entrada)
    print(formatar_relatorio(resultado))
"""

from .areas import QuadroAreas, calcular_quadro_areas
from .bdi import ResultadoBDI, calcular_bdi
from .coeficientes import (
    CONTINGENCIA_PADRAO,
    FATOR_LOGISTICA,
    FATOR_PADRAO_CONSTRUTIVO,
    FATOR_SOLO_TOPOGRAFIA,
    MACROETAPAS,
    ROTULOS_MACROETAPA,
    CoeficientesArea,
    ComponentesBDI,
    EquipeTecnicaMensal,
    InfraCanteiroMensal,
    pesos_macroetapa_default,
)
from .curva_s import CurvaS, gerar_curva_s
from .custo_direto import CustoDireto, calcular_custo_direto
from .custo_indireto import CustoIndireto, calcular_custo_indireto
from .entradas import AreasProjeto, EntradaProjeto, validar_entrada
from .orcamento import (
    DemonstrativoFinanceiro,
    IndicadoresUnitarios,
    ResultadoOrcamento,
    calcular_orcamento,
)
from .relatorio import formatar_relatorio

__all__ = [
    "AreasProjeto",
    "EntradaProjeto",
    "CoeficientesArea",
    "ComponentesBDI",
    "EquipeTecnicaMensal",
    "InfraCanteiroMensal",
    "pesos_macroetapa_default",
    "validar_entrada",
    "calcular_quadro_areas",
    "QuadroAreas",
    "calcular_custo_direto",
    "CustoDireto",
    "calcular_custo_indireto",
    "CustoIndireto",
    "calcular_bdi",
    "ResultadoBDI",
    "gerar_curva_s",
    "CurvaS",
    "calcular_orcamento",
    "ResultadoOrcamento",
    "IndicadoresUnitarios",
    "DemonstrativoFinanceiro",
    "formatar_relatorio",
    "MACROETAPAS",
    "ROTULOS_MACROETAPA",
    "FATOR_PADRAO_CONSTRUTIVO",
    "FATOR_SOLO_TOPOGRAFIA",
    "FATOR_LOGISTICA",
    "CONTINGENCIA_PADRAO",
]
