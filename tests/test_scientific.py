"""Known identities, numerical reference cases, and rejected invalid scientific inputs."""

import math

import pytest

from research_lab.information_theory import (
    empirical_entropy,
    kl_divergence,
    lz_complexity,
    mutual_information,
    shannon_entropy,
)
from research_lab.mathematics import (
    binomial_distribution,
    catalan,
    descriptive_statistics,
    finite_set_operations,
    high_precision_pi,
    normal_density,
    numerical_integral,
    optimize_scalar,
    primes_up_to,
    solve_linear_system,
    solve_ode,
    symbolic_report,
    truth_table,
)


def test_exact_combinatorics_and_sets():
    assert [catalan(i) for i in range(6)] == [1, 1, 2, 5, 14, 42]
    assert primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    result = finite_set_operations({1, 2}, {2, 3})
    assert result["union"] == {1, 2, 3}
    assert result["intersection"] == {2}
    assert result["symmetric_difference"] == {1, 3}
    assert primes_up_to(0) == []
    for invalid in (-1, 1.5, True):
        with pytest.raises(ValueError):
            catalan(invalid)
        with pytest.raises(ValueError):
            primes_up_to(invalid)


def test_probability_and_sample_statistics():
    assert binomial_distribution(2, 0.5) == pytest.approx([0.25, 0.5, 0.25])
    assert binomial_distribution(0, 0.2) == [1]
    assert binomial_distribution(3, 0) == [1, 0, 0, 0]
    assert binomial_distribution(3, 1) == [0, 0, 0, 1]
    assert sum(binomial_distribution(2000, 0.5)) == pytest.approx(1, abs=1e-10)
    summary = descriptive_statistics([1, 2, 3])
    assert summary["mean"] == 2
    assert summary["sample_variance"] == 1
    assert summary["population_variance"] == pytest.approx(2 / 3)
    assert descriptive_statistics([1])["sample_variance"] is None
    assert normal_density(0) == pytest.approx(1 / math.sqrt(2 * math.pi))
    for bad in ([], [math.nan], [math.inf]):
        with pytest.raises(ValueError):
            descriptive_statistics(bad)
    with pytest.raises(ValueError):
        binomial_distribution(3, 2)
    with pytest.raises(ValueError):
        normal_density(0, sigma=0)


def test_information_identities_and_order_limit():
    assert shannon_entropy([0.5, 0.5]) == 1
    assert shannon_entropy([1, 0]) == 0
    assert shannon_entropy([0.5, 0.5], math.e) == pytest.approx(math.log(2))
    assert empirical_entropy("0011") == empirical_entropy("0101") == 1
    assert mutual_information([[0.25, 0.25], [0.25, 0.25]]) == pytest.approx(0)
    assert mutual_information([[0.5, 0], [0, 0.5]]) == 1
    assert mutual_information([[1, 0], [0, 0]]) == 0
    assert kl_divergence([0.5, 0.5], [0.5, 0.5]) == 0
    assert kl_divergence([1, 0], [0.5, 0.5]) == 1
    assert math.isinf(kl_divergence([1, 0], [0, 1]))
    assert lz_complexity("") == 0
    assert lz_complexity("000000") == 3  # 0 | 00 | 000
    assert lz_complexity("010101") == 4  # 0 | 1 | 01 | 01


@pytest.mark.parametrize("bad", [[], [-1, 2], [0.1, 0.1], [math.nan], [math.inf]])
def test_information_rejects_invalid_distributions(bad):
    with pytest.raises(ValueError):
        shannon_entropy(bad)


def test_information_rejects_bad_shapes_and_bases():
    with pytest.raises(ValueError):
        empirical_entropy("")
    with pytest.raises(ValueError):
        mutual_information([[0.5], [0.25, 0.25]])
    with pytest.raises(ValueError):
        kl_divergence([1], [0.5, 0.5])
    with pytest.raises(ValueError):
        shannon_entropy([1], base=1)


def test_symbolic_calculus_and_logic():
    sp = pytest.importorskip("sympy")
    report = symbolic_report("x**2 - 1")
    x = sp.Symbol("x")
    assert report["derivative"] == 2 * x
    assert sp.expand(report["factored"]) == x**2 - 1
    assert sp.diff(report["integral"], x) == x**2 - 1
    table = truth_table("A & ~B")
    assert len(table) == 4
    assert [row for row in table if row["result"]] == [{"A": True, "B": False, "result": True}]
    assert truth_table(True) == [{"result": True}]
    assert truth_table("False") == [{"result": False}]
    assert truth_table("A") == [{"A": False, "result": False}, {"A": True, "result": True}]
    with pytest.raises(ValueError):
        truth_table("A + 1")


def test_numerical_reference_problems():
    np = pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    value, error = numerical_integral(lambda x: x * x, 0, 1)
    assert value == pytest.approx(1 / 3)
    assert error < 1e-10
    assert solve_linear_system([[2, 0], [0, 4]], [4, 8]) == [2, 2]
    optimum = optimize_scalar(lambda x: (x - 2) ** 2, (-1, 4))
    assert optimum["x"] == pytest.approx(2)
    assert optimum["fun"] < 1e-10
    solution = solve_ode(lambda t, y: -y, (0, 1), [1], points=11)
    assert len(solution["t"]) == 11
    assert solution["y"][0][-1] == pytest.approx(math.exp(-1), rel=1e-6)
    with pytest.raises(np.linalg.LinAlgError):
        solve_linear_system([[1, 1], [1, 1]], [1, 1])
    with pytest.raises(ValueError):
        solve_linear_system([[1, 2]], [1])
    with pytest.raises(ValueError):
        solve_ode(lambda t, y: -y, (1, 0), [1])
    with pytest.raises(ValueError):
        optimize_scalar(lambda x: x, (1, 1))


def test_high_precision_pi_preserves_context():
    mp = pytest.importorskip("mpmath")
    before = mp.mp.dps
    assert high_precision_pi(40).startswith("3.141592653589793238462643383279502884197")
    assert mp.mp.dps == before
