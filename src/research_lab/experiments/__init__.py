"""Independently executable, reproducible experiments with a lazy registry."""

from .core import (
    ExperimentContext,
    ExperimentExecutionError,
    ExperimentRegistry,
    ExperimentRun,
    ExperimentSpec,
    compare_results,
    list_experiments,
    load_result,
    run_experiment,
)

__all__ = [
    "ExperimentContext",
    "ExperimentExecutionError",
    "ExperimentRegistry",
    "ExperimentRun",
    "ExperimentSpec",
    "compare_results",
    "list_experiments",
    "load_result",
    "run_experiment",
]
