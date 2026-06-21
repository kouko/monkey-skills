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

# 6. end-to-end on a temp flat bundle: 0 broken after main()
with tempfile.TemporaryDirectory() as d:
    k = Path(d)
    (k / "account.md").write_text("# Account\nsee [MRR](../metrics/mrr.md)\nev [m](../_evidence/models/m.md)\n")
    (k / "mrr.md").write_text("# MRR\nrel [Account](../entities/account.md)\n")
    rc = main(k)
    check("end-to-end 0 broken + rc 0", rc == 0 and count_broken(k) == [])

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
