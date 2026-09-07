"""Configuration for the load-balancer experiments."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SimulationConfig:
    """Parameters for both the analytical and burst traffic profiles."""

    num_servers: int = 3
    mu: float = 1.0
    lambdas: list[float] = field(default_factory=lambda: [0.6, 1.2, 1.8, 2.4, 2.7])
    unstable_lambda: float = 3.3
    policies: list[str] = field(
        default_factory=lambda: ["random", "round_robin", "shortest_queue"]
    )
    sim_time: float = 5000.0
    warmup_time: float = 500.0
    num_replicas: int = 10
    base_seeds: list[int] = field(
        default_factory=lambda: [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    )
    workers_per_server: int = 1
    traffic_profile: str = "poisson"
    burst_sizes: list[int] = field(default_factory=lambda: [30, 60, 90, 120])
    hurst: float = 0.8
    service_time: float = 0.05
    finite_capacity: int | None = None
    sample_interval: float = 1.0
    output_dir: Path = Path("results")
    plots_dir: Path = Path("results/plots")
    data_dir: Path = Path("results/data")
    logs_dir: Path = Path("results/logs")

    @classmethod
    def burst_profile(cls) -> "SimulationConfig":
        """Return the parameters from the original assignment description."""
        return cls(
            mu=20.0,
            lambdas=[10.0, 20.0, 30.0, 40.0],
            unstable_lambda=40.0,
            sim_time=200.0,
            warmup_time=0.0,
            workers_per_server=15,
            traffic_profile="bounded_pareto",
            finite_capacity=15,
            service_time=0.05,
        )

    def prepare_output_dirs(self) -> None:
        for directory in (self.output_dir, self.plots_dir, self.data_dir, self.logs_dir):
            Path(directory).mkdir(parents=True, exist_ok=True)

    def burst_size_for(self, lambda_rate: float) -> int:
        """Select the configured burst size associated with a load level."""
        try:
            index = self.lambdas.index(lambda_rate)
        except ValueError:
            index = 0
        return self.burst_sizes[index % len(self.burst_sizes)]
