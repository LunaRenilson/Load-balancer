"""Command-line entry point for the complete experiment pipeline."""

import argparse
from collections import defaultdict

from config import SimulationConfig
from exporter import consolidate_samples, export_raw, policy_gains, summarize, write_csv
from logger import create_trace_logger
from plots import generate_plots
from simulation import Simulation


def parse_args():
    parser = argparse.ArgumentParser(description="Simulador de balanceador de carga MC714")
    parser.add_argument("--profile", choices=["plan", "burst"], default="plan")
    parser.add_argument("--policy", "-p", choices=["random", "round_robin", "shortest_queue", "all"], default="all")
    parser.add_argument("--lambda", "-l", dest="lambda_rate", type=float)
    parser.add_argument("--duration", "-d", type=float)
    parser.add_argument("--warmup", "-w", type=float)
    parser.add_argument("--replicas", "-r", type=int)
    parser.add_argument("--seed", "-s", type=int)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--export-csv", action="store_true")
    parser.add_argument("--generate-plots", action="store_true")
    parser.add_argument("--quick", action="store_true", help="Executa uma réplica curta para smoke test")
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SimulationConfig() if args.profile == "plan" else SimulationConfig.burst_profile()
    print(f"Servico iniciado e em execucao: perfil={args.profile}", flush=True)
    if args.policy != "all":
        config.policies = [args.policy]
    if args.lambda_rate is not None:
        config.lambdas = [args.lambda_rate]
    if args.duration is not None:
        config.sim_time = args.duration
    if args.warmup is not None:
        config.warmup_time = args.warmup
    if args.replicas is not None:
        config.num_replicas = args.replicas
    if args.seed is not None:
        config.base_seeds = [args.seed + index for index in range(config.num_replicas)]
    if args.quick:
        config.sim_time = min(config.sim_time, 50.0)
        config.warmup_time = min(config.warmup_time, config.sim_time / 10.0)
        config.num_replicas = 1
    if config.sim_time <= config.warmup_time:
        raise ValueError("duration must be greater than warmup")
    config.prepare_output_dirs()
    logger = create_trace_logger(config.logs_dir / "simulation_trace.log", enabled=args.verbose)
    engine = Simulation(config, logger)

    stable_results = []
    for policy in config.policies:
        for lambda_rate in config.lambdas:
            for replica in range(config.num_replicas):
                seed = config.base_seeds[replica % len(config.base_seeds)]
                stable_results.append(engine.run(policy, lambda_rate, seed))

    export_raw(stable_results, config.data_dir / "raw_replicas_results.csv")
    summary_rows = summarize(stable_results, config.mu, config.num_servers, args.profile)
    write_csv(config.data_dir / "summary_results.csv", summary_rows)
    write_csv(config.data_dir / "policy_gains.csv", policy_gains(summary_rows))

    unstable_samples = defaultdict(list)
    for policy in config.policies:
        replica_samples = []
        for replica in range(config.num_replicas):
            seed = config.base_seeds[replica % len(config.base_seeds)]
            replica_samples.append(engine.run(policy, config.unstable_lambda, seed).samples)
        by_time = defaultdict(list)
        for samples in replica_samples:
            for sample in samples:
                by_time[sample["time"]].append(sample["n_total"])
        unstable_samples[policy] = [
            {"time": time, "n_total": sum(values) / len(values)}
            for time, values in sorted(by_time.items())
        ]
    if unstable_samples:
        rows = consolidate_samples(
            unstable_samples,
            config.unstable_lambda,
            config.mu,
            config.num_servers,
        )
        lambda_label = str(config.unstable_lambda).replace(".", "_")
        write_csv(config.data_dir / f"queue_fluid_lambda_{lambda_label}.csv", rows)

    if not args.no_plots and (args.generate_plots or not args.export_csv):
        generate_plots(summary_rows, unstable_samples, config.plots_dir, args.profile)
    print(f"Experimentos concluídos: {len(stable_results)} réplicas")
    print(f"Resultados: {config.data_dir}")


if __name__ == "__main__":
    main()
