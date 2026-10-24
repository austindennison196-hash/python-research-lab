"""Dimensionless maps and a Lorenz system; numerical evidence is not a proof of chaos."""

from research_lab.simulations import integrate_rk4

from ._validation import finite, positive


def logistic_map(initial: float, rate: float = 3.8, steps: int = 100) -> list[float]:
    """Iterate x[n+1] = rate*x[n]*(1-x[n]) on [0,1], including initial state."""
    if not 0 <= finite(initial, "initial") <= 1 or not 0 <= finite(rate, "rate") <= 4:
        raise ValueError("initial must be in [0,1] and rate in [0,4]")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    values = [initial]
    for _ in range(steps):
        values.append(rate * values[-1] * (1 - values[-1]))
    return values


def lorenz_trajectory(
    initial: tuple[float, float, float] = (1.0, 1.0, 1.0),
    *,
    dt: float = 0.01,
    steps: int = 1000,
    sigma: float = 10.0,
    rho: float = 28.0,
    beta: float = 8 / 3,
) -> list[tuple[float, tuple[float, ...]]]:
    """Integrate the dimensionless Lorenz equations with explicit RK4.

    Short trajectories illustrate sensitivity; long trajectories need numerical
    convergence studies and cannot establish exact orbit prediction.
    """
    if len(initial) != 3:
        raise ValueError("Lorenz initial state needs three coordinates")
    positive(sigma, "sigma")
    positive(rho, "rho")
    positive(beta, "beta")

    def derivative(t: float, state: tuple[float, ...]) -> tuple[float, float, float]:
        x, y, z = state
        return sigma * (y - x), x * (rho - z) - y, x * y - beta * z

    return integrate_rk4(derivative, initial, dt, steps)
