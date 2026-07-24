# /// script
# requires-python = ">=3.10"
# ///
"""Smoke test for triage_worklist.py — synthetic, offline, no specifics.

Contract under test: given a redistill `groups` mapping and a `materiality_map`
classifying CHANGED models, partition each page into material (kept under its
original domain) vs cosmetic (collected into one flat list). OR-aggregation per
page: material iff ANY of its derived_from uids that the map classifies maps to
"material"; otherwise (all-cosmetic intersection, or empty intersection) cosmetic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from triage_worklist import triage  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


def pg(slug, derived_from, folder="entities"):
    return {"slug": slug, "path": f"/w/{folder}/{slug}.md",
            "folder": folder, "derived_from": list(derived_from)}


# ---- 1. mixed material+cosmetic derived_from -> material (edge 4) ----
p = pg("order", ["model.p.a", "model.p.b"])
out = triage({"sales": [p]}, {"model.p.a": "material", "model.p.b": "cosmetic"})
check("mixed material+cosmetic page is material",
      out["material"].get("sales") == [p] and out["cosmetic"] == [])

# ---- 2. only-cosmetic intersection -> cosmetic ----
p = pg("note", ["model.p.a", "model.p.b"])
out = triage({"sales": [p]}, {"model.p.a": "cosmetic", "model.p.b": "cosmetic"})
check("all-cosmetic page is cosmetic",
      out["material"] == {} and out["cosmetic"] == [p])

# ---- 3. no intersection with the map -> cosmetic (defensive) ----
p = pg("orphan", ["model.p.x", "model.p.y"])
out = triage({"sales": [p]}, {"model.p.a": "material"})
check("no-intersection page is cosmetic",
      out["material"] == {} and out["cosmetic"] == [p])

# ---- 4. cross-domain: triaged over FULL derived_from set (edge 8) ----
p = pg("shared", ["model.p.s1", "model.p.s2", "model.p.b1"])
out = triage({"sales": [p]},
             {"model.p.s1": "cosmetic", "model.p.b1": "material"})
check("page material when ANY uid in full derived_from set is material",
      out["material"].get("sales") == [p] and out["cosmetic"] == [])

# ---- 5. domain with only-cosmetic pages disappears from material ----
mat = pg("keep", ["model.p.m"])
cos = pg("drop", ["model.p.c"])
out = triage({"sales": [mat], "billing": [cos]},
             {"model.p.m": "material", "model.p.c": "cosmetic"})
check("material page keeps its domain", out["material"].get("sales") == [mat])
check("only-cosmetic domain dropped from material", "billing" not in out["material"])
check("cosmetic page in flat list", out["cosmetic"] == [cos])

# ---- 6. multiple pages in same domain partition correctly ----
m = pg("m1", ["model.p.m"])
c = pg("c1", ["model.p.c"])
out = triage({"sales": [m, c]},
             {"model.p.m": "material", "model.p.c": "cosmetic"})
check("same-domain material stays under domain", out["material"].get("sales") == [m])
check("same-domain cosmetic goes to flat list", out["cosmetic"] == [c])

# ---- 7. empty groups -> {"material": {}, "cosmetic": []} ----
out = triage({}, {"model.p.m": "material"})
check("empty groups -> empty partition",
      out == {"material": {}, "cosmetic": []})

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
