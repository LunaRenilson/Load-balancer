"""Execução dos experimentos do Trabalho 1 MC714."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from analytical import (
    analytical_table,
    mm1_per_server,
    mm1k_per_server,
    percent_gain,
    unstable_case_summary,
    verify_ordering,
)
from config import (
    BASE_SEED,
    BUFFER_K_VALUES,
    HETERO_MU,
    HETERO_WEIGHTS,
    LAMBDA_VALUES,
    NUM_REPLICAS,
    NUM_SERVERS,
    POLICIES,
    RESULTS_DIR,
    UNSTABLE_LAMBDA,
)
from metrics import aggregate_replicas
from policies import copy_state, get_policy
from simulator import run_simulation


def _ensure_results_dir() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def run_main_experiments() -> dict:
    """15 configurações: 5 λ × 3 políticas × 10 réplicas."""
    results = {}
    for policy_name in POLICIES:
        policy_fn, base_state = get_policy(policy_name)
        for lambda_rate in LAMBDA_VALUES:
            replicas = []
            for replica in range(NUM_REPLICAS):
                state = copy_state(base_state)
                seed = BASE_SEED + replica + int(lambda_rate * 100) + hash(policy_name) % 1000
                replicas.append(
                    run_simulation(policy_fn, state, lambda_rate, seed)
                )
            key = (policy_name, lambda_rate)
            results[key] = aggregate_replicas(replicas)
            results[key]["analytical"] = mm1_per_server(lambda_rate)
    return results


def run_unstable_experiment() -> dict:
    """Experimento λ=3.3 com rastreamento de N(t)."""
    unstable_results = {}
    for policy_name in POLICIES:
        policy_fn, base_state = get_policy(policy_name)
        replicas = []
        for replica in range(NUM_REPLICAS):
            state = copy_state(base_state)
            seed = BASE_SEED + 1000 + replica
            replicas.append(
                run_simulation(
                    policy_fn,
                    state,
                    UNSTABLE_LAMBDA,
                    seed,
                    record_n_trace=True,
                )
            )
        unstable_results[policy_name] = aggregate_replicas(replicas)
    unstable_results["analytical"] = unstable_case_summary()
    return unstable_results


def run_buffer_bonus(lambda_values: list[float] | None = None) -> dict:
    """Bônus: buffer finito M/M/1/K com política aleatória."""
    lambda_values = lambda_values or LAMBDA_VALUES
    policy_fn, base_state = get_policy("random")
    results = {}
    for k in BUFFER_K_VALUES:
        for lambda_rate in lambda_values:
            replicas = []
            for replica in range(NUM_REPLICAS):
                state = copy_state(base_state)
                seed = BASE_SEED + 2000 + k * 10 + replica + int(lambda_rate * 100)
                replicas.append(
                    run_simulation(
                        policy_fn,
                        state,
                        lambda_rate,
                        seed,
                        buffer_capacity=k,
                    )
                )
            key = (k, lambda_rate)
            results[key] = aggregate_replicas(replicas)
            results[key]["analytical"] = mm1k_per_server(lambda_rate, k)
    return results


def run_hetero_bonus(lambda_rate: float = 2.4) -> dict:
    """Bônus: servidores heterogêneos — roteamento uniforme vs proporcional a μ."""
    configs = {
        "uniform": ("random", {}),
        "proportional": ("random_weighted", {"weights": HETERO_WEIGHTS}),
    }
    results = {}
    for config_name, (policy_name, extra_state) in configs.items():
        policy_fn, base_state = get_policy(policy_name)
        state = copy_state(base_state)
        state.update(extra_state)
        replicas = []
        for replica in range(NUM_REPLICAS):
            rep_state = copy_state(state)
            seed = BASE_SEED + 3000 + replica + hash(config_name) % 100
            replicas.append(
                run_simulation(
                    policy_fn,
                    rep_state,
                    lambda_rate,
                    seed,
                    server_mus=HETERO_MU,
                )
            )
        results[config_name] = aggregate_replicas(replicas)
        results[config_name]["server_mus"] = HETERO_MU
    return results


def build_summary_rows(main_results: dict) -> list[dict]:
    """Converte resultados principais em linhas para CSV."""
    rows = []
    for policy_name in POLICIES:
        for lambda_rate in LAMBDA_VALUES:
            agg = main_results[(policy_name, lambda_rate)]
            analytical = agg["analytical"]
            row = {
                "policy": policy_name,
                "lambda": lambda_rate,
                "X_mean": agg["throughput"]["mean"],
                "X_ci_low": agg["throughput"]["ci_low"],
                "X_ci_high": agg["throughput"]["ci_high"],
                "E_R_mean": agg["mean_response"]["mean"],
                "E_R_ci_low": agg["mean_response"]["ci_low"],
                "E_R_ci_high": agg["mean_response"]["ci_high"],
                "E_N_mean": agg["mean_n"]["mean"],
                "E_N_ci_low": agg["mean_n"]["ci_low"],
                "E_N_ci_high": agg["mean_n"]["ci_high"],
                "U_mean": sum(u["mean"] for u in agg["utilizations"]) / NUM_SERVERS,
                "E_R_analytical": analytical["E_R"],
                "X_analytical": analytical["X"],
                "U_analytical": analytical["U_i"],
                "E_N_analytical": analytical["E_N"],
                "Little_product": agg["little_product"]["mean"],
                "Little_E_N": agg["mean_n"]["mean"],
            }
            rows.append(row)
    return rows


def build_ordering_analysis(main_results: dict) -> list[dict]:
    """Calcula ganhos percentuais e verifica ordenação de E[R]."""
    analysis = []
    for lambda_rate in LAMBDA_VALUES:
        er_random = main_results[("random", lambda_rate)]["mean_response"]["mean"]
        er_rr = main_results[("round_robin", lambda_rate)]["mean_response"]["mean"]
        er_jsq = main_results[("shortest_queue", lambda_rate)]["mean_response"]["mean"]
        er_analytical = mm1_per_server(lambda_rate)["E_R"]
        analysis.append(
            {
                "lambda": lambda_rate,
                "E_R_random": er_random,
                "E_R_round_robin": er_rr,
                "E_R_shortest_queue": er_jsq,
                "E_R_analytical": er_analytical,
                "gain_rr_pct": percent_gain(er_random, er_rr),
                "gain_jsq_pct": percent_gain(er_random, er_jsq),
                "ordering": verify_ordering(er_random, er_rr, er_jsq, er_analytical),
            }
        )
    return analysis


def save_results(
    main_results: dict,
    unstable_results: dict,
    buffer_results: dict,
    hetero_results: dict,
) -> None:
    """Persiste resultados em CSV e JSON."""
    out_dir = _ensure_results_dir()

    rows = build_summary_rows(main_results)
    csv_path = out_dir / "results.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    payload = {
        "main": {
            f"{policy}_{lam}": {
                "throughput": agg["throughput"],
                "mean_response": agg["mean_response"],
                "mean_n": agg["mean_n"],
                "utilizations": agg["utilizations"],
                "analytical": agg["analytical"],
            }
            for (policy, lam), agg in main_results.items()
        },
        "analytical_table": analytical_table(),
        "ordering_analysis": build_ordering_analysis(main_results),
        "unstable": {
            policy: {
                "mean_n": agg["mean_n"],
                "throughput": agg["throughput"],
                "n_trace": agg["replicas"][0].get("n_trace", []),
            }
            for policy, agg in unstable_results.items()
            if policy != "analytical"
        },
        "unstable_analytical": unstable_results.get("analytical"),
        "buffer_bonus": {
            f"K{k}_lambda{lam}": {
                "throughput": agg["throughput"],
                "dropped": agg["dropped"],
                "analytical": agg["analytical"],
            }
            for (k, lam), agg in buffer_results.items()
        },
        "hetero_bonus": hetero_results,
    }

    json_path = out_dir / "results.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)

    print(f"Resultados salvos em {csv_path} e {json_path}")


def run_all_experiments() -> tuple[dict, dict, dict, dict]:
    """Executa todos os experimentos e salva artefatos."""
    print("Executando experimentos principais (150 simulações)...")
    main_results = run_main_experiments()

    print(f"Executando experimento instável (λ={UNSTABLE_LAMBDA})...")
    unstable_results = run_unstable_experiment()

    print("Executando bônus buffer finito...")
    buffer_results = run_buffer_bonus()

    print("Executando bônus servidores heterogêneos...")
    hetero_results = run_hetero_bonus()

    save_results(main_results, unstable_results, buffer_results, hetero_results)
    return main_results, unstable_results, buffer_results, hetero_results
