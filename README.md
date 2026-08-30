# Calculadora AME

Calculadora paramétrica de custo de obra por m² — da fundação ao acabamento.
Motor de cálculo em Python + calculadora web, cobrindo área equivalente
(NBR 12.721), custo direto por macroetapa, custo indireto por prazo, contingência
e BDI (fórmula TCU, Acórdão 2622/2013).

## Instalação

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Sem dependências de runtime — só a biblioteca padrão. `pytest` apenas para testes.

## Calculadora web

**Online:** https://murilotbs.github.io/calculadora-ame/

`index.html` — página única, sem build, com a mesma lógica do motor Python
portada para JavaScript (conferida número a número). Abra no navegador ou publique
como página estática.

- Campos de identificação: cliente, obra / empreendimento e endereço da obra
- Todos os parâmetros de cálculo editáveis, 5 quadros de saída, Curva S, tema claro/escuro
- **Imprimir relatório** (`Ctrl/Cmd+P` ou o botão): gera folha com cabeçalho
  identificado, quadros e o cronograma físico-financeiro de desembolso mês a mês

## Uso rápido

```bash
python exemplo.py          # relatório completo de um caso realista
pytest                     # suíte de testes
```

```python
from orcamento_obra import AreasProjeto, EntradaProjeto, calcular_orcamento, formatar_relatorio

entrada = EntradaProjeto(
    areas=AreasProjeto(
        privativa_coberta_padrao=1_800,
        garagem_coberta_subsolo=600,
        varanda_sacada_aberta=180,
    ),
    custo_base_m2=2_600.0,                     # CUB-referência R$/m²
    padrao_construtivo="medio",               # baixo_popular | medio | alto | luxo_premium
    solo_topografia="aclive_declive_medio",   # plano_solo_firme | aclive_declive_medio | declive_acentuado_solo_mole
    logistica="condominio_fechado",           # urbano_central | condominio_fechado | area_remota
    prazo_meses=18,
)

resultado = calcular_orcamento(entrada)
print(formatar_relatorio(resultado))          # blocos 1–5 + avisos
```

## Modelo de cálculo (4 camadas encadeadas)

| # | Camada | Fórmula | Módulo |
|---|--------|---------|--------|
| 1 | Área equivalente | `A_eq = Σ (Aᵢ · kᵢ)` | `areas.py` |
| 2 | Custo direto | `CD = (Σⱼ pesoⱼ · custo_base · F_padrão · F_região · F_soloⱼ) · A_eq` | `custo_direto.py` |
| 3 | Custo indireto | `CI = custo_mensal · prazo_meses` (com `F_logística`) | `custo_indireto.py` |
| 4 | Custo total | `CT = (CD + CI) · (1 + contingência)` | `orcamento.py` |
|   | Preço de venda | `PV = CT · (1 + BDI)` | `bdi.py` + `orcamento.py` |

### BDI (TCU 2622/2013)

```
BDI = [ (1 + AC + S+G + R) · (1 + DF) · (1 + L) / (1 - I) ] − 1
```

O divisor `(1 − I)` já embute os tributos sobre o preço; por isso
`PV = CT · (1 + BDI)`, sem nova divisão.

### Sensibilidade de solo (regra de negócio)

`F_solo` incide **apenas** nas macroetapas `01 (Preliminares & Terraplenagem)` e
`02 (Fundações e Infraestrutura)`. Solo/topografia desfavoráveis elevam o CD
total **e** aumentam a participação relativa dessas etapas — sem encarecer
pintura, revestimento etc.

## Coeficientes default (ponto médio das faixas)

| Parâmetro | Faixa | Default |
|-----------|-------|---------|
| k garagem coberta / subsolo | 0,50–0,75 | **0,625** |
| k garagem descoberta | 0,30–0,50 | **0,40** |
| k varandas / sacadas | 0,50–0,60 | **0,55** |
| k áreas técnicas / reservatórios | 0,50–0,75 | **0,625** |
| k lazer coberto | 0,80–1,00 | **0,90** |
| k lazer descoberto / piscinas | 0,30–0,50 | **0,40** |
| F padrão — baixo/popular | 0,80–0,90 | **0,85** |
| F padrão — médio | — | **1,00** |
| F padrão — alto | 1,30–1,45 | **1,375** |
| F padrão — luxo/premium | 1,70–2,20 | **1,95** |
| F solo — aclive/declive médio | 1,08–1,15 | **1,115** |
| F solo — declive acentuado / solo mole | 1,20–1,40 | **1,30** |
| BDI — Administração Central | 3,00–5,50% | **4,25%** |
| BDI — Seguros + Garantias | 0,80–1,50% | **1,15%** |
| BDI — Risco e Imprevistos | 0,90–1,80% | **1,35%** |
| BDI — Despesas Financeiras | 0,50–1,20% | **0,85%** |
| BDI — Lucro | 6,00–12,00% | **9,00%** |
| BDI — Tributos | 5,65–14,50% | **10,075%** ⚠️ ajuste ao regime |
| Contingência sobre (CD+CI) | — | **2,00%** |

BDI total resultante dos defaults: **≈ 30,49%**.

Pesos de macroetapa: ponto médio de cada faixa da EAP (seção 3), soma ≈ 103,5%,
**normalizada para 100%** por padrão (`normalizar_pesos=True`).

### Tudo é editável

Qualquer default é sobrescrito passando o campo na dataclass correspondente:

```python
from orcamento_obra import ComponentesBDI, CoeficientesArea, EquipeTecnicaMensal

EntradaProjeto(
    ...,
    coef_area=CoeficientesArea(garagem_coberta_subsolo=0.70),
    bdi=ComponentesBDI(tributos=0.1115, lucro=0.10),
    equipe_tecnica=EquipeTecnicaMensal(engenheiro_residente=25_000),
    fator_regiao=1.08,
    fator_solo_override=1.22,          # ignora a tabela e usa este valor
    taxa_contingencia=0.0,             # zera a contingência
    normalizar_pesos=False,
)
```

## Saídas (`ResultadoOrcamento`)

1. **`quadro_areas`** — área real × área equivalente, por tipologia.
2. **`indicadores`** — R$/m² de CD, CI, CT e PV (por m² real e por m² equivalente).
3. **`custo_direto.itens`** — por macroetapa: custo total, R$/m² e % do CD.
4. **`demonstrativo`** — CD, CI, contingência, CT, memória de BDI, PV e participações.
5. **`curva_s`** — cronograma físico-financeiro mensal (sigmoide, base CT ou PV).
6. **`avisos`** — premissas e inconsistências não bloqueantes.

`formatar_relatorio(resultado)` devolve tudo isso como texto tabelado.

## Premissas e limites

- Custos mensais de equipe/canteiro são **referências de mercado** — calibre com
  a sua composição real antes de usar em proposta.
- `custo_base_m2` deve refletir o padrão e a data-base escolhidos (CUB estadual
  ou SINAPI desonerado / não-desonerado).
- Tributos do BDI no default genérico (ponto médio). Defina conforme Simples,
  Lucro Presumido ou RET.
- Orçamento **paramétrico** para viabilidade e proposta preliminar; não
  substitui orçamento analítico com composições e quantitativos de projeto.
