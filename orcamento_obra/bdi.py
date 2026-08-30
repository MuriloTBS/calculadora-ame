"""Camada 4 (parte) — taxa de BDI.

Fórmula consagrada (TCU, Acórdão 2622/2013), com Seguros+Garantias agrupados e
Risco isolado, conforme a seção E da especificação:

    BDI = [ (1 + AC + S+G + R) · (1 + DF) · (1 + L) / (1 - I) ] - 1

O divisor ``(1 - I)`` já embute a incidência de tributos sobre o preço; portanto
``PV = CT · (1 + BDI)`` — sem nova divisão por ``(1 - I)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .coeficientes import ComponentesBDI


@dataclass(frozen=True)
class ResultadoBDI:
    componentes: ComponentesBDI
    taxa_bdi: float        # fração (0.3049 = 30,49%)
    multiplicador: float   # 1 + taxa_bdi
    memoria: Mapping[str, float]


def calcular_bdi(componentes: ComponentesBDI) -> ResultadoBDI:
    c = componentes
    if not 0.0 <= c.tributos < 1.0:
        raise ValueError("tributos (I) deve estar em [0, 1).")
    for nome, valor in (
        ("administracao_central", c.administracao_central),
        ("seguros_garantias", c.seguros_garantias),
        ("risco_imprevistos", c.risco_imprevistos),
        ("despesas_financeiras", c.despesas_financeiras),
        ("lucro", c.lucro),
    ):
        if valor < 0:
            raise ValueError(f"Componente de BDI '{nome}' não pode ser negativo.")

    grupo_indiretos = (
        1 + c.administracao_central + c.seguros_garantias + c.risco_imprevistos
    )
    fator_df = 1 + c.despesas_financeiras
    fator_lucro = 1 + c.lucro
    divisor_tributos = 1 - c.tributos

    numerador = grupo_indiretos * fator_df * fator_lucro
    taxa = numerador / divisor_tributos - 1

    memoria = {
        "grupo_indiretos_(1+AC+SG+R)": grupo_indiretos,
        "fator_despesas_financeiras_(1+DF)": fator_df,
        "fator_lucro_(1+L)": fator_lucro,
        "divisor_tributos_(1-I)": divisor_tributos,
        "numerador": numerador,
        "taxa_bdi": taxa,
    }
    return ResultadoBDI(c, taxa, 1 + taxa, memoria)
