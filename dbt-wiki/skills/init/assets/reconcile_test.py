# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Smoke test for reconcile.py — synthetic, offline, no specifics."""
import sys
import json
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reconcile import resolve_target, main  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


def page(p, fm):
    p.write_text("---\n" + fm + "\n---\n\nbody\n", encoding="utf-8")


# 1-2. target resolution
check("cross-folder target", resolve_target("entities", "../concepts/x.md") == ("concepts", "x.md"))
check("bare slug -> sibling", resolve_target("entities", "order.md") == ("entities", "order.md"))

# 3. ownership PRESENT: reserved-miss warns, dangling stubs, contamination flagged
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    for f in ("entities", "metrics", "concepts", "_internal"):
        (wiki / f).mkdir()
    (wiki / "_internal" / "ownership.json").write_text(json.dumps({
        "reserved_entities": {"customer": "billing"},
        "domains": {"billing": ["model.p.stg_a", "model.p.dim_a"], "sales": ["model.p.fct_b"]},
    }), encoding="utf-8")
    # page references a reserved entity with no page -> WARNING (no stub)
    page(wiki / "entities" / "order.md",
         'title: Order\nrelationships:\n  - type: depends_on\n    target: ../entities/customer.md\n'
         'derived_from: [model.p.stg_a, model.p.fct_b]')  # spans billing+sales -> contamination
    # page references a non-reserved missing concept -> seed stub
    page(wiki / "entities" / "invoice.md",
         'title: Invoice\nrelationships:\n  - type: depends_on\n    target: ../concepts/tax-rule.md\n'
         'derived_from: [model.p.dim_a]')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(wiki, "2026-01-01")
    out = buf.getvalue()
    check("rc 0 (ownership present)", rc == 0)
    check("reserved miss -> warning, no stub", "customer" in out and not (wiki / "entities" / "customer.md").exists())
    check("dangling -> seed stub written", (wiki / "concepts" / "tax-rule.md").exists())
    check("stub is status: seed", "status: seed" in (wiki / "concepts" / "tax-rule.md").read_text())
    check("contamination flagged (billing/sales)", "spans ['billing', 'sales']" in out or "spans ['sales', 'billing']" not in out and "contamination (1)" in out)

# 4. ownership ABSENT (small project): graceful — every dangling stubs, no contamination, no crash
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    for f in ("entities", "metrics", "concepts"):
        (wiki / f).mkdir()
    page(wiki / "entities" / "thing.md",
         'title: Thing\nrelationships:\n  - type: depends_on\n    target: ../concepts/missing.md\n'
         'derived_from: [model.p.x]')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(wiki, "2026-01-01")
    out = buf.getvalue()
    check("rc 0 (no ownership.json)", rc == 0)
    check("small-project mode reported", "small-project mode" in out)
    check("dangling still stubbed without ownership", (wiki / "concepts" / "missing.md").exists())
    check("no contamination without domain map", "contamination (0)" in out)

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
