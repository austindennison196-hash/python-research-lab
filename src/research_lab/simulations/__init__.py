"""Reusable fixed-step numerical integration without scientific dependencies."""

from collections.abc import Callable, Sequence
from math import isfinite

Derivative = Callable[[float, tuple[float, ...]], Sequence[float]]


def integrate_rk4(
    derivative: Derivative,
    initial: Sequence[float],
    dt: float,
    steps: int,
    *,
    start: float = 0.0,
) -> list[tuple[float, tuple[float, ...]]]:
    """Classical fixed-step RK4, returning initial and all subsequent samples.

    Error is O(dt**4) globally for smooth nonstiff problems. This is not an
    adaptive solver; convergence must be checked by reducing dt. No state is
    silently clipped. The derivative must preserve the state dimension.
    """
    if not isfinite(dt) or dt <= 0 or not isfinite(start):
        raise ValueError("dt must be finite and positive, and start finite")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    state = tuple(float(x) for x in initial)
    if not state or not all(isfinite(x) for x in state):
        raise ValueError("initial state must be nonempty and finite")

    def evaluate(t: float, y: tuple[float, ...]) -> tuple[float, ...]:
        result = tuple(float(v) for v in derivative(t, y))
        if len(result) != len(state) or not all(isfinite(v) for v in result):
            raise ValueError("derivative must return finite values of the state dimension")
        return result

    samples = [(start, state)]
    for step in range(steps):
        t = start + step * dt
        k1 = evaluate(t, state)
        k2 = evaluate(t + dt / 2, tuple(y + dt * k / 2 for y, k in zip(state, k1, strict=True)))
        k3 = evaluate(t + dt / 2, tuple(y + dt * k / 2 for y, k in zip(state, k2, strict=True)))
        k4 = evaluate(t + dt, tuple(y + dt * k for y, k in zip(state, k3, strict=True)))
        state = tuple(
            y + dt * (a + 2 * b + 2 * c + d) / 6
            for y, a, b, c, d in zip(state, k1, k2, k3, k4, strict=True)
        )
        if not all(isfinite(v) for v in state):
            raise ValueError("integration produced nonfinite state; reduce step size")
        samples.append((start + (step + 1) * dt, state))
    return samples
