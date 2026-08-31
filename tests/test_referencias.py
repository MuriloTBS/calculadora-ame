from orcamento_obra import CUB_RJ_R8N_2026, CUB_RJ_R8N_ATUAL


def test_serie_cub_rj_tem_doze_meses_no_maximo_e_esta_ordenada():
    chaves = list(CUB_RJ_R8N_2026)

    assert chaves == sorted(chaves)
    assert all(k.startswith("2026-") for k in chaves)
    assert 1 <= len(chaves) <= 12


def test_valor_atual_e_o_ultimo_da_serie():
    ultimo_mes = sorted(CUB_RJ_R8N_2026)[-1]

    assert CUB_RJ_R8N_ATUAL == CUB_RJ_R8N_2026[ultimo_mes]
    assert ultimo_mes == "2026-08"
    assert CUB_RJ_R8N_ATUAL == 2471.58


def test_valores_plausiveis_para_cub_rj():
    for mes, valor in CUB_RJ_R8N_2026.items():
        assert 1_500.0 < valor < 4_000.0, f"{mes}: {valor} fora da faixa plausível"
