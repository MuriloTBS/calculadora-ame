import pytest

from orcamento_obra import (
    AreasProjeto,
    ComponentesBDI,
    EntradaProjeto,
    calcular_orcamento,
    formatar_relatorio,
)


def _entrada_exemplo(**kwargs):
    base = dict(
        areas=AreasProjeto(
            privativa_coberta_padrao=1_800.0,
            garagem_coberta_subsolo=600.0,
            varanda_sacada_aberta=180.0,
        ),
        custo_base_m2=2_600.0,
        padrao_construtivo="medio",
        solo_topografia="aclive_declive_medio",
        logistica="condominio_fechado",
        prazo_meses=18,
    )
    base.update(kwargs)
    return EntradaProjeto(**base)


def test_encadeamento_das_quatro_camadas():
    res = calcular_orcamento(_entrada_exemplo())
    d = res.demonstrativo

    assert d.subtotal_custos == pytest.approx(
        res.custo_direto.custo_direto_total + res.custo_indireto.custo_indireto_total
    )
    assert d.custo_total_obra == pytest.approx(
        d.subtotal_custos * (1 + d.taxa_contingencia)
    )
    assert d.valor_global_proposta == pytest.approx(
        d.custo_total_obra * res.bdi.multiplicador
    )
    assert d.valor_global_proposta > d.custo_total_obra > d.subtotal_custos


def test_participacoes_somam_um():
    d = calcular_orcamento(_entrada_exemplo()).demonstrativo

    total = (
        d.participacao_custo_direto
        + d.participacao_custo_indireto
        + d.participacao_contingencia
        + d.participacao_bdi
    )
    assert total == pytest.approx(1.0)


def test_indicadores_unitarios_consistentes():
    res = calcular_orcamento(_entrada_exemplo())
    i = res.indicadores
    a_real = res.quadro_areas.area_real_total
    a_eq = res.quadro_areas.area_equivalente_total

    assert i.custo_total_por_m2_real == pytest.approx(
        res.demonstrativo.custo_total_obra / a_real
    )
    assert i.preco_venda_por_m2_equivalente == pytest.approx(
        res.demonstrativo.valor_global_proposta / a_eq
    )


def test_curva_s_usa_ct_por_padrao_e_pode_usar_pv():
    ct_res = calcular_orcamento(_entrada_exemplo())
    pv_res = calcular_orcamento(_entrada_exemplo(), base_curva_s="preco_venda")

    assert ct_res.curva_s.valor_base == pytest.approx(
        ct_res.demonstrativo.custo_total_obra
    )
    assert pv_res.curva_s.valor_base == pytest.approx(
        pv_res.demonstrativo.valor_global_proposta
    )
    assert len(ct_res.curva_s.pontos) == 18


def test_relatorio_contem_todos_os_blocos():
    texto = formatar_relatorio(calcular_orcamento(_entrada_exemplo()))

    for marcador in (
        "1. QUADRO RESUMO DE ÁREAS",
        "2. INDICADORES DE CUSTO UNITÁRIO",
        "3. DETALHAMENTO POR MACROETAPA",
        "4. DEMONSTRATIVO FINANCEIRO E BDI",
        "5. CURVA DE DESEMBOLSO ESTIMADA (CURVA S)",
        "VALOR GLOBAL DA PROPOSTA",
    ):
        assert marcador in texto


def test_entradas_invalidas_levantam_erro():
    with pytest.raises(ValueError):
        _entrada_exemplo(custo_base_m2=0.0)
    with pytest.raises(ValueError):
        _entrada_exemplo(prazo_meses=0)
    with pytest.raises(ValueError):
        _entrada_exemplo(padrao_construtivo="inexistente")


def test_area_equivalente_zero_e_bloqueada():
    with pytest.raises(ValueError):
        calcular_orcamento(
            EntradaProjeto(areas=AreasProjeto(), custo_base_m2=2_600.0)
        )


def test_regime_tributario_altera_proposta():
    presumido = calcular_orcamento(_entrada_exemplo(bdi=ComponentesBDI(tributos=0.0665)))
    com_cprb = calcular_orcamento(_entrada_exemplo(bdi=ComponentesBDI(tributos=0.1115)))

    assert (
        com_cprb.demonstrativo.valor_global_proposta
        > presumido.demonstrativo.valor_global_proposta
    )
