# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Smoke test for build_bundle_index.py — synthetic, offline, no project specifics."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_bundle_index import line_for, build_index, main  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


ENTITY = """---
type: knowledge-entity
title: Account
title_local: 帳戶
status: developing
summary: "One row per account."
aliases: [account_id, 帳戶]
---
# Account
"""

METRIC = """---
type: knowledge-metric
title: Monthly Recurring Revenue
status: mature
summary: "SUM of recognized subscription revenue per month."
---
# MRR
"""

SYNTHESIS = """---
type: synthesis
question: "How is region_code derived for EU accounts?"
slug: region-code-derivation
date: 2026-01-15
---
# Synthesis
"""

NO_TYPE = """---
title: Mystery
---
# Mystery
"""

NO_FM = "# Bare Page\nNo frontmatter at all.\n"

SCALAR_FM = """---
42
---
# Scalar frontmatter (valid YAML, not a mapping)
"""

STR_ALIASES = """---
type: knowledge-entity
title: Order
status: developing
summary: "One row per order."
aliases: order_id
---
# Order
"""

# 1. entity line shape: title｜title_local + status + summary + aliases, flat link
line = line_for(Path("account.md"), ENTITY)
check(
    "entity line shape",
    line == "- [Account｜帳戶](account.md) `developing` — One row per account. 〔aka: account_id, 帳戶〕",
)

# 2. metric line without title_local/aliases
line = line_for(Path("monthly-recurring-revenue.md"), METRIC)
check(
    "metric line shape",
    line == "- [Monthly Recurring Revenue](monthly-recurring-revenue.md) `mature` — SUM of recognized subscription revenue per month.",
)

# 3. synthesis line uses question as head and `synthesis` tag
line = line_for(Path("region-code-derivation.md"), SYNTHESIS)
check(
    "synthesis line shape",
    line == "- [How is region_code derived for EU accounts?](region-code-derivation.md) `synthesis` — verified deep-dive (2026-01-15)",
)

# 3a. page with NO frontmatter: stem title, default status, no crash
line = line_for(Path("bare-page.md"), NO_FM)
check("no-frontmatter fallback", line == "- [bare-page](bare-page.md) `developing`")

# 3b. valid-YAML-non-mapping frontmatter (bare scalar): treated as no frontmatter
line = line_for(Path("scalar.md"), SCALAR_FM)
check("scalar frontmatter fallback", line == "- [scalar](scalar.md) `developing`")

# 3c. scalar-string aliases: normalized to a one-item list, not per-character
line = line_for(Path("order.md"), STR_ALIASES)
check(
    "string aliases normalized",
    line == "- [Order](order.md) `developing` — One row per order. 〔aka: order_id〕",
)

with tempfile.TemporaryDirectory() as d:
    k = Path(d)
    (k / "account.md").write_text(ENTITY, encoding="utf-8")
    (k / "monthly-recurring-revenue.md").write_text(METRIC, encoding="utf-8")
    (k / "region-code-derivation.md").write_text(SYNTHESIS, encoding="utf-8")
    (k / "mystery.md").write_text(NO_TYPE, encoding="utf-8")
    (k / "_relations.md").write_text("# relations anchor\n", encoding="utf-8")

    text = build_index(k)
    # 4. grouped sections in canonical order, each page under its own type
    check(
        "sections grouped by type",
        text.index("## Entities") < text.index("[Account｜帳戶]")
        < text.index("## Metrics") < text.index("[Monthly Recurring Revenue]")
        < text.index("## Concepts")
        < text.index("## Syntheses") < text.index("[How is region_code")
        < text.index("## Other pages") < text.index("[Mystery]"),
    )
    # 5. underscore files excluded from the index
    check("_relations.md not indexed", "_relations.md" not in text)
    # 6. empty section shows a placeholder, not a crash
    check("empty Concepts placeholder", "_(none)_" in text)

    # 7. end-to-end: main() writes _index.md, rc 0, idempotent
    rc1 = main(k)
    first = (k / "_index.md").read_text(encoding="utf-8")
    rc2 = main(k)
    second = (k / "_index.md").read_text(encoding="utf-8")
    check("main writes _index.md rc 0", rc1 == 0 and (k / "_index.md").exists())
    check("idempotent re-run", rc2 == 0 and first == second)
    # 8. total count covers all indexed pages (4 pages; _relations + _index excluded)
    check("total count line", "Total pages indexed: 4" in first)

# 9. empty knowledge dir -> rc 1 (packing produced nothing — fail loudly)
with tempfile.TemporaryDirectory() as d:
    check("empty dir rc 1", main(Path(d)) == 1)

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
