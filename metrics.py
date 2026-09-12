"""Coleta de métricas e estatísticas de simulação."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from config import MEASURE_DURATION, NUM_REPLICAS, T_CRITICAL_95, WARMUP


class SystemMetrics:
    """Rastreia N(t), tempos de resposta e utilização por servidor."""

    def __init__(self, num_servers: int, record_n_trace: bool = False):
        self.num_servers = num_servers
        self.record_n_trace = record_n_trace
        self.reset()

    def reset(self):
        self.current_n = 0
        self.last_event_time = WARMUP
        self.n_area = 0.0
        self.response_times: list[float] = []
        self.completions_in_window = 0
        self.arrivals_in_window = 0
        self.dropped_in_window = 0
        self.server_busy_time = [0.0] * self.num_servers
        self.server_assignments = [0] * self.num_servers
        self.server_busy_since: list[float | None] = [None] * self.num_servers
        self.n_trace: list[tuple[float, int]] = []

    def _accumulate_n(self, now: float):
        if now <= WARMUP:
            return
        start = max(self.last_event_time, WARMUP)
        if now > start:
            self.n_area += self.current_n * (now - start)
            self.last_event_time = now

    def on_arrival(self, now: float, server_id: int):
        self._accumulate_n(now)
        self.current_n += 1
        if now >= WARMUP:
            self.arrivals_in_window += 1
            self.server_assignments[server_id] += 1
        if self.record_n_trace and (
            len(self.n_trace) == 0 or self.n_trace[-1][0] != now
        ):
            self.n_trace.append((now, self.current_n))

    def on_enter_service(self, now: float, server_id: int):
        if self.server_busy_since[server_id] is None:
            self.server_busy_since[server_id] = now

    def on_completion(self, now: float, server_id: int, response_time: float):
        self._accumulate_n(now)
        self.current_n -= 1
        if self.server_busy_since[server_id] is not None:
            busy_start = max(self.server_busy_since[server_id], WARMUP)
            if now > busy_start:
                self.server_busy_time[server_id] += now - busy_start
            self.server_busy_since[server_id] = None
        if now >= WARMUP:
            self.completions_in_window += 1
            self.response_times.append(response_time)
        if self.record_n_trace:
            self.n_trace.append((now, self.current_n))

    def on_drop(self, now: float):
        if now >= WARMUP:
            self.dropped_in_window += 1

    def finalize(self, sim_time: float):
        self._accumulate_n(sim_time)
        for server_id, busy_since in enumerate(self.server_busy_since):
            if busy_since is not None:
                busy_start = max(busy_since, WARMUP)
                if sim_time > busy_start:
                    self.server_busy_time[server_id] += sim_time - busy_start

    def snapshot(self, sim_time: float) -> dict:
        self.finalize(sim_time)
        mean_n = self.n_area / MEASURE_DURATION if MEASURE_DURATION > 0 else 0.0
        throughput = self.completions_in_window / MEASURE_DURATION
        mean_response = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else float("nan")
        )
        utilizations = [
            busy / MEASURE_DURATION for busy in self.server_busy_time
        ]
        return {
            "throughput": throughput,
            "mean_response": mean_response,
            "mean_n": mean_n,
            "utilizations": utilizations,
            "completions": self.completions_in_window,
            "arrivals": self.arrivals_in_window,
            "dropped": self.dropped_in_window,
            "server_assignments": list(self.server_assignments),
            "n_trace": list(self.n_trace),
            "little_product": throughput * mean_response
            if not math.isnan(mean_response)
            else float("nan"),
        }


def confidence_interval_95(values: Iterable[float]) -> dict[str, float]:
    """Calcula média e intervalo de confiança de 95% (t de Student, n=10)."""
    arr = np.asarray(list(values), dtype=float)
    n = len(arr)
    if n == 0:
        return {"mean": float("nan"), "std": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    mean = float(np.mean(arr))
    if n == 1:
        return {"mean": mean, "std": 0.0, "ci_low": mean, "ci_high": mean}
    std = float(np.std(arr, ddof=1))
    margin = T_CRITICAL_95 * std / math.sqrt(n)
    return {
        "mean": mean,
        "std": std,
        "ci_low": mean - margin,
        "ci_high": mean + margin,
    }


def aggregate_replicas(replica_metrics: list[dict]) -> dict:
    """Agrega métricas de NUM_REPLICAS execuções com IC 95%."""
    fields = ["throughput", "mean_response", "mean_n", "little_product", "dropped"]
    aggregated: dict = {}
    for field in fields:
        aggregated[field] = confidence_interval_95(
            metric[field] for metric in replica_metrics
        )

    utilizations_per_server = []
    for server_idx in range(len(replica_metrics[0]["utilizations"])):
        utilizations_per_server.append(
            confidence_interval_95(
                metric["utilizations"][server_idx] for metric in replica_metrics
            )
        )
    aggregated["utilizations"] = utilizations_per_server

    assignments_per_server = []
    for server_idx in range(len(replica_metrics[0]["server_assignments"])):
        assignments_per_server.append(
            confidence_interval_95(
                metric["server_assignments"][server_idx] for metric in replica_metrics
            )
        )
    aggregated["server_assignments"] = assignments_per_server
    aggregated["replicas"] = replica_metrics
    return aggregated
