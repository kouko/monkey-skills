#!/usr/bin/env python3
"""Self-contained synthetic test for lint_identifier_fidelity.py. No real
project, no network. Builds a tiny .dbt-wiki/ in a temp dir and asserts the
linter catches a phantom-column citation while respecting the guards."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_identifier_fidelity as L


def _evidence(model, via, cols):
    names = "\n".join(f'  - name: "{c}"\n    type: null' for c in cols)
    return (
        "---\n"
        f"unique_id: model.proj.{model}\n"
        "type: model\n"
        f"columns_extracted_via: {via}\n"
        "columns:\n"
        f"{names}\n"
        "---\n\n## Description\nsynthetic\n"
    )


def _build(tmp):
    wiki = os.path.join(tmp, ".dbt-wiki")
    for d in ("_evidence/models", "entities", "metrics", "concepts"):
        os.makedirs(os.path.join(wiki, d))
    # sqlglot model with a full column set
    open(f"{wiki}/_evidence/models/int_daily.md", "w").write(
        _evidence("int_daily", "sqlglot", ["sales__daily", "data_date"]))
    # schema_yml_only model — partial columns, citations to it must be SKIPPED
    open(f"{wiki}/_evidence/models/int_partial.md", "w").write(
        _evidence("int_partial", "schema_yml_only", ["only_declared"]))
    # a knowledge page with: 1 good, 1 phantom, 1 unverifiable(non-sqlglot),
    # 1 non-evidence-model ref, and a markdown link that must NOT be parsed as model.col
    open(f"{wiki}/entities/thing.md", "w").write(
        "---\ntitle: Thing\n---\n\n## Fields\n"
        "| f | m | ev |\n|---|---|---|\n"
        "| `s` | ok | `int_daily.sales__daily` |\n"           # OK
        "| `bad` | phantom | `int_daily.sales` |\n"          # PHANTOM (missing __daily)
        "| `p`   | skip | `int_partial.real_but_undeclared` |\n"  # unverifiable (schema_yml_only)
        "| `s`   | skip | `some_source.col` |\n"              # unverifiable (non-evidence)
        "\nSee [other](../metrics/other.md) for more.\n")      # link, not a model.col
    return wiki


def main():
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        if cond:
            passed += 1
            print(f"[OK] {name}")
        else:
            print(f"[FAIL] {name}")

    with tempfile.TemporaryDirectory() as tmp:
        wiki = _build(tmp)
        r = L.lint(wiki)
        refs = {v["ref"] for v in r["violations"]}

        check("2 evidence models loaded", r["evidence_models"] == 2)
        check("good ref counted as checked+ok", r["refs_ok"] == 1)
        check("phantom int_daily.sales flagged", "int_daily.sales" in refs)
        check("exactly one violation", len(r["violations"]) == 1)
        check("schema_yml_only citation NOT flagged",
              "int_partial.real_but_undeclared" not in refs)
        check("non-evidence citation NOT flagged",
              "some_source.col" not in refs)
        check("two unverifiable skipped (partial + source)",
              r["refs_unverifiable"] == 2)
        check("markdown link not parsed as a column ref",
              not any("other" in v["ref"] for v in r["violations"]))

    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
