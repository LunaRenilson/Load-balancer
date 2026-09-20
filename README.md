# Load Balancer MC714 — Simulação e análise de políticas de balanceamento

Projeto em Python para simular um balanceador de carga com três servidores homogêneos M/M/1, comparar políticas de roteamento e validar resultados contra modelos analíticos.

## Visão geral

O simulador implementa:

- chegadas Poissonianas com taxa λ
- serviço exponencial com taxa μ = 1.0
- 3 servidores homogêneos
- fila FCFS por servidor
- políticas de balanceamento:
  - aleatória
  - round-robin
  - fila mais curta
- análise analítica M/M/1 por servidor
- experimento de instabilidade para λ = 3.3
- bônus de buffer finito M/M/1/K

## Modelo do sistema

- Chegadas: Poisson(λ)
- Serviço por servidor: exponencial com média E[S] = 1 / μ = 1 unidade de tempo
- Número de servidores: 3
- Warm-up: 500 u.t.
- Duração total da simulação: 5000 u.t.
- Réplicas: 10 por configuração
- Intervalo de confiança: 95%
- Métricas principais: vazão X, tempo médio de resposta E[R], número médio de requisições E[N], utilização média U

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
# Executa todos os experimentos, salva resultados e gera todos os gráficos
python3 main.py --mode all

# Apenas experimentos principais (5 λ × 3 políticas)
python3 main.py --mode main

# Experimento instável com λ = 3.3
python3 main.py --mode unstable

# Bônus: sistema com buffer finito M/M/1/K
python3 main.py --mode bonus-buffer

# Tabela analítica M/M/1 por servidor
python3 main.py --mode analytical
```

## Configurações de experimento

| Parâmetro | Valor |
|---|---|
| λ principal | 0.6, 1.2, 1.8, 2.4, 2.7 |
| λ instável | 3.3 |
| servidores | 3 |
| μ por servidor | 1.0 |
| duração | 5000 u.t. |
| warm-up | 500 u.t. |
| réplicas | 10 |
| políticas | random, round_robin, shortest_queue |

## Saída gerada

Os artefatos finais são salvos em `results/`:

- `results.csv` — resumo agregado por política e λ
- `results.json` — dados completos de simulação e analíticos
- `er_vs_lambda.png` — E[R] x λ (simulação vs analítico)
- `little_law_check.png` — verificação da Lei de Little
- `N_t_lambda33.png` — dinâmica de N(t) no caso instável
- `bonus_buffer.png` — vazão efetiva e probabilidade de perda para buffer finito

## Estrutura do projeto

```text
config.py       # parâmetros globais do projeto
policies.py     # implementações das políticas de roteamento
simulator.py    # simulação de eventos discretos em SimPy
metrics.py      # cálculo de métricas, IC 95% e agregação
analytical.py   # modelo analítico M/M/1 e M/M/1/K
experiments.py  # execução dos experimentos e persistência dos dados
plots.py        # geração dos gráficos
main.py         # entrada CLI
results/        # CSV/JSON e figuras geradas
project-description.md  # descrição do enunciado do trabalho
```

## Observações importantes

- O projeto atual está alinhado com a implementação real em código e não depende de uma pasta `report/` ou de um gerador de PDF interno.
- A descrição formal do trabalho está em `project-description.md`, enquanto este README documenta a execução e os resultados do simulador implementado.
- O comando `python main.py --mode all` é o ponto de entrada completo para reproduzir a análise do projeto.

## Referência rápida

A execução completa produz comparações entre:

- modelo analítico M/M/1 por servidor
- simulação para cada política
- ganho relativo da política mais eficiente
- validade da Lei de Little
- comportamento instável em λ = 3.3
- impacto do buffer finito em K = 5, 10, 20
