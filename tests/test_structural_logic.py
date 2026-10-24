"""Independent combinatorial oracles and counterexamples for candidate rules."""

from itertools import product

import pytest

from research_lab.structural_logic import (
    EXAMPLES,
    ResourceLimitError,
    Rule,
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
)


def test_original_notation_roundtrip():
    for binary, notation in EXAMPLES.items():
        assert binary_to_notation(binary) == notation
        assert notation_to_binary(notation) == binary


def test_original_stages_and_histories():
    result = explore(3)
    assert result.stages == (("0",), ("10",), ("1100",), ("110100", "111000"))
    assert {(edge.parent, edge.child, edge.position) for edge in result.transitions} == {
        ("0", "10", 0),
        ("10", "1100", 1),
        ("1100", "111000", 2),
        ("1100", "110100", 3),
    }
    assert result.to_dict()["stages"][3] == ["110100", "111000"]


def test_standard_dyck_generator_against_exhaustive_binary_oracle():
    for n in range(5):
        oracle = set()
        for bits in product("01", repeat=2 * n):
            word = "".join(bits)
            # Independent prefix criterion using counts of literal characters.
            if word.count("1") == n and all(
                word[:k].count("1") >= word[:k].count("0") for k in range(2 * n + 1)
            ):
                oracle.add(word)
        assert set(dyck_words(n)) == oracle
        assert len(oracle) == catalan(n)


def test_candidate_invariants_and_tree_bijection_through_generation_seven():
    for n, stage in enumerate(generate_stages(7)):
        if not n:
            assert stage == ("0",)
            continue
        assert len(stage) == catalan(n - 1)
        assert set(stage) == {tree_to_binary(tree) for tree in ordered_trees(n)}
        assert all(is_dyck(word, primitive=True) for word in stage)
        for word in stage:
            assert len(word) == 2 * n
            assert metrics(word)["tree_nodes"] == n
            assert notation_to_binary(binary_to_notation(word)) == word
            for child in successors(word):
                assert child.count("1") == n + 1
                assert child.count("0") == n + 1


def test_full_dyck_mode_is_separate_and_exhaustive():
    assert set(generate_stages(2, "dyck_insertion")[-1]) == {"1100", "1010"}
    for n, stage in enumerate(generate_stages(6, "dyck_insertion")):
        if n:
            assert set(stage) == set(dyck_words(n))
    comparison = compare_systems(3)
    assert comparison["zero_split_count"] == 2
    assert comparison["dyck_count"] == 5
    assert comparison["zero_split_equals_ordered_trees"] is True
    assert comparison["zero_split_subset_of_dyck"] is True


def test_literal_occupancy_interpretation_does_not_match_examples():
    assert generate_stages(3, "zero_occupancy") == (("0",), ("10",), ("110",), ("1110",))
    assert "1100" not in successors("10", "zero_occupancy")
    with pytest.raises(ValueError):
        binary_to_notation("110")


def test_custom_rule_and_limits():
    custom = Rule(
        "leftmost",
        "Only differentiate the first space",
        lambda word: [(word.replace("0", "10" if word == "0" else "100", 1), word.index("0"))],
    )
    assert generate_stages(3, custom)[-1] == ("111000",)
    with pytest.raises(ResourceLimitError):
        explore(10, max_states=3)
    with pytest.raises(ResourceLimitError):
        explore(3, max_transitions=2)
    with pytest.raises(ResourceLimitError):
        dyck_words(12, max_states=10)
    with pytest.raises(ResourceLimitError):
        explore(101)
    bad = Rule("bad", "nonbinary child", lambda word: [("abc", 0)])
    with pytest.raises(ValueError):
        explore(1, bad)


@pytest.mark.parametrize("word", ["0", "1010", "110", "abc", ""])
def test_tree_parser_rejects_nonprimitive_binary(word):
    with pytest.raises(ValueError):
        binary_to_tree(word)


@pytest.mark.parametrize("text", ["()", "(xx)", "(x)(x)", "((x))", "x)", "", "(x)x"])
def test_notation_parser_rejects_malformed_input(text):
    with pytest.raises(ValueError):
        notation_to_binary(text)


@pytest.mark.parametrize("value", [-1, 1.5, True])
def test_generation_arguments_are_checked(value):
    with pytest.raises(ValueError):
        generate_stages(value)
    with pytest.raises(ValueError):
        catalan(value)


def test_tree_graph_and_metrics_distinguish_same_symbol_entropy():
    chain, fork = binary_to_tree("111000"), binary_to_tree("110100")
    assert chain.height == 2
    assert fork.height == 1
    assert chain.size == fork.size == 3
    assert len(chain.edges()) == 2
    assert metrics("111000")["symbol_entropy_bits"] == metrics("110100")["symbol_entropy_bits"] == 1
    assert metrics("111000")["leaf_count"] == 1
    assert metrics("110100")["leaf_count"] == 2
    assert pattern_counts("111000") == {"00": 2, "10": 1, "11": 2}
    report = discover_invariants(["111000", "110100"])
    assert report["status"] == "COMPUTATIONAL RESULT"
    assert report["constant_metrics"]["balance"] == 0
    assert "tree_height" not in report["constant_metrics"]
    with pytest.raises(ValueError):
        discover_invariants([])


def test_successors_validate_custom_outputs_and_bound_duplicate_histories():
    from itertools import repeat

    malformed = Rule("malformed", "invalid child", lambda word: [("not-binary", 0)])
    with pytest.raises(ValueError, match="invalid binary state"):
        successors("0", malformed)
    endless = Rule("endless", "infinite repeated edit", lambda word: repeat(("10", 0)))
    with pytest.raises(ResourceLimitError, match="transition budget"):
        successors("0", endless, max_transitions=5)
    with pytest.raises(ResourceLimitError, match="state budget"):
        successors("1100", max_states=1)
    with pytest.raises(ValueError, match="max_states"):
        successors("0", max_states=0)
