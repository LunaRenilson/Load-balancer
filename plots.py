"""Geração de gráficos para o Trabalho 1 MC714."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analytical import fluid_approximation_n, mm1_per_server
from config import (
    BUFFER_K_VALUES,
    LAMBDA_VALUES,
    POLICIES,
    POLICY_LABELS,
    RESULTS_DIR,
    UNSTABLE_LAMBDA,
    WARMUP,
)
from experiments import build_ordering_analysis


def _ensure_results_dir() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def plot_er_vs_lambda(main_results: dict) -> Path:
    """Gráfico principal: E[R] analítico vs simulado com IC 95%."""
    out_dir = _ensure_results_dir()
    fig, ax = plt.subplots(figsize=(8, 5))

    lambdas = np.array(LAMBDA_VALUES, dtype=float)
    analytical_er = [mm1_per_server(lam)["E_R"] for lam in lambdas]
    ax.plot(lambdas, analytical_er, "k--", linewidth=2, label="Analítico (Aleatória)")

    markers = {"random": "o", "round_robin": "s", "shortest_queue": "^"}
    for policy in POLICIES:
        means = []
        yerr_low = []
        yerr_high = []
        for lam in LAMBDA_VALUES:
            agg = main_results[(policy, lam)]
            means.append(agg["mean_response"]["mean"])
            yerr_low.append(agg["mean_response"]["mean"] - agg["mean_response"]["ci_low"])
            yerr_high.append(agg["mean_response"]["ci_high"] - agg["mean_response"]["mean"])
        ax.errorbar(
            lambdas,
            means,
            yerr=[yerr_low, yerr_high],
            fmt=f"{markers[policy]}-",
            capsize=4,
            label=POLICY_LABELS[policy],
        )

    ax.set_xlabel("λ (requisições/u.t.)")
    ax.set_ylabel("E[R] (u.t.)")
    ax.set_title("Tempo médio de resposta vs taxa de chegada")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = out_dir / "er_vs_lambda.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_little_law(main_results: dict) -> Path:
    """Verificação da Lei de Little: E[N] vs X·E[R]."""
    out_dir = _ensure_results_dir()
    fig, ax = plt.subplots(figsize=(7, 5))

    x_vals = []
    y_vals = []
    for policy in POLICIES:
        for lam in LAMBDA_VALUES:
            agg = main_results[(policy, lam)]
            x_vals.append(agg["little_product"]["mean"])
            y_vals.append(agg["mean_n"]["mean"])

    ax.scatter(x_vals, y_vals, alpha=0.7)
    lim = max(max(x_vals), max(y_vals)) * 1.1
    ax.plot([0, lim], [0, lim], "k--", label="E[N] = X·E[R]")
    ax.set_xlabel("X · E[R]")
    ax.set_ylabel("E[N] (simulado)")
    ax.set_title("Lei de Little")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = out_dir / "little_law_check.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_unstable_n(unstable_results: dict) -> Path:
    """N(t) para λ=3.3 vs aproximação fluida."""
    out_dir = _ensure_results_dir()
    fig, ax = plt.subplots(figsize=(9, 5))

    agg = unstable_results["random"]
    trace = agg["replicas"][0].get("n_trace", [])
    if trace:
        times = [t for t, _ in trace if t >= WARMUP]
        values = [n for t, n in trace if t >= WARMUP]
        ax.plot(times, values, alpha=0.7, label="N(t) simulado (Aleatória)")

        n0 = values[0] if values else 0
        t_grid = np.linspace(WARMUP, max(times) if times else WARMUP + 100, 200)
        fluid = [fluid_approximation_n(t - WARMUP, n0, UNSTABLE_LAMBDA) for t in t_grid]
        ax.plot(t_grid, fluid, "r--", linewidth=2, label=r"$N(t) \approx N(0) + (\lambda - 3\mu)t$")

    ax.set_xlabel("Tempo (u.t.)")
    ax.set_ylabel("N(t) — requisições no sistema")
    ax.set_title(f"Dinâmica instável com λ = {UNSTABLE_LAMBDA}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = out_dir / "N_t_lambda33.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_buffer_bonus(buffer_results: dict) -> Path:
    """Bônus: vazão efetiva e perda vs K."""
    out_dir = _ensure_results_dir()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    lam = LAMBDA_VALUES[-1]

    x_vals = []
    x_sim = []
    x_ana = []
    p_sim = []
    p_ana = []
    for k in BUFFER_K_VALUES:
        agg = buffer_results[(k, lam)]
        x_vals.append(k)
        x_sim.append(agg["throughput"]["mean"])
        x_ana.append(agg["analytical"]["X_eff"])
        arrivals = agg["replicas"][0]["arrivals"]
        p_sim.append(agg["dropped"]["mean"] / arrivals if arrivals else 0)
        p_ana.append(agg["analytical"]["P_loss"])

    axes[0].plot(x_vals, x_sim, "o-", label="Simulado")
    axes[0].plot(x_vals, x_ana, "s--", label="Analítico")
    axes[0].set_xlabel("K (capacidade da fila)")
    axes[0].set_ylabel("Vazão efetiva X")
    axes[0].set_title(f"Vazão efetiva (λ={lam})")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(x_vals, p_sim, "o-", label="Simulado")
    axes[1].plot(x_vals, p_ana, "s--", label="Analítico")
    axes[1].set_xlabel("K (capacidade da fila)")
    axes[1].set_ylabel("Probabilidade de perda")
    axes[1].set_title(f"P_perda (λ={lam})")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    path = out_dir / "bonus_buffer.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_hetero_bonus(hetero_results: dict) -> Path:
    """Bônus: comparação uniforme vs roteamento proporcional a μ."""
    out_dir = _ensure_results_dir()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    configs = ["uniform", "proportional"]
    labels = ["Uniforme (1/3)", "Proporcional a μ"]
    er_vals = [hetero_results[c]["mean_response"]["mean"] for c in configs]
    axes[0].bar(labels, er_vals, color=["#4C72B0", "#55A868"])
    axes[0].set_ylabel("E[R]")
    axes[0].set_title("Tempo médio de resposta")

    util_uniform = hetero_results["uniform"]["utilizations"]
    util_prop = hetero_results["proportional"]["utilizations"]
    x = np.arange(3)
    width = 0.35
    axes[1].bar(x - width / 2, [u["mean"] for u in util_uniform], width, label="Uniforme")
    axes[1].bar(x + width / 2, [u["mean"] for u in util_prop], width, label="Proporcional")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(["μ=1.5", "μ=1.0", "μ=0.5"])
    axes[1].set_ylabel("Utilização U_i")
    axes[1].set_title("Utilização por servidor")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    path = out_dir / "bonus_hetero.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_all_plots(
    main_results: dict,
    unstable_results: dict,
    buffer_results: dict,
    hetero_results: dict,
) -> list[Path]:
    """Gera todos os gráficos exigidos."""
    paths = [
        plot_er_vs_lambda(main_results),
        plot_little_law(main_results),
        plot_unstable_n(unstable_results),
        plot_buffer_bonus(buffer_results),
        plot_hetero_bonus(hetero_results),
    ]
    for path in paths:
        print(f"Gráfico salvo: {path}")
    return paths


def print_ordering_table(main_results: dict) -> None:
    """Imprime tabela de ordenação e ganhos percentuais."""
    analysis = build_ordering_analysis(main_results)
    print(f"\n{'λ':>5} {'E[R]_Rand':>10} {'E[R]_RR':>10} {'E[R]_JSQ':>10} {'Analítico':>10} {'G%RR':>8} {'G%JSQ':>8}")
    print("-" * 70)
    for row in analysis:
        print(
            f"{row['lambda']:>5.1f} "
            f"{row['E_R_random']:>10.4f} "
            f"{row['E_R_round_robin']:>10.4f} "
            f"{row['E_R_shortest_queue']:>10.4f} "
            f"{row['E_R_analytical']:>10.4f} "
            f"{row['gain_rr_pct']:>8.2f} "
            f"{row['gain_jsq_pct']:>8.2f}"
        )
