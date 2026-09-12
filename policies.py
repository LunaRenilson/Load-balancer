"""Políticas de balanceamento de carga."""

from __future__ import annotations

from typing import Any


def policy_random(servers, rng, _state=None):
    """Escolha aleatória com probabilidade uniforme 1/n."""
    return rng.choice(servers)


def policy_round_robin(servers, rng, state):
    """Distribuição cíclica entre servidores."""
    server = servers[state["rr_index"] % len(servers)]
    state["rr_index"] += 1
    return server


def policy_shortest_queue(servers, rng, _state=None):
    """Envia para o servidor com menor carga; empates resolvidos aleatoriamente."""
    min_load = min(server.load for server in servers)
    candidates = [server for server in servers if server.load == min_load]
    return rng.choice(candidates)


def policy_random_weighted(servers, rng, state):
    """Escolha aleatória com pesos configurados em state['weights']."""
    return rng.choices(servers, weights=state["weights"], k=1)[0]


def get_policy(name: str):
    """Retorna função de política e estado inicial."""
    policies = {
        "random": (policy_random, {}),
        "round_robin": (policy_round_robin, {"rr_index": 0}),
        "shortest_queue": (policy_shortest_queue, {}),
        "random_weighted": (policy_random_weighted, {}),
    }
    if name not in policies:
        raise ValueError(f"Política desconhecida: {name}")
    return policies[name]


def copy_state(state: dict[str, Any]) -> dict[str, Any]:
    """Cria cópia do estado da política para cada réplica."""
    return dict(state)
