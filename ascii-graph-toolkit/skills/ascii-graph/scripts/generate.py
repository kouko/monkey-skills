"""Dispatch CLI for the four ASCII/Unicode diagram generators.

Reads a JSON payload from stdin describing one shape's input, routes to
the matching generator, prints the rendered diagram, returns 0. Shapes:

    table  {"headers": [...], "rows": [[...]], "ascii_only": false}
    flow   {"steps": [...]}
    tree   {"node": {...}}
    bar    {"pairs": [["label", value], ...], "width": 20}
    arch   {"layers": [{"name": str, "components": [str, ...]}, ...]}

Unknown shape -> error message on stderr, return 2.
"""

import json
import sys

# Suppress __pycache__ creation: these scripts live inside a skill folder whose
# flat-structure hook treats any nested dir (incl. __pycache__) as a violation.
sys.dont_write_bytecode = True

from gen_arch import render_arch
from gen_bar import render_bar
from gen_flow import render_flow
from gen_table import render_table
from gen_tree import render_tree

_SHAPES = ("table", "flow", "tree", "bar", "arch")


def render(shape: str, payload: dict) -> str:
    """Route a payload to the matching generator and return its output.

    Raises ValueError on an unknown shape so callers fail loud rather
    than silently producing an empty diagram.
    """
    if shape == "table":
        return render_table(
            payload["headers"],
            payload["rows"],
            ascii_only=payload.get("ascii_only", False),
        )
    if shape == "flow":
        return render_flow(payload["steps"])
    if shape == "tree":
        return render_tree(payload["node"])
    if shape == "bar":
        pairs = [(label, value) for label, value in payload["pairs"]]
        return render_bar(pairs, width=payload.get("width", 20))
    if shape == "arch":
        return render_arch(payload["layers"])
    raise ValueError(f"unknown shape: {shape!r} (expected one of {_SHAPES})")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(f"usage: generate.py <{'|'.join(_SHAPES)}> < payload.json",
              file=sys.stderr)
        return 2

    shape = argv[0]
    if shape not in _SHAPES:
        print(f"unknown shape: {shape!r} (expected one of {_SHAPES})",
              file=sys.stderr)
        return 2

    payload = json.load(sys.stdin)
    print(render(shape, payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
