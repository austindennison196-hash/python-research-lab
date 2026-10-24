"""Shared numerical input checks for introductory physical models."""

from math import isfinite


def finite(value: float, name: str) -> float:
    """Return a finite real value or raise a contextual error."""
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def positive(value: float, name: str) -> float:
    """Require a finite strictly positive scalar."""
    if finite(value, name) <= 0:
        raise ValueError(f"{name} must be positive")
    return value
