"""Domain entities and routing policies for the load balancer."""

from dataclasses import dataclass
import random
from typing import Callable

import simpy


@dataclass
class Request:
    req_id: int
    arrival_time: float
    dispatch_time: float | None = None
    service_start_time: float | None = None
    completion_time: float | None = None
    assigned_server_id: int | None = None

    @property
    def response_time(self) -> float | None:
        if self.completion_time is None:
            return None
        return self.completion_time - self.arrival_time

    @property
    def queue_time(self) -> float | None:
        if self.service_start_time is None or self.dispatch_time is None:
            return None
        return self.service_start_time - self.dispatch_time

    @property
    def service_time(self) -> float | None:
        if self.completion_time is None or self.service_start_time is None:
            return None
        return self.completion_time - self.service_start_time


class Server:
    def __init__(
        self,
        env: simpy.Environment,
        server_id: int,
        service_sampler: Callable[[], float],
        workers: int = 1,
        capacity: int | None = None,
        on_start: Callable[["Server", Request], None] | None = None,
        on_complete: Callable[["Server", Request], None] | None = None,
    ):
        self.env = env
        self.server_id = server_id
        self.service_sampler = service_sampler
        self.capacity = capacity
        self.queue: list[Request] = []
        self.current_requests: list[Request] = []
        self.on_start = on_start
        self.on_complete = on_complete
        self._store = simpy.Store(env)
        for _ in range(workers):
            env.process(self._worker())

    @property
    def current_request(self) -> Request | None:
        return self.current_requests[0] if self.current_requests else None

    @property
    def load(self) -> int:
        return len(self.queue) + len(self.current_requests)

    def enqueue(self, request: Request) -> bool:
        if self.capacity is not None and self.load >= self.capacity:
            return False
        self.queue.append(request)
        self._store.put(request)
        return True

    def _worker(self):
        while True:
            request = yield self._store.get()
            self.queue.remove(request)
            self.current_requests.append(request)
            request.service_start_time = self.env.now
            if self.on_start:
                self.on_start(self, request)
            yield self.env.timeout(self.service_sampler())
            request.completion_time = self.env.now
            if self.on_complete:
                self.on_complete(self, request)
            self.current_requests.remove(request)


class RandomPolicy:
    name = "random"

    def select(self, servers: list[Server], rng: random.Random) -> Server:
        return rng.choice(servers)


class RoundRobinPolicy:
    name = "round_robin"

    def __init__(self):
        self.index = 0

    def select(self, servers: list[Server], rng: random.Random) -> Server:
        server = servers[self.index % len(servers)]
        self.index += 1
        return server


class ShortestQueuePolicy:
    name = "shortest_queue"

    def select(self, servers: list[Server], rng: random.Random) -> Server:
        minimum = min(server.load for server in servers)
        candidates = [server for server in servers if server.load == minimum]
        return rng.choice(candidates)


class LoadBalancer:
    def __init__(self, policy: str, rng: random.Random):
        policies = {
            "random": RandomPolicy,
            "round_robin": RoundRobinPolicy,
            "shortest_queue": ShortestQueuePolicy,
        }
        if policy not in policies:
            raise ValueError(f"Unknown policy: {policy}")
        self.policy = policies[policy]()
        self.rng = rng

    def dispatch(self, request: Request, servers: list[Server], now: float) -> Server | None:
        server = self.policy.select(servers, self.rng)
        if not server.enqueue(request):
            return None
        request.dispatch_time = now
        request.assigned_server_id = server.server_id
        return server
