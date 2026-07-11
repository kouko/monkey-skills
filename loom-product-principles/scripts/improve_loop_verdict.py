"""Verdict helper for the L3 principles-improve-loop (Task 1, brief
docs/loom/specs/2026-07-11-principles-replay-l3-loop.md §Smallest End
State item 4).

Two subcommands, each reading matrix-run row-sets from JSON files and
returning an exit code — never printing anything on the accept/pass
path (mirrors `check_seed_traceability.py`'s exit-code convention).

INPUT FORMAT: each `--baseline`/`--candidate` argument is a path to a
JSON file holding either:

  - the full matrix return shape `{"runLabel": ..., "rows": [...],
    "passRate": ...}` (as returned by `.claude/workflows/
    principles-replay-matrix.js`), or
  - a bare JSON list of row dicts.

Each row dict MUST carry `seedId` (str) and `pass` (bool); any other
keys (validatorExit, misses, artifactPath, ...) are ignored. Malformed
JSON, a non-object/non-list root, a "rows" value that isn't a list, or
a row missing `seedId`/`pass` all count as malformed input.

`compare` — aggregates ALL `--baseline` row-sets into one per-seed
pass map using the rule: **a seed's baseline = pass if it passed
(pass: true) in ANY of the given baseline runs** (else fail). This is
then compared against the single `--candidate` row-set's per-seed pass
map. The candidate and the aggregated baseline MUST cover exactly the
same seed-id set — a mismatch is malformed input (a fixer round must
not silently score against a partial seed set).

  Exit 0 — a "win": no seed regresses (baseline-pass, candidate-fail)
           AND at least one seed improves (baseline-fail, candidate-pass).
  Exit 1 — anything else, including the trade case (one seed improves
           AND another regresses) and the no-change case.
  Exit 2 — malformed input (see above), or a named file does not exist.

`smoke` — compares one held-out `--baseline` row-set against one
held-out `--candidate` row-set, seed-for-seed (no aggregation — each
side is exactly one run). The only failure condition is a seed that
was baseline-pass and is now candidate-fail ("newly failing"); a
held-out seed improving, or staying failed, is not a smoke failure.

  Exit 0 — no held-out seed is newly failing.
  Exit 1 — at least one held-out seed is newly failing; each such
           seed id is printed on its own stdout line.
  Exit 2 — malformed input (same criteria as `compare`), or a named
           file does not exist.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class MalformedInputError(ValueError):
    """Raised for any input that fails the row-set contract above."""


def _rows_from_json(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        rows = data.get("rows")
        if not isinstance(rows, list):
            raise MalformedInputError(
                "JSON object must contain a 'rows' list (matrix return shape)"
            )
        return rows
    raise MalformedInputError(
        "JSON root must be a list of rows or an object with a 'rows' list"
    )


def _pass_map_from_rows(rows: list) -> dict:
    """Validate `rows` and return `{seedId: pass}`. Raises
    MalformedInputError if any row lacks a str `seedId` or a bool `pass`."""
    pass_map = {}
    for row in rows:
        if not isinstance(row, dict) or "seedId" not in row or "pass" not in row:
            raise MalformedInputError(
                f"row missing required 'seedId'/'pass' keys: {row!r}"
            )
        seed_id = row["seedId"]
        passed = row["pass"]
        if not isinstance(seed_id, str) or not isinstance(passed, bool):
            raise MalformedInputError(
                f"row has wrong types for 'seedId'/'pass': {row!r}"
            )
        pass_map[seed_id] = passed
    return pass_map


def load_row_set(path: str) -> list:
    """Read one row-set JSON file. Raises MalformedInputError (including
    on a missing file or invalid JSON) — never a bare exception type the
    CLI would have to guess about."""
    file_path = Path(path)
    if not file_path.is_file():
        raise MalformedInputError(f"file not found: {path}")
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MalformedInputError(f"invalid JSON in {path}: {exc}") from exc
    return _rows_from_json(data)


def aggregate_pass_map(row_sets: list) -> dict:
    """Aggregate multiple baseline row-sets into one per-seed pass map:
    a seed passes if it passed (pass: true) in ANY of the given row-sets.
    """
    aggregated = {}
    for rows in row_sets:
        for seed_id, passed in _pass_map_from_rows(rows).items():
            aggregated[seed_id] = aggregated.get(seed_id, False) or passed
    return aggregated


def _require_same_seeds(baseline_map: dict, candidate_map: dict) -> None:
    if set(baseline_map) != set(candidate_map):
        raise MalformedInputError(
            "baseline and candidate seed sets differ: "
            f"baseline-only={sorted(set(baseline_map) - set(candidate_map))}, "
            f"candidate-only={sorted(set(candidate_map) - set(baseline_map))}"
        )


def compare(baseline_row_sets: list, candidate_rows: list):
    """Returns (exit_code, worse_seeds, better_seeds)."""
    baseline_map = aggregate_pass_map(baseline_row_sets)
    candidate_map = _pass_map_from_rows(candidate_rows)
    _require_same_seeds(baseline_map, candidate_map)

    worse = sorted(s for s in baseline_map if baseline_map[s] and not candidate_map[s])
    better = sorted(s for s in baseline_map if not baseline_map[s] and candidate_map[s])

    exit_code = 0 if (not worse and better) else 1
    return exit_code, worse, better


def smoke(baseline_rows: list, candidate_rows: list):
    """Returns (exit_code, newly_failing_seeds)."""
    baseline_map = _pass_map_from_rows(baseline_rows)
    candidate_map = _pass_map_from_rows(candidate_rows)
    _require_same_seeds(baseline_map, candidate_map)

    newly_failing = sorted(
        s for s in baseline_map if baseline_map[s] and not candidate_map[s]
    )
    exit_code = 1 if newly_failing else 0
    return exit_code, newly_failing


def _cmd_compare(args) -> int:
    try:
        baseline_row_sets = [load_row_set(p) for p in args.baseline]
        candidate_rows = load_row_set(args.candidate)
        exit_code, worse, better = compare(baseline_row_sets, candidate_rows)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if worse:
        print(f"worse: {', '.join(worse)}", file=sys.stderr)
    if not better:
        print("no seed improved", file=sys.stderr)
    return exit_code


def _cmd_smoke(args) -> int:
    try:
        baseline_rows = load_row_set(args.baseline)
        candidate_rows = load_row_set(args.candidate)
        exit_code, newly_failing = smoke(baseline_rows, candidate_rows)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for seed_id in newly_failing:
        print(seed_id)
    return exit_code


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Two-stage verdict helper for the L3 principles-improve-loop: "
                    "'compare' judges a visible-seed round (no seed worse AND >=1 "
                    "better); 'smoke' judges the held-out confirmation (no seed "
                    "newly failing).")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare_parser = subparsers.add_parser(
        "compare",
        help="compare >=1 baseline row-sets (aggregated: pass if ANY run passed) "
             "against exactly one candidate row-set",
    )
    compare_parser.add_argument(
        "--baseline", action="append", required=True, metavar="PATH",
        help="path to a baseline matrix-run JSON row-set; repeatable, >=1 required",
    )
    compare_parser.add_argument(
        "--candidate", required=True, metavar="PATH",
        help="path to the candidate matrix-run JSON row-set",
    )
    compare_parser.epilog = "Exit codes: 0 win (no worse, >=1 better), 1 no win, 2 malformed input."
    compare_parser.set_defaults(func=_cmd_compare)

    smoke_parser = subparsers.add_parser(
        "smoke",
        help="compare one held-out baseline row-set against one held-out "
             "candidate row-set",
    )
    smoke_parser.add_argument(
        "--baseline", required=True, metavar="PATH",
        help="path to the held-out baseline JSON row-set",
    )
    smoke_parser.add_argument(
        "--candidate", required=True, metavar="PATH",
        help="path to the held-out candidate JSON row-set",
    )
    smoke_parser.epilog = "Exit codes: 0 no newly-failing seed, 1 newly-failing seed(s) (named on stdout), 2 malformed input."
    smoke_parser.set_defaults(func=_cmd_smoke)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
