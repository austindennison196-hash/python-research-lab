"""Deterministic scientific plots with lazy, optional plotting dependencies.

Interactive graphs use self-contained Plotly HTML. Static PNG/SVG exports use
Matplotlib and never require Kaleido, a browser, or a remote visualization service.
Edges must be supplied explicitly: pictures do not infer a transformation law.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


def _figure(figsize: tuple[float, float] = (8, 5)) -> Any:
    try:
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise ImportError("Install python-research-lab[scientific] for plotting") from exc
    return Figure(figsize=figsize, layout="constrained")


def _go() -> Any:
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise ImportError("Install python-research-lab[scientific] for interactive plots") from exc
    return go


def _finite(values: Iterable[float]) -> list[float]:
    output = [float(value) for value in values]
    if any(not math.isfinite(value) for value in output):
        raise ValueError("plot data must be finite")
    return output


def _graph_data(
    edges: Iterable[tuple[Any, Any]],
    nodes: Iterable[Any] | None,
    levels: Mapping[Any, int] | None,
) -> tuple[list[tuple[Any, Any]], list[Any], dict[Any, tuple[float, float]]]:
    links = list(edges)
    vertices = list(dict.fromkeys([*(nodes or []), *(node for edge in links for node in edge)]))
    positions: dict[Any, tuple[float, float]] = {}
    if levels is not None:
        if any(node not in levels for node in vertices):
            raise ValueError("every node requires an explicit level")
        groups: dict[int, list[Any]] = {}
        for node in vertices:
            groups.setdefault(levels[node], []).append(node)
        for level, group in groups.items():
            for index, node in enumerate(group):
                positions[node] = (float(level), (len(group) - 1) / 2 - index)
    else:
        for index, node in enumerate(vertices):
            angle = 2 * math.pi * index / max(1, len(vertices))
            positions[node] = (math.cos(angle), math.sin(angle))
    return links, vertices, positions


def _graph_extent(
    vertices: Sequence[Any],
    labels: Mapping[Any, str] | None,
    levels: Mapping[Any, int] | None,
) -> tuple[int, int, int]:
    """Estimate rows, columns and label width to preserve readable graph spacing.

    Large state spaces remain bounded in screen/export size. The interactive plot
    supports zooming when those bounds are reached; no states are hidden.
    """
    if levels is None:
        rows = columns = max(1, math.ceil(math.sqrt(len(vertices))))
    else:
        counts: dict[int, int] = {}
        for node in vertices:
            counts[levels[node]] = counts.get(levels[node], 0) + 1
        rows = max(counts.values(), default=1)
        columns = max(1, len(counts))
    label_width = max(
        (
            len(labels.get(node, str(node)) if labels is not None else str(node))
            for node in vertices
        ),
        default=1,
    )
    return rows, columns, min(label_width, 40)


def graph_figure(
    edges: Iterable[tuple[Any, Any]],
    *,
    nodes: Iterable[Any] | None = None,
    labels: Mapping[Any, str] | None = None,
    levels: Mapping[Any, int] | None = None,
    title: str = "Directed structural graph",
) -> Any:
    """Create an interactive, directed graph with deterministic layout.

    ``levels`` lays out generations from left to right. Without levels a circle
    is used; circular placement does not imply a temporal or geometric model.
    """
    links, vertices, positions = _graph_data(edges, nodes, levels)
    rows, columns, label_width = _graph_extent(vertices, labels, levels)
    go = _go()
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for left, right in links:
        edge_x.extend([positions[left][0], positions[right][0], None])
        edge_y.extend([positions[left][1], positions[right][1], None])
    text = [labels.get(node, str(node)) if labels is not None else str(node) for node in vertices]
    figure = go.Figure(
        [
            go.Scatter(
                x=edge_x, y=edge_y, mode="lines", line={"color": "#8a96a3"}, hoverinfo="skip"
            ),
            go.Scatter(
                x=[positions[node][0] for node in vertices],
                y=[positions[node][1] for node in vertices],
                mode="markers+text",
                text=text,
                textposition="top center",
                hovertext=text,
                hoverinfo="text",
                marker={"size": 12, "color": "#175c83"},
            ),
        ]
    )
    for left, right in links:
        figure.add_annotation(
            x=positions[right][0],
            y=positions[right][1],
            ax=positions[left][0],
            ay=positions[left][1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text="",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#8a96a3",
            standoff=9,
        )
    figure.update_layout(
        title=title,
        width=min(2400, max(800, 140 + columns * (100 + 6 * label_width))),
        height=min(2400, max(500, 140 + rows * 28)),
        showlegend=False,
        template="plotly_white",
        xaxis={
            "title": "Generation" if levels is not None else "Layout coordinate",
            "showgrid": False,
            **({"dtick": 1} if levels is not None else {}),
        },
        yaxis={"visible": False},
        margin={"l": 40, "r": 40, "t": 80, "b": 40},
    )
    return figure


def plot_graph(
    edges: Iterable[tuple[Any, Any]],
    *,
    nodes: Iterable[Any] | None = None,
    labels: Mapping[Any, str] | None = None,
    levels: Mapping[Any, int] | None = None,
    title: str = "Directed structural graph",
) -> Any:
    """Matplotlib counterpart to :func:`graph_figure`, suitable for PNG/SVG."""
    links, vertices, positions = _graph_data(edges, nodes, levels)
    rows, columns, label_width = _graph_extent(vertices, labels, levels)
    width = min(24.0, max(8.0, 1.3 + columns * (1.0 + 0.06 * label_width)))
    height = min(24.0, max(5.0, 2.0 + rows * 0.34))
    figure = _figure((width, height))
    axis = figure.subplots()
    for left, right in links:
        axis.annotate(
            "",
            xy=positions[right],
            xytext=positions[left],
            arrowprops={"arrowstyle": "->", "color": "#8a96a3", "shrinkA": 9, "shrinkB": 9},
        )
    axis.scatter(
        [positions[node][0] for node in vertices],
        [positions[node][1] for node in vertices],
        s=70,
        color="#175c83",
        zorder=3,
    )
    for node in vertices:
        label = labels.get(node, str(node)) if labels is not None else str(node)
        axis.annotate(
            label,
            positions[node],
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    axis.set_title(title)
    axis.set_xlabel("Generation" if levels is not None else "Layout coordinate")
    axis.set_yticks([])
    if levels is not None:
        axis.set_xticks(sorted(set(levels.values())))
    axis.margins(x=0.2, y=0.08)
    return figure


def _tree_data(
    tree: Any,
) -> tuple[list[tuple[int, int]], list[int], dict[int, str], dict[int, int]]:
    edges: list[tuple[int, int]] = []
    labels: dict[int, str] = {}
    levels: dict[int, int] = {}

    def visit(node: Any, depth: int, ancestors: frozenset[int]) -> int:
        if depth > 200:
            raise ValueError("tree depth exceeds plotting limit 200")
        if id(node) in ancestors and node is not None:
            raise ValueError("cyclic objects are not trees")
        index = len(labels)
        labels[index] = "x" if node is None else str(index)
        levels[index] = depth
        children = getattr(node, "children", node if isinstance(node, (tuple, list)) else ())
        for child in children:
            child_index = visit(child, depth + 1, ancestors | {id(node)})
            edges.append((index, child_index))
        return index

    visit(tree, 0, frozenset())
    return edges, list(labels), labels, levels


def tree_figure(tree: Any, *, title: str = "Rooted ordered tree") -> Any:
    """Plot a Tree.children object or nested tuples; ``None`` labels the seed x."""
    edges, nodes, labels, levels = _tree_data(tree)
    figure = graph_figure(edges, nodes=nodes, labels=labels, levels=levels, title=title)
    figure.update_xaxes(title="Tree depth (edges)")
    return figure


def plot_tree(tree: Any, *, title: str = "Rooted ordered tree") -> Any:
    """Render an ordered tree as a static plot; child order follows input order."""
    edges, nodes, labels, levels = _tree_data(tree)
    figure = plot_graph(edges, nodes=nodes, labels=labels, levels=levels, title=title)
    figure.axes[0].set_xlabel("Tree depth (edges)")
    return figure


def _transition_data(
    stages: Sequence[Iterable[str]],
    transitions: Iterable[Any],
) -> tuple[list[tuple[Any, Any]], list[Any], dict[Any, str], dict[Any, int]]:
    nodes = [(generation, state) for generation, stage in enumerate(stages) for state in stage]
    labels = {node: node[1] for node in nodes}
    levels = {node: node[0] for node in nodes}
    edges = []
    for transition in transitions:
        if hasattr(transition, "parent"):
            generation, parent, child = transition.generation, transition.parent, transition.child
        else:
            generation, parent, child = transition[:3]
        # generation is the child stage; seed 0 is at stage 0.
        left, right = (generation - 1, parent), (generation, child)
        if left not in labels or right not in labels:
            raise ValueError("transition endpoint is missing from the supplied stages")
        edges.append((left, right))
    return list(dict.fromkeys(edges)), nodes, labels, levels


def transition_figure(
    stages: Sequence[Iterable[str]],
    transitions: Iterable[Any],
    *,
    title: str = "Structural generation history",
) -> Any:
    """Plot explicit transitions, keeping equal strings at different stages distinct.

    Accepts structural_logic.Transition records; tuple records use
    ``(child_generation, parent, child)``. Duplicate action edges are drawn once.
    """
    edges, nodes, labels, levels = _transition_data(stages, transitions)
    return graph_figure(edges, nodes=nodes, labels=labels, levels=levels, title=title)


def plot_transitions(
    stages: Sequence[Iterable[str]],
    transitions: Iterable[Any],
    *,
    title: str = "Structural generation history",
) -> Any:
    """Static generation-history diagram using the same endpoints as the HTML plot."""
    edges, nodes, labels, levels = _transition_data(stages, transitions)
    return plot_graph(edges, nodes=nodes, labels=labels, levels=levels, title=title)


def plot_function(
    function: Callable[[float], float],
    start: float,
    stop: float,
    *,
    points: int = 200,
    title: str = "Mathematical function",
    xlabel: str = "x",
    ylabel: str = "f(x)",
) -> Any:
    """Sample a scalar function on a closed interval; evaluation errors propagate."""
    if not isinstance(points, int) or isinstance(points, bool) or points < 2:
        raise ValueError("points must be an integer of at least two")
    if not math.isfinite(start) or not math.isfinite(stop) or start >= stop:
        raise ValueError("start and stop must be finite, increasing bounds")
    xs = [start + (stop - start) * index / (points - 1) for index in range(points)]
    ys = _finite(function(x) for x in xs)
    figure = _figure()
    axis = figure.subplots()
    axis.plot(xs, ys)
    axis.set(title=title, xlabel=xlabel, ylabel=ylabel)
    axis.grid(alpha=0.2)
    return figure


def plot_distribution(
    values: Iterable[float],
    *,
    bins: int = 20,
    density: bool = False,
    title: str = "Empirical distribution",
) -> Any:
    """Histogram observations, labeling counts and density distinctly."""
    data = _finite(values)
    if not data or not isinstance(bins, int) or isinstance(bins, bool) or bins < 1:
        raise ValueError("nonempty observations and a positive integer bin count are required")
    figure = _figure()
    axis = figure.subplots()
    axis.hist(data, bins=bins, density=density, color="#175c83", edgecolor="white")
    axis.set(title=title, xlabel="Observed value", ylabel="Density" if density else "Count")
    return figure


def plot_comparison(
    records: Iterable[Mapping[str, Any]],
    *,
    x: str = "generation",
    metrics: Iterable[str] = ("count",),
    title: str = "Experimental comparison",
) -> Any:
    """Compare numeric columns against a numeric independent variable."""
    rows, names = list(records), list(metrics)
    if not rows or not names:
        raise ValueError("records and metric names must be nonempty")
    xs = _finite(row[x] for row in rows)
    figure = _figure()
    axis = figure.subplots()
    for name in names:
        axis.plot(xs, _finite(row[name] for row in rows), marker="o", label=name)
    axis.set(title=title, xlabel=x, ylabel="Metric value")
    axis.legend()
    axis.grid(alpha=0.2)
    return figure


def save_figure(figure: Any, path: str | Path) -> Path:
    """Export Plotly HTML with embedded JS or Matplotlib PNG/SVG.

    Unsupported figure/extension pairs fail explicitly. Plotly raster export is
    intentionally not required: use a static plot function for PNG or SVG.
    """
    target = Path(path)
    suffix = target.suffix.lower()
    if suffix == ".html" and hasattr(figure, "write_html"):
        target.parent.mkdir(parents=True, exist_ok=True)
        figure.write_html(str(target), include_plotlyjs=True, full_html=True)
    elif suffix in {".png", ".svg"} and hasattr(figure, "savefig"):
        target.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(target, format=suffix[1:], dpi=150)
    else:
        raise ValueError("use a Plotly figure for .html or a Matplotlib figure for .png/.svg")
    return target


__all__ = [
    "graph_figure",
    "plot_graph",
    "tree_figure",
    "plot_tree",
    "transition_figure",
    "plot_transitions",
    "plot_function",
    "plot_distribution",
    "plot_comparison",
    "save_figure",
]
