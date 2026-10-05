"""Validator tests for obsidian-canvas-creator (Acceptance #3 / #4).

Covers the checks the validator must make: a clean file exits 0, a duplicate
id is named, a dangling edge reference is named, a missing required field is
named, overlapping non-group nodes are named, and a group overlapping its own
children is NOT flagged (groups are containers).
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).parent.parent
    / "skills"
    / "obsidian-canvas-creator"
    / "scripts"
    / "validate_canvas.py"
)

_spec = importlib.util.spec_from_file_location("validate_canvas", SCRIPT)
validate_canvas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_canvas)

# A valid 16-character lowercase hex id, and a few distinct siblings.
ID_A = "0123456789abcdef"
ID_B = "fedcba9876543210"
ID_C = "aaaaaaaabbbbcccc"
ID_D = "1111222233334444"


def _canvas(nodes, edges=None):
    data = {"nodes": nodes}
    if edges is not None:
        data["edges"] = edges
    return json.dumps(data)


def _run(canvas_path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(canvas_path)],
        capture_output=True,
        text=True,
    )


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def _text_node(node_id, x, y, width=100, height=50):
    return {
        "id": node_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "text": "content",
    }


def test_clean_valid_canvas_exits_zero(tmp_path):
    path = _write(
        tmp_path,
        "clean.canvas",
        _canvas(
            [_text_node(ID_A, 0, 0), _text_node(ID_B, 500, 0)],
            edges=[
                {"id": ID_C, "fromNode": ID_A, "toNode": ID_B},
            ],
        ),
    )
    result = _run(path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_duplicate_id_is_reported(tmp_path):
    path = _write(
        tmp_path,
        "dupe.canvas",
        _canvas([_text_node(ID_A, 0, 0), _text_node(ID_A, 500, 0)]),
    )
    result = _run(path)
    assert result.returncode != 0
    assert "duplicate id" in result.stdout
    assert ID_A in result.stdout


def test_dangling_edge_reference_is_reported(tmp_path):
    path = _write(
        tmp_path,
        "dangling.canvas",
        _canvas(
            [_text_node(ID_A, 0, 0)],
            edges=[{"id": ID_C, "fromNode": ID_A, "toNode": ID_D}],
        ),
    )
    result = _run(path)
    assert result.returncode != 0
    assert ID_D in result.stdout


def test_missing_required_field_is_reported(tmp_path):
    node = _text_node(ID_A, 0, 0)
    del node["text"]
    path = _write(tmp_path, "missing.canvas", _canvas([node]))
    result = _run(path)
    assert result.returncode != 0
    assert "text" in result.stdout


def test_overlapping_non_group_nodes_are_reported(tmp_path):
    path = _write(
        tmp_path,
        "overlap.canvas",
        _canvas([_text_node(ID_A, 0, 0), _text_node(ID_B, 50, 25)]),
    )
    result = _run(path)
    assert result.returncode != 0
    assert ID_A in result.stdout and ID_B in result.stdout


def test_group_overlapping_its_children_is_not_flagged(tmp_path):
    group = {
        "id": ID_A,
        "type": "group",
        "x": 0,
        "y": 0,
        "width": 400,
        "height": 300,
        "label": "Container",
    }
    child = _text_node(ID_B, 50, 50)
    path = _write(tmp_path, "group.canvas", _canvas([group, child]))
    result = _run(path)
    assert result.returncode == 0
    assert result.stdout == ""
