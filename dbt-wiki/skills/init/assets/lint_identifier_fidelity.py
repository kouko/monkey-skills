#!/usr/bin/env python3
"""
lint_identifier_fidelity.py — dbt-wiki knowledge-layer build-time gate.

Detects "phantom column" identifier errors: a distilled knowledge page
(`entities/` `metrics/` `concepts/`) cites a `model.column` in its `## Fields`
table (or anywhere in its body) that DOES NOT EXIST in that model's
manifest-extracted column list. The failure mode this catches is the worst kind
of knowledge defect for a SQL-generating consumer: it emits a query referencing
a non-existent column, which fails at execution — and unlike a value-domain gap,
nothing in the page looks wrong on inspection.

Observed real instances (the class this exists to catch):
  • a `__daily` suffix dropped         (cites `sales`, real `sales__daily`)
  • an invented prefix                 (cites `effective_start_date`, real `start_date`)
  • a bare name for a split column      (cites `plan_length`, real `plan_present_length` / `plan_product_length`)
Root cause: distillation paraphrased an identifier instead of copying it
verbatim from the evidence layer.

Two roles, one tool (mirrors lint_schema_divergence.py):
  • BASELINE — count phantom-column citations before/after a distillation change.
  • GATE — exit non-zero when any knowledge page cites a column that the
    manifest-extracted evidence does not contain (CI / review / post-init).

Authority + false-positive guard: a model's column set is read from its
evidence page `columns:` frontmatter. Citations are verified ONLY against
models whose `columns_extracted_via: sqlglot` (a complete output-column set).
Models extracted `schema_yml_only` or `failed` have a PARTIAL column list, so
citations to them are SKIPPED (reported as "unverifiable", never as violations)
to avoid false positives. Citations whose model isn't an evidence model at all
(sources, uncaptured models) are likewise skipped.

Deterministic; pure stdlib; reads the generated `.dbt-wiki/` only. Never
connects to a warehouse or reads the dbt project.

Usage:
  python lint_identifier_fidelity.py [WIKI_DIR] [--json]
  # WIKI_DIR defaults to <git-root>/.dbt-wiki, else ./.dbt-wiki
  # exit 0 = clean; exit 1 = phantom-column citations found (gate)
"""
import os
import re
import sys
import json
import glob
import subprocess

# A dbt identifier segment: snake_case, allow upper for non-lowercasing warehouses.
_REF = re.compile(r"`([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)`")
_NAME = re.compile(r'^\s*-\s*name:\s*"?([A-Za-z0-9_]+)"?\s*$')


def resolve_wiki_dir(argv):
    positional = [a for a in argv[1:] if not a.startswith("--")]
    if positional:
        cand = positional[0]
        return cand if cand.endswith(".dbt-wiki") else os.path.join(cand, ".dbt-wiki")
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True).strip()
        if root and os.path.isdir(os.path.join(root, ".dbt-wiki")):
            return os.path.join(root, ".dbt-wiki")
    except Exception:
        pass
    return ".dbt-wiki"


def _frontmatter(text):
    """Return the text between the first two '---' fences (or '' if none)."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def load_evidence_models(wiki_dir):
    """{model_name: {"cols": set, "via": str}} from _evidence/models/*.md."""
    models = {}
    for path in glob.glob(os.path.join(wiki_dir, "_evidence", "models", "*.md")):
        text = open(path, encoding="utf-8").read()
        fm = _frontmatter(text)
        if not fm:
            continue
        uid = via = None
        cols = set()
        in_cols = False
        for line in fm.splitlines():
            if line.startswith("unique_id:"):
                uid = line.split(":", 1)[1].strip().split(".")[-1]
            elif line.startswith("columns_extracted_via:"):
                via = line.split(":", 1)[1].strip()
            elif line.startswith("columns:"):
                in_cols = True
            elif in_cols:
                m = _NAME.match(line)
                if m:
                    cols.add(m.group(1))
                elif line and not line[0].isspace():
                    in_cols = False  # left the columns: block
        if uid:
            entry = models.setdefault(uid, {"cols": set(), "via": via})
            entry["cols"] |= cols
            # prefer the strongest extraction status seen for this name
            if via == "sqlglot":
                entry["via"] = "sqlglot"
            elif entry["via"] is None:
                entry["via"] = via
    return models


def lint(wiki_dir):
    models = load_evidence_models(wiki_dir)
    violations = []      # (page, "model.column")
    unverifiable = 0     # citations to non-sqlglot or unknown models
    checked = ok = 0
    seen = set()
    for sub in ("entities", "metrics", "concepts"):
        for path in glob.glob(os.path.join(wiki_dir, sub, "*.md")):
            page = os.path.relpath(path, wiki_dir)
            text = open(path, encoding="utf-8").read()
            for model, col in _REF.findall(text):
                key = (page, model, col)
                if key in seen:
                    continue
                seen.add(key)
                ent = models.get(model)
                if ent is None or ent["via"] != "sqlglot":
                    unverifiable += 1
                    continue
                checked += 1
                if col in ent["cols"]:
                    ok += 1
                else:
                    violations.append((page, f"{model}.{col}"))
    return {
        "wiki_dir": wiki_dir,
        "evidence_models": len(models),
        "refs_checked": checked,
        "refs_ok": ok,
        "refs_unverifiable": unverifiable,
        "violations": [{"page": p, "ref": r} for p, r in sorted(violations)],
    }


def main():
    argv = sys.argv
    as_json = "--json" in argv
    wiki_dir = resolve_wiki_dir(argv)
    if not os.path.isdir(wiki_dir):
        sys.stderr.write(f"No .dbt-wiki/ at {wiki_dir}\n")
        return 2
    result = lint(wiki_dir)
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        v = result["violations"]
        print(f"identifier-fidelity: {result['refs_checked']} cited columns checked "
              f"against {result['evidence_models']} sqlglot evidence models")
        print(f"  ✓ exists: {result['refs_ok']}   "
              f"✗ phantom: {len(v)}   "
              f"(skipped {result['refs_unverifiable']} unverifiable: non-sqlglot / non-evidence)")
        if v:
            print("\n=== PHANTOM COLUMN CITATIONS (knowledge cites a column the model lacks) ===")
            cur = None
            for item in v:
                if item["page"] != cur:
                    cur = item["page"]
                    print(f"\n{cur}:")
                print(f"    ✗ {item['ref']}")
            print("\nFix: correct each to the manifest-true identifier (see the model's "
                  "evidence page `columns:` / `_relations.md`), then re-run.")
        else:
            print("✓ no phantom-column citations — every verifiable cited column exists.")
    return 1 if result["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
