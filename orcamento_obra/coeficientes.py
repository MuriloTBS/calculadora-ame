"""Coeficientes paramétricos e seus valores default.

Todo default aqui é o **ponto médio** da faixa indicada na especificação
metodológica. Nenhum valor é fixo: as dataclasses são criadas com os campos
que se deseja sobrescrever e o restante assume o default de ponto médio; as
tabelas (dicionários) podem ser copiadas e ajustadas antes de montar a entrada.

Referências:
* NBR 12.721 — áreas equivalentes de construção (fatores ``k``).
* TCU, Acórdão 2622/2013 — fórmula consagrada de BDI.
* Faixas de peso por macroetapa — prática de orçamento paramétrico (SINAPI/CUB).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


def meio(inferior: float, superior: float) -> float:
    """Ponto médio da faixa ``[inferior, superior]``."""
    return (inferior + superior) / 2


# --------------------------------------------------------------------------- #
# A. Coeficientes de equivalência de área (NBR 12.721)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CoeficientesArea:
    """Fatores ``k`` de área equivalente. Default = ponto médio da faixa NBR."""

    privativa_coberta_padrao: float = 1.00
    garagem_coberta_subsolo: float = meio(0.50, 0.75)      # 0.625
    garagem_descoberta: float = meio(0.30, 0.50)           # 0.400
    varanda_sacada_aberta: float = meio(0.50, 0.60)        # 0.550
    area_tecnica_reservatorio: float = meio(0.50, 0.75)    # 0.625
    lazer_coberto: float = meio(0.80, 1.00)                # 0.900
    lazer_descoberto_piscina: float = meio(0.30, 0.50)     # 0.400


# --------------------------------------------------------------------------- #
# C. Fatores de condicionamento
# --------------------------------------------------------------------------- #
FATOR_PADRAO_CONSTRUTIVO: Mapping[str, float] = {
    "baixo_popular": meio(0.80, 0.90),   # 0.850
    "medio": 1.00,
    "alto": meio(1.30, 1.45),            # 1.375
    "luxo_premium": meio(1.70, 2.20),    # 1.950
}

FATOR_SOLO_TOPOGRAFIA: Mapping[str, float] = {
    "plano_solo_firme": 1.00,
    "aclive_declive_medio": meio(1.08, 1.15),          # 1.115
    "declive_acentuado_solo_mole": meio(1.20, 1.40),   # 1.300
}

# Aplicado ao custo indireto (mobilização, restrição de horário, transporte).
FATOR_LOGISTICA: Mapping[str, float] = {
    "urbano_central": 1.00,
    "condominio_fechado": 1.05,
    "area_remota": 1.15,
}


# --------------------------------------------------------------------------- #
# 3. Estrutura Analítica do Projeto — macroetapas e pesos
# --------------------------------------------------------------------------- #
MACROETAPAS: tuple[str, ...] = (
    "01_preliminares_terraplenagem",
    "02_fundacoes_infraestrutura",
    "03_superestrutura",
    "04_alvenarias_vedacoes",
    "05_coberturas_impermeabilizacoes",
    "06_hidrossanitarias_gas",
    "07_eletricas_especiais",
    "08_revestimentos_parede_piso",
    "09_esquadrias_vidros_portas",
    "10_pinturas_tratamentos",
    "11_loucas_metais_complementares",
    "12_limpeza_pos_obra_entrega",
)

ROTULOS_MACROETAPA: Mapping[str, str] = {
    "01_preliminares_terraplenagem": "01. Serviços Preliminares & Terraplenagem",
    "02_fundacoes_infraestrutura": "02. Fundações e Infraestrutura",
    "03_superestrutura": "03. Superestrutura",
    "04_alvenarias_vedacoes": "04. Alvenarias e Vedações",
    "05_coberturas_impermeabilizacoes": "05. Coberturas e Impermeabilizações",
    "06_hidrossanitarias_gas": "06. Instalações Hidrossanitárias e Gás",
    "07_eletricas_especiais": "07. Instalações Elétricas e Especiais",
    "08_revestimentos_parede_piso": "08. Revestimentos de Parede e Pisos",
    "09_esquadrias_vidros_portas": "09. Esquadrias, Vidros e Portas",
    "10_pinturas_tratamentos": "10. Pinturas e Tratamentos",
    "11_loucas_metais_complementares": "11. Louças, Metais e Complementares",
    "12_limpeza_pos_obra_entrega": "12. Limpeza Pós-Obra e Entrega",
}

# Faixa de participação de cada macroetapa no Custo Direto (fração).
FAIXAS_PESO_MACROETAPA: Mapping[str, tuple[float, float]] = {
    "01_preliminares_terraplenagem": (0.04, 0.07),
    "02_fundacoes_infraestrutura": (0.07, 0.12),
    "03_superestrutura": (0.20, 0.26),
    "04_alvenarias_vedacoes": (0.06, 0.09),
    "05_coberturas_impermeabilizacoes": (0.04, 0.07),
    "06_hidrossanitarias_gas": (0.06, 0.09),
    "07_eletricas_especiais": (0.06, 0.09),
    "08_revestimentos_parede_piso": (0.14, 0.19),
    "09_esquadrias_vidros_portas": (0.06, 0.10),
    "10_pinturas_tratamentos": (0.05, 0.08),
    "11_loucas_metais_complementares": (0.03, 0.06),
    "12_limpeza_pos_obra_entrega": (0.01, 0.03),
}

# Macroetapas cuja participação sobe automaticamente com solo/topografia
# desfavoráveis (regra de negócio 2 — sensibilidade de solo).
ETAPAS_SENSIVEIS_SOLO: frozenset[str] = frozenset(
    {"01_preliminares_terraplenagem", "02_fundacoes_infraestrutura"}
)


def pesos_macroetapa_default() -> dict[str, float]:
    """Peso de cada macroetapa no ponto médio da faixa.

    A soma dos pontos médios é ~1.035; por padrão o motor normaliza para 1.000
    (ver ``EntradaProjeto.normalizar_pesos``).
    """
    return {etapa: meio(*faixa) for etapa, faixa in FAIXAS_PESO_MACROETAPA.items()}


# --------------------------------------------------------------------------- #
# D. Custos indiretos mensais (valores de referência de mercado — editáveis)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class EquipeTecnicaMensal:
    """Custo mensal da equipe técnica e de gestão (R$/mês)."""

    engenheiro_residente: float = 18_000.0
    mestre_de_obras: float = 7_500.0
    encarregado: float = 4_500.0
    tecnico_seguranca: float = 5_500.0


@dataclass(frozen=True)
class InfraCanteiroMensal:
    """Custo mensal de infraestrutura de canteiro (R$/mês)."""

    ligacao_provisoria_agua_luz: float = 1_500.0
    locacao_containers: float = 2_500.0
    andaimes: float = 3_000.0
    cacambas_entulho: float = 2_000.0
    banheiros_quimicos: float = 1_200.0


# --------------------------------------------------------------------------- #
# E. Componentes de BDI (fração — ponto médio das faixas da seção E)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ComponentesBDI:
    """Componentes da taxa de BDI. Valores em fração (0.0425 = 4,25%)."""

    administracao_central: float = meio(0.0300, 0.0550)   # 0.042500
    seguros_garantias: float = meio(0.0080, 0.0150)        # 0.011500
    risco_imprevistos: float = meio(0.0090, 0.0180)        # 0.013500
    despesas_financeiras: float = meio(0.0050, 0.0120)     # 0.008500
    lucro: float = meio(0.0600, 0.1200)                    # 0.090000
    tributos: float = meio(0.0565, 0.1450)                 # 0.100750


# Reserva física/quantitativa aplicada sobre (CD + CI), distinta do componente
# "Risco e Imprevistos" do BDI. Zerar se o risco já estiver todo no BDI.
CONTINGENCIA_PADRAO: float = 0.02
