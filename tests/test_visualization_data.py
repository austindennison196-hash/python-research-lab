"""Functional data/plot checks including exported artifact contents."""

import json
import subprocess
import sys
from types import SimpleNamespace

import pytest

from research_lab.data_analysis import (
    compare_metrics,
    load_records,
    save_records,
    summarize,
    summarize_records,
)


def test_summary_uses_sample_variance_and_handles_singletons():
    result = summarize([1, 2, 3])
    assert result == {
        "n": 3,
        "mean": 2,
        "median": 2,
        "stdev": 1,
        "min": 1,
        "max": 3,
        "total": 6,
    }
    assert summarize([4])["stdev"] is None


@pytest.mark.parametrize("values", [[], [float("nan")], [float("inf")], [True], ["4"]])
def test_summary_rejects_invalid_observations(values):
    with pytest.raises(ValueError):
        summarize(values)


def test_records_and_comparisons(tmp_path):
    rows = [{"run": "a", "count": 1}, {"run": "b", "count": 3}]
    assert summarize_records(rows)["count"]["mean"] == 2
    with pytest.raises(KeyError):
        summarize_records(rows, fields=["absent"])
    comparison = compare_metrics({"count": 1, "zero": 0}, {"count": 3, "zero": 1})
    assert comparison["count"]["relative_change"] == 2
    assert comparison["zero"]["relative_change"] is None
    assert compare_metrics({"negative": -2}, {"negative": -1})["negative"]["relative_change"] == 0.5
    with pytest.raises(ValueError, match="same names"):
        compare_metrics({"left": 1}, {"right": 2})
    target = save_records(rows, tmp_path / "records.json")
    assert load_records(target) == rows
    csv_target = save_records(rows, tmp_path / "records.csv")
    assert load_records(csv_target)[1] == {"run": "b", "count": "3"}
    malformed = tmp_path / "malformed.json"
    malformed.write_text(json.dumps({"not": "records"}))
    with pytest.raises(ValueError):
        load_records(malformed)


def test_imports_do_not_eagerly_load_large_plotting_dependencies():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import research_lab.visualization; import research_lab.data_analysis; "
            "assert not {'matplotlib', 'plotly', 'pandas', 'numpy'} & sys.modules.keys()",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_static_function_distribution_and_comparison_exports(tmp_path):
    pytest.importorskip("matplotlib")
    from research_lab.visualization import (
        plot_comparison,
        plot_distribution,
        plot_function,
        save_figure,
    )

    figure = plot_function(lambda x: x * x, -1, 1, points=5)
    assert list(figure.axes[0].lines[0].get_ydata()) == [1, 0.25, 0, 0.25, 1]
    png = save_figure(figure, tmp_path / "function.png")
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    svg = save_figure(figure, tmp_path / "function.svg")
    assert "Mathematical function" in svg.read_text()
    hist = plot_distribution([0, 0, 1, 1], bins=2)
    assert [patch.get_height() for patch in hist.axes[0].patches] == [2, 2]
    comp = plot_comparison([{"generation": 0, "count": 1}, {"generation": 1, "count": 2}])
    assert list(comp.axes[0].lines[0].get_ydata()) == [1, 2]
    with pytest.raises(ValueError):
        plot_function(lambda x: x, 1, 0)
    with pytest.raises(ValueError):
        plot_distribution([])
    with pytest.raises(ValueError):
        save_figure(figure, tmp_path / "invalid.html")


def test_interactive_history_includes_only_supplied_edges_and_is_self_contained(tmp_path):
    pytest.importorskip("plotly")
    from research_lab.visualization import save_figure, transition_figure, tree_figure

    stages = [("0",), ("10",), ("1100",), ("111000", "110100")]
    transitions = [
        SimpleNamespace(generation=1, parent="0", child="10"),
        SimpleNamespace(generation=2, parent="10", child="1100"),
        SimpleNamespace(generation=3, parent="1100", child="111000"),
        SimpleNamespace(generation=3, parent="1100", child="110100"),
    ]
    figure = transition_figure(stages, transitions)
    assert list(figure.data[1].text) == ["0", "10", "1100", "111000", "110100"]
    assert len(figure.layout.annotations) == 4
    target = save_figure(figure, tmp_path / "history.html")
    html = target.read_text()
    assert "plotly.js" in html and "111000" in html
    assert '<script src="https://cdn.plot.ly/' not in html
    tree = tree_figure(((), ()))
    assert len(tree.data[1].x) == 3
    assert len(tree.layout.annotations) == 2
    with pytest.raises(ValueError, match="endpoint"):
        transition_figure(stages, [(1, "0", "nonexistent")])


def test_tree_and_graph_validation():
    pytest.importorskip("matplotlib")
    from research_lab.visualization import plot_graph, plot_tree

    figure = plot_tree(((), ()))
    assert len(figure.axes[0].texts) == 5  # two edge arrows + three labels
    with pytest.raises(ValueError, match="level"):
        plot_graph([("a", "b")], levels={"a": 0})
    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(ValueError, match="cyclic"):
        plot_tree(cyclic)
