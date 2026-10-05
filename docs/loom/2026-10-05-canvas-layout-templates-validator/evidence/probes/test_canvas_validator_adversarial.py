#!/usr/bin/env python3
"""Adversarial probes for obsidian-canvas-creator's validate_canvas.py.

concern: false passes and false crashes on hostile or boundary canvas input —
malformed ids (non-hex, wrong length, uppercase), cross-kind duplicate ids,
dangling and edge-id edge references, non-object top level, non-array
nodes/edges, group-overlap exclusion, empty input, and large canvases.

Each probe asserts the validator's exit code AND the reported violation are
correct: a clean file exits 0 with no output, a violating file exits 1 naming
the violation, and no input may crash the validator (no traceback). A false
pass or a false crash is a defect.

Run: python3 test_canvas_validator_adversarial.py   (or pytest)
"""

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

VALIDATOR = None


def _validator_path():
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = (
            parent
            / "obsidian"
            / "skills"
            / "obsidian-canvas-creator"
            / "scripts"
            / "validate_canvas.py"
        )
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("validate_canvas.py not found above this test file")


VALIDATOR = _validator_path()

# Distinct valid 16-char lowercase-hex ids.
N1 = "0123456789abcdef"
N2 = "fedcba9876543210"
N3 = "aaaaaaaabbbbcccc"
E1 = "1111222233334444"
E2 = "5555666677778888"
E3 = "9999aaaabbbbcccc"
DANGLING = "ffffffffffffffff"


def _node(node_id, node_type="text", x=0, y=0, width=100, height=50, **extra):
    node = {
        "id": node_id,
        "type": node_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }
    node.update(extra)
    return node


def _canvas(nodes, edges=None):
    data = {"nodes": nodes}
    if edges is not None:
        data["edges"] = edges
    return json.dumps(data)


