# Experimental methods

A run records a unique identifier, explicit parameters and hypothesis, random seed, timestamps, numerical outputs, validation outcomes, and artifact locations. Results are stored below a caller-selected output directory (normally ignored `results/`); they are not scientific findings until the recorded checks and assumptions are examined.

## Reproducibility

Use a fixed seed for stochastic experiments, and retain the parameters and software version metadata beside the results. A seed does not make UUIDs, timestamps, or environment metadata identical, and exact floating-point equality across hardware and library versions is not guaranteed. Compare scientific outputs with stated numerical tolerances. Keep raw measurements separate from derived summaries and never overwrite an earlier run to conceal a failure.

Before interpreting a result:

1. Inspect the hypothesis and model assumptions.
2. Check that intended generations, samples, or integration intervals actually ran.
3. Inspect every automated validation and numerical tolerance.
4. Compare against a known mathematical or physical baseline.
5. Report finite ranges and any truncation bounds.
6. Distinguish an observed pattern from a general proof.

## Structural experiment counting conventions

Generation 0 is the exceptional seed `0`. Generation n after it counts n distinctions in the balanced candidate mode. State counts deduplicate identical words; transition records retain local choices. The count of complete generation histories is different from both. Standard Dyck enumeration uses n pairs; tree enumeration uses n nodes. A size shift must be written explicitly in every comparison.

Uniformly sampling an available rewrite does not generally induce a uniform distribution on distinct terminal states. An entropy computed from the latter must not be described as the entropy of the former. The initial deterministic enumerations make no probability claim.

## Numerical and physical examples

Introductory modules implement named idealizations, such as an ideal gas or harmonic oscillator. Their checks establish consistency with those equations over tested parameters, not universal fidelity to real materials or arbitrary regimes. Record SI assumptions and analytic reference solutions where available. Set seeds explicitly for stochastic models and use appropriate units before passing bare floats.

## Notebooks

The thirteen notebooks use library modules instead of duplicating scientific algorithms. Each has a finite, inexpensive example, assertions, a visualization, interpretation, and limitations. Execute them from an editable installation with the scientific and notebook extras. Quantum demonstrations use the optional physics dependencies when needed. Generated notebook outputs can be cleared before committing; saved run data belongs under ignored `results/`.
