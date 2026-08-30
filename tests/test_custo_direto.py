import pytest

from orcamento_obra import (
    AreasProjeto,
    CoeficientesArea,
    EntradaProjeto,
    calcular_custo_direto,
    calcular_quadro_areas,
)
from orcamento_obra.coeficientes import MACROETAPAS


def _quadro(area_privativa: float = 100.0):
    return calcular_quadro_areas(
        AreasProjeto(privativa_coberta_padrao=area_privativa), CoeficientesArea()
    )


def test_custo_direto_etapa_unica_normalizada():
    # Arrange — todo o peso na superestrutura, fatores neutros
    pesos = {etapa: 0.0 for etapa in MACROETAPAS}
    pesos["03_superestrutura"] = 1.0
    entrada = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=1_000.0,
        pesos_macroetapa=pesos,
        normalizar_pesos=True,
    )

    # Act
    cd = calcular_custo_direto(entrada, _quadro())

    # Assert — 1000 R$/m² * 100 m² * 100%
    assert cd.custo_direto_total == pytest.approx(100_000.0)
    supra = next(i for i in cd.itens if i.chave == "03_superestrutura")
    assert supra.percentual == pytest.approx(1.0)


def test_pesos_default_sao_normalizados_para_100pct():
    entrada = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=1_000.0,
    )

    cd = calcular_custo_direto(entrada, _quadro())

    assert sum(i.percentual for i in cd.itens) == pytest.approx(1.0)
    # base neutra: CD/m²eq == custo_base ajustado
    assert cd.custo_direto_por_m2_equivalente == pytest.approx(1_000.0)


def test_sensibilidade_de_solo_eleva_fundacao_e_preliminares():
    base = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=100.0), custo_base_m2=1_000.0
    )
    ruim = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=1_000.0,
        solo_topografia="declive_acentuado_solo_mole",
    )

    cd_base = calcular_custo_direto(base, _quadro())
    cd_ruim = calcular_custo_direto(ruim, _quadro())

    assert cd_ruim.custo_direto_total > cd_base.custo_direto_total

    def pct(cd, chave):
        return next(i for i in cd.itens if i.chave == chave).percentual

    assert pct(cd_ruim, "01_preliminares_terraplenagem") > pct(
        cd_base, "01_preliminares_terraplenagem"
    )
    assert pct(cd_ruim, "02_fundacoes_infraestrutura") > pct(
        cd_base, "02_fundacoes_infraestrutura"
    )
    # etapa não sensível perde participação relativa
    assert pct(cd_ruim, "08_revestimentos_parede_piso") < pct(
        cd_base, "08_revestimentos_parede_piso"
    )


def test_fatores_padrao_e_regiao_multiplicam_a_base():
    entrada = EntradaProjeto(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=1_000.0,
        padrao_construtivo="alto",   # F = 1.375
        fator_regiao=1.10,
    )

    cd = calcular_custo_direto(entrada, _quadro())

    assert cd.custo_base_ajustado_m2 == pytest.approx(1_000.0 * 1.375 * 1.10)
