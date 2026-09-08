"""
Load Balancer MC714 — Simulação simplificada.

Políticas: Random, Round-Robin, Join-the-Shortest-Queue.
Tráfego: Bounded Pareto (Hurst 0.8), rajadas de 30/60/90/120.
"""

import random
import math
import simpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Parâmetros fixos do enunciado ────────────────────────────────────────────
NUM_SERVERS = 3
WORKERS_PER_SERVER = 15
CAPACITY = 15
SERVICE_TIME = 0.05
MU = 1.0 / SERVICE_TIME  # 20.0
SIM_TIME = 200.0
HURST = 0.8
BURST_SIZES = [30, 60, 90, 120]
NUM_REPLICAS = 10
BASE_SEED = 42
LAMBDA = 30.0  # taxa média de chegada (fixa para todos os experimentos)


# ── Geração de tráfego ──────────────────────────────────────────────────────
class BoundedPareto:
    """Amostras de Pareto Limitada com parâmetro Hurst."""

    def __init__(self, minimum, maximum, hurst, rng):
        self.minimum = minimum
        self.maximum = maximum
        self.alpha = 3.0 - 2.0 * hurst
        self.rng = rng

    def sample(self):
        lower = self.minimum ** (-self.alpha)
        upper = self.maximum ** (-self.alpha)
        value = lower - self.rng.random() * (lower - upper)
        return value ** (-1.0 / self.alpha)


class BurstTraffic:
    """Gera gaps Pareto dentro de rajadas, com pausas exponenciais entre rajadas."""

    def __init__(self, burst_size, rate, hurst, rng):
        self.burst_size = burst_size
        self.burst_rate = rate / burst_size
        self.rng = rng
        self.remaining = 0
        self.gap_gen = BoundedPareto(0.001, 1.0, hurst, rng)

    def next_interarrival(self):
        if self.remaining == 0:
            self.remaining = self.burst_size
            interval = self.rng.expovariate(self.burst_rate)
        else:
            interval = self.gap_gen.sample()
        self.remaining -= 1
        return interval


# ── Políticas de balanceamento ───────────────────────────────────────────────
def policy_random(servers, rng, _state=None):
    return rng.choice(servers)


def policy_round_robin(servers, rng, state):
    server = servers[state["rr_index"] % len(servers)]
    state["rr_index"] += 1
    return server


def policy_shortest_queue(servers, rng, _state=None):
    min_load = min(s.load for s in servers)
    candidates = [s for s in servers if s.load == min_load]
    return rng.choice(candidates)


# ── Servidor ────────────────────────────────────────────────────────────────
class Server:
    def __init__(self, env, server_id, capacity):
        self.env = env
        self.server_id = server_id
        self.capacity = capacity
        self.queue = []
        self.processing = []
        self.resource = simpy.Resource(env, capacity=capacity)

    @property
    def load(self):
        return len(self.queue) + len(self.processing)

    def process(self, request, completions):
        with self.resource.request() as req:
            yield req
            self.queue.remove(request)
            self.processing.append(request)
            yield self.env.timeout(SERVICE_TIME)
            self.processing.remove(request)
            request["completion_time"] = self.env.now
            completions.append(request)


# ── Simulação ───────────────────────────────────────────────────────────────
def run_simulation(policy_fn, state, lambda_rate, seed, burst_size):
    rng = random.Random(seed)
    env = simpy.Environment()
    servers = [Server(env, i, CAPACITY) for i in range(NUM_SERVERS)]
    traffic = BurstTraffic(burst_size, lambda_rate, HURST, rng)

    completions = []
    response_times = []
    total_arrivals = 0
    dropped = 0

    def arrival_process():
        nonlocal total_arrivals, dropped
        req_id = 0
        while True:
            interval = traffic.next_interarrival()
            yield env.timeout(interval)
            if env.now > SIM_TIME:
                return
            req_id += 1
            total_arrivals += 1
            request = {"id": req_id, "arrival_time": env.now, "completion_time": None}
            server = policy_fn(servers, rng, state)
            if server.load < server.capacity:
                server.queue.append(request)
                env.process(server.process(request, completions))
            else:
                dropped += 1

    env.process(arrival_process())
    env.run(until=SIM_TIME)

    for req in completions:
        response_times.append(req["completion_time"] - req["arrival_time"])

    throughput = len(completions) / SIM_TIME
    mean_response = sum(response_times) / len(response_times) if response_times else 0.0

    return {
        "throughput": throughput,
        "mean_response": mean_response,
        "completions": len(completions),
        "total_arrivals": total_arrivals,
        "dropped": dropped,
    }


