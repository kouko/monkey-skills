#!/usr/bin/env python3
"""Smoke test for build_relations_anchor.py.

Run from this directory:
    python3 build_relations_anchor_test.py

Invokes the script via `uv run` (the script declares pyyaml via PEP 723).
Builds a tiny synthetic .dbt-wiki/_evidence/ + bundle knowledge/ in a tempdir,
runs the anchor generator offline and with a catalog dump, and asserts the
emitted _relations.md.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile, os
from pathlib import Path

SCRIPT = Path(__file__).parent / "build_relations_anchor.py"

EVIDENCE_MODELS = {
    "foo.md": """---
unique_id: model.proj.foo
type: model
schema: dbt_prod
columns:
  - name: a
    type: null
    description: "col a meaning"
  - name: b
    type: null
---
## Description
foo
""",
    "bar.md": """---
unique_id: model.proj.bar
type: model
schema: dbt_prod__marts
columns:
  - name: x
    type: null
---
## Description
bar
""",
}
EVIDENCE_SOURCES = {
    "raw__t.md": """---
unique_id: source.proj.raw.t
type: source
source_name: raw
table_name: t
schema: raw_schema
columns:
  - name: s
---
## Description
t
""",
}
KNOWLEDGE = {
    "k1.md": """---
type: knowledge-entity
title: K1
derived_from:
  - model.proj.foo
  - model.proj.bar
---
body
""",
    "k2.md": """---
type: knowledge-metric
title: K2
derived_from:
  - model.proj.foo
---
body
""",
    "INDEX.md": "# index (must be ignored)\n",
}
CATALOG = {"data": [
    {"table_schema": "dbt_prod", "table_name": "foo", "column_name": "a", "data_type": "integer"},
    {"table_schema": "dbt_prod", "table_name": "foo", "column_name": "b", "data_type": "character varying"},
]}


def setup(tmp: Path):
    ev = tmp / ".dbt-wiki" / "_evidence"
    (ev / "models").mkdir(parents=True); (ev / "sources").mkdir(parents=True)
    for n, c in EVIDENCE_MODELS.items(): (ev / "models" / n).write_text(c, encoding="utf-8")
    for n, c in EVIDENCE_SOURCES.items(): (ev / "sources" / n).write_text(c, encoding="utf-8")
    k = tmp / "bundle" / "knowledge"; k.mkdir(parents=True)
    for n, c in KNOWLEDGE.items(): (k / n).write_text(c, encoding="utf-8")
    (tmp / "catalog.json").write_text(json.dumps(CATALOG), encoding="utf-8")
    return ev, k


def run(ev, k, out, catalog=None):
    cmd = ["uv", "run", str(SCRIPT), "--evidence-dir", str(ev), "--knowledge-dir", str(k), "--out", str(out)]
    if catalog: cmd += ["--catalog", str(catalog)]
    return subprocess.run(cmd, capture_output=True, text=True)


CHECKS = []
def check(name):
    def deco(fn): CHECKS.append((name, fn)); return fn
    return deco


@check("offline run exits 0 + emits _relations.md")
def c1(ctx):
    return ctx["off"].returncode == 0 and ctx["out"].exists(), f"rc={ctx['off'].returncode} err={ctx['off'].stderr[-200:]}"

@check("cited model foo -> dbt_prod.foo with cols a,b + description")
def c2(ctx):
    t = ctx["out"].read_text(encoding="utf-8")
    return ("`dbt_prod.foo`" in t and "`a`" in t and "`b`" in t and "col a meaning" in t), t[:300]

@check("marts schema preserved (bar -> dbt_prod__marts.bar)")
def c3(ctx):
    return "`dbt_prod__marts.bar`" in ctx["out"].read_text(encoding="utf-8"), "missing marts schema"

@check("un-cited source raw.t is excluded")
def c4(ctx):
    return "raw_schema.t" not in ctx["out"].read_text(encoding="utf-8"), "uncited relation leaked in"

@check("INDEX.md is not treated as a knowledge page")
def c5(ctx):
    # k1+k2 cite foo,bar only; if INDEX parsed, nothing breaks but ensure only foo/bar present
    t = ctx["out"].read_text(encoding="utf-8")
    return t.count("### ") == 2, f"expected 2 relations, got {t.count('### ')}"

@check("--catalog overrides types (foo.a integer, foo.b character varying)")
def c6(ctx):
    out2 = ctx["tmp"] / "rel2.md"
    p = run(ctx["ev"], ctx["k"], out2, ctx["tmp"] / "catalog.json")
    if p.returncode != 0: return False, f"catalog run rc={p.returncode} {p.stderr[-200:]}"
    t = out2.read_text(encoding="utf-8")
    return ("`a` *integer*" in t and "`b` *character varying*" in t), t[:400]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d); ev, k = setup(tmp); out = tmp / "rel.md"
        off = run(ev, k, out)
        ctx = {"tmp": tmp, "ev": ev, "k": k, "out": out, "off": off}
        for i, (name, fn) in enumerate(CHECKS, 1):
            try: ok, msg = fn(ctx)
            except Exception as e: ok, msg = False, f"exception: {e}"
            print(f"[{i}/{len(CHECKS)}] {'OK  ' if ok else 'FAIL'} {name}")
            if not ok: print(f"         {msg}"); failures += 1
    print(f"\n{len(CHECKS) - failures}/{len(CHECKS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
