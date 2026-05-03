#!/usr/bin/env python3
"""Smoke test for format_lineage_diagram.py.

Runs both modes (column + model) on synthetic JSONL + manifest fixtures.
Pure stdlib — no sqlglot needed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "format_lineage_diagram.py"


def _runner_cmd() -> list[str]:
    if shutil.which("uv"):
        return ["uv", "run", "--quiet", str(SCRIPT)]
    return [sys.executable, str(SCRIPT)]


def write_synthetic_recursive(workdir: Path) -> Path:
    """Same shape as extract_recursive_column_lineage.py output."""
    records = [
        {
            "model_uid": "model.proj.fct_orders",
            "column": "customer_id",
            "ancestors": {
                "model.proj.stg_orders::customer_id": {
                    "source.proj.raw.orders_raw::customer_id": {}
                },
                "model.proj.stg_customers::id": {
                    "source.proj.raw.customers_raw::id": {}
                }
            },
            "descendants": {
                "model.proj.dim_orders_summary::customer_id": {
                    "model.proj.mart_finance::customer_id": {}
                }
            }
        }
    ]
    path = workdir / "recursive.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return path


def write_synthetic_manifest(workdir: Path) -> Path:
    manifest = {
        "nodes": {
            "model.proj.stg_orders": {
                "resource_type": "model",
                "name": "stg_orders",
                "depends_on": {"nodes": ["source.proj.raw.orders_raw"]},
            },
            "model.proj.stg_customers": {
                "resource_type": "model",
                "name": "stg_customers",
                "depends_on": {"nodes": ["source.proj.raw.customers_raw"]},
            },
            "model.proj.fct_orders": {
                "resource_type": "model",
                "name": "fct_orders",
                "depends_on": {"nodes": ["model.proj.stg_orders", "model.proj.stg_customers"]},
            },
            "model.proj.mart_finance": {
                "resource_type": "model",
                "name": "mart_finance",
                "depends_on": {"nodes": ["model.proj.fct_orders"]},
            },
        },
        "sources": {
            "source.proj.raw.orders_raw": {"name": "orders_raw"},
            "source.proj.raw.customers_raw": {"name": "customers_raw"},
        },
    }
    path = workdir / "manifest.json"
    path.write_text(json.dumps(manifest))
    return path


def run(*args: str) -> dict:
    cmd = _runner_cmd() + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    # exit 0 = success, exit 1 = soft error (script printed _error JSON to stdout
    # and returned non-zero so callers can detect it). Anything ≥2 = hard error.
    if proc.returncode >= 2:
        return {"_test_error": f"exit={proc.returncode}: {proc.stderr[:300]}"}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {"_test_error": f"non-JSON: {e}; raw={proc.stdout[:300]}"}


CASES_DESCRIBED: list[tuple[str, callable]] = []


def case(name: str):
    def decorator(fn):
        CASES_DESCRIBED.append((name, fn))
        return fn
    return decorator


@case("Column mode: fct_orders.customer_id ancestors+descendants → ASCII has source markers + Mermaid valid")
def test_column_both(workdir: Path) -> tuple[bool, str]:
    rj = write_synthetic_recursive(workdir)
    out = run("column", "--recursive-jsonl", str(rj),
              "--model", "model.proj.fct_orders",
              "--column", "customer_id",
              "--direction", "both")
    if "_test_error" in out:
        return False, out["_test_error"]
    ascii_s = out.get("ascii", "")
    mermaid_s = out.get("mermaid", "")
    # ASCII checks: should contain target + ancestor + source marker
    if "fct_orders.customer_id" not in ascii_s:
        return False, f"ASCII missing target: {ascii_s[:200]}"
    if "stg_orders.customer_id" not in ascii_s:
        return False, f"ASCII missing ancestor: {ascii_s[:200]}"
    if "*(source)*" not in ascii_s:
        return False, f"ASCII missing source marker: {ascii_s[:200]}"
    if "Ancestors" not in ascii_s or "Descendants" not in ascii_s:
        return False, f"ASCII missing direction headers: {ascii_s[:200]}"
    # Mermaid checks: graph LR + nodes + edges
    if not mermaid_s.startswith("graph LR"):
        return False, f"Mermaid header wrong: {mermaid_s[:100]}"
    if "stg_orders.customer_id" not in mermaid_s:
        return False, f"Mermaid missing ancestor label: {mermaid_s[:200]}"
    if "-->" not in mermaid_s:
        return False, f"Mermaid missing edges"
    return True, "ok"


@case("Column mode: ancestors only — descendants not in output")
def test_column_ancestors_only(workdir: Path) -> tuple[bool, str]:
    rj = write_synthetic_recursive(workdir)
    out = run("column", "--recursive-jsonl", str(rj),
              "--model", "model.proj.fct_orders",
              "--column", "customer_id",
              "--direction", "ancestors")
    if "_test_error" in out:
        return False, out["_test_error"]
    if "Descendants" in out["ascii"]:
        return False, "ascii includes Descendants section despite direction=ancestors"
    if "mart_finance" in out["mermaid"]:
        return False, "mermaid includes descendant despite direction=ancestors"
    if "stg_orders.customer_id" not in out["ascii"]:
        return False, "ancestor missing"
    return True, "ok"


@case("Model mode: fct_orders both directions → ascii lists deps + feeds")
def test_model_both(workdir: Path) -> tuple[bool, str]:
    mp = write_synthetic_manifest(workdir)
    out = run("model", "--manifest", str(mp),
              "--model", "model.proj.fct_orders",
              "--direction", "both",
              "--max-depth", "3")
    if "_test_error" in out:
        return False, out["_test_error"]
    ascii_s = out["ascii"]
    if "depends on" not in ascii_s:
        return False, f"ascii missing 'depends on' section: {ascii_s[:200]}"
    if "feeds into" not in ascii_s:
        return False, f"ascii missing 'feeds into' section: {ascii_s[:200]}"
    if "stg_orders" not in ascii_s:
        return False, f"ascii missing upstream stg_orders: {ascii_s[:200]}"
    if "mart_finance" not in ascii_s:
        return False, f"ascii missing downstream mart_finance: {ascii_s[:200]}"
    if "(src)" not in out["mermaid"]:
        return False, "mermaid should mark sources with (src) suffix"
    return True, "ok"


@case("Column mode: missing record → _error returned")
def test_column_missing(workdir: Path) -> tuple[bool, str]:
    rj = write_synthetic_recursive(workdir)
    out = run("column", "--recursive-jsonl", str(rj),
              "--model", "model.proj.does_not_exist",
              "--column", "missing")
    if "_error" not in out:
        return False, f"expected _error for missing record, got: {out}"
    return True, "ok"


@case("Mermaid output: nodes use safe ids (alphanumeric + underscore)")
def test_mermaid_node_id_safety(workdir: Path) -> tuple[bool, str]:
    rj = write_synthetic_recursive(workdir)
    out = run("column", "--recursive-jsonl", str(rj),
              "--model", "model.proj.fct_orders",
              "--column", "customer_id")
    mermaid_s = out["mermaid"]
    # Check no special characters in node identifiers (line should look like `n_xxx["label"]`)
    import re
    node_def_lines = [l for l in mermaid_s.split("\n") if "[" in l and "]" in l]
    for line in node_def_lines:
        m = re.match(r"\s*(\S+)\[", line)
        if m:
            node_id = m.group(1)
            if not all(c.isalnum() or c == "_" for c in node_id):
                return False, f"unsafe node id: {node_id} in line: {line}"
    return True, "ok"


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="dbt-wiki-diagram-test-"))
    failures = 0
    for i, (name, fn) in enumerate(CASES_DESCRIBED, 1):
        try:
            ok, msg = fn(workdir)
        except Exception as e:
            ok, msg = False, f"raised {type(e).__name__}: {e}"
        status = "OK  " if ok else "FAIL"
        print(f"[{i}/{len(CASES_DESCRIBED)}] {status} {name}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    shutil.rmtree(workdir, ignore_errors=True)
    print(f"\n{len(CASES_DESCRIBED) - failures}/{len(CASES_DESCRIBED)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
