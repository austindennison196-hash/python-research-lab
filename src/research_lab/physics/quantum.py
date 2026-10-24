"""A closed two-level system; no claim about quantum gravity or physical emergence."""

from math import cos, sin

from ._validation import finite


def two_level_probabilities(t: float, omega: float = 1.0) -> tuple[float, float]:
    """P(0), P(1) for H=ℏ*omega*σx/2 and initial |0>; t in s, omega rad/s."""
    finite(t, "t")
    finite(omega, "omega")
    angle = omega * t / 2
    return cos(angle) ** 2, sin(angle) ** 2


def qutip_rabi(times: list[float], omega: float = 1.0) -> list[float]:
    """Optional QuTiP calculation of P(1), using ℏ=1; times must start at zero.

    Install the quantum extra if QuTiP is unavailable. Returned populations can
    be compared against two_level_probabilities to check numerical integration.
    """
    finite(omega, "omega")
    if not times or times[0] != 0:
        raise ValueError("times must start at zero")
    if any(not a < b for a, b in zip(times, times[1:], strict=False)):
        raise ValueError("times must be strictly increasing")
    for t in times:
        finite(t, "time")
    try:
        import qutip
    except ImportError as exc:
        raise ImportError("QuTiP is optional; install python-research-lab[physics]") from exc
    result = qutip.sesolve(
        omega * qutip.sigmax() / 2,
        qutip.basis(2, 0),
        times,
        e_ops=[qutip.basis(2, 1).proj()],
    )
    return [float(value) for value in result.expect[0]]
