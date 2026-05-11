#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""detect_conflicts — duplicate clause_id + overlapping ABAC gates.

Scans a `legal-playbook/` folder (or any directory containing
playbook .md files) and reports two kinds of structural conflict:

  1. **Duplicate clause_id**: two flat files OR a flat file +
     variant-folder with the same `clause_id`. Only one canonical
     entry per clause_id is allowed.

  2. **Overlapping gates within a variant-folder**: two variants
     of the same clause whose `gates` ranges overlap, so that some
     deal_context could match both. ABAC pre-filter (L7) would
     pick first-match arbitrarily and log a warning — but the
     real fix is to author non-overlapping gates here.

Usage:
    detect_conflicts.py <playbook-dir>
    detect_conflicts.py --format json legal-playbook/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def _enumerate_entries(playbook_dir: Path) -> list[dict]:
    """Yield {clause_id, layout, path, gates?} for each entry.

    Variant-folder entries become one record per variant file
    (plus the _clause.md container is included with layout=variant-container
    so duplicate-id detection can see it too).
    """
    out: list[dict] = []
    if not playbook_dir.is_dir():
        return out
    for entry in sorted(playbook_dir.iterdir()):
        if entry.name.startswith(".") or entry.name in {"README.md", ".skipped"}:
            continue
        if entry.is_file() and entry.suffix == ".md":
            fm = _frontmatter(entry) or {}
            out.append(
                {
                    "clause_id": fm.get("clause_id"),
                    "layout": "flat",
                    "path": str(entry),
                }
            )
        elif entry.is_dir():
            container = entry / "_clause.md"
            if not container.is_file():
                continue
            fm = _frontmatter(container) or {}
            out.append(
                {
                    "clause_id": fm.get("clause_id"),
                    "layout": "variant-container",
                    "path": str(container),
                }
            )
            for vf in sorted(entry.iterdir()):
                if vf.is_file() and vf.suffix == ".md" and vf.name != "_clause.md":
                    vfm = _frontmatter(vf) or {}
                    out.append(
                        {
                            "clause_id": vfm.get("clause_id"),
                            "variant_id": vfm.get("variant_id"),
                            "layout": "variant",
                            "path": str(vf),
                            "gates": vfm.get("gates", {}),
                        }
                    )
    return out


def _duplicate_conflicts(entries: list[dict]) -> list[dict]:
    """Detect duplicate clause_ids across files — flat-vs-flat, flat-vs-folder."""
    out: list[dict] = []
    by_id: dict[str | None, list[dict]] = defaultdict(list)
    for e in entries:
        # group only flat + variant-container — both represent a single clause id
        if e["layout"] in ("flat", "variant-container"):
            by_id[e["clause_id"]].append(e)
    for clause_id, group in by_id.items():
        if clause_id is None:
            for g in group:
                out.append(
                    {
                        "type": "missing_clause_id",
                        "path": g["path"],
                        "detail": "clause_id is missing or null",
                    }
                )
            continue
        if len(group) > 1:
            out.append(
                {
                    "type": "duplicate_clause_id",
                    "clause_id": clause_id,
                    "paths": [g["path"] for g in group],
                    "detail": (
                        "More than one canonical entry for this clause_id "
                        "(flat file + variant-folder both present, or two flat files)."
                    ),
                }
            )
    return out


def _normalise_gate(gate: dict | str) -> tuple[float | None, float | None, set[str]]:
    """Normalise a single gate-value to (numeric_lower, numeric_upper, enum_values).

    For wildcard ("any") returns full numeric range + empty enum (effectively
    matches everything). For numeric ranges, returns half-open [lower, upper).
    For enum-only gates, numeric range is None / None.
    """
    if gate == "any":
        return (float("-inf"), float("inf"), set())
    if not isinstance(gate, dict):
        return (None, None, set())
    lower = float("-inf")
    upper = float("inf")
    enum: set[str] = set()
    if "eq" in gate:
        v = gate["eq"]
        if isinstance(v, (int, float)):
            return (float(v), float(v) + 1e-9, set())
        return (None, None, {str(v)})
    if "gte" in gate:
        lower = max(lower, float(gate["gte"]))
    if "gt" in gate:
        # treat strict > as slightly larger
        lower = max(lower, float(gate["gt"]) + 1e-9)
    if "lt" in gate:
        upper = min(upper, float(gate["lt"]))
    if "lte" in gate:
        upper = min(upper, float(gate["lte"]) + 1e-9)
    if "any_of" in gate:
        enum |= {str(v) for v in gate["any_of"]}
    # if neither numeric nor enum was set, leave both as wide-open
    if lower == float("-inf") and upper == float("inf") and not enum and "eq" not in gate:
        return (None, None, set())
    return (lower, upper, enum)


