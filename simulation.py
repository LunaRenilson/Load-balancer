"""SimPy simulation and metric collection."""

from dataclasses import dataclass, field
import random

import simpy

from analytical import fluid_queue_size
from config import SimulationConfig
from core import LoadBalancer, Request, Server
from logger import trace
from traffic import BurstTrafficGenerator, PoissonTrafficGenerator, exponential_sample


@dataclass
class SimulationResult:
    policy: str
    lambda_rate: float
    seed: int
    throughput: float
    mean_response_time: float
    mean_system_customers: float
    utilizations: list[float]
    arrivals: int
    accepted_arrivals: int
    completions: int
    dropped: int
    samples: list[dict[str, float]] = field(default_factory=list)

    def as_dict(self) -> dict[str, float | int | str]:
        values: dict[str, float | int | str] = {
            "policy": self.policy,
            "lambda": self.lambda_rate,
            "seed": self.seed,
            "throughput": self.throughput,
            "mean_response_time": self.mean_response_time,
            "mean_system_customers": self.mean_system_customers,
            "arrivals": self.arrivals,
            "accepted_arrivals": self.accepted_arrivals,
            "completions": self.completions,
            "dropped": self.dropped,
        }
        for index, utilization in enumerate(self.utilizations, 1):
            values[f"u{index}"] = utilization
        values["u_mean"] = sum(self.utilizations) / len(self.utilizations)
        return values


class Simulation:
    def __init__(self, config: SimulationConfig, trace_logger=None):
        self.config = config
        self.trace_logger = trace_logger

    def run(self, policy: str, lambda_rate: float, seed: int) -> SimulationResult:
        rng = random.Random(seed)
        env = simpy.Environment()
        completions: list[Request] = []
        accepted_arrivals: list[Request] = []
        busy_area = [0.0] * self.config.num_servers
        area_n = 0.0
        last_change = 0.0
        samples: list[dict[str, float]] = []
        dropped = 0
        total_arrivals = 0

        def total_load() -> int:
            return sum(server.load for server in servers)

        def integrate_until(time: float) -> None:
            nonlocal area_n, last_change
            left = max(last_change, self.config.warmup_time)
            right = min(time, self.config.sim_time)
            if right > left:
                area_n += total_load() * (right - left)
            last_change = time

        def on_start(server: Server, request: Request) -> None:
            trace(self.trace_logger, env.now, "START", f"Servidor {server.server_id + 1} iniciou Req #{request.req_id}.")

        def on_complete(server: Server, request: Request) -> None:
            integrate_until(env.now)
            if request.service_start_time is not None:
                busy_area[server.server_id] += self._window_overlap(request.service_start_time, env.now)
            completions.append(request)
            trace(
                self.trace_logger,
                env.now,
                "COMPL",
                f"Servidor {server.server_id + 1} concluiu Req #{request.req_id}; "
                f"resposta={request.response_time:.4f}.",
            )

        service_sampler = (
            (lambda: exponential_sample(self.config.mu, rng))
            if self.config.traffic_profile == "poisson"
            else (lambda: self.config.service_time)
        )
        servers = [
            Server(
                env,
                index,
                service_sampler,
                workers=self.config.workers_per_server,
                capacity=self.config.finite_capacity,
                on_start=on_start,
                on_complete=on_complete,
            )
            for index in range(self.config.num_servers)
        ]
        balancer = LoadBalancer(policy, rng)
        if self.config.traffic_profile == "poisson":
            traffic_generator = PoissonTrafficGenerator(lambda_rate, rng)
        else:
            traffic_generator = BurstTrafficGenerator(
                self.config.burst_size_for(lambda_rate),
                lambda_rate,
                self.config.hurst,
                rng,
            )

        def arrival_process():
            nonlocal dropped, total_arrivals
            request_id = 0
            while True:
                interval = traffic_generator.next_interarrival()
                yield env.timeout(interval)
                if env.now > self.config.sim_time:
                    return
                request_id += 1
                total_arrivals += 1
                request = Request(request_id, env.now)
                integrate_until(env.now)
                trace(
                    self.trace_logger,
                    env.now,
                    "ARRIV",
                    f"Req #{request_id} chegou; ocupacao=[{servers[0].load}, {servers[1].load}, {servers[2].load}].",
                )
                server = balancer.dispatch(request, servers, env.now)
                if server is None:
                    dropped += 1
                    trace(self.trace_logger, env.now, "DROP", f"Req #{request_id} descartada por capacidade.")
                    continue
                accepted_arrivals.append(request)
                trace(
                    self.trace_logger,
                    env.now,
                    "DISP",
                    f"Req #{request_id} -> Servidor {server.server_id + 1}; ocupacao=[{servers[0].load}, {servers[1].load}, {servers[2].load}].",
                )

        samples.append(
            {
                "time": 0.0,
                "n1": 0.0,
                "n2": 0.0,
                "n3": 0.0,
                "n_total": 0.0,
                "fluid": fluid_queue_size(0.0, lambda_rate, self.config.mu),
            }
        )

        def sampler():
            while env.now < self.config.sim_time:
                yield env.timeout(self.config.sample_interval)
                samples.append(
                    {
                        "time": env.now,
                        "n1": float(servers[0].load),
                        "n2": float(servers[1].load),
                        "n3": float(servers[2].load),
                        "n_total": float(total_load()),
                        "fluid": fluid_queue_size(env.now, lambda_rate, self.config.mu),
                    }
                )

        env.process(arrival_process())
        env.process(sampler())
        env.run(until=self.config.sim_time)
        integrate_until(self.config.sim_time)
        for server in servers:
            for request in server.current_requests:
                if request.service_start_time is not None:
                    busy_area[server.server_id] += self._window_overlap(
                        request.service_start_time,
                        self.config.sim_time,
                    )

        useful_completions = [
            request
            for request in completions
            if request.arrival_time >= self.config.warmup_time
            and request.completion_time is not None
            and request.completion_time <= self.config.sim_time
        ]
        duration = self.config.sim_time - self.config.warmup_time
        return SimulationResult(
            policy=policy,
            lambda_rate=lambda_rate,
            seed=seed,
            throughput=len(useful_completions) / duration,
            mean_response_time=(
                sum(request.response_time for request in useful_completions) / len(useful_completions)
                if useful_completions
                else 0.0
            ),
            mean_system_customers=area_n / duration,
            utilizations=[
                busy / (duration * self.config.workers_per_server)
                for busy in busy_area
            ],
            arrivals=total_arrivals,
            accepted_arrivals=len(accepted_arrivals),
            completions=len(completions),
            dropped=dropped,
            samples=samples,
        )

    def _window_overlap(self, start: float, end: float) -> float:
        left = max(start, self.config.warmup_time)
        right = min(end, self.config.sim_time)
        return max(0.0, right - left)
