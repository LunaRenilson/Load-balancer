"""Ponto de entrada: simulador MC714 Trabalho 1 (PDF oficial)."""

from __future__ import annotations

import argparse

from analytical import analytical_table, mm1_per_server
from config import LAMBDA_VALUES, MU, NUM_REPLICAS, POLICIES, SIM_TIME, WARMUP
from experiments import (
    run_all_experiments,
    run_buffer_bonus,
    run_main_experiments,
    run_unstable_experiment,
)
from plots import generate_all_plots, print_ordering_table


def print_analytical_table() -> None:
    """Imprime tabela analítica M/M/1 para os λ do experimento."""
    print(f"\n{'='*80}")
    print(f"  MODELO ANALÍTICO M/M/1 (μ={MU}, 3 servidores, política aleatória)")
    print(f"{'='*80}")
    print(
        f"{'λ':>6} {'ρ_i':>8} {'U_i':>8} {'E[N_i]':>10} {'E[TQ]':>10} "
        f"{'E[R]':>10} {'E[N]':>10} {'X':>8} {'Estável':>8}"
    )
    print("-" * 80)
    for row in analytical_table():
        stable = "Sim" if row["stable"] else "Não"
        if row["stable"]:
            print(
                f"{row['lambda']:>6.1f} {row['rho']:>8.4f} {row['U_i']:>8.4f} "
                f"{row['E_N_i']:>10.4f} {row['E_TQ']:>10.4f} {row['E_R']:>10.4f} "
                f"{row['E_N']:>10.4f} {row['X']:>8.2f} {stable:>8}"
            )
        else:
            print(f"{row['lambda']:>6.1f} {'∞':>8} {'—':>8} {'∞':>10} {'∞':>10} {'∞':>10} {'∞':>10} {'—':>8} {stable:>8}")


def print_main_summary(main_results: dict) -> None:
    """Imprime resumo dos experimentos principais."""
    print(f"\n{'='*90}")
    print(f"  RESULTADOS SIMULADOS ({NUM_REPLICAS} réplicas, {SIM_TIME} u.t., warm-up {WARMUP})")
    print(f"{'='*90}")
    print(
        f"{'Política':<18} {'λ':>5} {'X':>10} {'E[R]':>10} {'E[N]':>10} "
        f"{'U_avg':>8} {'E[R]_ana':>10}"
    )
    print("-" * 90)
    for policy in POLICIES:
        for lam in LAMBDA_VALUES:
            agg = main_results[(policy, lam)]
            u_avg = sum(u["mean"] for u in agg["utilizations"]) / len(agg["utilizations"])
            print(
                f"{policy:<18} {lam:>5.1f} "
                f"{agg['throughput']['mean']:>10.4f} "
                f"{agg['mean_response']['mean']:>10.4f} "
                f"{agg['mean_n']['mean']:>10.4f} "
                f"{u_avg:>8.4f} "
                f"{agg['analytical']['E_R']:>10.4f}"
            )
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulador MC714 Trabalho 1")
    parser.add_argument(
        "--mode",
        choices=["all", "main", "unstable", "bonus-buffer", "analytical"],
        default="all",
        help="Modo de execução",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "analytical":
        print_analytical_table()
        return

    if args.mode == "main":
        main_results = run_main_experiments()
        print_main_summary(main_results)
        print_ordering_table(main_results)
        print_analytical_table()
        return

    if args.mode == "unstable":
        run_unstable_experiment()
        return

    if args.mode == "bonus-buffer":
        run_buffer_bonus()
        return

    main_results, unstable_results, buffer_results = run_all_experiments()
    print_main_summary(main_results)
    print_ordering_table(main_results)
    print_analytical_table()
    generate_all_plots(main_results, unstable_results, buffer_results)


if __name__ == "__main__":
    main()
