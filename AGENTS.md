# Research laboratory conventions

Read `README.md` and the relevant research documentation before editing a module. Use the existing checkout: cloud tasks are already isolated; do not create Git worktrees unless the user requests one. Cloud Python and a Chromebook's Linux Python are separate installations. Never require local JupyterLab for Codex development.

## Scientific rigor

Preserve the user's original binary sequences, parentheses notation, and stated conceptual relationships. Keep alternative interpretations explicitly named. Early agreement does not prove equivalence. Separate **DEFINITION**, **THEOREM** (with proof), **COMPUTATIONAL RESULT** (with reproducible evidence), **CONJECTURE**, **HYPOTHESIS**, and **SPECULATION**. Never label a finite experiment as a proof or infer physical cosmology from a structural analogy. State assumptions, units, validity domains, and limitations.

## Architecture and dependencies

Use `src/research_lab/` packages with small independent modules. Keep core structural logic and experiment orchestration usable with the standard library. Import optional scientific libraries inside the functions that need them; give an actionable extras-install error when unavailable. Preserve `requirements.txt` as the existing full cloud dependency snapshot. Manage new lightweight installations and optional dependency groups through `pyproject.toml`. Do not add large packages to the default dependency list.

Use an isolated `.venv`. In cloud shells with a read-only home directory, set `XDG_CACHE_HOME=/workspace/.cache` and `PRE_COMMIT_HOME=/workspace/.cache/pre-commit` before running developer tools. For lightweight development, `python -m pip install -e '.[dev]'`; add `scientific`, `physics`, or `notebooks` extras only for the work being performed. Never print credentials, check in `.env`, bypass TLS checks, or overwrite existing research data.

## Adding research

Give each model explicit mathematical definitions and testable assumptions. Add reusable code to the appropriate package, meaningful tests under `tests/`, documentation under `docs/`, and a small reproducible notebook when explanatory visualization helps. Register experiments using the existing experiment framework instead of bespoke result-writing scripts. Record parameters, hypotheses, seeds, timestamps, validation, data, and outputs. Bound combinatorial state spaces and large numerical simulations; avoid an accidental exponential enumeration on a 4 GB machine.

## Validation

Run `ruff check src tests`, `ruff format --check src tests`, `mypy`, and `pytest`. Run relevant optional-library tests with the corresponding extras installed. Execute edited notebooks with `nbclient`; retain failures, skips, and unrun checks distinctly in reports. Test mathematical invariants, error cases, known reference solutions, and persisted experiment behavior rather than just reproducing implementation details. CI runs lightweight core checks and a separate scientific/notebook workflow.

Generated data belongs in ignored `data/raw/`, `data/processed/`, `results/`, or `figures/generated/`. Curated research findings and their reproduction commands belong in documentation. Never fabricate experiment results. A suspected repository bug should be diagnosed and fixed with evidence; an unsupported scientific interpretation should remain a labeled research question.
