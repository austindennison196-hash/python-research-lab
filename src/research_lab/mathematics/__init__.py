"""Small, reusable mathematical investigations with lazily imported scientific extras.

Symbolic expression strings are trusted research input, not a sandbox for untrusted code.
"""

from .discrete import catalan, finite_set_operations, primes_up_to, truth_table
from .numerical import (
    high_precision_pi,
    numerical_integral,
    optimize_scalar,
    solve_linear_system,
    solve_ode,
    symbolic_report,
)
from .statistics import binomial_distribution, descriptive_statistics, normal_density

__all__ = [
    "binomial_distribution",
    "catalan",
    "descriptive_statistics",
    "finite_set_operations",
    "high_precision_pi",
    "normal_density",
    "numerical_integral",
    "optimize_scalar",
    "primes_up_to",
    "solve_linear_system",
    "solve_ode",
    "symbolic_report",
    "truth_table",
]
