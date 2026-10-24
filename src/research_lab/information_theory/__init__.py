"""Discrete information measures and explicitly defined finite-string complexity proxies."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Hashable, Iterable, Sequence

__all__ = [
    "empirical_entropy",
    "kl_divergence",
    "lz_complexity",
    "mutual_information",
    "shannon_entropy",
]


def _distribution(probabilities: Iterable[float]) -> list[float]:
    values = [float(p) for p in probabilities]
    if not values or not all(math.isfinite(p) and p >= 0 for p in values):
        raise ValueError("provide a nonempty collection of finite nonnegative probabilities")
    if not math.isclose(math.fsum(values), 1.0, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("probabilities must sum to one; inputs are not silently normalized")
    return values


def _log_base(base: float) -> float:
    if not math.isfinite(base) or base <= 1:
        raise ValueError("logarithm base must be finite and greater than one")
    return math.log(base)


def shannon_entropy(probabilities: Iterable[float], base: float = 2) -> float:
    """Shannon entropy of a discrete distribution, in bits by default (0 log 0 = 0)."""
    divisor = _log_base(base)
    return -math.fsum(p * math.log(p) / divisor for p in _distribution(probabilities) if p)


def empirical_entropy(sequence: Iterable[Hashable], base: float = 2) -> float:
    """Zero-order sample entropy; symbol frequencies ignore order and dependency."""
    counts = Counter(sequence)
    n = sum(counts.values())
    if not n:
        raise ValueError("sequence must not be empty")
    return shannon_entropy([count / n for count in counts.values()], base)


def kl_divergence(p: Iterable[float], q: Iterable[float], base: float = 2) -> float:
    """D_KL(p || q); infinity if q assigns zero to an event having positive p."""
    left, right = _distribution(p), _distribution(q)
    divisor = _log_base(base)
    if len(left) != len(right):
        raise ValueError("distributions must have identical support lengths")
    if any(x > 0 and y == 0 for x, y in zip(left, right, strict=True)):
        return math.inf
    value = math.fsum(
        x * (math.log(x) - math.log(y)) / divisor for x, y in zip(left, right, strict=True) if x > 0
    )
    # Clamp only tiny negative roundoff; exact KL divergence is nonnegative.
    return max(0.0, value)


def mutual_information(joint: Sequence[Sequence[float]], base: float = 2) -> float:
    """I(X;Y) for a rectangular joint probability table, rows X and columns Y."""
    if not joint or not joint[0] or any(len(row) != len(joint[0]) for row in joint):
        raise ValueError("joint must be a nonempty rectangular table")
    table = [list(map(float, row)) for row in joint]
    _distribution(p for row in table for p in row)
    divisor = _log_base(base)
    rows = [math.fsum(row) for row in table]
    cols = [math.fsum(row[j] for row in table) for j in range(len(table[0]))]
    value = math.fsum(
        p * (math.log(p) - math.log(rows[i]) - math.log(cols[j])) / divisor
        for i, row in enumerate(table)
        for j, p in enumerate(row)
        if p > 0
    )
    return max(0.0, value)


def lz_complexity(sequence: Iterable[Hashable]) -> int:
    """Count phrases in a greedy LZ78 parsing, including an unfinished final phrase.

    Starting with an empty dictionary, extend a phrase while it is present; add the first
    unseen phrase and restart. A final repeated phrase counts once. This is a finite
    compression proxy, not Kolmogorov complexity or a proof of physical emergence.
    Empty input has complexity zero. Hashable symbols allow strings or other sequences.
    """
    dictionary: set[tuple[Hashable, ...]] = set()
    phrase: tuple[Hashable, ...] = ()
    count = 0
    for symbol in sequence:
        phrase += (symbol,)
        if phrase not in dictionary:
            dictionary.add(phrase)
            count += 1
            phrase = ()
    return count + bool(phrase)