def _run(payload, timeout=120):
    """Run the validator on payload (str or bytes) in a temp file.

    Asserts the validator never crashes (a traceback on stderr is a defect),
    and returns the CompletedProcess and elapsed seconds.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.canvas"
        if isinstance(payload, bytes):
            path.write_bytes(payload)
        else:
            path.write_text(payload, encoding="utf-8")
        started = time.monotonic()
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - started
    assert "Traceback" not in result.stderr, (
        f"validator crashed (false crash defect): rc={result.returncode}\n"
        f"{result.stderr}"
    )
    return result, elapsed


class CanvasValidatorAdversarial(unittest.TestCase):
    # --- ids: non-hex, wrong length, uppercase -------------------------

    def test_node_id_non_hex_16chars_rejected(self):
        # 16 chars but not hex: must be reported, not silently accepted.
        result, _ = _run(_canvas([_node("zzzz000000000000", text="hi")]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid id", result.stdout)

    def test_node_id_15chars_rejected(self):
        result, _ = _run(_canvas([_node("0123456789abcde", text="hi")]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid id", result.stdout)

    def test_node_id_17chars_rejected(self):
        result, _ = _run(_canvas([_node("0123456789abcdef0", text="hi")]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid id", result.stdout)

    def test_node_id_uppercase_rejected(self):
        result, _ = _run(_canvas([_node("ABCDEF0123456789", text="hi")]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid id", result.stdout)

    # --- duplicate ids across kinds -----------------------------------

    def test_edge_id_duplicate_of_node_id_reported(self):
        payload = _canvas(
            [_node(N1, x=0, y=0, text="a"), _node(N2, x=500, y=0, text="b")],
            edges=[{"id": N1, "fromNode": N1, "toNode": N2}],
        )
        result, _ = _run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate id", result.stdout)

    # --- edge references ----------------------------------------------

    def test_fromnode_referencing_missing_node_reported(self):
        payload = _canvas(
            [_node(N1, x=0, y=0, text="a"), _node(N2, x=500, y=0, text="b")],
            edges=[{"id": E1, "fromNode": DANGLING, "toNode": N2}],
        )
        result, _ = _run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("references missing node", result.stdout)
        self.assertIn(DANGLING, result.stdout)

    def test_tonode_referencing_edge_id_reported(self):
        # An edge id is not a valid fromNode/toNode target: pointing at one
        # must be reported as a missing node, never silently accepted.
        payload = _canvas(
            [_node(N1, x=0, y=0, text="a"), _node(N2, x=500, y=0, text="b")],
            edges=[
                {"id": E1, "fromNode": N1, "toNode": N2},
                {"id": E2, "fromNode": N1, "toNode": E1},
            ],
        )
        result, _ = _run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("references missing node", result.stdout)
        self.assertIn(E1, result.stdout)

    # --- structure: missing/non-array keys, non-object top level ------

    def test_missing_nodes_edges_keys_exit_zero(self):
        # Both arrays are optional per the validator contract.
        result, _ = _run("{}")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_nodes_without_edges_key_exit_zero(self):
        result, _ = _run(_canvas([_node(N1, x=0, y=0, text="hi")]))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_nodes_not_an_array_reported(self):
        result, _ = _run('{"nodes": 5}')
        self.assertEqual(result.returncode, 1)
        self.assertIn("nodes is not an array", result.stdout)

    def test_top_level_array_rejected(self):
        result, _ = _run("[]")
        self.assertEqual(result.returncode, 1)
        self.assertIn("top level is not an object", result.stdout)

    def test_top_level_string_rejected(self):
        result, _ = _run('"not a canvas"')
        self.assertEqual(result.returncode, 1)
        self.assertIn("top level is not an object", result.stdout)

    # --- node types ---------------------------------------------------

    def test_unknown_node_type_common_fields_exit_zero(self):
        # Per-type required fields apply to known types only; an unknown type
        # with all common fields is not a violation.
        payload = _canvas([_node(E1, node_type="image", x=0, y=0)])
        result, _ = _run(payload)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    # --- overlap: group exclusion -------------------------------------

    def test_two_overlapping_groups_not_flagged(self):
        g1 = _node(E1, node_type="group", x=0, y=0, width=300, height=200, label="A")
        g2 = _node(E2, node_type="group", x=100, y=50, width=300, height=200, label="B")
        result, _ = _run(_canvas([g1, g2]))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_node_inside_group_not_flagged(self):
        group = _node(E1, node_type="group", x=0, y=0, width=400, height=300, label="C")
        child = _node(E2, node_type="text", x=50, y=50, width=100, height=50, text="hi")
        result, _ = _run(_canvas([group, child]))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_sibling_overlap_inside_group_still_flagged(self):
        # The group exclusion is group-vs-child only: two text siblings inside
        # the same group still overlap each other and must be reported.
        group = _node(E1, node_type="group", x=0, y=0, width=400, height=300, label="C")
        c1 = _node(E2, node_type="text", x=50, y=50, width=100, height=50, text="a")
        c2 = _node(E3, node_type="text", x=80, y=70, width=100, height=50, text="b")
        result, _ = _run(_canvas([group, c1, c2]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("overlaps", result.stdout)

    # --- empty input --------------------------------------------------

    def test_empty_file_reported_as_invalid_json(self):
        result, _ = _run("")
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stdout)

    def test_missing_file_reported_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.canvas"
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(missing)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    # --- scale --------------------------------------------------------

    def test_large_canvas_clean_exits_zero(self):
        # 3000 non-overlapping nodes plus a 2999-edge chain: clean, and fast
        # enough that the O(n^2) overlap scan does not hang.
        nodes = [
            _node(f"{i:016x}", x=i * 120, y=0, width=100, height=50, text="n")
            for i in range(3000)
        ]
        edges = [
            {"id": f"{10000 + i:016x}", "fromNode": f"{i - 1:016x}", "toNode": f"{i:016x}"}
            for i in range(1, 3000)
        ]
        result, elapsed = _run(_canvas(nodes, edges))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertLess(elapsed, 60.0)

    def test_large_canvas_late_overlap_caught(self):
        # At scale the scan must still find an overlap placed at the very end.
        nodes = [
            _node(f"{i:016x}", x=i * 120, y=0, width=100, height=50, text="n")
            for i in range(3000)
        ]
        nodes[-1]["x"] = 2998 * 120 + 10
        result, _ = _run(_canvas(nodes))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count("overlaps"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
