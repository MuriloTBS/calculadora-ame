"""Exemplo executável: edifício residencial multifamiliar de padrão médio.

Rode com:  python exemplo.py
"""

from __future__ import annotations

from dataclasses import replace

from orcamento_obra import (
    CUB_RJ_R8N_ATUAL,
    AreasProjeto,
    ComponentesBDI,
    EntradaProjeto,
    calcular_orcamento,
    formatar_relatorio,
)


def main() -> None:
    entrada = EntradaProjeto(
        areas=AreasProjeto(
            privativa_coberta_padrao=1_800.0,
            garagem_coberta_subsolo=600.0,
            varanda_sacada_aberta=180.0,
            area_tecnica_reservatorio=60.0,
            lazer_coberto=120.0,
            lazer_descoberto_piscina=90.0,
        ),
        custo_base_m2=CUB_RJ_R8N_ATUAL,   # CUB-RJ R8-N ago/2026 (SindusCon-Rio)
        padrao_construtivo="medio",
        solo_topografia="aclive_declive_medio",
        logistica="condominio_fechado",
        fator_regiao=1.00,
        prazo_meses=18,
        # Tributos ajustados ao regime (ex.: Lucro Presumido com CPRB) —
        # os demais componentes de BDI ficam no ponto médio default.
        bdi=ComponentesBDI(tributos=0.1115),
    )

    resultado = calcular_orcamento(entrada)
    print(formatar_relatorio(resultado))

    # Exemplo de reuso imutável: mesmo projeto, solo desfavorável.
    pior_solo = replace(entrada, solo_topografia="declive_acentuado_solo_mole")
    r2 = calcular_orcamento(pior_solo)
    delta = (
        r2.demonstrativo.valor_global_proposta
        - resultado.demonstrativo.valor_global_proposta
    )
    print(
        f"\nΔ Proposta ao trocar solo p/ 'declive acentuado / solo mole': "
        f"R$ {delta:,.2f}"
    )


if __name__ == "__main__":
    main()
