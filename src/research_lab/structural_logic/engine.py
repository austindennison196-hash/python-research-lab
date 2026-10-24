"""Bounded enumeration, validation, and measurement of binary structures.

Definitions and the proof for zero splitting are documented in
``docs/structural_formalism.md``. Symbols retain their literal user spelling.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any

EXAMPLES: dict[str, str] = {
    "0": "x",
    "10": "(x)",
    "1100": "((x)x)",
    "111000": "(((x)x)x)",
    "110100": "((x)(x)x)",
}


class ResourceLimitError(ValueError):
    """An enumeration exceeds the caller's explicit computational budget."""


def _integer(value: int, name: str, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def catalan(n: int) -> int:
    """The established Catalan number C_n = binomial(2n,n)/(n+1)."""
    _integer(n, "n")
    return math.comb(2 * n, n) // (n + 1)


def is_dyck(word: str, *, primitive: bool = False) -> bool:
    """Check nonnegative prefix balance and zero final balance, with 1 opening.

    A primitive word is nonempty and returns to balance zero only at its end.
    The user's exceptional initial symbol ``0`` is not a Dyck word.
    """
    balance = 0
    for index, symbol in enumerate(word):
        if symbol not in "01":
            return False
        balance += 1 if symbol == "1" else -1
        if balance < 0 or (primitive and balance == 0 and index != len(word) - 1):
            return False
    return balance == 0 and (not primitive or bool(word))


@dataclass(frozen=True)
class Tree:
    """A nonempty, unlabeled rooted ordered tree; child order is significant."""

    children: tuple[Tree, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple) or any(
            not isinstance(child, Tree) for child in self.children
        ):
            raise TypeError("children must be a tuple of Tree instances")

    @property
    def size(self) -> int:
        return 1 + sum(child.size for child in self.children)

    @property
    def height(self) -> int:
        """Root-to-leaf edge height (a singleton tree has height zero)."""
        return max((child.height + 1 for child in self.children), default=0)

    def to_dict(self) -> dict[str, Any]:
        return {"children": [child.to_dict() for child in self.children]}

    def edges(self) -> tuple[tuple[int, int], ...]:
        """Preorder-indexed parent-child edges; singleton has no edges."""
        edges: list[tuple[int, int]] = []
        next_id = 0

        def visit(node: Tree) -> int:
            nonlocal next_id
            current = next_id
            next_id += 1
            for child in node.children:
                child_id = visit(child)
                edges.append((current, child_id))
            return current

        visit(self)
        return tuple(edges)


def tree_to_binary(tree: Tree) -> str:
    """Enter a node with 1 and exit it with 0 (a primitive Dyck word)."""
    return "1" + "".join(tree_to_binary(child) for child in tree.children) + "0"


def binary_to_tree(word: str) -> Tree:
    """Decode a nonempty primitive Dyck word; ``0`` is an exceptional seed."""
    if not is_dyck(word, primitive=True):
        raise ValueError("a tree requires a nonempty primitive Dyck word")
    stack: list[list[Tree]] = []
    result: Tree | None = None
    for symbol in word:
        if symbol == "1":
            stack.append([])
        else:
            node = Tree(tuple(stack.pop()))
            if stack:
                stack[-1].append(node)
            else:
                result = node
    assert result is not None
    return result


def tree_to_notation(tree: Tree) -> str:
    """A node is '(' followed by its children, followed by 'x)'."""
    return "(" + "".join(tree_to_notation(child) for child in tree.children) + "x)"


def binary_to_notation(word: str) -> str:
    """Extend the user's five correspondences by a labeled candidate grammar."""
    return "x" if word == "0" else tree_to_notation(binary_to_tree(word))


def notation_to_binary(text: str) -> str:
    """Parse grammar ``seed := x`` and ``node := '(' node* 'x)'`` strictly."""
    if text == "x":
        return "0"
    position = 0

    def parse() -> Tree:
        nonlocal position
        if position >= len(text) or text[position] != "(":
            raise ValueError("expected opening parenthesis")
        position += 1
        children = []
        while position < len(text) and text[position] == "(":
            children.append(parse())
        if text[position : position + 2] != "x)":
            raise ValueError("each node must end in 'x)'")
        position += 2
        return Tree(tuple(children))

    result = parse()
    if position != len(text):
        raise ValueError("trailing characters in structural notation")
    return tree_to_binary(result)


def dyck_words(n: int, *, max_states: int = 10000) -> tuple[str, ...]:
    """Enumerate standard Dyck words with n pairs in deterministic order."""
    _integer(n, "n")
    _integer(max_states, "max_states", 1)
    if catalan(n) > max_states:
        raise ResourceLimitError("Catalan count exceeds max_states")
    result: list[str] = []

    def visit(prefix: str, opened: int, closed: int) -> None:
        if closed == n:
            result.append(prefix)
            return
        if opened < n:
            visit(prefix + "1", opened + 1, closed)
        if closed < opened:
            visit(prefix + "0", opened, closed + 1)

    visit("", 0, 0)
    return tuple(result)


def ordered_trees(n: int, *, max_states: int = 10000) -> tuple[Tree, ...]:
    """Enumerate rooted ordered trees with n NODES, counted by C_(n-1).

    Wrapping a Dyck word of n-1 pairs by 1 ... 0 supplies the explicit root.
    """
    _integer(n, "n", 1)
    return tuple(
        binary_to_tree("1" + word + "0") for word in dyck_words(n - 1, max_states=max_states)
    )


Rewrite = Callable[[str], Iterable[tuple[str, int | None]]]


@dataclass(frozen=True)
class Rule:
    """An experimental rewrite function returning (child, edited_position)."""

    name: str
    description: str
    rewrite: Rewrite
    seed: str = "0"

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise ValueError("a rule requires a nonempty name")
        if not callable(self.rewrite):
            raise TypeError("rewrite must be callable")
        if (
            not isinstance(self.seed, str)
            or not self.seed
            or any(symbol not in "01" for symbol in self.seed)
        ):
            raise ValueError("a rule seed must be a nonempty binary string")


def _zero_split(word: str) -> Iterator[tuple[str, int]]:
    if word == "0":
        yield "10", 0
    else:
        if not is_dyck(word, primitive=True):
            raise ValueError("zero_split requires the seed or a primitive Dyck word")
        for i, symbol in enumerate(word):
            if symbol == "0":
                yield word[:i] + "100" + word[i + 1 :], i


def _zero_occupancy(word: str) -> Iterator[tuple[str, int]]:
    for i, symbol in enumerate(word):
        if symbol == "0":
            yield word[:i] + "10" + word[i + 1 :], i


def _dyck_insertion(word: str) -> Iterator[tuple[str, int]]:
    if word == "0":
        yield "10", 0
    else:
        if not is_dyck(word):
            raise ValueError("dyck_insertion requires the seed or a Dyck word")
        for i in range(len(word) + 1):
            yield word[:i] + "10" + word[i:], i


RULES: dict[str, Rule] = {
    "zero_split": Rule(
        "zero_split", "Special seed 0→10; then replace one existing 0 by 100.", _zero_split
    ),
    "zero_occupancy": Rule(
        "zero_occupancy", "Replace one existing 0 by 10, including the seed.", _zero_occupancy
    ),
    "dyck_insertion": Rule(
        "dyck_insertion", "Special seed 0→10; then insert 10 at any word boundary.", _dyck_insertion
    ),
}


def _resolve(rule: str | Rule) -> Rule:
    if isinstance(rule, Rule):
        return rule
    try:
        return RULES[rule]
    except KeyError as exc:
        raise ValueError(f"unknown rule {rule!r}; choose {tuple(RULES)} or supply Rule") from exc


def successors(
    word: str,
    rule: str | Rule = "zero_split",
    *,
    max_states: int = 10000,
    max_transitions: int = 100000,
) -> tuple[str, ...]:
    """Validated, bounded one-step children for a built-in or custom rule.

    The transition cap counts duplicate edits too, so even a custom generator
    yielding the same child forever cannot evade the enumeration budget.
    """
    if not isinstance(word, str) or not word or any(symbol not in "01" for symbol in word):
        raise ValueError("states must be nonempty binary strings")
    _integer(max_states, "max_states", 1)
    _integer(max_transitions, "max_transitions", 1)
    children: set[str] = set()
    for index, (child, _) in enumerate(_resolve(rule).rewrite(word), 1):
        if index > max_transitions:
            raise ResourceLimitError("transition budget exceeded")
        if not isinstance(child, str) or not child or any(symbol not in "01" for symbol in child):
            raise ValueError("a rule produced an invalid binary state")
        children.add(child)
        if len(children) > max_states:
            raise ResourceLimitError("state budget exceeded")
    return tuple(sorted(children))


@dataclass(frozen=True)
class Transition:
    generation: int
    parent: str
    child: str
    position: int | None = None


@dataclass(frozen=True)
class Exploration:
    stages: tuple[tuple[str, ...], ...]
    transitions: tuple[Transition, ...]
    rule: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "stages": [list(stage) for stage in self.stages],
            "transitions": [
                {
                    "generation": t.generation,
                    "parent": t.parent,
                    "child": t.child,
                    "position": t.position,
                }
                for t in self.transitions
            ],
        }


