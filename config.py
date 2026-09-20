"""Parâmetros do Trabalho 1 MC714 conforme PDF oficial."""

from pathlib import Path

NUM_SERVERS = 3
MU = 1.0  # taxa de serviço por servidor (E[S] = 1 u.t.)

SIM_TIME = 5000.0
WARMUP = 500.0
MEASURE_DURATION = SIM_TIME - WARMUP

LAMBDA_VALUES = [0.6, 1.2, 1.8, 2.4, 2.7]
UNSTABLE_LAMBDA = 3.3

NUM_REPLICAS = 10
BASE_SEED = 42

# t_{0.975, 9} para IC 95% com 10 réplicas
T_CRITICAL_95 = 2.262

POLICIES = ("random", "round_robin", "shortest_queue")
POLICY_LABELS = {
    "random": "Aleatória",
    "round_robin": "Round-Robin",
    "shortest_queue": "Fila Mais Curta",
}

# Bônus: buffer finito
BUFFER_K_VALUES = [5, 10, 20]

RESULTS_DIR = Path(__file__).resolve().parent / "results"
REPORT_DIR = Path(__file__).resolve().parent / "report"
