# /// script
# requires-python = ">=3.10"
# ///
"""Smoke test for flatten_links.py — synthetic, offline, no project specifics."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from flatten_links import flatten_text, count_broken, main  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


# 1. cross-folder body link -> flat sibling
out, cross, evid = flatten_text("see [Account](../entities/account.md) for grain")
check("body cross-folder flattened", out == "see [Account](account.md) for grain" and cross == 1)

# 2. frontmatter target -> flat sibling
out, cross, evid = flatten_text("  - type: depends_on\n    target: ../concepts/active-account.md\n")
check("frontmatter target flattened", "target: active-account.md" in out and cross == 1)

# 3. evidence link -> delinked label
out, cross, evid = flatten_text("- [stg_account](../_evidence/models/stg_account.md)")
check("evidence delinked to label", out == "- stg_account" and evid == 1)

# 4. already-flat link untouched (idempotent)
out, cross, evid = flatten_text("see [MRR](mrr.md) and target: order.md")
check("already-flat untouched", out == "see [MRR](mrr.md) and target: order.md" and cross == 0)

# 5. http link untouched
out, cross, evid = flatten_text("[docs](https://example.com/x.md)")
check("http untouched", out == "[docs](https://example.com/x.md)")

# 5a. synthesis cross-link -> flat sibling (syntheses freeze into the bundle too)
out, cross, evid = flatten_text("see [deep dive](../syntheses/mrr-recognition.md)")
check("synthesis cross-folder flattened", out == "see [deep dive](mrr-recognition.md)" and cross == 1)

# 5b. SCHEMA-shaped synthesis evidence link (.dbt-wiki/_evidence/...) -> delinked
out, cross, evid = flatten_text("- [fct_orders](.dbt-wiki/_evidence/models/fct_orders.md) — User Notes")
check("dotted evidence delinked", out == "- fct_orders — User Notes" and evid == 1)

# 5c. source-repo relative link (escapes the bundle) -> delinked, label kept
out, cross, evid = flatten_text("SSOT: [SPEC](../../models/marts/SPEC__orders.md)")
check("repo-path delinked", out == "SSOT: SPEC" and evid == 1)

# 5d. archived-page link (dropped layer) -> delinked
out, cross, evid = flatten_text("was [old page](../_archive/old-metric.md)")
check("archive delinked", out == "was old page" and evid == 1)

# 6. end-to-end on a temp flat bundle (incl. a SCHEMA-shaped synthesis page):
#    0 broken after main()
with tempfile.TemporaryDirectory() as d:
    k = Path(d)
    (k / "account.md").write_text("# Account\nsee [MRR](../metrics/mrr.md)\nev [m](../_evidence/models/m.md)\n")
    (k / "mrr.md").write_text("# MRR\nrel [Account](../entities/account.md)\nsee [dive](../syntheses/mrr-recognition.md)\n")
    (k / "mrr-recognition.md").write_text(
        "# Synthesis\n"
        "1. [fct_orders](../_evidence/models/fct_orders.md) — CASE source\n"
        "## Sources Consulted\n"
        "- [fct_orders](.dbt-wiki/_evidence/models/fct_orders.md) — User Notes\n"
        "- SSOT: [SPEC](../../models/marts/SPEC__orders.md)\n"
        "- rel [MRR](../metrics/mrr.md)\n"
    )
    rc = main(k)
    check("end-to-end 0 broken + rc 0", rc == 0 and count_broken(k) == [])

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
