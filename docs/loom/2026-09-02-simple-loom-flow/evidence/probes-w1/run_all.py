#!/usr/bin/env python3
"""Run every W1 adversary probe (p01..p13 + x1a/x1b/x1c/x2) and print a
table. `EXPECTED: escaped-by-design` probes (p06, p10, battery-B inside
p12) are records, not gates -- they always exit 0 and are shown as such,
never counted as an escape. Any other probe exiting non-zero is a real
escape and fails the run.

Usage: python3 run_all.py [selector ...]
  no args        -- run every probe file below, in order
  one or more     -- run only the named probe modules (e.g. `p04` or
                     `p04_probe_command_true.py`), matched by stem prefix
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

PROBES = [
    "p01_no_dispatch_record.py",
    "p02_after_task_no_reason.py",
    "p03_review_only_head_rename.py",
    "p04_probe_command_true.py",
    "p05_needs_design_untracked.py",
    "p06_question_type_what.py",
    "p07_second_vendor_codex_missing.py",
    "p08_contract_require_minor.py",
    "p09_replay_stale_review.py",
    "p10_forged_dispatch_ids.py",
    "p11_kickoff_narrows_surfaces.py",
    "p12_push_command_detection.py",
    "p13_race_review_json.py",
    "x1a_masked_exit_semicolon_space.py",
    "x1b_masked_exit_semicolon_nospace.py",
    "x1c_control_bare_failing_probe.py",
    "x2_trailer_on_docs_commit_not_code.py",
]


def select(argv: list[str]) -> list[str]:
    if not argv:
        return PROBES
    chosen = []
    for name in argv:
        stem = name.removesuffix(".py")
        matches = [p for p in PROBES if p == name or Path(p).stem == stem
                  or Path(p).stem.startswith(stem)]
        if not matches:
            raise SystemExit(f"no probe matches selector {name!r}")
        chosen.extend(matches)
    # de-dupe, keep order
    seen = set()
    return [p for p in chosen if not (p in seen or seen.add(p))]


def main(argv: list[str]) -> int:
    targets = select(argv)
    rows = []
    real_escapes = 0
    for name in targets:
        proc = subprocess.run([sys.executable, str(HERE / name)],
                              capture_output=True, text=True)
        out = (proc.stdout + proc.stderr).strip()
        last_line = out.splitlines()[-1] if out else ""
        if last_line.startswith("EXPECTED:"):
            status = "EXPECTED"
        elif proc.returncode == 0:
            status = "CAUGHT"
        else:
            status = "ESCAPED"
            real_escapes += 1
        rows.append((name, status, proc.returncode, last_line))

    width = max(len(name) for name, *_ in rows)
    for name, status, rc, note in rows:
        print(f"{name:<{width}}  {status:<8} rc={rc}  {note[:160]}")

    print(f"\n{real_escapes} real escape(s) / {len(rows)} probes run "
          f"({sum(1 for _, s, *_ in rows if s == 'EXPECTED')} EXPECTED, "
          f"{sum(1 for _, s, *_ in rows if s == 'CAUGHT')} CAUGHT).")
    return 1 if real_escapes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
