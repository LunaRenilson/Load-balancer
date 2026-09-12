# Load Balancer MC714 — Trabalho 1

Simulador de balanceador de carga com três servidores **M/M/1** homogêneos, conforme o PDF oficial do Trabalho 1 (MC714).

## Modelo

- **Chegadas:** Poisson(λ) — tempos entre chegadas exponenciais de média 1/λ
- **Serviço:** exponencial com μ = 1,0 (E[S] = 1 u.t.)
- **Servidores:** 3 homogêneos, 1 thread cada, fila FCFS ilimitada
- **Balanceador:** instantâneo (sem tempo de processamento)
- **Políticas:** Aleatória, Round-Robin, Fila Mais Curta

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
# Todos os experimentos + gráficos + tabelas
python main.py --mode all

# Apenas experimentos principais (15 configurações)
python main.py --mode main

# Experimento instável λ=3.3
python main.py --mode unstable

# Bônus: buffer finito M/M/1/K
python main.py --mode bonus-buffer

# Bônus: servidores heterogêneos
python main.py --mode bonus-hetero

# Tabela analítica M/M/1
python main.py --mode analytical
```

## Experimentos

| Parâmetro | Valor |
|---|---|
| λ (principal) | 0,6 · 1,2 · 1,8 · 2,4 · 2,7 |
| λ (instabilidade) | 3,3 |
| Duração | 5000 u.t. |
| Warm-up | 500 u.t. |
| Réplicas | 10 (IC 95%) |
| Métricas | X, E[R], E[N], Uᵢ |

## Saída

Artefatos gerados em `results/`:

- `results.csv` — métricas agregadas
- `results.json` — dados completos
- `er_vs_lambda.png` — comparação analítico × simulação
- `little_law_check.png` — Lei de Little
- `N_t_lambda33.png` — instabilidade
- `bonus_buffer.png` — buffer finito
- `bonus_hetero.png` — servidores heterogêneos

## Relatório

Opção 1 — gerar PDF diretamente (sem LaTeX):

```bash
python report/generate_report.py
```

Opção 2 — compilar LaTeX (requer `pdflatex`):

```bash
cd report
pdflatex relatorio_projeto1_integrante1.tex
```

Gera `report/relatorio_projeto1_integrante1.pdf`.

## Estrutura do código

```
config.py       # parâmetros do PDF
policies.py     # políticas de balanceamento
simulator.py    # simulador SimPy M/M/1
metrics.py      # E[N], Uᵢ, IC 95%
analytical.py   # fórmulas M/M/1 e M/M/1/K
experiments.py  # execução dos experimentos
plots.py        # gráficos
main.py         # ponto de entrada CLI
report/         # relatório LaTeX
```

## Entregáveis

- `relatorio_projeto1_integrante1.pdf`
- Código-fonte (compactar em `.zip` para submissão)
