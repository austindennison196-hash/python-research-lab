"""Experimental constraint models; no physical interpretation is assumed."""

from random import Random


def constrained_walk(steps: int, *, seed: int = 0, bound: int | None = None) -> list[int]:
    """Seeded ±1 walk; reject proposals outside [-bound,bound] when constrained.

    This operationalizes one possible meaning of stabilization (a permitted
    transition constraint). It does not derive physics from the author's rules.
    A rejected move remains at its current position, rather than reflecting.
    """
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    if bound is not None and (isinstance(bound, bool) or not isinstance(bound, int) or bound < 0):
        raise ValueError("bound must be a nonnegative integer or None")
    random = Random(seed)
    path = [0]
    for _ in range(steps):
        proposal = path[-1] + random.choice((-1, 1))
        path.append(proposal if bound is None or abs(proposal) <= bound else path[-1])
    return path
