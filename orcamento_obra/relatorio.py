"""Formatação do resultado em relatório textual (tabelas limpas, pt-BR)."""

from __future__ import annotations

from .areas import QuadroAreas
from .coeficientes import ROTULOS_MACROETAPA
from .orcamento import ResultadoOrcamento

_ROTULOS_AREA = {
    "privativa_coberta_padrao": "Privativa coberta padrão",
    "garagem_coberta_subsolo": "Garagem coberta / subsolo",
    "garagem_descoberta": "Garagem descoberta",
    "varanda_sacada_aberta": "Varandas / sacadas abertas",
    "area_tecnica_reservatorio": "Áreas técnicas / reservatórios",
    "lazer_coberto": "Lazer coberto",
    "lazer_descoberto_piscina": "Lazer descoberto / piscinas",
}


def _n(valor: float, casas: int = 2) -> str:
    """Número no formato pt-BR (1.234.567,89)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _moeda(valor: float) -> str:
    return "R$ " + _n(valor, 2)


def _pct(fracao: float, casas: int = 2) -> str:
    return _n(fracao * 100, casas) + "%"


def _titulo(texto: str) -> str:
    return f"\n{texto}\n" + "=" * len(texto)


def _quadro_areas(quadro: QuadroAreas) -> str:
    linhas = [_titulo("1. QUADRO RESUMO DE ÁREAS")]
    linhas.append(f"{'Tipologia':<34}{'Área real (m²)':>16}{'k':>8}{'Área equiv. (m²)':>18}")
    linhas.append("-" * 76)
    for chave, rotulo in _ROTULOS_AREA.items():
        real = quadro.por_tipo_real.get(chave, 0.0)
        if real == 0.0:
            continue
        k = quadro.coeficientes.get(chave, 0.0)
        equiv = quadro.por_tipo_equivalente.get(chave, 0.0)
        linhas.append(f"{rotulo:<34}{_n(real):>16}{_n(k, 3):>8}{_n(equiv):>18}")
    linhas.append("-" * 76)
    linhas.append(
        f"{'TOTAL':<34}{_n(quadro.area_real_total):>16}"
        f"{'':>8}{_n(quadro.area_equivalente_total):>18}"
    )
    linhas.append(
        f"Fator de equivalência médio (A_eq / A_real): "
        f"{_n(quadro.fator_equivalencia_medio, 4)}"
    )
    return "\n".join(linhas)


def _indicadores(res: ResultadoOrcamento) -> str:
    i = res.indicadores
    linhas = [_titulo("2. INDICADORES DE CUSTO UNITÁRIO")]
    linhas.append(f"Custo Direto            {_moeda(i.custo_direto_por_m2_equivalente):>20} /m² equivalente")
    linhas.append(f"Custo Indireto          {_moeda(i.custo_indireto_por_m2_equivalente):>20} /m² equivalente")
    linhas.append(f"Custo Total da Obra     {_moeda(i.custo_total_por_m2_real):>20} /m² real")
    linhas.append(f"Custo Total da Obra     {_moeda(i.custo_total_por_m2_equivalente):>20} /m² equivalente")
    linhas.append(f"Preço Final de Venda    {_moeda(i.preco_venda_por_m2_real):>20} /m² real")
    linhas.append(f"Preço Final de Venda    {_moeda(i.preco_venda_por_m2_equivalente):>20} /m² equivalente")
    return "\n".join(linhas)


def _macroetapas(res: ResultadoOrcamento) -> str:
    linhas = [_titulo("3. DETALHAMENTO POR MACROETAPA")]
    linhas.append(
        f"{'Macroetapa':<42}{'Custo total':>18}{'R$/m² real':>14}{'% CD':>9}"
    )
    linhas.append("-" * 83)
    for item in res.custo_direto.itens:
        rotulo = item.rotulo if len(item.rotulo) <= 42 else item.rotulo[:41] + "…"
        marca = " *" if item.fator_solo_aplicado != 1.0 else ""
        linhas.append(
            f"{rotulo:<42}{_moeda(item.custo_total):>18}"
            f"{_n(item.custo_por_m2_real):>14}{_pct(item.percentual, 1):>9}{marca}"
        )
    linhas.append("-" * 83)
    linhas.append(
        f"{'CUSTO DIRETO TOTAL':<42}{_moeda(res.custo_direto.custo_direto_total):>18}"
        f"{_n(res.custo_direto.custo_direto_por_m2_real):>14}{_pct(1.0, 1):>9}"
    )
    if res.custo_direto.fator_solo != 1.0:
        linhas.append(
            f"(*) F_solo {_n(res.custo_direto.fator_solo, 3)} aplicado — "
            "sensibilidade de solo nas etapas 01 e 02."
        )
    return "\n".join(linhas)


def _demonstrativo(res: ResultadoOrcamento) -> str:
    d = res.demonstrativo
    b = res.bdi
    linhas = [_titulo("4. DEMONSTRATIVO FINANCEIRO E BDI")]
    linhas.append(f"Custo Direto (CD) .................... {_moeda(d.custo_direto_total):>20}  ({_pct(d.participacao_custo_direto, 1)} do PV)")
    linhas.append(f"Custo Indireto (CI) ................. {_moeda(d.custo_indireto_total):>20}  ({_pct(d.participacao_custo_indireto, 1)} do PV)")
    linhas.append(f"Subtotal de Custos (CD + CI) ........ {_moeda(d.subtotal_custos):>20}")
    linhas.append(f"Contingência ({_pct(d.taxa_contingencia)}) ............... {_moeda(d.valor_contingencia):>20}  ({_pct(d.participacao_contingencia, 1)} do PV)")
    linhas.append(f"CUSTO TOTAL DA OBRA (CT) ............ {_moeda(d.custo_total_obra):>20}")
    linhas.append("")
    linhas.append("Memória de cálculo do BDI (TCU 2622/2013):")
    linhas.append(f"  Administração Central (AC) ....... {_pct(b.componentes.administracao_central)}")
    linhas.append(f"  Seguros + Garantias (S+G) ....... {_pct(b.componentes.seguros_garantias)}")
    linhas.append(f"  Risco e Imprevistos (R) ......... {_pct(b.componentes.risco_imprevistos)}")
    linhas.append(f"  Despesas Financeiras (DF) ....... {_pct(b.componentes.despesas_financeiras)}")
    linhas.append(f"  Lucro (L) ....................... {_pct(b.componentes.lucro)}")
    linhas.append(f"  Tributos (I) .................... {_pct(b.componentes.tributos)}")
    linhas.append(
        "  BDI = [(1+AC+SG+R)·(1+DF)·(1+L) / (1-I)] - 1 = "
        f"{_pct(b.taxa_bdi)}"
    )
    linhas.append("")
    linhas.append(f"Valor do BDI (PV - CT) ............. {_moeda(d.valor_bdi):>20}  ({_pct(d.participacao_bdi, 1)} do PV)")
    linhas.append(f"  dos quais lucro bruto estimado .. {_moeda(d.margem_lucro_bruta_estimada):>20}")
    linhas.append("=" * 60)
    linhas.append(f"VALOR GLOBAL DA PROPOSTA (PV) ...... {_moeda(d.valor_global_proposta):>20}")
    return "\n".join(linhas)


def _curva_s(res: ResultadoOrcamento) -> str:
    c = res.curva_s
    linhas = [_titulo("5. CURVA DE DESEMBOLSO ESTIMADA (CURVA S)")]
    linhas.append(
        f"Base financeira: {c.base_financeira}  |  valor: {_moeda(c.valor_base)}  |  "
        f"forma: {_n(c.forma, 2)}"
    )
    linhas.append(f"{'Mês':>4}{'% mês':>10}{'% acum.':>10}{'Desembolso mês':>20}{'Acumulado':>20}")
    linhas.append("-" * 64)
    for p in c.pontos:
        linhas.append(
            f"{p.mes:>4}{_pct(p.percentual_periodo, 1):>10}{_pct(p.percentual_acumulado, 1):>10}"
            f"{_moeda(p.desembolso_periodo):>20}{_moeda(p.desembolso_acumulado):>20}"
        )
    return "\n".join(linhas)


def _avisos(res: ResultadoOrcamento) -> str:
    if not res.avisos:
        return ""
    linhas = [_titulo("AVISOS E PREMISSAS")]
    linhas.extend(f"  • {aviso}" for aviso in res.avisos)
    return "\n".join(linhas)


def formatar_relatorio(res: ResultadoOrcamento) -> str:
    """Monta o relatório completo (blocos 1 a 5 + avisos) como string."""
    cd = res.custo_direto
    cabecalho = [
        "ORÇAMENTO PARAMÉTRICO DE OBRA — R$/m²",
        "=" * 44,
        f"Padrão construtivo ...... {res.entrada.padrao_construtivo}  (F = {_n(cd.fator_padrao, 3)})",
        f"Solo / topografia ....... {res.entrada.solo_topografia}  (F = {_n(cd.fator_solo, 3)})",
        f"Logística ............... {res.entrada.logistica}  (F = {_n(res.custo_indireto.fator_logistica, 3)})",
        f"Fator região ........... {_n(cd.fator_regiao, 3)}",
        f"Custo base ............. {_moeda(cd.custo_base_m2)} /m²   →  ajustado {_moeda(cd.custo_base_ajustado_m2)} /m²",
        f"Prazo de execução ...... {res.entrada.prazo_meses} meses",
    ]
    blocos = [
        "\n".join(cabecalho),
        _quadro_areas(res.quadro_areas),
        _indicadores(res),
        _macroetapas(res),
        _demonstrativo(res),
        _curva_s(res),
        _avisos(res),
    ]
    return "\n".join(bloco for bloco in blocos if bloco) + "\n"
