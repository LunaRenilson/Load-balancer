"""CSV export and summary statistics."""

import csv
import math
from pathlib import Path
from statistics import mean, stdev

from scipy.stats import t

from analytical import analytical_metrics
from simulation import SimulationResult


def write_csv(path: str | Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_raw(results: list[SimulationResult], path: str | Path) -> None:
    write_csv(path, [result.as_dict() for result in results])


def _summary(values: list[float]) -> tuple[float, float, float]:
    average = mean(values)
    deviation = stdev(values) if len(values) > 1 else 0.0
    margin = (
        t.ppf(0.975, len(values) - 1) * deviation / math.sqrt(len(values))
        if len(values) > 1
        else 0.0
    )
    return average, deviation, margin


def summarize(
    results: list[SimulationResult],
    mu: float,
    num_servers: int,
    profile: str = "plan",
) -> list[dict]:
    groups: dict[tuple[str, float], list[SimulationResult]] = {}
    for result in results:
        groups.setdefault((result.policy, result.lambda_rate), []).append(result)
    rows = []
    for (policy, lambda_rate), group in sorted(groups.items()):
        values = {
            "throughput": [item.throughput for item in group],
            "response": [item.mean_response_time for item in group],
            "system_customers": [item.mean_system_customers for item in group],
        }
        for index in range(num_servers):
            values[f"u{index + 1}"] = [item.utilizations[index] for item in group]
        summaries = {name: _summary(items) for name, items in values.items()}
        row = {
            "policy": policy,
            "lambda": lambda_rate,
            "replicas": len(group),
        }
        for name, (average, deviation, margin) in summaries.items():
            output_name = {
                "throughput": "throughput",
                "response": "response_time",
                "system_customers": "system_customers",
            }.get(name, name)
            row[f"{output_name}_mean"] = average
            row[f"{output_name}_std"] = deviation
            row[f"{output_name}_ci95"] = margin
        row["u_mean"] = mean(sum(item.utilizations) / len(item.utilizations) for item in group)
        row["little_law_product"] = row["throughput_mean"] * row["response_time_mean"]
        row["little_law_error"] = row["system_customers_mean"] - row["little_law_product"]
        row["little_law_relative_error"] = (
            abs(row["little_law_error"]) / row["system_customers_mean"]
            if row["system_customers_mean"]
            else 0.0
        )
        row["little_law_ok"] = row["little_law_relative_error"] <= 0.05
        if profile == "plan":
            metrics = analytical_metrics(lambda_rate, mu, num_servers)
            row.update(
                {
                    "theoretical_response_time": metrics["E_R_theoretical"],
                    "theoretical_throughput": metrics["X_theoretical"],
                    "theoretical_utilization": metrics["U_theoretical"],
                    "theoretical_system_customers": metrics["E_N_system_theoretical"],
                }
            )
        rows.append(row)
    return rows


def policy_gains(summary_rows: list[dict]) -> list[dict]:
    random_response = {
        row["lambda"]: row["response_time_mean"]
        for row in summary_rows
        if row["policy"] == "random"
    }
    rows = []
    for row in summary_rows:
        if row["policy"] == "random":
            continue
        if row["lambda"] not in random_response:
            continue
        baseline = random_response[row["lambda"]]
        gain = 100.0 * (baseline - row["response_time_mean"]) / baseline if baseline else 0.0
        rows.append({"lambda": row["lambda"], "policy": row["policy"], "gain_percent": gain})
    return rows


def consolidate_samples(
    samples_by_policy: dict[str, list[dict[str, float]]],
    lambda_rate: float,
    mu: float,
    num_servers: int,
) -> list[dict[str, float]]:
    policy_columns = {
        "random": "N_sim_Random",
        "round_robin": "N_sim_RR",
        "shortest_queue": "N_sim_JSQ",
    }
    by_time: dict[float, dict[str, float]] = {}
    for policy, samples in samples_by_policy.items():
        for sample in samples:
            row = by_time.setdefault(sample["time"], {"time": sample["time"]})
            row[policy_columns.get(policy, f"N_sim_{policy}")] = sample["n_total"]
    for row in by_time.values():
        row["N_fluido"] = max(0.0, (lambda_rate - num_servers * mu) * row["time"])
    return [by_time[time] for time in sorted(by_time)]
