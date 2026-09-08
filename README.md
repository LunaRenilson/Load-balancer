# Load Balancer MC714

Simulação de um balanceador de carga com 3 servidores e 3 políticas: Random, Round-Robin e Join-the-Shortest-Queue.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python3 main.py
```

Gera `resultados.png` com 3 gráficos e imprime tabela de métricas no terminal.

## Parâmetros

Todos os parâmetros estão hardcoded no topo de `main.py` conforme o enunciado:

- 3 servidores, 15 workers cada, capacidade 15
- Serviço constante 0.05 (μ = 20)
- Tráfego Bounded Pareto, Hurst 0.8
- Rajadas: 30, 60, 90, 120 requisições
- Duração: 200 unidades de tempo
- 10 réplicas por configuração
- λ fixo = 30.0
