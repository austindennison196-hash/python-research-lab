"""Build a bounded browser dataset directly from the laboratory's Python engine."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from research_lab.structural_logic import (
    EXAMPLES,
    RULES,
    binary_to_notation,
    binary_to_tree,
    explore,
    is_dyck,
    metrics,
)


def build(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for source in (Path(__file__).resolve().parents[1] / "web").iterdir():
        if source.is_file():
            shutil.copy2(source, destination / source.name)
    models = {}
    for name, rule in RULES.items():
        exploration = explore(6, name, max_states=10000)
        states = {}
        for stage in exploration.stages:
            for word in stage:
                encodable = word == "0" or is_dyck(word, primitive=True)
                states[word] = {
                    "word": word,
                    "metrics": metrics(word),
                    "notation": binary_to_notation(word) if encodable else None,
                    "tree": binary_to_tree(word).to_dict() if word != "0" and encodable else None,
                }
        models[name] = {
            "description": rule.description,
            "exploration": exploration.to_dict(),
            "states": states,
        }
    data = {"schema_version": 1, "max_generation": 6, "examples": EXAMPLES, "models": models}
    (destination / "data.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    (destination / ".nojekyll").touch()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist/site"))
    build(parser.parse_args().output)
