"""Small builtin experiments. Scientific packages load only inside each callback."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any

from .core import ExperimentContext, ExperimentSpec


def _integer(parameters: dict[str, Any], name: str, lower: int, upper: int) -> int:
    value = parameters[name]
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{name} must be an integer between {lower} and {upper}")
    return value


def _structural(context: ExperimentContext) -> dict[str, Any]:
    from research_lab.structural_logic import (
        EXAMPLES,
        binary_to_notation,
        binary_to_tree,
        dyck_words,
        explore,
        metrics,
        ordered_trees,
    )

    generation = _integer(context.parameters, "max_generation", 0, 8)
    cap = _integer(context.parameters, "max_states", 1, 50000)
    rules = context.parameters["rules"]
    if not isinstance(rules, list) or not rules or any(not isinstance(r, str) for r in rules):
        raise ValueError("rules must be a nonempty list of rule names")
    if len(rules) != len(set(rules)):
        raise ValueError("rule names must be unique")
    if type(context.parameters["visualize"]) is not bool:
        raise ValueError("visualize must be a boolean")
    models: dict[str, Any] = {}
    for rule in rules:
        exploration = explore(generation, rule=rule, max_states=cap)
        models[rule] = {
            "stages": [list(stage) for stage in exploration.stages],
            "counts": [len(stage) for stage in exploration.stages],
            "transitions": [asdict(edge) for edge in exploration.transitions],
            "measurements": [
                {"generation": i, "word": word, **metrics(word)}
                for i, stage in enumerate(exploration.stages)
                for word in stage
            ],
            "examples_reached": {
                word: any(word in stage for stage in exploration.stages) for word in EXAMPLES
            },
        }
        if context.parameters["visualize"]:
            from research_lab.visualization import plot_transitions, save_figure, transition_figure

            save_figure(
                transition_figure(exploration.stages, exploration.transitions),
                context.artifacts / f"{rule}-transitions.html",
            )
            fig = plot_transitions(exploration.stages, exploration.transitions)
            save_figure(fig, context.artifacts / f"{rule}-transitions.svg")
            import matplotlib.pyplot as plt

            plt.close(fig)
    examples: dict[str, Any] = {}
    for word, original_notation in EXAMPLES.items():
        tree = None if word == "0" else binary_to_tree(word)
        examples[word] = {
            "original_notation": original_notation,
            "candidate_notation": binary_to_notation(word),
            "metrics": metrics(word),
            "tree": None if tree is None else tree.to_dict(),
        }
        if context.parameters["visualize"]:
            from research_lab.visualization import plot_tree, save_figure, tree_figure

            save_figure(tree_figure(tree), context.artifacts / f"tree-{word}.html")
            fig = plot_tree(tree)
            save_figure(fig, context.artifacts / f"tree-{word}.svg")
            save_figure(fig, context.artifacts / f"tree-{word}.png")
            import matplotlib.pyplot as plt

            plt.close(fig)
    standard = [
        {
            "generation": n,
            "dyck_pairs": n,
            "dyck_count": len(dyck_words(n)),
            "ordered_tree_nodes": n + 1,
            "ordered_tree_count": len(ordered_trees(n + 1)),
            "catalan": math.comb(2 * n, n) // (n + 1),
        }
        for n in range(generation + 1)
    ]
    return {
        "evidence_type": "COMPUTATIONAL RESULT",
        "interpretation": "Finite comparisons of explicit candidate rules; the original examples do not specify a unique rule or establish a physical theory.",
        "examples": examples,
        "models": models,
        "standard_comparison": standard,
        "ambiguities": [
            "The seed has one zero; 0 -> 10 preserves its zero count, while 10 -> 1100 adds one zero.",
            "Only example correspondences are given; a complete encoding and transformation grammar must be chosen explicitly.",
            "Different rules can agree at early stages and diverge later; finite agreement does not prove equivalence.",
        ],
    }


def _validate_structural(outputs: dict[str, Any]) -> dict[str, bool]:
    checks = {
        "example_notation_preserved": all(
            e["original_notation"] == e["candidate_notation"] for e in outputs["examples"].values()
        ),
        "standard_counts_match_catalan": all(
            row["dyck_count"] == row["ordered_tree_count"] == row["catalan"]
            for row in outputs["standard_comparison"]
        ),
        "all_models_start_with_seed": all(
            model["stages"][0] == ["0"] for model in outputs["models"].values()
        ),
    }
    candidate = outputs["models"].get("zero_split")
    if candidate and len(candidate["stages"]) > 3:
        checks["candidate_reaches_both_third_examples"] = all(
            candidate["examples_reached"].values()
        )
    return checks


def _entropy_sampling(context: ExperimentContext) -> dict[str, Any]:
    samples = _integer(context.parameters, "samples", 1, 1_000_000)
    probability = context.parameters["probability"]
    if (
        isinstance(probability, bool)
        or not isinstance(probability, (int, float))
        or not math.isfinite(probability)
        or not 0 <= probability <= 1
    ):
        raise ValueError("probability must be finite and between zero and one")
    ones = sum(context.rng.random() < probability for _ in range(samples))

    def entropy(p: float) -> float:
        return -sum(q * math.log2(q) for q in (p, 1 - p) if q > 0)

    return {
        "ones": ones,
        "zeros": samples - ones,
        "empirical_probability": ones / samples,
        "empirical_entropy_bits": entropy(ones / samples),
        "theoretical_entropy_bits": entropy(probability),
        "evidence_type": "COMPUTATIONAL RESULT",
    }


def _oscillator(context: ExperimentContext) -> dict[str, Any]:
    from research_lab.physics.classical import harmonic_oscillator, oscillator_energy
    from research_lab.simulations import integrate_rk4

    steps = _integer(context.parameters, "steps", 10, 10000)
    values = {}
    for key in ("duration", "position", "velocity", "omega", "mass"):
        value = context.parameters[key]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"{key} must be a finite number")
        values[key] = float(value)
    if any(values[key] <= 0 for key in ("duration", "omega", "mass")):
        raise ValueError("duration, omega, and mass must be positive")
    dt = values["duration"] / steps
    if dt * values["omega"] > 0.1:
        raise ValueError("increase steps so dt * omega <= 0.1 for this nonstiff experiment")
    samples = integrate_rk4(
        lambda t, y: (y[1], -(values["omega"] ** 2) * y[0]),
        (values["position"], values["velocity"]),
        dt,
        steps,
    )
    rows = []
    errors = []
    for t, (x, v) in samples:
        exact_x, exact_v = harmonic_oscillator(
            t, values["position"], values["velocity"], values["omega"]
        )
        rows.append(
            {
                "t": t,
                "position": x,
                "velocity": v,
                "exact_position": exact_x,
                "energy": oscillator_energy(x, v, values["mass"], values["omega"]),
            }
        )
        errors.append(max(abs(x - exact_x), abs(v - exact_v) / values["omega"]))
    initial_energy = rows[0]["energy"]
    return {
        "evidence_type": "COMPUTATIONAL RESULT",
        "model": "Established ideal undamped oscillator in SI units; RK4 compared to its analytic solution.",
        "samples": rows,
        "max_absolute_state_error": max(errors),
        "energy_tolerance_joules": 1e-5 * max(initial_energy, 1e-300),
        "max_absolute_energy_drift": max(abs(row["energy"] - initial_energy) for row in rows),
        "error_tolerance": 1e-4
        * max(1.0, abs(values["position"]), abs(values["velocity"]) / values["omega"]),
    }


def specifications() -> tuple[ExperimentSpec, ...]:
    return (
        ExperimentSpec(
            name="harmonic-oscillator",
            description="RK4 oscillator simulation checked against exact motion and energy conservation.",
            hypothesis="For a sufficiently small fixed step, RK4 approximates the analytic oscillator within the stated tolerance.",
            parameters={
                "duration": 10.0,
                "steps": 1000,
                "position": 1.0,
                "velocity": 0.0,
                "omega": 1.0,
                "mass": 1.0,
            },
            execute=_oscillator,
            validate=lambda out: {
                "analytic_solution_agreement": out["max_absolute_state_error"]
                <= out["error_tolerance"],
                "energy_conservation_within_tolerance": out["max_absolute_energy_drift"]
                <= out["energy_tolerance_joules"],
            },
        ),
        ExperimentSpec(
            name="structural-growth",
            description="Compare the original structural examples under explicitly labeled candidate rules.",
            hypothesis="The zero-split interpretation generates the supplied examples; other interpretations may diverge.",
            parameters={
                "max_generation": 5,
                "rules": ["zero_split", "zero_occupancy", "dyck_insertion"],
                "max_states": 10000,
                "visualize": False,
            },
            execute=_structural,
            validate=_validate_structural,
        ),
        ExperimentSpec(
            name="entropy-sampling",
            description="Seeded Bernoulli sampling and binary entropy estimates.",
            hypothesis="The plug-in entropy estimate approaches binary entropy as sample size grows; finite samples fluctuate.",
            parameters={"samples": 1000, "probability": 0.5},
            execute=_entropy_sampling,
            validate=lambda out: {
                "counts_nonnegative": out["ones"] >= 0 and out["zeros"] >= 0,
                "entropy_within_binary_bound": 0 <= out["empirical_entropy_bits"] <= 1,
            },
        ),
    )
