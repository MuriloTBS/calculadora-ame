import pytest

from orcamento_obra import gerar_curva_s


def test_curva_s_soma_o_valor_base():
    curva = gerar_curva_s(1_000_000.0, prazo_meses=12)

    assert sum(p.desembolso_periodo for p in curva.pontos) == pytest.approx(1_000_000.0)
    assert curva.pontos[-1].percentual_acumulado == pytest.approx(1.0)
    assert curva.pontos[-1].desembolso_acumulado == pytest.approx(1_000_000.0)


def test_acumulado_e_monotonico_crescente():
    curva = gerar_curva_s(500_000.0, prazo_meses=24, forma=2.2)

    acumulados = [p.percentual_acumulado for p in curva.pontos]
    assert acumulados == sorted(acumulados)
    assert all(p.percentual_periodo >= 0 for p in curva.pontos)


def test_forma_1_gera_desembolso_linear():
    curva = gerar_curva_s(1_200_000.0, prazo_meses=12, forma=1.0)

    for ponto in curva.pontos:
        assert ponto.percentual_periodo == pytest.approx(1 / 12)


def test_forma_maior_que_1_concentra_no_miolo():
    curva = gerar_curva_s(1_000_000.0, prazo_meses=10, forma=2.5)

    primeiro = curva.pontos[0].percentual_periodo
    meio = curva.pontos[4].percentual_periodo
    assert meio > primeiro


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        gerar_curva_s(100.0, prazo_meses=0)
    with pytest.raises(ValueError):
        gerar_curva_s(100.0, prazo_meses=6, forma=0)
