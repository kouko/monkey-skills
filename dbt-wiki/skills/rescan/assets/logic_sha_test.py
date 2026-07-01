# /// script
# requires-python = ">=3.10"
# dependencies = ["sqlglot>=25.0"]
# ///
"""Smoke test for logic_sha.py — synthetic, offline, no specifics.

Contract under test: compute_logic_sha(sql, dialect) returns a comment-stripped,
normalized SQL fingerprint {"sha", "method"} so cosmetic (comment/whitespace-only)
changes are indistinguishable while material (logic) changes diverge. sqlglot is
the primary path; an unparseable input falls back to a regex comment-strip + whitespace
collapse so the function never crashes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from logic_sha import compute_logic_sha  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


# ---- 1. comment-only difference -> identical sha ----
base = compute_logic_sha("SELECT a FROM t")
commented = compute_logic_sha("SELECT a FROM t -- a comment")
check("comment-only change -> same sha", base["sha"] == commented["sha"])

# ---- 2. whitespace/formatting-only difference -> identical sha ----
spaced = compute_logic_sha("SELECT   a\nFROM t")
check("whitespace-only change -> same sha", base["sha"] == spaced["sha"])

# ---- 3. logic change keeping the SAME column name -> DIFFERENT sha ----
filtered = compute_logic_sha("SELECT a FROM t WHERE x > 0")
check("logic change (added WHERE) -> different sha", base["sha"] != filtered["sha"])

# ---- 4. unparseable SQL -> does NOT crash, method=regex, stable sha ----
broken_a = compute_logic_sha("SELECT FROM WHERE )(")
broken_b = compute_logic_sha("SELECT FROM WHERE )(")
check("unparseable SQL -> method=regex", broken_a["method"] == "regex")
check("unparseable SQL -> stable sha", broken_a["sha"] == broken_b["sha"])

# ---- 5. method flag: sqlglot on clean parse, regex on fallback ----
check("clean parse -> method=sqlglot", base["method"] == "sqlglot")
check("broken parse -> method=regex", broken_a["method"] == "regex")

# ---- 6. empty string and None -> no crash, method=regex, deterministic sha ----
empty = compute_logic_sha("")
none_in = compute_logic_sha(None)
check("empty string -> method=regex", empty["method"] == "regex")
check("None -> method=regex", none_in["method"] == "regex")
check("empty and None -> same deterministic sha", empty["sha"] == none_in["sha"])

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
