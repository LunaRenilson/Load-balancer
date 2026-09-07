# Load Balancer MC714

Simulação e análise de um balanceador de carga com três servidores e três políticas: escolha aleatória, Round-Robin e Join-the-Shortest-Queue.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Perfis e parâmetros da simulação |
| `traffic.py` | Tráfego Poisson e Bounded Pareto |
| `core.py` | Requisições, servidores e políticas |
| `simulation.py` | Motor SimPy e métricas temporais |
| `analytical.py` | Modelo M/M/1 por servidor e aproximação fluida |
| `logger.py` | Rastreamento de chegadas, despacho e conclusão |
| `exporter.py` | CSV bruto, sumários, IC de 95% e ganhos |
| `plots.py` | Gráficos comparativos |
| `main.py` | CLI e orquestração dos experimentos |

## Instalação

Criar e ativar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar as dependências:

```bash
python3 -m pip install -r requirements.txt
```

No Windows, a ativação do ambiente virtual pode ser feita com:

```powershell
.venv\Scripts\Activate.ps1
```

## Execução

O perfil padrão segue o `plan.md`: chegadas Poisson, serviço exponencial com `mu=1.0`, 5000 unidades de tempo, aquecimento de 500 unidades e 10 réplicas por configuração.

```bash
python3 main.py
```

Com o ambiente virtual ativado, os mesmos comandos podem ser executados com
`.venv/bin/python`:

```bash
.venv/bin/python main.py
```

Para executar uma verificação curta, sem gerar gráficos:

```bash
python3 main.py --quick --no-plots
```

Executar os testes automatizados:

```bash
python3 -m unittest discover -s tests -v
```

Executar testes e uma simulação curta em sequência:

```bash
python3 -m unittest discover -s tests -v && \
python3 main.py --profile plan --quick --no-plots
```

Parâmetros principais da CLI:

```bash
python3 main.py --profile plan --policy random --lambda 1.2 \
	--duration 5000 --warmup 500 --replicas 10 --seed 42 \
	--verbose --generate-plots
```

`--policy` aceita `random`, `round_robin`, `shortest_queue` ou `all`. Quando
`--seed` é informado, as réplicas usam sementes consecutivas a partir desse
valor. `--export-csv` mantém a execução sem gerar gráficos; por padrão, os
gráficos também são gerados, exceto com `--no-plots`.

O perfil `burst` cobre os requisitos originais do enunciado: tráfego Bounded Pareto com Hurst 0.8, serviço constante de 0.05, 15 trabalhadores por servidor e duração de 200 unidades.

```bash
python3 main.py --profile burst
```

Para executar o perfil `burst` sem gráficos:

```bash
python3 main.py --profile burst --no-plots
```

## Resultados

Os artefatos são escritos em `results/`:

- `results/data/raw_replicas_results.csv`: métricas de cada réplica;
- `results/data/summary_results.csv`: médias, desvios, IC de 95% e Lei de Little;
- `results/data/policy_gains.csv`: redução relativa do tempo de resposta;
- `results/data/queue_fluid_lambda_3_3.csv` ou `queue_fluid_lambda_40_0.csv`: amostras médias do cenário instável, consolidadas por política;
- `results/logs/simulation_trace.log`: dinâmica de despacho e atendimento;
- `results/plots/`: figuras PNG para o relatório.

O número médio de requisições no sistema é calculado pela área sob $N(t)$ na janela de medição. A vazão e a utilização também são calculadas somente nessa janela.

O perfil `plan` usa o modelo analítico M/M/1 por servidor. O perfil `burst`
usa Bounded Pareto, serviço constante e capacidade finita; por isso, não anexa
valores teóricos M/M/1 ao resumo desse perfil. A utilização é a fração média
dos workers ocupados em cada servidor.
