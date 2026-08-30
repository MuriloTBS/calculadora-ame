from orcamento_obra import (
    AreasProjeto,
    ComponentesBDI,
    EntradaProjeto,
    pesos_macroetapa_default,
    validar_entrada,
)


def _entrada(**kwargs):
    base = dict(
        areas=AreasProjeto(privativa_coberta_padrao=100.0),
        custo_base_m2=2_000.0,
    )
    base.update(kwargs)
    return EntradaProjeto(**base)


def test_pesos_default_ficam_dentro_das_faixas():
    avisos = validar_entrada(_entrada())

    assert not any("fora da faixa" in a for a in avisos)


def test_peso_fora_da_faixa_gera_aviso():
    pesos = pesos_macroetapa_default()
    pesos["03_superestrutura"] = 0.40  # faixa típica 20%–26%

    avisos = validar_entrada(_entrada(pesos_macroetapa=pesos))

    assert any("03_superestrutura" in a and "fora da faixa" in a for a in avisos)


def test_aviso_de_regime_tributario_sempre_presente():
    avisos = validar_entrada(_entrada())

    assert any("Tributos do BDI" in a for a in avisos)


def test_aviso_de_dupla_contagem_contingencia_x_risco():
    avisos = validar_entrada(_entrada(taxa_contingencia=0.03))

    assert any("dupla contagem" in a for a in avisos)


def test_sem_dupla_contagem_quando_contingencia_zero():
    avisos = validar_entrada(_entrada(taxa_contingencia=0.0))

    assert not any("dupla contagem" in a for a in avisos)


def test_aviso_de_sensibilidade_de_solo():
    avisos = validar_entrada(_entrada(solo_topografia="aclive_declive_medio"))

    assert any("sensibilidade de solo" in a for a in avisos)


def test_fator_override_dispensa_chave_valida():
    entrada = _entrada(padrao_construtivo="qualquer", fator_padrao_override=1.2)

    assert entrada.fator_padrao == 1.2


def test_area_negativa_bloqueada():
    import pytest

    with pytest.raises(ValueError):
        AreasProjeto(privativa_coberta_padrao=-10.0)
