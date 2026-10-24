"""Exact undamped harmonic oscillator with displacement in m and time in s."""

from math import cos, sin

from ._validation import finite, positive


def harmonic_oscillator(
    t: float, position: float = 1.0, velocity: float = 0.0, omega: float = 1.0
) -> tuple[float, float]:
    """Return (position, velocity) for x'' = -omega² x; omega in rad/s."""
    finite(t, "t")
    finite(position, "position")
    finite(velocity, "velocity")
    positive(omega, "omega")
    return (
        position * cos(omega * t) + velocity * sin(omega * t) / omega,
        -position * omega * sin(omega * t) + velocity * cos(omega * t),
    )


def oscillator_energy(
    position: float, velocity: float, mass: float = 1.0, omega: float = 1.0
) -> float:
    """Kinetic plus potential energy in J, with spring constant k = mass*omega²."""
    finite(position, "position")
    finite(velocity, "velocity")
    positive(mass, "mass")
    positive(omega, "omega")
    return mass * (velocity * velocity + omega * omega * position * position) / 2
