#!/usr/bin/env python3
"""Validate dbt model header conventions (dbt-model-style skill).

Always-on, deterministic checks (no SQL parsing):

  1. HEADER     — first /* ... */ block holds a `---` YAML frontmatter that
                  parses, is layer-appropriately complete, and has non-empty `grain`.
  2. SHAPE      — `keys` is `{primary: [...], join?: [...]}`; `related` is a list
                  of `{table, join_on, adds?}`. Catches malformed/half-filled
                  entries. (Field is `join_on`, not `on` — bare `on` is a YAML 1.1
                  reserved boolean and would parse to True.)
  3. COMMENTS   — every /* has a matching */ (an unclosed /* silently eats the
                  rest of the file on Redshift and breaks `dbt run`).
  4. MATERIALIZED — flags the `materialization` typo (valid dbt key is `materialized`).

Opt-in referential check (needs a dbt manifest, `--manifest <path>`):

  5. REFERENCE  — every `related[].table` and `sources[]` entry resolves to a real
                  model/source in the manifest (catches renamed/deleted/typo'd
                  tables — the `related` staleness problem).

Required frontmatter keys are layer-tiered: every model needs BASE_REQUIRED;
consumer-facing layers (intermediate / marts / dashboard) also need
CONSUMER_EXTRA. Layer is read from a `layer:` frontmatter value, else the path /
filename prefix (stg_ vs int_/mart_/dash_), else treated as base-only.

Without --manifest the validator stays zero-config + project-agnostic (PyYAML
only). Adopters wire it into pre-commit / CI / a dbt step. Tune the layer-tiered
key lists + classification below to match your project.

Usage:
    python validate_header.py path/to/model.sql ...
    python validate_header.py models/                       # recurse dir for *.sql
    python validate_header.py "models/**/*.sql"             # glob (quote it)
    python validate_header.py --manifest target/manifest.json models/

Exit code: 0 = all clean, 1 = at least one violation, 2 = usage / env error.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

# --- (adapt) layer-tiered required frontmatter keys ---------------------------
# Every layer must carry these:
BASE_REQUIRED = ["title", "summary", "grain", "sources"]
# Consumer-facing layers (intermediate / marts / dashboard) must also carry these
# (they get queried + JOINed by analysts/BI/MCP; staging views usually don't):
CONSUMER_EXTRA = ["purpose", "keys"]

# Layer classification — explicit `layer:` frontmatter wins, else path/dir, else
# filename prefix, else lenient (base-only).
CONSUMER_LAYERS = {"intermediate", "interm", "mart", "marts", "dashboard", "dash"}
STAGING_LAYERS = {"staging", "stg"}
CONSUMER_PREFIXES = ("int_", "mart_", "dash_", "fct_", "dim_")
STAGING_PREFIXES = ("stg_",)
CONSUMER_DIRS = ("/intermediate/", "/interm/", "/marts/", "/dash/")
STAGING_DIRS = ("/staging/",)

BLOCK_RE = re.compile(r"/\*(.*?)\*/", re.DOTALL)
FENCE = "---"


def _is_consumer(path: str, data: dict) -> bool:
    """True if the model is a consumer-facing layer (stricter requirements)."""
    layer = str(data.get("layer", "")).strip().lower()
    if layer in CONSUMER_LAYERS:
        return True
    if layer in STAGING_LAYERS:
        return False
    p = path.replace(os.sep, "/").lower()
    base = os.path.basename(p)
    if any(d in p for d in STAGING_DIRS) or base.startswith(STAGING_PREFIXES):
        return False
    if any(d in p for d in CONSUMER_DIRS) or base.startswith(CONSUMER_PREFIXES):
        return True
    return False  # unknown (e.g. expt_, seeds) → base-only, avoid false alarms


def _first_block(content: str) -> str | None:
    """Return the inner text of the first /* ... */ block, or None."""
    m = BLOCK_RE.search(content)
    return m.group(1) if m else None


def _frontmatter_yaml(block_inner: str) -> str | None:
    """Extract the text between the first pair of `---` fence lines."""
    lines = block_inner.splitlines()
    fences = [i for i, ln in enumerate(lines) if ln.strip() == FENCE]
    if len(fences) < 2:
        return None
    return "\n".join(lines[fences[0] + 1 : fences[1]])


def parse_frontmatter(content: str, yaml_mod) -> tuple[dict | None, list[str]]:
    """Parse the header frontmatter. Returns (data, header_errors)."""
    inner = _first_block(content)
    if inner is None:
        return None, ["HEADER: no /* ... */ header block found"]
    fm_text = _frontmatter_yaml(inner)
    if fm_text is None:
        return None, ["HEADER: no `---` YAML frontmatter inside the first /* */ block"]
    try:
        data = yaml_mod.safe_load(fm_text)
    except yaml_mod.YAMLError as exc:
        first = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        return None, [f"HEADER: frontmatter is not parseable YAML ({first})"]
    if not isinstance(data, dict):
        return None, ["HEADER: frontmatter did not parse to a key:value mapping"]
    return data, []


def check_required(data: dict, path: str) -> list[str]:
    errs: list[str] = []
    consumer = _is_consumer(path, data)
    required = BASE_REQUIRED + (CONSUMER_EXTRA if consumer else [])
    missing = [k for k in required if k not in data]
    if missing:
        tier = "consumer-layer" if consumer else "base"
        errs.append(f"HEADER: missing required frontmatter key(s) [{tier}]: {', '.join(missing)}")
    if "grain" in data and not str(data.get("grain") or "").strip():
        errs.append("HEADER: `grain` is present but empty — state what one row represents")
    return errs


def _is_str_list(v) -> bool:
    return isinstance(v, list) and bool(v) and all(isinstance(x, str) for x in v)


def check_shapes(data: dict) -> list[str]:
    """SHAPE — `keys` and `related` are well-formed (when present)."""
    errs: list[str] = []

    if "keys" in data:
        k = data["keys"]
        if not isinstance(k, dict):
            errs.append("SHAPE: `keys` must be a mapping with `primary` (+ optional `join`)")
        else:
            if "primary" not in k:
                errs.append("SHAPE: `keys.primary` is required")
            elif not _is_str_list(k["primary"]):
                errs.append("SHAPE: `keys.primary` must be a non-empty list of column names")
            if "join" in k and not _is_str_list(k["join"]):
                errs.append("SHAPE: `keys.join` must be a list of column names")

    if "related" in data:
        r = data["related"]
        if not isinstance(r, list):
            errs.append("SHAPE: `related` must be a list of { table, join_on, adds? } entries")
        else:
            for i, item in enumerate(r):
                if not isinstance(item, dict):
                    errs.append(f"SHAPE: related[{i}] must be a mapping with `table` + `join_on`")
                    continue
                if not isinstance(item.get("table"), str) or not item.get("table"):
                    errs.append(f"SHAPE: related[{i}] missing string `table`")
                # `join_on`, not `on`: bare `on` is a YAML 1.1 reserved boolean.
                join_on = item.get("join_on")
                if not (isinstance(join_on, str) and join_on) and not _is_str_list(join_on):
                    errs.append(f"SHAPE: related[{i}] `join_on` must be a column name or non-empty list")
                if "adds" in item and not isinstance(item["adds"], str):
                    errs.append(f"SHAPE: related[{i}] `adds` must be a string")
    return errs


def check_references(data: dict, index: dict) -> list[str]:
    """REFERENCE — related/sources tables exist in the manifest (opt-in)."""
    errs: list[str] = []
    known = index["known"]

    related = data.get("related")
    if isinstance(related, list):
        for item in related:
            if isinstance(item, dict):
                table = item.get("table")
                if isinstance(table, str) and table and table not in known:
                    errs.append(f"REFERENCE: related table not found in manifest: {table}")

    sources = data.get("sources")
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, str) and s and s not in known:
                errs.append(f"REFERENCE: source not found in manifest: {s}")
    return errs


def load_manifest(path: str) -> dict:
    """Build {known: set(names)} of models/seeds/snapshots/sources from a dbt manifest."""
    with open(path, encoding="utf-8") as fh:
        m = json.load(fh)
    if not isinstance(m, dict) or "nodes" not in m:
        raise ValueError("not a dbt manifest (no `nodes` key)")
    known: set[str] = set()
    for node in (m.get("nodes") or {}).values():
        if node.get("resource_type") in {"model", "seed", "snapshot"}:
            name = node.get("name")
            if name:
                known.add(name)
    for src in (m.get("sources") or {}).values():
        name, sname = src.get("name"), src.get("source_name")
        if name:
            known.add(name)
            if sname:
                known.add(f"{sname}.{name}")
    return {"known": known}


def validate_file(path: str, yaml_mod, manifest_index: dict | None) -> list[str]:
    try:
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return [f"FILE: cannot read ({exc})"]

    errs: list[str] = []
    data, header_errs = parse_frontmatter(content, yaml_mod)
    errs += header_errs
    if data is not None:
        errs += check_required(data, path)
        errs += check_shapes(data)
        if manifest_index is not None:
            errs += check_references(data, manifest_index)
    errs += check_comments(content)
    errs += check_materialized(content)
    return errs


def check_comments(content: str) -> list[str]:
    # Remove matched block comments; any leftover marker = unbalanced.
    stripped = BLOCK_RE.sub("", content)
    if "/*" in stripped:
        return ["COMMENTS: unclosed /* block comment (missing */) — will break Redshift parsing"]
    if "*/" in stripped:
        return ["COMMENTS: stray */ with no matching /*"]
    return []


def check_materialized(content: str) -> list[str]:
    if re.search(r"\bmaterialization\b", content):
        return ["MATERIALIZED: found `materialization` — the valid dbt config key is `materialized`"]
    return []


def _expand(args: list[str]) -> list[str]:
    files: list[str] = []
    for arg in args:
        if any(c in arg for c in "*?["):
            files.extend(glob.glob(arg, recursive=True))
        elif os.path.isdir(arg):
            for root, _, names in os.walk(arg):
                files.extend(os.path.join(root, n) for n in names if n.endswith(".sql"))
        else:
            files.append(arg)
    # de-dupe, keep only .sql, stable order
    seen, out = set(), []
    for f in files:
        if f.endswith(".sql") and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _parse_argv(argv: list[str]) -> tuple[str | None, list[str]]:
    """Split off `--manifest <path>` / `--manifest=<path>`; return (manifest, paths)."""
    manifest, paths, i = None, [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--manifest":
            i += 1
            manifest = argv[i] if i < len(argv) else None
        elif a.startswith("--manifest="):
            manifest = a.split("=", 1)[1]
        else:
            paths.append(a)
        i += 1
    return manifest, paths


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2

    try:
        import yaml  # PyYAML — ships with dbt-core
    except ImportError:
        print("error: PyYAML not found. Install with `pip install pyyaml`.", file=sys.stderr)
        return 2

    manifest_path, paths = _parse_argv(argv)
    manifest_index = None
    if manifest_path:
        try:
            manifest_index = load_manifest(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: cannot load manifest '{manifest_path}': {exc}", file=sys.stderr)
            return 2

    files = _expand(paths)
    if not files:
        print("error: no .sql files matched the given paths.", file=sys.stderr)
        return 2

    total = 0
    for path in files:
        errs = validate_file(path, yaml, manifest_index)
        if errs:
            total += len(errs)
            print(f"✗ {path}")
            for e in errs:
                print(f"    {e}")

    n = len(files)
    mode = " (+manifest references)" if manifest_index is not None else ""
    if total:
        print(f"\n{total} violation(s) across {n} file(s){mode}.")
        return 1
    print(f"✓ {n} file(s) clean{mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
