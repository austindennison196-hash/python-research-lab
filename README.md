# Python Research Laboratory

**[Open the Research Laboratory app](https://austindennison196-hash.github.io/python-research-lab/)** — runs in your browser; no installation needed.

A modular laboratory for formal structural models, reproducible experiments, mathematics, introductory physics, and scientific visualization. Its first research program preserves the originator's binary and parentheses examples and compares explicitly labeled transformation rules without assuming that they are equivalent or physically established.

```text
0  →  10  →  1100  →  111000  or  110100
x  →  (x) →  ((x)x) →  (((x)x)x) or ((x)(x)x)
```

The core package has no mandatory third-party dependencies. Large scientific libraries, notebook tools, and specialized physics packages are optional and loaded when used.

## Browser interface

The interactive browser app includes structural state exploration, generation playback, tree inspection, rule comparisons, depth constraints, an animated oscillator, and a binary-entropy explorer. Visitors need no Python installation. See [browser features and hosting](docs/browser_app.md). The app is published on GitHub Pages at the link above.

## Start in Codex or another cloud machine

Use the existing checkout and an isolated Python **3.12+** environment. The already prepared Codex environment has `.venv`; activate it before running commands. Cloud and Chromebook Python installations are independent.

```bash
cd /workspace/python-research-lab
source .venv/bin/activate
python -m pip install -e '.[dev]'
research-lab list
research-lab run structural-growth --params '{"max_generation":5}' --seed 0 --output results
python -m pytest
ruff check .
mypy
```

For static and interactive visualizations, add the optional scientific tools, then enable figure generation:

```bash
python -m pip install -e '.[scientific]'
research-lab run structural-growth --params '{"max_generation":5,"visualize":true}' --seed 0 --output results
```

The prepared cloud instance already has these optional libraries. The experiment prints its saved result location. Each run has a unique directory containing `result.json`, parameters, hypothesis, seed, timestamps, validation results, provenance, and optional figures. PNG/SVG figures and interactive HTML show generation transitions and individual trees. Results live in ignored `results/`; copy a selected research summary into documentation when appropriate.

```bash
research-lab run entropy-sampling --params '{"samples":2000,"probability":0.5}' --seed 2026
research-lab run harmonic-oscillator --params '{"duration":10,"steps":1000}'
research-lab compare results/FIRST_RUN/result.json results/SECOND_RUN/result.json
```

Replace `FIRST_RUN` and `SECOND_RUN` with actual run directory names. Comparison reports whether parameters, seeds, and outputs match; it does not decide scientific significance.

## Lightweight installation

On a Chromebook or another small machine, install only the core unless a specific activity needs more:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
research-lab run structural-growth --params '{"max_generation":5}'
```

No local JupyterLab server is required for Codex development or CLI experiments. Avoid the aggregate optional stacks on a 4 GB machine unless needed. Available extras are:

| Extra | Purpose |
| --- | --- |
| `scientific` | NumPy, SciPy, SymPy, mpmath, NetworkX, pandas, Matplotlib, Plotly |
| `quantum` | Focused QuTiP demonstrations |
| `cosmology` | Focused Astropy calculations |
| `physics` | Aggregate Astropy, QuTiP, Pint, ASE, RDKit tools |
| `notebooks` | JupyterLab, IPython, nbclient, nbformat, ipykernel |
| `dev` | pytest, ruff, mypy, pre-commit, Rich, tqdm, python-dotenv |

Install an extra with, for example, `python -m pip install -e '.[scientific]'`. `requirements.txt` preserves the original full pinned cloud environment; it is **not** the lightweight default. Python 3.12 is the tested cloud interpreter. ARM/Linux package availability depends on optional libraries and their wheels.

## First structural analysis

The examples do not uniquely determine a rewrite rule. The candidate `zero_split` makes the seed step `0→10` exceptional, then replaces a selected `0` with `100`. It produces both supplied third-generation examples. Literal `0→10` replacement instead reaches `110` and fails the supplied second transition. A full Dyck-insertion mode includes additional states such as `1010`.

For the explicit `zero_split` definition, a proof identifies positive generation n with primitive Dyck words having n pairs, equivalently rooted ordered trees having n nodes. The count is **C(n−1)**, while unrestricted Dyck words at n pairs have count **C(n)**. This conditional mathematical relationship does not establish that this is the uniquely intended interpretation, nor validate any physical hypothesis.

Read [the formal model and proof](docs/structural_formalism.md), [established mathematical connections](docs/established_connections.md), [definitions](docs/definitions.md), [candidate rules](docs/transformation_rules.md), [recorded results](docs/results.md), and [open questions](docs/research_agenda.md). Documentation labels definitions, theorems, computational results, conjectures, hypotheses, and speculation separately.

## Reusable modules

| Package | Implemented work |
| --- | --- |
| `structural_logic` | Candidate rewrites, bounded exploration, histories, exact notation, trees, independent Dyck/tree enumeration, metrics, comparisons, sampled invariant checks |
| `mathematics` | Symbolic transforms, calculus, linear systems, quadrature, ODEs, optimization, number theory, sets, logic, probability, statistics |
| `physics` | Ideal oscillator, logistic/Lorenz dynamics, ideal gas, Boltzmann weights, Coulomb force, two-level quantum dynamics, optional cosmology, cellular automata |
| `information_theory` | Shannon and empirical entropy, mutual information, KL divergence, LZ78 phrase count |
| `emergence` / `simulations` | Explicitly constrained toy processes and reusable simulation support |
| `experiments` | Lazy registry, seeded execution, saved metadata/results, validation, comparison |
| `visualization` | Trees, networks, transition histories, functions, distributions, comparisons; PNG/SVG/HTML export |
| `data_analysis` | Numerical summaries, record summaries, metric comparisons, optional pandas conversion |

Import only the modules you need. Established physics examples remain separate from speculative interpretations of structural emergence. Scientific functions document inputs, assumptions, and units.

## Research notebooks

The [notebooks directory](notebooks) contains thirteen worked studies, in order:

1. Laboratory introduction
2. Structural definitions
3. Binary generation
4. Parentheses transformations
5. Dyck words and Catalan numbers
6. Recursive trees
7. Structural complexity and constrained emergence
8. Symbolic mathematics
9. Numerical mathematics
10. Classical physics
11. Quantum mechanics
12. Information theory
13. Reproducible hypothesis testing

Each includes explanatory mathematics, reusable library code, reproducible computations, assertions, visualizations, interpretation, and limitations. Install `.[scientific,notebooks]`; add `quantum` for the optional QuTiP cross-check. Source notebooks keep outputs cleared to make code review manageable. CI executes them independently with optional dependencies installed.

## Contribute research

See [development conventions](AGENTS.md), [the extension guide](docs/development.md), and [experimental methods](docs/methods.md). Add a model with explicit assumptions, meaningful tests, a reproducible experiment, and a bounded example. The repository is designed to accumulate tested models and research records, rather than treat computational patterns as discoveries or speculate beyond available evidence.
