"""Small, explicit data-analysis tools; pandas is an optional adapter."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("observations must be real numbers, excluding booleans")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("observations must be finite")
    return result


def summarize(values: Iterable[float]) -> dict[str, float | int | None]:
    """Describe nonempty finite observations, using sample standard deviation.

    A single observation has undefined sample standard deviation, represented by
    ``None`` rather than a misleading zero. No missing values are silently dropped.
    """
    data = [_number(value) for value in values]
    if not data:
        raise ValueError("at least one observation is required")
    return {
        "n": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "stdev": statistics.stdev(data) if len(data) > 1 else None,
        "min": min(data),
        "max": max(data),
        "total": math.fsum(data),
    }


def summarize_records(
    records: Iterable[Mapping[str, Any]],
    fields: Iterable[str] | None = None,
) -> dict[str, dict[str, float | int | None]]:
    """Summarize selected columns, or all columns that are numeric in every row.

    Explicit fields require a value in every record; implicit selection excludes
    incomplete, boolean and textual columns. Every selected value must be finite.
    """
    rows = list(records)
    if not rows:
        raise ValueError("at least one record is required")
    if fields is None:
        names = [
            name
            for name in rows[0]
            if all(
                name in row
                and isinstance(row[name], (int, float))
                and not isinstance(row[name], bool)
                for row in rows
            )
        ]
    else:
        names = list(fields)
    return {name: summarize(row[name] for row in rows) for name in names}


def compare_metrics(
    before: Mapping[str, float],
    after: Mapping[str, float],
) -> dict[str, dict[str, float | None]]:
    """Compare identically named numeric metrics, preserving zero-baseline cases.

    Relative change is ``(after-before)/abs(before)``; it is undefined (None)
    at a zero baseline. This describes observations, not statistical significance.
    """
    if before.keys() != after.keys():
        raise ValueError("both metric sets must have exactly the same names")
    comparisons = {}
    for name in before:
        left, right = _number(before[name]), _number(after[name])
        delta = right - left
        comparisons[name] = {
            "before": left,
            "after": right,
            "delta": delta,
            "relative_change": delta / abs(left) if left else None,
        }
    return comparisons


def save_records(records: Iterable[Mapping[str, Any]], path: str | Path) -> Path:
    """Export records to JSON or CSV; reject nonfinite JSON values."""
    target = Path(path)
    rows = [dict(row) for row in records]
    suffix = target.suffix.lower()
    if suffix not in {".json", ".csv"}:
        raise ValueError("record format must be .json or .csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    if suffix == ".json":
        target.write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n")
    else:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with target.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return target


def load_records(path: str | Path) -> list[dict[str, Any]]:
    """Load JSON records or CSV string records (convert CSV types explicitly)."""
    source = Path(path)
    if source.suffix.lower() == ".json":
        value = json.loads(source.read_text())
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            raise ValueError("JSON records must be a list of objects")
        return value
    if source.suffix.lower() == ".csv":
        with source.open(newline="") as stream:
            return list(csv.DictReader(stream))
    raise ValueError("record format must be .json or .csv")


def to_dataframe(records: Iterable[Mapping[str, Any]]) -> Any:
    """Construct a pandas DataFrame only when this optional adapter is called."""
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("Install python-research-lab[scientific] for pandas") from exc
    return pd.DataFrame(list(records))


__all__ = [
    "summarize",
    "summarize_records",
    "compare_metrics",
    "save_records",
    "load_records",
    "to_dataframe",
]
