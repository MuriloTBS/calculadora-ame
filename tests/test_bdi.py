import pytest

from orcamento_obra import ComponentesBDI, calcular_bdi


def test_bdi_ponto_medio_das_faixas():
    # Arrange — todos os componentes no ponto médio (defaults)
    componentes = ComponentesBDI()

    # Act
    resultado = calcular_bdi(componentes)

    # Assert — valor de referência calculado pela fórmula TCU 2622/2013
    assert resultado.taxa_bdi == pytest.approx(0.304938, abs=1e-5)
    assert resultado.multiplicador == pytest.approx(1.304938, abs=1e-5)


def test_memoria_de_calculo_exposta():
    resultado = calcular_bdi(ComponentesBDI())
    memoria = resultado.memoria

    assert memoria["grupo_indiretos_(1+AC+SG+R)"] == pytest.approx(1.0675)
    assert memoria["divisor_tributos_(1-I)"] == pytest.approx(1 - 0.100750)


def test_lucro_maior_eleva_bdi():
    baixo = calcular_bdi(ComponentesBDI(lucro=0.06))
    alto = calcular_bdi(ComponentesBDI(lucro=0.12))

    assert alto.taxa_bdi > baixo.taxa_bdi


def test_tributos_invalidos_levantam_erro():
    with pytest.raises(ValueError):
        calcular_bdi(ComponentesBDI(tributos=1.0))
    with pytest.raises(ValueError):
        calcular_bdi(ComponentesBDI(tributos=-0.01))
