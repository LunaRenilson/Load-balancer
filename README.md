# Load-balancer

Implementation, tests and analysis of a load balancer with 3 servers.

## Estrutura do Projeto

```
load-balancer/
├── main.py                  # Ponto de entrada, executa experimentos
├── config.py                # Constantes e parâmetros (Hurst, burst sizes, etc.)
├── traffic.py               # Gerador de tráfego (Bounded Pareto)
├── server.py                # Classe Server (capacidade 15, processamento 0.05)
├── load_balancer.py         # Classe LoadBalancer com políticas
├── policies.py              # Random, RoundRobin, ShortestQueue
├── simulation.py            # Loop principal de simulação com SimPy
├── metrics.py               # Coleta e cálculo de throughput/response time
├── analytical_model.py      # Modelo analítico (M/M/3 com 1/3)
├── run_experiments.py       # Executa 10x cada combinação e gera resultados
├── plots.py                 # Gera gráficos comparativos
├── requirements.txt         # simpy, numpy, matplotlib
└── README.md                # Instruções de compilação/execução
```
**Possível simplificação**
A princípio, *simulation.py*, *metrics.py*, *plot.py* e *analytical_model.py* poderiam compreender classes diferentes em um mesmo arquivo *simulation_analysis.py*. Fica a critério de que implementará.



## Módulos

| Módulo | Responsabilidade |
|--------|------------------|
| `config.py` | Hurst=0.8, bursts=[30,60,90,120], servers=3, capacity=15, proc_time=0.05 |
| `traffic.py` | Distribuição Bounded Pareto, gera rajadas de requisições |
| `server.py` | Fila FIFO, capacidade 15, processamento concorrente |
| `policies.py` | 3 classes: `RandomPolicy`, `RoundRobinPolicy`, `ShortestQueuePolicy` |
| `load_balancer.py` | Recebe requisição, consulta política, encaminha para servidor |
| `simulation.py` | SimPy environment, orquestra chegada/saída de requisições |
| `metrics.py` | Calcula throughput (req/tempo) e tempo médio resposta |
| `analytical_model.py` | Modelo M/M/3: λ, μ, ρ, Lq, Wq, W |

## Como Executar

```bash
pip install -r requirements.txt
python main.py
```
