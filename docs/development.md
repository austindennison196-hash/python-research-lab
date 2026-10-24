# Extending the laboratory

Use Python 3.12 or newer in a virtual environment. Cloud and Chromebook installations are independent. The default package is deliberately lightweight; optional modules import large libraries only when their functions are called. Keep this property when adding research areas.

## Add a module

1. Select an existing domain package under `src/research_lab/`, or add a clearly named domain with a small public API.
2. State mathematical definitions, input domains, units, and failure modes in docstrings.
3. Keep heavy optional imports inside the functions that need them, and raise an actionable missing-dependency error.
4. Add tests that can expose a wrong scientific result: known analytic solutions, boundary cases, invariants, invalid inputs, or counterexamples. Avoid tests that merely repeat implementation steps.
5. Add an example using the reusable API and explain its limitations.
6. Run pytest, ruff, and mypy before preparing a change for review.

## Add an experiment

Register a callable through the experiment framework. Separate model computation from orchestration and visualization. Keep parameters JSON-serializable, validate resource bounds, use the run's seed, and return numerical outputs together with named automated checks. Write figures into the run's artifact directory and retain the hypothesis and methodological limitations.

A scientific failure is useful evidence: report a failed validation rather than disabling it. Do not relabel unproven conjectures as results just because a bounded search found no counterexample.

## Add a notebook

Follow the existing notebooks: explanation and assumptions, reusable imports, reproducible code, at least one interpretable visualization, a check, and limitations. Keep notebooks inexpensive enough for cloud smoke execution. Large sweeps should be scripts or registered experiments with explicit resource bounds, rather than hidden work in a notebook cell.

## Dependency policy

`requirements.txt` preserves the original full pinned cloud scientific environment. It is not the lightweight installation path. Project extras in `pyproject.toml` describe domain-specific installations; select only those needed. Never replace a dependency pin, bypass artifact verification, or silently install large optional stacks to resolve an unrelated error.

No application server is required for CLI research or automated notebook execution, and developing through Codex does not require JupyterLab on the Chromebook. The user has requested a browser interface with no local installation. Keep that interface static and independent of the full Python stack; generate structural data from the shared engine. See browser_app.md for build, validation, and hosting contracts.
