#!/usr/bin/env python3
"""Smoke test for lint_schema_divergence.py.

Run from this directory:

    python3 lint_schema_divergence_test.py

Pure stdlib. Builds throwaway .dbt-wiki fixtures and asserts the gate's
exit code + SCORE, covering: usage error, divergent-undocumented,
documented (per-variant map), column-identical, drop-only over-flag, and
the flag-value positional-collision fix in resolve_wiki_dir.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "lint_schema_divergence.py"


def evidence(d: Path, name: str, cols: list[str]) -> None:
    body = "---\nunique_id: model.p.%s\ncolumns:\n%s\n---\n" % (
        name, "\n".join(f"  - name: {c}" for c in cols))
    (d / "_evidence" / "models" / f"{name}.md").write_text(body, encoding="utf-8")


def knowledge(d: Path, slug: str, derived: list[str], body: str) -> None:
    fm = "---\ntype: knowledge-metric\nderived_from:\n%s\n---\n%s\n" % (
        "\n".join(f"  - model.p.{x}" for x in derived), body)
    (d / "metrics" / f"{slug}.md").write_text(fm, encoding="utf-8")


def build(td: Path) -> Path:
    w = td / ".dbt-wiki"
    (w / "_evidence" / "models").mkdir(parents=True)
    (w / "metrics").mkdir(parents=True)
    return w


def run(args, cwd=None) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(SCRIPT), *args],
                       capture_output=True, text=True, timeout=15, cwd=cwd)
    return p.returncode, p.stdout


def main() -> int:
    fails = 0
    n = 0

    def case(label, ok, detail=""):
        nonlocal fails, n
        n += 1
        print(f"[{n}] {'OK  ' if ok else 'FAIL'} {label}" + (f"  ({detail})" if not ok else ""))
        if not ok:
            fails += 1

    # 1. no --strip-tokens -> usage exit 2
    with tempfile.TemporaryDirectory() as t:
        w = build(Path(t)); evidence(w, "fct_sales", ["a"])
        rc, _ = run([str(w)])
        case("no strip-tokens -> exit 2", rc == 2, f"rc={rc}")

    # 2. nonexistent dir -> exit 2
    rc, _ = run(["/no/such/dir/.dbt-wiki", "--strip-tokens", "online"])
    case("nonexistent dir -> exit 2", rc == 2, f"rc={rc}")

    # 3. divergent twin (rename+drop), UNDOCUMENTED -> exit 1, 0/1
    with tempfile.TemporaryDirectory() as t:
        w = build(Path(t))
        evidence(w, "fct_sales", ["region_code", "channel_code", "revenue", "revenue__gross"])
        evidence(w, "fct_sales_online", ["region", "channel", "revenue"])
        knowledge(w, "sales", ["fct_sales"], "## Calculation\nSUM(revenue) by region_code.")
        rc, out = run([str(w), "--strip-tokens", "online"])
        case("divergent undocumented -> exit 1 + 0/1", rc == 1 and "0/1" in out, f"rc={rc}")

    # 4. same divergence, DOCUMENTED (per-variant line names twin + twin-only col) -> exit 0, 1/1
    with tempfile.TemporaryDirectory() as t:
        w = build(Path(t))
        evidence(w, "fct_sales", ["region_code", "channel_code", "revenue", "revenue__gross"])
        evidence(w, "fct_sales_online", ["region", "channel", "revenue"])
        knowledge(w, "sales", ["fct_sales"],
                  "## Calculation\n| total fct_sales | region_code |\n"
                  "| online fct_sales_online | region |\n")
        rc, out = run([str(w), "--strip-tokens", "online"])
        case("divergent documented -> exit 0 + 1/1", rc == 0 and "1/1" in out, f"rc={rc} out~{out[:60]!r}")

    # 5. column-identical twins -> no divergent family -> exit 0, 0/0
    with tempfile.TemporaryDirectory() as t:
        w = build(Path(t))
        evidence(w, "fct_e", ["a", "b"])
        evidence(w, "fct_e_online", ["a", "b"])
        rc, out = run([str(w), "--strip-tokens", "online"])
        case("identical twins -> exit 0 + 0/0", rc == 0 and "0/0" in out, f"rc={rc}")

    # 6. drop-only twin (no rename/add) -> always flagged even if knowledge names both -> exit 1
    with tempfile.TemporaryDirectory() as t:
        w = build(Path(t))
        evidence(w, "fct_d", ["a", "b", "c"])
        evidence(w, "fct_d_online", ["a", "b"])
        knowledge(w, "d", ["fct_d"], "fct_d and fct_d_online: online drops c.")
        rc, out = run([str(w), "--strip-tokens", "online"])
        case("drop-only over-flag -> exit 1", rc == 1, f"rc={rc}")

    # 7. positional-collision fix: strip-token value 'online' is also a real dir in cwd;
    #    resolve_wiki_dir must NOT mistake it for the wiki dir.
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        (tp / "online").mkdir()                       # decoy dir matching the strip-token value
        w = build(tp / "proj")
        evidence(w, "fct_sales", ["region_code", "revenue", "revenue__gross"])
        evidence(w, "fct_sales_online", ["region", "revenue"])
        # value 'online' precedes the positional wiki path; old code would grab online/.dbt-wiki
        rc, out = run([str(w.resolve()), "--strip-tokens", "online"], cwd=str(tp))
        case("flag-value not mistaken for wiki dir -> processes wiki (exit 1, not 2)",
             rc == 1, f"rc={rc} (2=misresolved to ./online)")

    print(f"\n{n - fails}/{n} passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