def explore(
    max_generation: int,
    rule: str | Rule = "zero_split",
    *,
    max_states: int = 10000,
    max_transitions: int = 100000,
) -> Exploration:
    """Breadth-first generation with all edit histories retained and hard caps.

    max_states limits total retained states, rather than only the final layer.
    Generation 0 is the seed; deduplication is within each generation.
    """
    _integer(max_generation, "max_generation")
    _integer(max_states, "max_states", 1)
    _integer(max_transitions, "max_transitions", 1)
    if max_generation > 100:
        raise ResourceLimitError("max_generation must not exceed 100")
    resolved = _resolve(rule)
    stages: list[tuple[str, ...]] = [(resolved.seed,)]
    transitions: list[Transition] = []
    state_count = 1
    for generation in range(1, max_generation + 1):
        next_states: set[str] = set()
        for word in stages[-1]:
            for child, position in resolved.rewrite(word):
                if (
                    not isinstance(child, str)
                    or not child
                    or any(symbol not in "01" for symbol in child)
                ):
                    raise ValueError("a rule produced an invalid binary state")
                next_states.add(child)
                transitions.append(Transition(generation, word, child, position))
                if len(transitions) > max_transitions:
                    raise ResourceLimitError("transition budget exceeded")
                if state_count + len(next_states) > max_states:
                    raise ResourceLimitError("state budget exceeded")
        stages.append(tuple(sorted(next_states)))
        state_count += len(next_states)
    return Exploration(tuple(stages), tuple(transitions), resolved.name)


