"""Lazy experiment registration, reproducible execution, and auditable JSON results."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import logging
import platform
import random
import subprocess
import time
import uuid
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research_lab import __version__

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExperimentContext:
    parameters: dict[str, Any]
    seed: int
    artifacts: Path
    rng: random.Random


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    description: str
    hypothesis: str
    execute: Callable[[ExperimentContext], dict[str, Any]]
    validate: Callable[[dict[str, Any]], dict[str, bool]]
    parameters: Mapping[str, Any] = field(default_factory=dict)


class ExperimentRegistry:
    """Explicit registration allows plugins without importing unrelated experiments."""

    def __init__(self) -> None:
        self._specs: dict[str, ExperimentSpec] = {}

    def register(self, specification: ExperimentSpec) -> None:
        if not specification.name or any(
            c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in specification.name
        ):
            raise ValueError("experiment names must use lowercase letters, numbers, '-' or '_'")
        if specification.name in self._specs:
            raise ValueError(f"duplicate experiment: {specification.name}")
        self._specs[specification.name] = specification

    def get(self, name: str) -> ExperimentSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise ValueError(
                f"unknown experiment {name!r}; available: {', '.join(self._specs)}"
            ) from exc

    def list(self) -> tuple[ExperimentSpec, ...]:
        return tuple(self._specs[name] for name in sorted(self._specs))


@dataclass(frozen=True)
class ExperimentRun:
    record: dict[str, Any]
    directory: Path
    path: Path

    @property
    def passed(self) -> bool:
        return self.record["status"] == "passed"


class ExperimentExecutionError(RuntimeError):
    """Execution failed; the result path points to the persisted failure record."""

    def __init__(self, message: str, path: Path) -> None:
        super().__init__(f"{message}; failure record: {path}")
        self.path = path


def default_registry() -> ExperimentRegistry:
    # Builtin callbacks themselves import their dependencies only when executed.
    from .builtin import specifications

    registry = ExperimentRegistry()
    for specification in specifications():
        registry.register(specification)
    return registry


def list_experiments() -> tuple[ExperimentSpec, ...]:
    return default_registry().list()


def _provenance() -> dict[str, Any]:
    source = Path(__file__).resolve().parents[3]
    provenance: dict[str, Any] = {
        "package_version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    versions = {}
    for package in (
        "numpy",
        "scipy",
        "sympy",
        "mpmath",
        "networkx",
        "pandas",
        "matplotlib",
        "plotly",
        "astropy",
        "qutip",
        "pint",
        "nbclient",
        "ipykernel",
    ):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            continue
    provenance["installed_optional_versions"] = versions
    digest = hashlib.sha256()
    package_root = Path(__file__).resolve().parents[1]
    for path in sorted(package_root.rglob("*.py")):
        digest.update(str(path.relative_to(package_root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    provenance["source_sha256"] = digest.hexdigest()
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=source,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=source,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        provenance.update(git_commit=head.stdout.strip(), git_dirty=bool(dirty.stdout))
    except (OSError, subprocess.SubprocessError):
        provenance["git_commit"] = None
    return provenance


def run_experiment(
    name: str,
    parameters: Mapping[str, Any] | None = None,
    *,
    seed: int = 0,
    output_dir: str | Path = "results",
    registry: ExperimentRegistry | None = None,
) -> ExperimentRun:
    """Run once, validate outputs, and atomically persist a unique result record.

    Identical seeds and parameters reproduce numerical outputs, not identifiers,
    timings, or timestamps. Failed execution is also recorded, then raised.
    Validation failure is a returned run with status ``failed``.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    spec = (registry if registry is not None else default_registry()).get(name)
    supplied = dict(parameters or {})
    unknown = supplied.keys() - spec.parameters.keys()
    if unknown:
        raise ValueError(f"unknown parameters: {', '.join(sorted(unknown))}")
    resolved = deepcopy({**spec.parameters, **supplied})
    # Reject non-JSON metadata before creating output directories.
    json.dumps(resolved, allow_nan=False)
    identifier = f"{name}-{uuid.uuid4().hex}"
    directory = Path(output_dir).resolve() / identifier
    artifacts = directory / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=False)
    result_path = directory / "result.json"
    record: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": identifier,
        "name": name,
        "hypothesis": spec.hypothesis,
        "parameters": resolved,
        "seed": seed,
        "started_at": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
    }
    started = time.perf_counter()
    error: Exception | None = None
    logger.info("Starting experiment %s (%s)", name, identifier)
    try:
        outputs = spec.execute(
            ExperimentContext(deepcopy(resolved), seed, artifacts, random.Random(seed))
        )
        json.dumps(outputs, allow_nan=False)
        record["outputs"] = outputs
        validation = spec.validate(outputs)
        if not validation or any(type(value) is not bool for value in validation.values()):
            raise ValueError("validators must return a nonempty mapping of names to bools")
        record["validation"] = validation
        record["status"] = "passed" if all(validation.values()) else "failed"
    except Exception as exc:
        error = exc
        record.update(status="error", error={"type": type(exc).__name__, "message": str(exc)})
        logger.warning("Experiment %s failed: %s", name, exc)
    record["finished_at"] = datetime.now(UTC).isoformat()
    record["duration_seconds"] = time.perf_counter() - started
    record["artifacts"] = sorted(
        str(p.relative_to(directory)) for p in artifacts.rglob("*") if p.is_file()
    )
    temporary = result_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(result_path)
    if error is not None:
        raise ExperimentExecutionError(str(error), result_path) from error
    return ExperimentRun(record, directory, result_path)


def load_result(path: str | Path) -> dict[str, Any]:
    result = json.loads(Path(path).read_text())
    if not isinstance(result, dict) or result.get("schema_version") != 1:
        raise ValueError("unsupported experiment result schema")
    for key in ("name", "parameters", "seed", "status"):
        if key not in result:
            raise ValueError(f"missing result field {key!r}")
    return result


def compare_results(left: str | Path, right: str | Path) -> dict[str, Any]:
    """Compare outputs explicitly; equal outputs do not imply a theorem."""
    a, b = load_result(left), load_result(right)
    return {
        "same_experiment": a["name"] == b["name"],
        "same_parameters": a["parameters"] == b["parameters"],
        "same_seed": a["seed"] == b["seed"],
        "same_outputs": a.get("outputs") == b.get("outputs"),
        "statuses": [a["status"], b["status"]],
    }
