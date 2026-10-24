"""Explicit candidate interpretations of the user's structural notation.

``zero_split`` is a candidate formalization, not a deduction from the informal
hypothesis.  Standard Dyck enumeration remains a separate operation.
"""

from .engine import (
    EXAMPLES,
    RULES,
    Exploration,
    ResourceLimitError,
    Rule,
    Transition,
    Tree,
    binary_to_notation,
    binary_to_tree,
    catalan,
    compare_systems,
    discover_invariants,
    dyck_words,
    explore,
    generate_stages,
    is_dyck,
    metrics,
    notation_to_binary,
    ordered_trees,
    pattern_counts,
    successors,
    tree_to_binary,
    tree_to_notation,
)

__all__ = [
    "EXAMPLES",
    "RULES",
    "Exploration",
    "ResourceLimitError",
    "Rule",
    "Transition",
    "Tree",
    "binary_to_notation",
    "binary_to_tree",
    "catalan",
    "compare_systems",
    "discover_invariants",
    "dyck_words",
    "explore",
    "generate_stages",
    "is_dyck",
    "metrics",
    "notation_to_binary",
    "ordered_trees",
    "pattern_counts",
    "successors",
    "tree_to_binary",
    "tree_to_notation",
]