def _gates_overlap(a: dict, b: dict) -> bool:
    """Two gates overlap if for every shared key the values can both match.

    Different keys are treated as ANDed across the gate; if either gate
    silently lacks a key the other constrains, that key is wide-open in
    the silent one. We require ALL shared/required keys to overlap.
    """
    keys = set(a.keys()) | set(b.keys())
    for k in keys:
        ga = a.get(k, "any")
        gb = b.get(k, "any")
        la, ua, ea = _normalise_gate(ga)
        lb, ub, eb = _normalise_gate(gb)
        # Enum-only overlap
        if ea and eb:
            if not (ea & eb):
                return False
            continue
        # Mixed enum + numeric — only overlap if BOTH have valid numeric range
        if ea and (lb is not None or ub is not None):
            # enum vs numeric — no way to compare; conservative: assume overlap
            continue
        if eb and (la is not None or ua is not None):
            continue
        if la is None and ua is None and lb is None and ub is None:
            continue
        # Both numeric — half-open interval overlap test
        la = la if la is not None else float("-inf")
        ua = ua if ua is not None else float("inf")
        lb = lb if lb is not None else float("-inf")
        ub = ub if ub is not None else float("inf")
        if not (la < ub and lb < ua):
            return False
    return True


def _overlap_conflicts(entries: list[dict]) -> list[dict]:
    """Detect overlapping gates within the same variant-folder."""
    out: list[dict] = []
    by_clause: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        if e["layout"] == "variant" and e.get("clause_id"):
            by_clause[e["clause_id"]].append(e)
    for clause_id, variants in by_clause.items():
        for i in range(len(variants)):
            for j in range(i + 1, len(variants)):
                a, b = variants[i], variants[j]
                if _gates_overlap(a.get("gates") or {}, b.get("gates") or {}):
                    out.append(
                        {
                            "type": "overlapping_gates",
                            "clause_id": clause_id,
                            "variant_a": a.get("variant_id"),
                            "variant_b": b.get("variant_id"),
                            "paths": [a["path"], b["path"]],
                            "detail": (
                                "Some deal_context could match both variants. "
                                "ABAC pre-filter would pick the first and log a warning."
                            ),
                        }
                    )
    return out


def detect(playbook_dir: Path) -> dict:
    entries = _enumerate_entries(playbook_dir)
    conflicts: list[dict] = []
    conflicts.extend(_duplicate_conflicts(entries))
    conflicts.extend(_overlap_conflicts(entries))
    return {
        "playbook_dir": str(playbook_dir),
        "total_entries": len(entries),
        "total_conflicts": len(conflicts),
        "conflicts": conflicts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("playbook_dir", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    if not args.playbook_dir.is_dir():
        print(f"detect_conflicts: not a directory: {args.playbook_dir}", file=sys.stderr)
        return 2
    report = detect(args.playbook_dir)
    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        if report["total_conflicts"] == 0:
            print(
                f"detect_conflicts: PASS — {report['total_entries']} entries scanned, "
                f"no conflicts"
            )
        else:
            print(
                f"detect_conflicts: {report['total_conflicts']} conflict(s) "
                f"across {report['total_entries']} entries"
            )
            for c in report["conflicts"]:
                if c["type"] == "duplicate_clause_id":
                    print(f"  duplicate clause_id '{c['clause_id']}':")
                    for p in c["paths"]:
                        print(f"    - {p}")
                elif c["type"] == "overlapping_gates":
                    print(
                        f"  overlapping gates in '{c['clause_id']}': "
                        f"{c['variant_a']} vs {c['variant_b']}"
                    )
                    for p in c["paths"]:
                        print(f"    - {p}")
                elif c["type"] == "missing_clause_id":
                    print(f"  missing clause_id: {c['path']}")
    return 0 if report["total_conflicts"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
