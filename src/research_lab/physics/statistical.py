"""Canonical finite-state equilibrium distribution, with energies in joules."""

from collections.abc import Sequence
from math import exp, fsum

from ._validation import finite, positive

BOLTZMANN_CONSTANT = 1.380649e-23  # J K^-1, exact SI definition


def boltzmann_probabilities(energies: Sequence[float], temperature: float) -> list[float]:
    """Normalized exp(-E/kT), treating each supplied state as nondegenerate.

    Subtracting the lowest energy avoids overflow and demonstrates invariance
    under a common energy shift. Repeat energies to represent degeneracy.
    """
    positive(temperature, "temperature")
    if not energies:
        raise ValueError("at least one state is required")
    for energy in energies:
        finite(energy, "energy")
    minimum = min(energies)
    weights = [exp(-(energy - minimum) / (BOLTZMANN_CONSTANT * temperature)) for energy in energies]
    total = fsum(weights)
    return [weight / total for weight in weights]


def expected_energy(energies: Sequence[float], temperature: float) -> float:
    """Canonical mean energy in J."""
    return fsum(
        e * p for e, p in zip(energies, boltzmann_probabilities(energies, temperature), strict=True)
    )
