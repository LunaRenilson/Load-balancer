"""Simulador de eventos discretos M/M/1 com balanceador de carga."""

from __future__ import annotations

import random
from typing import Callable

import simpy

from config import MU, NUM_SERVERS, SIM_TIME, WARMUP
from metrics import SystemMetrics


class Server:
    """Servidor M/M/1 com fila FCFS (limitada opcionalmente)."""

    def __init__(
        self,
        env: simpy.Environment,
        server_id: int,
        mu: float = MU,
        buffer_capacity: int | None = None,
    ):
        self.env = env
        self.server_id = server_id
        self.mu = mu
        self.buffer_capacity = buffer_capacity
        self.queue: list[dict] = []
        self.in_service = False
        self._wakeup = env.event()
        env.process(self._worker_loop())

    @property
    def load(self) -> int:
        return len(self.queue) + (1 if self.in_service else 0)

    def can_accept(self) -> bool:
        if self.buffer_capacity is None:
            return True
        return self.load < self.buffer_capacity

    def enqueue(self, request: dict) -> bool:
        if not self.can_accept():
            return False
        self.queue.append(request)
        if not self._wakeup.triggered:
            self._wakeup.succeed()
        return True

    def _worker_loop(self):
        while True:
            if not self.queue:
                self._wakeup = self.env.event()
                yield self._wakeup
            if self.env.now >= SIM_TIME and not self.queue:
                return
            request = self.queue.pop(0)
            self.in_service = True
            metrics: SystemMetrics = self.env.metrics  # type: ignore[attr-defined]
            metrics.on_enter_service(self.env.now, self.server_id)
            service_time = self.env.rng.expovariate(self.mu)  # type: ignore[attr-defined]
            yield self.env.timeout(service_time)
            self.in_service = False
            request["completion_time"] = self.env.now
            response_time = request["completion_time"] - request["arrival_time"]
            metrics.on_completion(self.env.now, self.server_id, response_time)


def run_simulation(
    policy_fn: Callable,
    policy_state: dict,
    lambda_rate: float,
    seed: int,
    *,
    server_mus: list[float] | None = None,
    buffer_capacity: int | None = None,
    record_n_trace: bool = False,
) -> dict:
    """
    Executa uma réplica da simulação.

    Retorna métricas agregadas no intervalo [WARMUP, SIM_TIME].
    """
    rng = random.Random(seed)
    env = simpy.Environment()
    env.rng = rng  # type: ignore[attr-defined]

    mus = server_mus or [MU] * NUM_SERVERS
    servers = [
        Server(env, i, mu=mus[i], buffer_capacity=buffer_capacity)
        for i in range(len(mus))
    ]
    metrics = SystemMetrics(num_servers=len(servers), record_n_trace=record_n_trace)
    env.metrics = metrics  # type: ignore[attr-defined]

    def arrival_process():
        req_id = 0
        while True:
            interarrival = rng.expovariate(lambda_rate)
            yield env.timeout(interarrival)
            if env.now >= SIM_TIME:
                return
            req_id += 1
            request = {
                "id": req_id,
                "arrival_time": env.now,
                "completion_time": None,
            }
            server = policy_fn(servers, rng, policy_state)
            if server.enqueue(request):
                metrics.on_arrival(env.now, server.server_id)
            else:
                metrics.on_drop(env.now)

    env.process(arrival_process())
    env.run(until=SIM_TIME)

    result = metrics.snapshot(SIM_TIME)
    return result
