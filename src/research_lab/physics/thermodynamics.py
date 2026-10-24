"""Equilibrium ideal-gas laws in SI units; no phase transitions or interactions."""

from ._validation import positive

GAS_CONSTANT = 8.31446261815324  # J mol^-1 K^-1


def ideal_gas_pressure(moles: float, temperature: float, volume: float) -> float:
    """Pressure in Pa from positive amount (mol), temperature (K), volume (m³)."""
    return (
        positive(moles, "moles")
        * GAS_CONSTANT
        * positive(temperature, "temperature")
        / positive(volume, "volume")
    )


def carnot_efficiency(hot_temperature: float, cold_temperature: float) -> float:
    """Maximum reversible engine efficiency; absolute temperatures must satisfy 0<Tc<Th."""
    positive(hot_temperature, "hot_temperature")
    positive(cold_temperature, "cold_temperature")
    if cold_temperature >= hot_temperature:
        raise ValueError("cold temperature must be below hot temperature")
    return 1 - cold_temperature / hot_temperature
