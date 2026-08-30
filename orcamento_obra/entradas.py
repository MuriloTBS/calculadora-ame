"""Estruturas de entrada da calculadora e validação de contorno."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Mapping

from .coeficientes import (
    CONTINGENCIA_PADRAO,
    FAIXAS_PESO_MACROETAPA,
    FATOR_LOGISTICA,
    FATOR_PADRAO_CONSTRUTIVO,
    FATOR_SOLO_TOPOGRAFIA,
    CoeficientesArea,
    ComponentesBDI,
    EquipeTecnicaMensal,
    InfraCanteiroMensal,
    pesos_macroetapa_default,
)


@dataclass(frozen=True)
class AreasProjeto:
    """Áreas reais do projeto por tipologia, em m².

    Os nomes dos campos espelham ``CoeficientesArea`` para o pareamento
    área x fator ``k``.
    """

    privativa_coberta_padrao: float = 0.0
    garagem_coberta_subsolo: float = 0.0
    garagem_descoberta: float = 0.0
    varanda_sacada_aberta: float = 0.0
    area_tecnica_reservatorio: float = 0.0
    lazer_coberto: float = 0.0
    lazer_descoberto_piscina: float = 0.0

    def __post_init__(self) -> None:
        for f in fields(self):
            if getattr(self, f.name) < 0:
                raise ValueError(f"Área '{f.name}' não pode ser negativa.")


@dataclass(frozen=True)
class EntradaProjeto:
    """Conjunto completo de parâmetros para um orçamento paramétrico."""

    areas: AreasProjeto
    custo_base_m2: float  # R$/m² — referência CUB estadual ou SINAPI

    padrao_construtivo: str = "medio"          # chave de FATOR_PADRAO_CONSTRUTIVO
    solo_topografia: str = "plano_solo_firme"  # chave de FATOR_SOLO_TOPOGRAFIA
    logistica: str = "urbano_central"          # chave de FATOR_LOGISTICA
    fator_regiao: float = 1.00                 # ajuste regional livre
    prazo_meses: int = 12

    coef_area: CoeficientesArea = field(default_factory=CoeficientesArea)
    pesos_macroetapa: Mapping[str, float] = field(
        default_factory=pesos_macroetapa_default
    )
    normalizar_pesos: bool = True

    equipe_tecnica: EquipeTecnicaMensal = field(default_factory=EquipeTecnicaMensal)
    infra_canteiro: InfraCanteiroMensal = field(default_factory=InfraCanteiroMensal)

    bdi: ComponentesBDI = field(default_factory=ComponentesBDI)
    taxa_contingencia: float = CONTINGENCIA_PADRAO

    # Multiplicadores explícitos: quando informados, sobrepõem as tabelas.
    fator_padrao_override: float | None = None
    fator_solo_override: float | None = None
    fator_logistica_override: float | None = None

    def __post_init__(self) -> None:
        if self.custo_base_m2 <= 0:
            raise ValueError("custo_base_m2 deve ser > 0 (R$/m²).")
        if self.prazo_meses <= 0:
            raise ValueError("prazo_meses deve ser > 0.")
        if self.fator_regiao <= 0:
            raise ValueError("fator_regiao deve ser > 0.")
        if (
            self.fator_padrao_override is None
            and self.padrao_construtivo not in FATOR_PADRAO_CONSTRUTIVO
        ):
            raise ValueError(
                f"padrao_construtivo inválido: {self.padrao_construtivo!r}. "
                f"Use um de {sorted(FATOR_PADRAO_CONSTRUTIVO)} ou informe "
                f"fator_padrao_override."
            )
        if (
            self.fator_solo_override is None
            and self.solo_topografia not in FATOR_SOLO_TOPOGRAFIA
        ):
            raise ValueError(
                f"solo_topografia inválido: {self.solo_topografia!r}. "
                f"Use um de {sorted(FATOR_SOLO_TOPOGRAFIA)} ou informe "
                f"fator_solo_override."
            )
        if (
            self.fator_logistica_override is None
            and self.logistica not in FATOR_LOGISTICA
        ):
            raise ValueError(
                f"logistica inválida: {self.logistica!r}. "
                f"Use um de {sorted(FATOR_LOGISTICA)} ou informe "
                f"fator_logistica_override."
            )

    # -- fatores efetivos ---------------------------------------------------- #
    @property
    def fator_padrao(self) -> float:
        if self.fator_padrao_override is not None:
            return self.fator_padrao_override
        return FATOR_PADRAO_CONSTRUTIVO[self.padrao_construtivo]

    @property
    def fator_solo(self) -> float:
        if self.fator_solo_override is not None:
            return self.fator_solo_override
        return FATOR_SOLO_TOPOGRAFIA[self.solo_topografia]

    @property
    def fator_logistica(self) -> float:
        if self.fator_logistica_override is not None:
            return self.fator_logistica_override
        return FATOR_LOGISTICA[self.logistica]


_TOLERANCIA_FAIXA = 1e-6


def validar_entrada(entrada: EntradaProjeto) -> list[str]:
    """Retorna avisos (não bloqueantes) sobre a consistência da entrada."""
    avisos: list[str] = []

    for etapa, (inf, sup) in FAIXAS_PESO_MACROETAPA.items():
        peso = entrada.pesos_macroetapa.get(etapa)
        if peso is None:
            avisos.append(f"Macroetapa '{etapa}' sem peso informado (assumido 0).")
            continue
        if peso < inf - _TOLERANCIA_FAIXA or peso > sup + _TOLERANCIA_FAIXA:
            avisos.append(
                f"Peso de '{etapa}' ({peso:.1%}) fora da faixa típica "
                f"{inf:.0%}–{sup:.0%}."
            )

    soma_pesos = sum(entrada.pesos_macroetapa.values())
    if not entrada.normalizar_pesos and abs(soma_pesos - 1.0) > 0.02:
        avisos.append(
            f"Soma dos pesos de macroetapa = {soma_pesos:.1%} e "
            f"normalizar_pesos=False; o Custo Direto ficará escalado por esse total."
        )

    avisos.append(
        "Tributos do BDI no ponto médio genérico "
        f"({entrada.bdi.tributos:.2%}). Ajuste ao regime real "
        "(Simples / Lucro Presumido / RET)."
    )

    if entrada.taxa_contingencia > 0 and entrada.bdi.risco_imprevistos > 0:
        avisos.append(
            f"Contingência ({entrada.taxa_contingencia:.2%}) é adicional ao "
            f"componente Risco do BDI ({entrada.bdi.risco_imprevistos:.2%}); "
            "confirme que não há dupla contagem."
        )

    if entrada.fator_solo != 1.0:
        avisos.append(
            f"F_solo = {entrada.fator_solo:.3f} aplicado apenas às macroetapas "
            "01 (Preliminares) e 02 (Fundações) — sensibilidade de solo."
        )

    return avisos
