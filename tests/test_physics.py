"""Analytic identities and model-domain checks for introductory physics."""

import importlib.util
from math import exp, isclose, pi

import pytest

from research_lab.emergence import constrained_walk
from research_lab.physics.classical import harmonic_oscillator, oscillator_energy
from research_lab.physics.complex_systems import game_of_life
from research_lab.physics.cosmology import hubble_distance, luminosity_distance_mpc
from research_lab.physics.dynamics import logistic_map, lorenz_trajectory
from research_lab.physics.electromagnetism import COULOMB_CONSTANT, coulomb_force
from research_lab.physics.quantum import qutip_rabi, two_level_probabilities
from research_lab.physics.statistical import BOLTZMANN_CONSTANT, boltzmann_probabilities
from research_lab.physics.thermodynamics import carnot_efficiency, ideal_gas_pressure
from research_lab.simulations import integrate_rk4


def test_oscillator_analytic_solution_conserves_energy():
    initial = oscillator_energy(0.3, 0.7, mass=2, omega=1.7)
    for t in (0, 0.1, 1, 10):
        x, v = harmonic_oscillator(t, 0.3, 0.7, 1.7)
        assert oscillator_energy(x, v, 2, 1.7) == pytest.approx(initial)
    assert harmonic_oscillator(pi / 2) == pytest.approx((0, -1))
    with pytest.raises(ValueError):
        harmonic_oscillator(0, omega=0)


def test_rk4_accuracy_and_convergence():
    def derivative(t, y):
        return (-y[0],)

    coarse = integrate_rk4(derivative, (1,), 0.2, 5)[-1][1][0]
    fine = integrate_rk4(derivative, (1,), 0.1, 10)[-1][1][0]
    assert abs(fine - exp(-1)) < abs(coarse - exp(-1)) / 10
    assert fine == pytest.approx(exp(-1), abs=4e-7)
    with pytest.raises(ValueError):
        integrate_rk4(lambda t, y: (), (1,), 0.1, 1)


def test_dynamical_systems_fixed_points():
    assert logistic_map(0.75, rate=4, steps=3) == [0.75] * 4
    trajectory = lorenz_trajectory((0, 0, 0), steps=4)
    assert all(state == (0, 0, 0) for _, state in trajectory)
    with pytest.raises(ValueError):
        logistic_map(0.1, rate=5)


def test_thermal_models_and_boltzmann_shift_invariance():
    assert ideal_gas_pressure(1, 273.15, 0.022414) == pytest.approx(101325, rel=1e-4)
    assert carnot_efficiency(600, 300) == 0.5
    energies = [0, BOLTZMANN_CONSTANT * 300]
    probabilities = boltzmann_probabilities(energies, 300)
    assert sum(probabilities) == pytest.approx(1)
    assert probabilities[1] / probabilities[0] == pytest.approx(exp(-1))
    assert boltzmann_probabilities([e + 1e-20 for e in energies], 300) == pytest.approx(
        probabilities
    )
    with pytest.raises(ValueError):
        ideal_gas_pressure(1, -1, 1)
    with pytest.raises(ValueError):
        boltzmann_probabilities([], 300)


def test_electrostatics_inverse_square_and_sign():
    assert coulomb_force(1, 1, (2, 0, 0))[0] == pytest.approx(COULOMB_CONSTANT / 4)
    assert coulomb_force(-1, 1, (2, 0, 0))[0] < 0
    with pytest.raises(ValueError):
        coulomb_force(1, 1, (0, 0, 0))


def test_quantum_normalization_and_full_transition():
    assert two_level_probabilities(pi) == pytest.approx((0, 1))
    assert isclose(sum(two_level_probabilities(0.3)), 1)


def test_cosmology_domain_and_linear_scaling():
    assert hubble_distance(0.02) == 2 * hubble_distance(0.01)
    with pytest.raises(ValueError):
        hubble_distance(1)


def test_life_blinker_and_constrained_walk_reproducibility():
    blinker = [[0, 0, 0], [1, 1, 1], [0, 0, 0]]
    assert game_of_life(game_of_life(blinker)) == blinker
    path = constrained_walk(100, seed=7, bound=2)
    assert path == constrained_walk(100, seed=7, bound=2)
    assert max(abs(x) for x in path) <= 2
    assert constrained_walk(4, bound=0) == [0] * 5


@pytest.mark.skipif(
    importlib.util.find_spec("qutip") is None, reason="optional QuTiP not installed"
)
def test_optional_qutip_agrees_with_analytic_result():
    times = [0, 0.5, 1, 1.5]
    assert qutip_rabi(times) == pytest.approx(
        [two_level_probabilities(t)[1] for t in times], abs=1e-5
    )


@pytest.mark.skipif(
    importlib.util.find_spec("astropy") is None, reason="optional Astropy not installed"
)
def test_optional_astropy_distance_low_redshift_limit():
    assert luminosity_distance_mpc(1e-5) == pytest.approx(hubble_distance(1e-5), rel=2e-5)
