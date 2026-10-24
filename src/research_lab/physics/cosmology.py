"""Limited established cosmology calculations, separate from structural hypotheses."""

from ._validation import finite, positive

SPEED_OF_LIGHT_KM_S = 299792.458


def hubble_distance(redshift: float, hubble_constant: float = 70.0) -> float:
    """Low-redshift approximation d=cz/H0 in Mpc, H0 in km/s/Mpc.

    Only 0<=z<=0.1 is accepted; even within this range this is an approximation
    which neglects cosmological acceleration and peculiar velocities.
    """
    if not 0 <= finite(redshift, "redshift") <= 0.1:
        raise ValueError("low-redshift approximation requires 0 <= z <= 0.1")
    return SPEED_OF_LIGHT_KM_S * redshift / positive(hubble_constant, "hubble_constant")


def luminosity_distance_mpc(
    redshift: float, hubble_constant: float = 70.0, omega_m: float = 0.3
) -> float:
    """Optional Astropy flat ΛCDM luminosity distance (Mpc), with Tcmb0=0.

    Parameters define a cosmological model; they are not inferred measurements.
    Radiation is omitted with this simple model's default background temperature.
    """
    if finite(redshift, "redshift") < 0:
        raise ValueError("redshift must be nonnegative")
    positive(hubble_constant, "hubble_constant")
    if not 0 <= finite(omega_m, "omega_m") <= 1:
        raise ValueError("omega_m must be in [0,1]")
    try:
        from astropy.cosmology import FlatLambdaCDM
    except ImportError as exc:
        raise ImportError("Astropy is optional; install python-research-lab[physics]") from exc
    model = FlatLambdaCDM(H0=hubble_constant, Om0=omega_m)
    return float(model.luminosity_distance(redshift).value)
