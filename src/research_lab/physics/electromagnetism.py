"""Vacuum electrostatic point-charge model, invalid at coincident charges."""

from collections.abc import Sequence
from math import sqrt

from ._validation import finite

COULOMB_CONSTANT = 8.9875517923e9  # N m² C^-2, approximate CODATA value


def coulomb_force(
    charge: float, source_charge: float, displacement: Sequence[float]
) -> tuple[float, float, float]:
    """Force on charge (C), displacement (m) pointing from source to target."""
    finite(charge, "charge")
    finite(source_charge, "source_charge")
    if len(displacement) != 3:
        raise ValueError("displacement must have three coordinates")
    coords = tuple(finite(float(value), "displacement") for value in displacement)
    radius = sqrt(sum(value * value for value in coords))
    if radius == 0:
        raise ValueError("point-charge force is singular at zero separation")
    factor = COULOMB_CONSTANT * charge * source_charge / radius**3
    return factor * coords[0], factor * coords[1], factor * coords[2]
