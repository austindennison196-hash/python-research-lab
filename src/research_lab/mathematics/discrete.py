"""Exact combinatorics, elementary number theory, finite sets and propositional logic."""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable
from typing import Any


def catalan(n: int) -> int:
    """Count Dyck words of semilength n; this does not assert a new model's equivalence."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return math.comb(2 * n, n) // (n + 1)


def primes_up_to(n: int) -> list[int]:
    """Sieve of Eratosthenes, including n if it is prime; O(n) memory."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            sieve[p * p :: p] = b"\x00" * (((n - p * p) // p) + 1)
    return [i for i, prime in enumerate(sieve) if prime]


def finite_set_operations(a: Iterable[Hashable], b: Iterable[Hashable]) -> dict[str, set[Hashable]]:
    """Compute union, intersection, differences and symmetric difference of finite sets."""
    left, right = set(a), set(b)
    return {
        "union": left | right,
        "intersection": left & right,
        "left_difference": left - right,
        "right_difference": right - left,
        "symmetric_difference": left ^ right,
    }


def truth_table(expression: Any) -> list[dict[str, bool]]:
    """Evaluate a SymPy Boolean expression over every valuation.

    Strings are passed to sympify and must be trusted. Use e.g. ``'A & ~B'``.
    Enumeration is limited to 16 variables to avoid accidental exponential allocation.
    """
    from itertools import product

    from sympy import false, sympify, true
    from sympy.core.relational import Relational
    from sympy.logic.boolalg import Boolean

    expr = sympify(expression)
    if isinstance(expr, bool):
        expr = true if expr else false
    if not isinstance(expr, Boolean) or expr.has(Relational):
        raise ValueError("expression must be propositional Boolean logic")
    variables = sorted(expr.free_symbols, key=str)
    if len(variables) > 16:
        raise ValueError("truth tables are limited to 16 variables")
    rows = []
    for values in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, values, strict=True))
        result = expr.subs(assignment)
        if result not in (True, False):
            raise ValueError("expression must evaluate to a Boolean under every valuation")
        row = {str(symbol): value for symbol, value in assignment.items()}
        if "result" in row:
            raise ValueError("'result' is reserved for the output column")
        row["result"] = bool(result)
        rows.append(row)
    return rows
