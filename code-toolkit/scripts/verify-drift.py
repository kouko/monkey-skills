#!/usr/bin/env python3
"""CI gate: verify every routed functional copy is byte-identical to the
expected payload *(SSOT header + canonical content)*.

- Exit 0: every functional copy matches expected.
- Exit 1: drift, missing functional copy, or missing canonical. Each
  failure is printed with an md5 fingerprint and a unified diff (≤50 lines)
  so the failure is actionable in CI logs.
- Exit 2: setup error (canonical root absent).

Repair locally with ``python3 code-toolkit/scripts/distribute.py``.

Pure stdlib (P1-E). Imports the routing table + expected-payload helper
from ``distribute.py`` so the two scripts cannot disagree on what
"expected" means.
"""
from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    AGENT_BASELINE_TARGETS,
    CODE_TEAM_ROOT,
    REPO_ROOT,
    ROOT,
    ROUTE,
    expected_agent_text,
    expected_payload,
)


def _md5(data: bytes) -> str:
    # usedforsecurity=False keeps this working on FIPS-140 systems — the md5
    # here is a fingerprint for the drift report, not a security primitive.
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def _unified_diff(expected: bytes, actual: bytes, label: str) -> list[str]:
    exp_lines = expected.decode("utf-8", errors="replace").splitlines()
    act_lines = actual.decode("utf-8", errors="replace").splitlines()
    out = list(
        difflib.unified_diff(
            exp_lines,
            act_lines,
            fromfile=f"expected ({label})",
            tofile=f"on-disk ({label})",
            lineterm="",
        )
    )
    max_lines = 50
    if len(out) > max_lines:
        out = out[:max_lines] + [
            f"... ({len(out) - max_lines} more diff lines truncated)"
        ]
    return out


def main() -> int:
    if not CODE_TEAM_ROOT.is_dir():
        print(
            f"ERROR: code-team canonical root not found: "
            f"{CODE_TEAM_ROOT.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 2

    failures: list[str] = []
    checked = 0
    for canonical_subpath, dests in ROUTE.items():
        src = CODE_TEAM_ROOT / canonical_subpath
        if not src.is_file():
            failures.append(
                f"MISSING-CANONICAL  code-team:{canonical_subpath}"
            )
            continue
        expected = expected_payload(canonical_subpath)
        for rel_dst in dests:
            dst = ROOT / rel_dst
            if not dst.is_file():
                failures.append(f"MISSING            code-toolkit/{rel_dst}")
                continue
            actual = dst.read_bytes()
            checked += 1
            if actual == expected:
                continue
            failures.append(
                f"DRIFT              code-toolkit/{rel_dst}\n"
                f"    expected: code-team:{canonical_subpath} + SSOT header\n"
                f"    md5(expected) = {_md5(expected)}\n"
                f"    md5(on-disk)  = {_md5(actual)}"
            )
            for line in _unified_diff(expected, actual, rel_dst):
                failures.append(f"    {line}")

    # ─── Agent in-file injection drift check ─────────────────────────
    # Each routed agent file must carry the BEGIN/END marker(s) for the
    # injection block(s) it should embed. `expected_agent_text` rebuilds
    # every applicable block from SSOT (baseline for all routed agents,
    # reviewer-discipline for reviewer agents only). Role-contract content
    # outside the blocks is unique per agent and not compared.
    injection_checked = 0
    for agent_rel in AGENT_BASELINE_TARGETS:
        dst = ROOT / agent_rel
        if not dst.is_file():
            failures.append(f"MISSING-AGENT      code-toolkit/{agent_rel}")
            continue
        try:
            expected_text = expected_agent_text(agent_rel)
        except ValueError as e:
            failures.append(f"INJECTION-MARKERS  code-toolkit/{agent_rel}: {e}")
            continue
        expected_bytes = expected_text.encode("utf-8")
        actual_bytes = dst.read_bytes()
        injection_checked += 1
        if actual_bytes == expected_bytes:
            continue
        failures.append(
            f"INJECTION-DRIFT    code-toolkit/{agent_rel}\n"
            f"    expected: role-contract + SSOT injection blocks "
            f"(baseline + reviewer-discipline where applicable)\n"
            f"    md5(expected) = {_md5(expected_bytes)}\n"
            f"    md5(on-disk)  = {_md5(actual_bytes)}"
        )
        for line in _unified_diff(expected_bytes, actual_bytes, agent_rel):
            failures.append(f"    {line}")

    if failures:
        for line in failures:
            print(line)
        print(
            f"\nFAIL: drift detected "
            f"(checked {checked} functional-copy pairs "
            f"+ {injection_checked} agent injection block file(s))."
            f"\nFix: python3 code-toolkit/scripts/distribute.py"
        )
        return 1
    print(
        f"OK: all {checked} functional copies match expected "
        f"(canonical + SSOT header) "
        f"and all {injection_checked} agent file(s) carry valid "
        f"injection blocks (baseline + reviewer-discipline where applicable)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
