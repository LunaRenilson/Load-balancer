"""Small structured logger for simulation traces."""

import logging
from pathlib import Path


def create_trace_logger(path: str | Path, enabled: bool = True) -> logging.Logger:
    logger = logging.getLogger(f"load_balancer.trace.{Path(path)}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if enabled and not logger.handlers:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(path, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


def trace(logger: logging.Logger | None, time: float, event: str, message: str) -> None:
    if logger is not None and logger.handlers:
        logger.info(f"[T={time:8.4f}] [{event:<5}] {message}")
