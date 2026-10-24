"""Numerical and symbolic tools; NumPy, SciPy, SymPy and mpmath load only on demand."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any


def symbolic_report(expression: Any, variable: str = "x") -> dict[str, Any]:
    """Simplify, factor, differentiate, and integrate a trusted symbolic expression.

    Returned objects remain SymPy expressions so callers can continue exact calculations.
    This routine is not an untrusted-expression evaluator.
    """
    import sympy as sp

    symbol = sp.Symbol(variable)
    expr = sp.sympify(expression, locals={variable: symbol})
    return {
        "expression": expr,
        "simplified": sp.simplify(expr),
        "expanded": sp.expand(expr),
        "factored": sp.factor(expr),
        "derivative": sp.diff(expr, symbol),
        "integral": sp.integrate(expr, symbol),
    }


def high_precision_pi(digits: int = 50) -> str:
    """Return pi with arbitrary precision without changing mpmath's global precision."""
    if isinstance(digits, bool) or not isinstance(digits, int) or digits < 2:
        raise ValueError("digits must be an integer >= 2")
    import mpmath as mp

    with mp.workdps(digits + 5):
        return str(mp.nstr(mp.pi, digits))


def numerical_integral(
    function: Callable[[float], float], a: float, b: float
) -> tuple[float, float]:
    """Adaptive quadrature: return estimate and QUADPACK's estimated absolute error."""
    from scipy.integrate import quad

    value, error = quad(function, a, b)
    if not math.isfinite(value) or not math.isfinite(error):
        raise ArithmeticError("quadrature did not yield a finite result")
    return float(value), float(error)


def solve_linear_system(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    """Solve a finite square linear system; singular matrices raise LinAlgError."""
    import numpy as np

    a, b = np.asarray(matrix, dtype=float), np.asarray(vector, dtype=float)
    if a.ndim != 2 or a.shape[0] == 0 or a.shape[0] != a.shape[1]:
        raise ValueError("matrix must be nonempty and square")
    if b.ndim != 1 or len(b) != len(a):
        raise ValueError("vector must have one entry per matrix row")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("matrix and vector entries must be finite")
    return [float(value) for value in np.linalg.solve(a, b)]


def optimize_scalar(
    function: Callable[[float], float], bounds: tuple[float, float]
) -> dict[str, float]:
    """Bounded scalar minimization, reliable for unimodal functions on the interval.

    This local method does not certify a global minimum for arbitrary objectives.
    """
    from scipy.optimize import minimize_scalar

    low, high = bounds
    if not all(math.isfinite(v) for v in bounds) or low >= high:
        raise ValueError("bounds must be finite and strictly increasing")
    result = minimize_scalar(function, bounds=bounds, method="bounded")
    if not result.success or not math.isfinite(result.fun):
        raise ArithmeticError(f"minimization failed: {result.message}")
    return {"x": float(result.x), "fun": float(result.fun)}


def solve_ode(
    rhs: Callable[[float, Any], Any],
    t_span: tuple[float, float],
    y0: Sequence[float],
    points: int = 100,
) -> dict[str, list[Any]]:
    """Integrate a finite initial-value problem with adaptive RK45 and report samples.

    ``y`` contains one list per state variable; solver failure raises ArithmeticError.
    """
    import numpy as np
    from scipy.integrate import solve_ivp

    if isinstance(points, bool) or not isinstance(points, int) or points < 2:
        raise ValueError("points must be an integer >= 2")
    if len(t_span) != 2 or not all(math.isfinite(v) for v in t_span):
        raise ValueError("t_span must contain two finite endpoints")
    if t_span[0] >= t_span[1]:
        raise ValueError("t_span must be increasing")
    initial = np.asarray(y0, dtype=float)
    if initial.ndim != 1 or initial.size == 0 or not np.isfinite(initial).all():
        raise ValueError("y0 must be a nonempty finite vector")
    result = solve_ivp(
        rhs,
        t_span,
        initial,
        t_eval=np.linspace(*t_span, points),
        rtol=1e-8,
        atol=1e-10,
    )
    if not result.success or not np.isfinite(result.y).all():
        raise ArithmeticError(f"integration failed: {result.message}")
    return {"t": result.t.tolist(), "y": result.y.tolist()}
