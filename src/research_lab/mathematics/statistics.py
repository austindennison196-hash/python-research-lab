"""Finite-sample summaries and elementary probability with explicit domains."""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable


def descriptive_statistics(values: Iterable[float]) -> dict[str, float | int | None]:
    """Summarize finite observations; sample variance is undefined for one observation."""
    data = [float(value) for value in values]
    if not data or not all(math.isfinite(value) for value in data):
        raise ValueError("provide at least one finite observation")
    return {
        "count": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "minimum": min(data),
        "maximum": max(data),
        "population_variance": statistics.pvariance(data),
        "sample_variance": statistics.variance(data) if len(data) > 1 else None,
    }


def binomial_distribution(n: int, p: float) -> list[float]:
    """Return P(X=k), k=0..n for n independent Bernoulli trials."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("p must lie in [0, 1]")
    if p == 0:
        return [1.0] + [0.0] * n
    if p == 1:
        return [0.0] * n + [1.0]
    # log-gamma avoids overflow converting large exact binomial coefficients to float.
    return [
        math.exp(
            math.lgamma(n + 1)
            - math.lgamma(k + 1)
            - math.lgamma(n - k + 1)
            + k * math.log(p)
            + (n - k) * math.log1p(-p)
        )
        for k in range(n + 1)
    ]


def normal_density(x: float, mean: float = 0, sigma: float = 1) -> float:
    """Normal density (not a probability at a point), with sigma > 0."""
    if not all(math.isfinite(v) for v in (x, mean, sigma)) or sigma <= 0:
        raise ValueError("x and mean must be finite, and sigma must be finite and positive")
    z = (x - mean) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2 * math.pi))