# ── Modelo analítico M/M/1 ─────────────────────────────────────────────────
def analytical_model(lambda_val):
    lambda_i = lambda_val / NUM_SERVERS
    rho = lambda_i / MU
    if rho >= 1.0:
        return {"rho": rho, "E_R": float("inf"), "E_N": float("inf"),
                "throughput": float("inf"), "stable": False}
    E_R = 1.0 / (MU - lambda_i)
    E_N = rho / (1.0 - rho) * NUM_SERVERS
    return {"rho": rho, "E_R": E_R, "E_N": E_N,
            "throughput": lambda_val, "stable": True}


# ── Gráficos ────────────────────────────────────────────────────────────────
def generate_plots(results):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    policies = ["random", "round_robin", "shortest_queue"]
    labels = {"random": "Random", "round_robin": "Round-Robin", "shortest_queue": "JSQ"}
    markers = {"random": "o", "round_robin": "s", "shortest_queue": "^"}

    # Gráfico 1: Tempo médio de resposta vs tamanho da rajada
    for pol in policies:
        xs = BURST_SIZES
        ys = [results[(pol, bs)]["mean_response"] for bs in BURST_SIZES]
        axes[0].plot(xs, ys, f"{markers[pol]}-", label=labels[pol])
    axes[0].set_xlabel("Tamanho da rajada")
    axes[0].set_ylabel("Tempo médio de resposta")
    axes[0].set_title("Resposta vs Rajada")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Gráfico 2: Vazão vs tamanho da rajada
    for pol in policies:
        xs = BURST_SIZES
        ys = [results[(pol, bs)]["throughput"] for bs in BURST_SIZES]
        axes[1].plot(xs, ys, f"{markers[pol]}-", label=labels[pol])
    axes[1].set_xlabel("Tamanho da rajada")
    axes[1].set_ylabel("Vazão (requisições/unidade de tempo)")
    axes[1].set_title("Vazão vs Rajada")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Gráfico 3: Requisições descartadas vs tamanho da rajada
    for pol in policies:
        xs = BURST_SIZES
        ys = [results[(pol, bs)]["dropped"] for bs in BURST_SIZES]
        axes[2].plot(xs, ys, f"{markers[pol]}-", label=labels[pol])
    axes[2].set_xlabel("Tamanho da rajada")
    axes[2].set_ylabel("Requisições descartadas")
    axes[2].set_title("Descartes vs Rajada")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("resultados.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Gráfico salvo em resultados.png")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    policies = {
        "random": (policy_random, {}),
        "round_robin": (policy_round_robin, {"rr_index": 0}),
        "shortest_queue": (policy_shortest_queue, {}),
    }

    results = {}
    for policy_name, (policy_fn, state) in policies.items():
        for bs in BURST_SIZES:
            replicas = []
            for r in range(NUM_REPLICAS):
                seed = BASE_SEED + r
                res = run_simulation(policy_fn, dict(state), LAMBDA, seed, bs)
                replicas.append(res)
            avg_tp = sum(r["throughput"] for r in replicas) / NUM_REPLICAS
            avg_rt = sum(r["mean_response"] for r in replicas) / NUM_REPLICAS
            avg_dr = sum(r["dropped"] for r in replicas) / NUM_REPLICAS
            results[(policy_name, bs)] = {
                "throughput": avg_tp,
                "mean_response": avg_rt,
                "dropped": avg_dr,
            }

    # Tabela de resultados
    print(f"\n{'='*65}")
    print(f"  RESULTADOS (λ={LAMBDA}, {NUM_REPLICAS} réplicas, {SIM_TIME} u.t.)")
    print(f"{'='*65}")
    print(f"{'Política':<16} {'Rajada':>8} {'Vazão':>12} {'T.Resposta':>12} {'Descartes':>10}")
    print(f"{'-'*65}")
    for pol in ["random", "round_robin", "shortest_queue"]:
        for bs in BURST_SIZES:
            r = results[(pol, bs)]
            print(f"{pol:<16} {bs:>8} {r['throughput']:>12.3f} {r['mean_response']:>12.4f} {r['dropped']:>10.1f}")
        print()

    # Modelo analítico
    am = analytical_model(LAMBDA)
    print(f"{'='*65}")
    print(f"  MODELO ANALÍTICO M/M/1 (λ={LAMBDA}, μ={MU}, 3 servidores)")
    print(f"{'='*65}")
    print(f"  λ por servidor: {LAMBDA/NUM_SERVERS:.2f}")
    print(f"  ρ: {am['rho']:.4f}")
    print(f"  Tempo resposta teórico: {am['E_R']:.4f}")
    print(f"  No sistema teórico: {am['E_N']:.4f}")
    print(f"  Vazão teórica: {am['throughput']:.2f}")
    print(f"  Estável: {'Sim' if am['stable'] else 'Não'}")

    generate_plots(results)


if __name__ == "__main__":
    main()
