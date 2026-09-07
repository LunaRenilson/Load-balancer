"""Stochastic traffic generators used by the simulation engine."""

import math
import random


def exponential_sample(rate: float, rng: random.Random) -> float:
    """Sample an exponential variate using inverse transform sampling."""
    if rate <= 0:
        raise ValueError("rate must be positive")
    return -math.log1p(-rng.random()) / rate


class PoissonTrafficGenerator:
    def __init__(self, lambda_rate: float, rng: random.Random):
        if lambda_rate <= 0:
            raise ValueError("lambda_rate must be positive")
        self.lambda_rate = lambda_rate
        self.rng = rng

    def next_interarrival(self) -> float:
        return exponential_sample(self.lambda_rate, self.rng)


class BoundedParetoGenerator:
    """Bounded Pareto variates with a configurable Hurst-oriented shape."""

    def __init__(self, minimum: float, maximum: float, hurst: float, rng: random.Random):
        if not 0 < minimum <= maximum:
            raise ValueError("minimum and maximum must satisfy 0 < minimum <= maximum")
        if not 0 < hurst < 1:
            raise ValueError("hurst must be between 0 and 1")
        self.minimum = minimum
        self.maximum = maximum
        self.alpha = 3.0 - 2.0 * hurst
        self.rng = rng

    def sample(self) -> float:
        alpha = self.alpha
        lower = self.minimum ** (-alpha)
        upper = self.maximum ** (-alpha)
        value = lower - self.rng.random() * (lower - upper)
        return value ** (-1.0 / alpha)


class BurstTrafficGenerator:
    """Generate bounded-Pareto gaps while capping each burst size."""

    def __init__(self, burst_size: int, lambda_rate: float, hurst: float, rng: random.Random):
        if burst_size <= 0:
            raise ValueError("burst_size must be positive")
        if lambda_rate <= 0:
            raise ValueError("lambda_rate must be positive")
        self.burst_size = burst_size
        self.burst_rate = lambda_rate / burst_size
        self.rng = rng
        self.remaining = 0
        self.gap_generator = BoundedParetoGenerator(0.001, 1.0, hurst, rng)

    def next_interarrival(self) -> float:
        if self.remaining == 0:
            self.remaining = self.burst_size
            interval = self.rng.expovariate(self.burst_rate)
        else:
            interval = self.gap_generator.sample()
        self.remaining -= 1
        return interval

    def burst(self) -> list[float]:
        return [self.next_interarrival() for _ in range(self.burst_size)]
