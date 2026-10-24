"""Command-line entry point with no optional imports until an experiment runs."""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Sequence

from research_lab.experiments import (
    ExperimentExecutionError,
    compare_results,
    list_experiments,
    run_experiment,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="research-lab", description="Reproducible scientific research experiments"
    )
    parser.add_argument("--verbose", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "list", help="List registered experiments without loading scientific libraries"
    )
    run = commands.add_parser("run", help="Run and save one experiment")
    run.add_argument("name")
    run.add_argument("--params", default="{}", help="JSON object of experiment parameters")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--output", default="results")
    compare = commands.add_parser("compare", help="Compare two saved result.json files")
    compare.add_argument("left")
    compare.add_argument("right")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    try:
        if args.command == "list":
            print(
                json.dumps(
                    [
                        {
                            "name": s.name,
                            "description": s.description,
                            "hypothesis": s.hypothesis,
                            "parameters": s.parameters,
                        }
                        for s in list_experiments()
                    ],
                    indent=2,
                )
            )
        elif args.command == "run":
            parameters = json.loads(args.params)
            if not isinstance(parameters, dict):
                raise ValueError("--params must be a JSON object")
            result = run_experiment(args.name, parameters, seed=args.seed, output_dir=args.output)
            print(
                json.dumps(
                    {"status": result.record["status"], "result": str(result.path)}, indent=2
                )
            )
            return 0 if result.passed else 1
        else:
            print(json.dumps(compare_results(args.left, args.right), indent=2))
    except (ValueError, OSError, ExperimentExecutionError) as exc:
        parser.exit(2, f"research-lab: {exc}\n")
    return 0
