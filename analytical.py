"""Analytical M/M/1-per-server model for the Poisson profile."""


def analytical_metrics(lambda_val: float, mu: float = 1.0, num_servers: int = 3) -> dict[str, float | bool]:
    lambda_i = lambda_val / num_servers
    rho = lambda_i / mu
    stable = rho < 1.0
    if stable:
        mean_queue = rho / (mu * (1.0 - rho))
        mean_response = 1.0 / (mu - lambda_i)
        mean_server_customers = rho / (1.0 - rho)
    else:
        mean_queue = float("inf")
        mean_response = float("inf")
        mean_server_customers = float("inf")
    return {
        "lambda_i": lambda_i,
        "rho": rho,
        "U_theoretical": rho,
        "E_TQ_theoretical": mean_queue,
        "E_R_theoretical": mean_response,
        "E_N_i_theoretical": mean_server_customers,
        "E_N_system_theoretical": num_servers * mean_server_customers,
        "X_theoretical": lambda_val,
        "is_stable": stable,
        "fluid_growth_rate": max(0.0, lambda_val - num_servers * mu),
    }


def fluid_queue_size(time: float, lambda_val: float, mu: float, num_servers: int = 3) -> float:
    return max(0.0, (lambda_val - num_servers * mu) * time)
