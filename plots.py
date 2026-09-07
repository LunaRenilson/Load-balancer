"""Plot generation kept separate from the simulation engine."""

from pathlib import Path

from analytical import analytical_metrics, fluid_queue_size


def generate_plots(
    summary_rows: list[dict],
    unstable_results,
    output_dir: str | Path,
    profile: str = "plan",
) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("matplotlib is required to generate plots") from error

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    policies = sorted({row["policy"] for row in summary_rows})
    lambdas = sorted({row["lambda"] for row in summary_rows})

    figure, axis = plt.subplots(figsize=(8, 5))
    if profile == "plan":
        theory = [analytical_metrics(value)["E_R_theoretical"] for value in lambdas]
        axis.plot(lambdas, theory, "k--", label="M/M/1 teórico")
    for policy in policies:
        rows = [row for row in summary_rows if row["policy"] == policy]
        rows.sort(key=lambda row: row["lambda"])
        axis.errorbar(
            [row["lambda"] for row in rows],
            [row["response_time_mean"] for row in rows],
            yerr=[row["response_time_ci95"] for row in rows],
            marker="o",
            capsize=3,
            label=policy,
        )
    axis.set(xlabel="Taxa de chegada (lambda)", ylabel="Tempo médio de resposta")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output / "fig1_response_time_vs_lambda.png", dpi=300)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 5))
    for policy in policies:
        rows = sorted((row for row in summary_rows if row["policy"] == policy), key=lambda row: row["lambda"])
        axis.plot([row["lambda"] for row in rows], [row["u_mean"] for row in rows], "o-", label=policy)
    if profile == "plan":
        axis.plot(lambdas, [value / 3.0 for value in lambdas], "k--", label="rho teórico")
    axis.set(xlabel="Taxa de chegada (lambda)", ylabel="Utilização média")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output / "fig2_server_utilization.png", dpi=300)
    plt.close(figure)

    if unstable_results:
        figure, axis = plt.subplots(figsize=(8, 5))
        for policy in policies:
            samples = unstable_results.get(policy, [])
            if samples:
                axis.plot([sample["time"] for sample in samples], [sample["n_total"] for sample in samples], label=policy)
        if unstable_results:
            first = next(iter(unstable_results.values()))
            axis.plot([sample["time"] for sample in first], [fluid_queue_size(sample["time"], 3.3, 1.0) for sample in first], "k--", label="fluido")
        axis.set(xlabel="Tempo", ylabel="Requisições no sistema")
        axis.grid(alpha=0.25)
        axis.legend()
        figure.tight_layout()
        figure.savefig(output / "fig3_unstable_queue_growth.png", dpi=300)
        plt.close(figure)
