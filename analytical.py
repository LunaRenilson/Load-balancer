"""Modelagem analítica M/M/1 e M/M/1/K conforme PDF do trabalho."""

from __future__ import annotations

import math

from config import LAMBDA_VALUES, MU, NUM_SERVERS, UNSTABLE_LAMBDA


def mm1_per_server(lambda_rate: float, mu: float = MU, num_servers: int = NUM_SERVERS) -> dict:
    """Modelo M/M/1 por servidor sob política aleatória (λ_i = λ/n)."""
    lambda_i = lambda_rate / num_servers
    rho = lambda_i / mu
    stable = rho < 1.0

    if not stable:
        return {
            "lambda": lambda_rate,
            "lambda_i": lambda_i,
            "rho": rho,
            "stable": False,
            "X": lambda_rate,
            "U_i": rho,
            "E_N_i": float("inf"),
            "E_TQ": float("inf"),
            "E_R": float("inf"),
            "E_N": float("inf"),
        }

    e_n_i = rho / (1.0 - rho)
    e_tq = rho / (mu * (1.0 - rho))
    e_r = 1.0 / (mu - lambda_i)
    return {
        "lambda": lambda_rate,
        "lambda_i": lambda_i,
        "rho": rho,
        "stable": True,
        "X": lambda_rate,
        "U_i": rho,
        "E_N_i": e_n_i,
        "E_TQ": e_tq,
        "E_R": e_r,
        "E_N": e_n_i * num_servers,
    }


def mm1k_per_server(
    lambda_rate: float,
    k: int,
    mu: float = MU,
    num_servers: int = NUM_SERVERS,
) -> dict:
    """Modelo M/M/1/K por servidor com roteamento aleatório uniforme."""
    lambda_i = lambda_rate / num_servers
    rho = lambda_i / mu

    if abs(rho - 1.0) < 1e-12:
        p0 = 1.0 / (k + 1)
        pk = p0
    else:
        p0 = (1.0 - rho) / (1.0 - rho ** (k + 1))
        pk = p0 * (rho ** k)

    p_loss = pk
    x_eff = lambda_rate * (1.0 - p_loss)
    return {
        "lambda": lambda_rate,
        "K": k,
        "rho": rho,
        "p0": p0,
        "p_K": pk,
        "P_loss": p_loss,
        "X_eff": x_eff,
    }


def analytical_table(lambda_values: list[float] | None = None) -> list[dict]:
    """Tabela analítica para os λ do experimento principal."""
    values = lambda_values or LAMBDA_VALUES
    return [mm1_per_server(lam) for lam in values]


def fluid_approximation_n(t: float, n0: float, lambda_rate: float, mu: float = MU) -> float:
    """Aproximação fluida N(t) ≈ N(0) + (λ - n·μ) t para n servidores."""
    return n0 + (lambda_rate - NUM_SERVERS * mu) * t


def stability_condition(lambda_rate: float, mu: float = MU, num_servers: int = NUM_SERVERS) -> bool:
    """Sistema estável quando λ < n·μ."""
    return lambda_rate < num_servers * mu


def percent_gain(baseline: float, improved: float) -> float:
    """Ganho percentual de redução de E[R] em relação à política aleatória."""
    if baseline <= 0 or math.isnan(baseline) or math.isinf(baseline):
        return float("nan")
    return 100.0 * (baseline - improved) / baseline


def verify_ordering(
    er_random: float,
    er_rr: float,
    er_jsq: float,
    er_analytical: float,
) -> dict:
    """Verifica ordenação esperada E[R]_JSQ ≤ E[R]_RR ≤ E[R]_Random ≈ analítico."""
    return {
        "jsq_le_rr": er_jsq <= er_rr + 1e-9,
        "rr_le_random": er_rr <= er_random + 1e-9,
        "random_near_analytical": abs(er_random - er_analytical) / er_analytical < 0.1
        if er_analytical > 0
        else False,
    }


def unstable_case_summary() -> dict:
    """Resumo analítico para λ = 3.3."""
    lam = UNSTABLE_LAMBDA
    return {
        "lambda": lam,
        "capacity": NUM_SERVERS * MU,
        "stable": stability_condition(lam),
        "drift": lam - NUM_SERVERS * MU,
        "explanation": "λ > 3μ implica filas crescentes; fórmulas M/M/1 estacionárias não se aplicam.",
    }