def generate_stages(
    max_generation: int,
    rule: str | Rule = "zero_split",
    *,
    max_states: int = 10000,
) -> tuple[tuple[str, ...], ...]:
    """Return the complete layers from seed through max_generation inclusive."""
    return explore(max_generation, rule, max_states=max_states).stages


def pattern_counts(word: str, width: int = 2) -> dict[str, int]:
    """Overlapping contiguous k-mer counts; no significance is implied."""
    _integer(width, "width", 1)
    return dict(sorted(Counter(word[i : i + width] for i in range(len(word) - width + 1)).items()))


def metrics(word: str) -> dict[str, Any]:
    """Finite descriptive measurements; entropy is marginal symbol entropy.

    Symbol entropy ignores order and is 1 bit for EVERY nonempty balanced
    binary word. It must not be mistaken for algorithmic complexity.
    """
    if not word or any(symbol not in "01" for symbol in word):
        raise ValueError("states must be nonempty binary strings")
    ones, zeros = word.count("1"), word.count("0")
    balances = [0]
    for symbol in word:
        balances.append(balances[-1] + (1 if symbol == "1" else -1))
    entropy = -sum(p * math.log2(p) for count in (ones, zeros) if (p := count / len(word)))
    tree = binary_to_tree(word) if is_dyck(word, primitive=True) else None
    return {
        "length": len(word),
        "ones": ones,
        "zeros": zeros,
        "balance": ones - zeros,
        "min_prefix_balance": min(balances),
        "max_prefix_balance": max(balances),
        "is_dyck": is_dyck(word),
        "is_primitive": is_dyck(word, primitive=True),
        "symbol_entropy_bits": entropy,
        "distinct_bigrams": len(pattern_counts(word)),
        "tree_nodes": tree.size if tree else None,
        "tree_height": tree.height if tree else None,
        "leaf_count": word.count("10") if tree else None,
    }


def discover_invariants(words: Iterable[str]) -> dict[str, Any]:
    """Report empirically constant measurements, never certify a theorem."""
    rows = [metrics(word) for word in words]
    if not rows:
        raise ValueError("at least one state is required")
    constants = {
        key: value for key, value in rows[0].items() if all(row[key] == value for row in rows)
    }
    return {
        "status": "COMPUTATIONAL RESULT",
        "sample_size": len(rows),
        "constant_metrics": constants,
    }


def compare_systems(generation: int, *, max_states: int = 10000) -> dict[str, Any]:
    """Compare sets at a finite generation without claiming general equivalence."""
    _integer(generation, "generation")
    proposed = set(generate_stages(generation, max_states=max_states)[-1])
    standard = set(dyck_words(generation, max_states=max_states))
    tree_words = (
        {tree_to_binary(tree) for tree in ordered_trees(generation, max_states=max_states)}
        if generation
        else set()
    )
    return {
        "generation": generation,
        "status": "COMPUTATIONAL RESULT",
        "zero_split_count": len(proposed),
        "dyck_count": len(standard),
        "ordered_tree_count": len(tree_words),
        "zero_split_equals_ordered_trees": proposed == tree_words,
        "zero_split_subset_of_dyck": proposed <= standard,
        "dyck_only": sorted(standard - proposed),
    }
