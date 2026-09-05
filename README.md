# Load-balancer

Implementation, tests and analysis of a load balancer with 3 servers.

## Estrutura do Projeto

```
load-balancer/
├── main.py           # Ponto de entrada, orquestra experimentos
├── config.py         # Constantes e parâmetros (Hurst, burst sizes, etc.)
├── traffic.py        # Gerador de tráfego (Bounded Pareto)
├── core.py           # Server, LoadBalancer e políticas (domínio do sistema)
├── simulation.py     # Loop de simulação SimPy + coleta de métricas
├── analytical.py     # Modelo analítico (M/M/3 com 1/3)
├── plots.py          # Geração de gráficos comparativos
├── requirements.txt  # simpy, numpy, matplotlib
└── README.md         # Instruções de compilação/execução
```

**Organização lógica**
- **`core.py`** concentra tudo que é o domínio do problema: `Server`, `LoadBalancer` e as 3 políticas (`RandomPolicy`, `RoundRobinPolicy`, `ShortestQueuePolicy`), que estão intimamente acopladas.
- **`simulation.py`** orquestra o loop de eventos com SimPy e coleta métricas (throughput e tempo médio de resposta).
- **`analytical.py`** contém apenas a matemática do modelo M/M/3, sem dependência de SimPy.
- **`plots.py`** gera os gráficos comparativos entre simulação e modelo analítico.



## Módulos

| Módulo | Responsabilidade |
|--------|------------------|
| `config.py` | Hurst=0.8, bursts=[30,60,90,120], servers=3, capacity=15, proc_time=0.05 |
| `traffic.py` | Distribuição Bounded Pareto, gera rajadas de requisições |
| `core.py` | `Server` (fila FIFO, capacidade 15), `LoadBalancer` e 3 políticas |
| `simulation.py` | SimPy environment + coleta de métricas (throughput, response time) |
| `analytical.py` | Modelo M/M/3: λ, μ, ρ, Lq, Wq, W |
| `plots.py` | Gera gráficos comparativos (simulação vs analítico) |

## Como Executar

```bash
pip install -r requirements.txt
python main.py
```
