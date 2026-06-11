"""Tests for the pairwise (all-pairs) generator core."""

from __future__ import annotations

import json
import subprocess
import sys
from itertools import combinations, product
from pathlib import Path

from pairwise import pairwise

PAIRWISE_PY = Path(__file__).with_name("pairwise.py")


def _required_pair_count(params: dict[str, list[str]]) -> int:
    """Total number of cross-object value pairs that MUST be covered."""
    objects = [obj for obj, states in params.items() if states]
    return sum(
        len(params[a]) * len(params[b])
        for a, b in combinations(objects, 2)
    )


def _assert_full_coverage(params: dict[str, list[str]], rows):
    """Every row is well-formed and every cross-object value pair is covered."""
    for row in rows:
        assert set(row) == set(params)
        for obj, state in row.items():
            assert state in params[obj]

    for obj_a, obj_b in combinations(params, 2):
        for val_a, val_b in product(params[obj_a], params[obj_b]):
            assert any(
                row[obj_a] == val_a and row[obj_b] == val_b
                for row in rows
            ), f"pair ({obj_a}={val_a}, {obj_b}={val_b}) not covered"


def test_covers_all_pairs():
    params = {
        "A": ["a1", "a2", "a3"],
        "B": ["b1", "b2", "b3"],
        "C": ["c1", "c2", "c3"],
        "D": ["d1", "d2", "d3"],
    }
    rows = pairwise(params)

    _assert_full_coverage(params, rows)

    # Strictly smaller than the full cartesian product (3**4 == 81).
    assert len(rows) < 3 ** 4


def test_terminates_within_required_pair_bound():
    """Regression guard: the greedy algorithm covers >=1 new pair per row, so
    it MUST finish in at most |required pairs| rows. A future key-consistency
    bug (the prior infinite-loop class) would blow past this bound — this
    assertion makes that fail FAST instead of hanging on a wall-clock timeout.
    """
    params = {
        "A": ["a1", "a2", "a3"],
        "B": ["b1", "b2", "b3"],
        "C": ["c1", "c2", "c3"],
        "D": ["d1", "d2", "d3"],
    }
    rows = pairwise(params)
    assert len(rows) <= _required_pair_count(params)


def test_two_objects_full_coverage():
    """With exactly two objects, all pairs == the cartesian product; every
    combination must appear and the bound still holds."""
    params = {
        "A": ["a1", "a2"],
        "B": ["b1", "b2", "b3"],
    }
    rows = pairwise(params)

    _assert_full_coverage(params, rows)
    assert len(rows) <= _required_pair_count(params)


def test_five_objects_terminates_and_covers():
    """Larger case (5 objects) exercises termination + coverage at scale and
    stays well under the cartesian product (3**5 == 243)."""
    params = {
        "A": ["a1", "a2", "a3"],
        "B": ["b1", "b2", "b3"],
        "C": ["c1", "c2", "c3"],
        "D": ["d1", "d2", "d3"],
        "E": ["e1", "e2", "e3"],
    }
    rows = pairwise(params)

    _assert_full_coverage(params, rows)
    assert len(rows) <= _required_pair_count(params)
    assert len(rows) < 3 ** 5


def test_fewer_than_two_objects_is_empty():
    assert pairwise({}) == []
    assert pairwise({"A": ["a1", "a2"]}) == []
    # An object with no states contributes no cross-object pairs.
    assert pairwise({"A": ["a1"], "B": []}) == []


def test_cli_stdin_stdout_roundtrip():
    """The CLI wrapper reads {"params": {...}} from stdin, runs pairwise(),
    and writes the rows as a JSON list to stdout. The emitted rows must cover
    every cross-object value pair for the input — same contract as the
    in-process call, exercised end-to-end through the process boundary."""
    params = {"A": ["a1", "a2"], "B": ["b1", "b2"], "C": ["c1", "c2"]}
    proc = subprocess.run(
        [sys.executable, str(PAIRWISE_PY)],
        input=json.dumps({"params": params}),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert proc.returncode == 0, proc.stderr
    rows = json.loads(proc.stdout)
    assert isinstance(rows, list)
    _assert_full_coverage(params, rows)
