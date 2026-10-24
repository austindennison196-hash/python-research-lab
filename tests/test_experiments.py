import json
import subprocess
import sys

import pytest

from research_lab.cli import main
from research_lab.experiments import (
    ExperimentExecutionError,
    ExperimentRegistry,
    ExperimentSpec,
    compare_results,
    load_result,
    run_experiment,
)


def test_seeded_runs_are_unique_and_reproducible(tmp_path):
    first = run_experiment("entropy-sampling", {"samples": 300}, seed=42, output_dir=tmp_path)
    second = run_experiment("entropy-sampling", {"samples": 300}, seed=42, output_dir=tmp_path)
    assert first.passed and second.passed
    assert first.directory != second.directory
    assert first.record["outputs"] == second.record["outputs"]
    assert first.record["outputs"]["ones"] + first.record["outputs"]["zeros"] == 300
    assert load_result(first.path) == first.record
    assert compare_results(first.path, second.path)["same_outputs"]
    assert first.record["parameters"] == {"samples": 300, "probability": 0.5}
    assert first.record["provenance"]["package_version"]
    assert first.record["started_at"] <= first.record["finished_at"]


def test_invalid_parameters_rejected_and_execution_errors_saved(tmp_path):
    with pytest.raises(ValueError, match="unknown parameters"):
        run_experiment("entropy-sampling", {"missing": 1}, output_dir=tmp_path)
    assert not list(tmp_path.iterdir())
    with pytest.raises(ExperimentExecutionError) as raised:
        run_experiment("entropy-sampling", {"samples": -1}, output_dir=tmp_path)
    saved = load_result(raised.value.path)
    assert saved["status"] == "error"
    assert saved["error"]["type"] == "ValueError"
    assert not raised.value.path.with_suffix(".json.tmp").exists()


def test_plugins_and_failed_validation_are_persisted(tmp_path):
    registry = ExperimentRegistry()
    spec = ExperimentSpec(
        "toy",
        "test fixture",
        "a failed expectation",
        lambda context: {"x": 1},
        lambda out: {"expected": out["x"] == 2},
    )
    registry.register(spec)
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(spec)
    run = run_experiment("toy", output_dir=tmp_path, registry=registry)
    assert not run.passed
    assert load_result(run.path)["validation"] == {"expected": False}


def test_empty_validator_does_not_vacuously_pass(tmp_path):
    registry = ExperimentRegistry()
    registry.register(ExperimentSpec("empty", "", "", lambda context: {}, lambda out: {}))
    with pytest.raises(ExperimentExecutionError, match="nonempty"):
        run_experiment("empty", output_dir=tmp_path, registry=registry)


def test_core_import_is_lazy():
    code = "import sys; from research_lab.experiments import list_experiments; list_experiments(); assert not any(n in sys.modules for n in ('numpy','scipy','sympy','matplotlib','qutip','astropy','plotly'))"
    subprocess.run([sys.executable, "-c", code], check=True)


def test_cli(tmp_path, capsys):
    assert main(["list"]) == 0
    assert "structural-growth" in capsys.readouterr().out
    assert main(["run", "entropy-sampling", "--output", str(tmp_path), "--seed", "12"]) == 0
    path = json.loads(capsys.readouterr().out)["result"]
    assert main(["compare", path, path]) == 0
    assert json.loads(capsys.readouterr().out)["same_outputs"]
    with pytest.raises(SystemExit) as error:
        main(["run", "entropy-sampling", "--params", "[]"])
    assert error.value.code == 2


def test_structural_experiment_first_three_generations(tmp_path):
    run = run_experiment("structural-growth", {"max_generation": 4}, output_dir=tmp_path)
    assert run.passed
    models = run.record["outputs"]["models"]
    assert models["zero_split"]["stages"][:4] == [["0"], ["10"], ["1100"], ["110100", "111000"]]
    assert models["zero_occupancy"]["stages"][2] == ["110"]
    assert models["zero_split"]["counts"] == [1, 1, 1, 2, 5]
    assert models["dyck_insertion"]["counts"] == [1, 1, 2, 5, 14]


def test_oscillator_against_exact_solution(tmp_path):
    run = run_experiment("harmonic-oscillator", seed=1, output_dir=tmp_path)
    assert run.passed
    assert run.record["outputs"]["max_absolute_energy_drift"] < 1e-8
    assert len(run.record["outputs"]["samples"]) == 1001


def test_plugin_cannot_mutate_saved_parameters_or_registry_defaults(tmp_path):
    defaults = {"items": [1]}

    def mutate(context):
        context.parameters["items"].append(2)
        return {"length": len(context.parameters["items"])}

    registry = ExperimentRegistry()
    registry.register(
        ExperimentSpec(
            "mutating", "", "", mutate, lambda out: {"two": out["length"] == 2}, defaults
        )
    )
    first = run_experiment("mutating", output_dir=tmp_path, registry=registry)
    second = run_experiment("mutating", output_dir=tmp_path, registry=registry)
    assert first.record["parameters"] == second.record["parameters"] == defaults == {"items": [1]}
    assert first.record["outputs"] == second.record["outputs"] == {"length": 2}
