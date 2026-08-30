import pytest

from orcamento_obra import (
    AreasProjeto,
    EntradaProjeto,
    EquipeTecnicaMensal,
    InfraCanteiroMensal,
    calcular_custo_indireto,
)

_EQUIPE_DEFAULT = 18_000 + 7_500 + 4_500 + 5_500          # 35_500
_CANTEIRO_DEFAULT = 1_500 + 2_500 + 3_000 + 2_000 + 1_200  # 10_200


def _entrada(**kwargs):
    base = dict(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=1_000.0,
        prazo_meses=10,
    )
    base.update(kwargs)
    return EntradaProjeto(**base)


def test_custo_indireto_default_urbano():
    ci = calcular_custo_indireto(_entrada())

    assert ci.custo_equipe_mensal == _EQUIPE_DEFAULT
    assert ci.custo_canteiro_mensal == _CANTEIRO_DEFAULT
    assert ci.custo_mensal_indireto == pytest.approx(_EQUIPE_DEFAULT + _CANTEIRO_DEFAULT)
    assert ci.custo_indireto_total == pytest.approx(45_700.0 * 10)


def test_fator_logistica_area_remota_encarece():
    ci = calcular_custo_indireto(_entrada(logistica="area_remota"))  # F = 1.15

    assert ci.fator_logistica == 1.15
    assert ci.custo_mensal_indireto == pytest.approx(45_700.0 * 1.15)


def test_componentes_editaveis():
    ci = calcular_custo_indireto(
        _entrada(
            equipe_tecnica=EquipeTecnicaMensal(engenheiro_residente=25_000.0),
            infra_canteiro=InfraCanteiroMensal(andaimes=0.0),
        )
    )

    assert ci.custo_equipe_mensal == 25_000 + 7_500 + 4_500 + 5_500
    assert ci.custo_canteiro_mensal == _CANTEIRO_DEFAULT - 3_000
