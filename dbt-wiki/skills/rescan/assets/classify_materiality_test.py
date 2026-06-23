# /// script
# requires-python = ">=3.10"
# dependencies = ["sqlglot>=25.0"]
# ///
"""Smoke test for classify_materiality.py — synthetic, offline, no specifics.

Contract under test: per changed dbt model, decide material (logic/structure
change) vs cosmetic (comment/whitespace-only change), and maintain the
logic_sha cache. added/removed are always material; modified is material if any
structural field changed, the logic_sha drifted from the cached baseline, the
fingerprint fell back to regex, or there is no cached baseline; else cosmetic.
The returned cache is a NEW dict (input never mutated): added/modified seed the
new sha+method, removed drops the uid, everything else carries over."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify_materiality import classify_changed_models  # noqa: E402
from logic_sha import compute_logic_sha  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


def model(uid, status, old=None, new=None):
    return {"uid": uid, "status": status, "old": old, "new": new}


def struct(columns, depends_on, materialization, compiled_sql=None):
    d = {"columns": set(columns), "depends_on": set(depends_on),
         "materialization": materialization}
    if compiled_sql is not None:
        d["compiled_sql"] = compiled_sql
    return d


BASE_SQL = "SELECT a, b FROM t"
WHERE_SQL = "SELECT a, b FROM t WHERE a > 0"
COMMENT_SQL = "SELECT a, b FROM t -- a tweaked comment"
UNPARSEABLE = "SELECT a, b FROM WHERE WHERE )))("

# ---- 1. modified, logic changed (added WHERE), structural same -> material ----
cache = {"m.x": {"sha": compute_logic_sha(BASE_SQL)["sha"], "method": "sqlglot"}}
changed = [model(
    "m.x", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=WHERE_SQL))]
mat, _ = classify_changed_models(changed, cache)
check("logic change (added WHERE) -> material", mat["m.x"] == "material")

# ---- 2. modified, comment-only SQL change -> cosmetic (edge 2/3) ----
base_sha = compute_logic_sha(BASE_SQL)
cache = {"m.c": {"sha": base_sha["sha"], "method": base_sha["method"]}}
changed = [model(
    "m.c", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=COMMENT_SQL))]
mat, _ = classify_changed_models(changed, cache)
check("comment-only SQL change -> cosmetic", mat["m.c"] == "cosmetic")

# ---- 3. modified, column-name-set changed -> material ----
cache = {"m.col": {"sha": compute_logic_sha(BASE_SQL)["sha"], "method": "sqlglot"}}
changed = [model(
    "m.col", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "c"], ["t"], "view", compiled_sql=BASE_SQL))]
mat, _ = classify_changed_models(changed, cache)
check("column-name-set change -> material", mat["m.col"] == "material")

# ---- 4. modified, depends_on changed -> material ----
cache = {"m.dep": {"sha": compute_logic_sha(BASE_SQL)["sha"], "method": "sqlglot"}}
changed = [model(
    "m.dep", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t", "u"], "view", compiled_sql=BASE_SQL))]
mat, _ = classify_changed_models(changed, cache)
check("depends_on change -> material", mat["m.dep"] == "material")

# ---- 5. modified, materialization changed (view->table) -> material ----
cache = {"m.mat": {"sha": compute_logic_sha(BASE_SQL)["sha"], "method": "sqlglot"}}
changed = [model(
    "m.mat", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "table", compiled_sql=BASE_SQL))]
mat, _ = classify_changed_models(changed, cache)
check("materialization change -> material", mat["m.mat"] == "material")

# ---- 6. modified, uid NOT in cache (no baseline) -> material (edge 5) ----
changed = [model(
    "m.new", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=BASE_SQL))]
mat, _ = classify_changed_models(changed, {})
check("no cached baseline -> material", mat["m.new"] == "material")

# ---- 7. modified, unparseable SQL -> regex method -> material (edge 6) ----
fp = compute_logic_sha(UNPARSEABLE)
cache = {"m.re": {"sha": fp["sha"], "method": "regex"}}
changed = [model(
    "m.re", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=UNPARSEABLE))]
mat, _ = classify_changed_models(changed, cache)
check("regex-method fingerprint -> material", mat["m.re"] == "material")

# ---- 8. added -> material; removed -> material + dropped from cache (edge 7) --
cache = {"m.gone": {"sha": "deadbeef", "method": "sqlglot"}}
changed = [
    model("m.add", "added",
          new=struct(["a"], ["t"], "view", compiled_sql=BASE_SQL)),
    model("m.gone", "removed", old=struct(["a"], ["t"], "view"))]
mat, updated = classify_changed_models(changed, cache)
check("added -> material", mat["m.add"] == "material")
check("removed -> material", mat["m.gone"] == "material")
check("removed uid dropped from updated cache", "m.gone" not in updated)
check("added uid seeded into updated cache", "m.add" in updated
      and updated["m.add"]["sha"] == compute_logic_sha(BASE_SQL)["sha"])

# ---- 9. updated_cache is a new object; input cache NOT mutated ----
cache = {"m.x": {"sha": compute_logic_sha(BASE_SQL)["sha"], "method": "sqlglot"}}
snapshot = {"m.x": dict(cache["m.x"])}
changed = [model(
    "m.x", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=WHERE_SQL))]
_, updated = classify_changed_models(changed, cache)
check("updated cache is a new object", updated is not cache)
check("input cache not mutated", cache == snapshot)

# ---- 10. cosmetic case updates cache entry with new sha+method ----
base_sha = compute_logic_sha(BASE_SQL)
cache = {"m.c": {"sha": base_sha["sha"], "method": base_sha["method"]}}
changed = [model(
    "m.c", "modified",
    old=struct(["a", "b"], ["t"], "view"),
    new=struct(["a", "b"], ["t"], "view", compiled_sql=COMMENT_SQL))]
mat, updated = classify_changed_models(changed, cache)
expected = compute_logic_sha(COMMENT_SQL)
check("cosmetic case still updates cache sha+method",
      updated["m.c"]["sha"] == expected["sha"]
      and updated["m.c"]["method"] == expected["method"])

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
