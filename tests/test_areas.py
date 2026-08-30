from orcamento_obra import AreasProjeto, CoeficientesArea, calcular_quadro_areas


def test_area_equivalente_soma_ponderada():
    # Arrange
    areas = AreasProjeto(
        privativa_coberta_padrao=100.0,
        garagem_coberta_subsolo=100.0,  # k default = 0.625
    )

    # Act
    quadro = calcular_quadro_areas(areas, CoeficientesArea())

    # Assert
    assert quadro.area_real_total == 200.0
    assert quadro.area_equivalente_total == 100.0 * 1.0 + 100.0 * 0.625
    assert quadro.fator_equivalencia_medio == 162.5 / 200.0


def test_coeficientes_customizados_sao_respeitados():
    # Arrange
    areas = AreasProjeto(garagem_descoberta=200.0)
    coef = CoeficientesArea(garagem_descoberta=0.30)

    # Act
    quadro = calcular_quadro_areas(areas, coef)

    # Assert
    assert quadro.area_equivalente_total == 60.0
    assert quadro.coeficientes["garagem_descoberta"] == 0.30


def test_projeto_sem_area_tem_fator_zero():
    quadro = calcular_quadro_areas(AreasProjeto(), CoeficientesArea())

    assert quadro.area_real_total == 0.0
    assert quadro.fator_equivalencia_medio == 0.0
