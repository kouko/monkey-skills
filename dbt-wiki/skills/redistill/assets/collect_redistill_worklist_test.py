# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Smoke test for collect_redistill_worklist.py — synthetic, offline, no specifics.

Contract under test: given a .dbt-wiki/ knowledge layer, return the redistill
work-list — stale + non-mature + non-archived pages with provenance, grouped by
the domain that owns the majority of their derived_from evidence. Falls back to a
single group when ownership.json is absent (small / sequential projects)."""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from collect_redistill_worklist import collect_worklist  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


def page(wiki, folder, slug, fm):
    d = wiki / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text("---\n" + fm + "\n---\n\nbody\n", encoding="utf-8")


def ownership(wiki, domains):
    internal = wiki / "_internal"
    internal.mkdir(parents=True, exist_ok=True)
    (internal / "ownership.json").write_text(
        json.dumps({"domains": domains}), encoding="utf-8")


# ---- 1. ownership present: stale developing page grouped by owning domain ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "entities", "order",
         "type: knowledge-entity\nstatus: developing\nstale: true\n"
         "derived_from: [model.p.sales_orders, model.p.sales_lines]")
    ownership(wiki, {"sales": ["model.p.sales_orders", "model.p.sales_lines"],
                     "billing": ["model.p.invoices"]})
    wl = collect_worklist(wiki)
    check("not fallback when ownership.json present", wl["fallback"] is False)
    check("stale developing page selected", wl["total_selected"] == 1)
    check("grouped under owning domain 'sales'", "sales" in wl["groups"]
          and wl["groups"]["sales"][0]["slug"] == "order")

# ---- 2. mature stale page skipped (reported separately for --force-mature) ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "entities", "customer",
         "type: knowledge-entity\nstatus: mature\nstale: true\n"
         "derived_from: [model.p.dim_customer]")
    ownership(wiki, {"core": ["model.p.dim_customer"]})
    wl = collect_worklist(wiki)
    check("mature stale page NOT selected", wl["total_selected"] == 0)
    check("mature stale page reported in skipped_mature",
          [p["slug"] for p in wl["skipped_mature"]] == ["customer"])

# ---- 3. archived stale page skipped entirely (not selected, not reported) ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "concepts", "legacy",
         "type: knowledge-concept\nstatus: archived\nstale: true\n"
         "derived_from: [model.p.old]")
    wl = collect_worklist(wiki)
    check("archived page not selected", wl["total_selected"] == 0)
    check("archived page not in skipped_mature",
          all(p["slug"] != "legacy" for p in wl["skipped_mature"]))

# ---- 4. non-stale page ignored ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "metrics", "revenue",
         "type: knowledge-metric\nstatus: developing\nstale: false\n"
         "derived_from: [model.p.fct_rev]")
    wl = collect_worklist(wiki)
    check("non-stale page ignored", wl["total_selected"] == 0 and wl["total_stale"] == 0)

# ---- 5. stale developing page with no derived_from -> skipped_no_provenance ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "concepts", "vague",
         "type: knowledge-concept\nstatus: developing\nstale: true")
    wl = collect_worklist(wiki)
    check("no-provenance page not selected", wl["total_selected"] == 0)
    check("no-provenance page reported",
          [p["slug"] for p in wl["skipped_no_provenance"]] == ["vague"])

# ---- 6. fallback: no ownership.json -> single '(all)' group, fallback=True ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "entities", "a",
         "type: knowledge-entity\nstatus: developing\nstale: true\nderived_from: [model.p.x]")
    page(wiki, "entities", "b",
         "type: knowledge-entity\nstatus: developing\nstale: true\nderived_from: [model.p.y]")
    wl = collect_worklist(wiki)
    check("fallback flagged when no ownership.json", wl["fallback"] is True)
    check("fallback puts all in one '(all)' group",
          list(wl["groups"].keys()) == ["(all)"] and len(wl["groups"]["(all)"]) == 2)

# ---- 7. cross-domain derived_from -> assigned to majority domain ----
with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    page(wiki, "entities", "shared",
         "type: knowledge-entity\nstatus: developing\nstale: true\n"
         "derived_from: [model.p.s1, model.p.s2, model.p.b1]")  # 2 sales, 1 billing
    ownership(wiki, {"sales": ["model.p.s1", "model.p.s2"], "billing": ["model.p.b1"]})
    wl = collect_worklist(wiki)
    check("cross-domain page assigned to majority domain 'sales'",
          "sales" in wl["groups"] and wl["groups"]["sales"][0]["slug"] == "shared")

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
