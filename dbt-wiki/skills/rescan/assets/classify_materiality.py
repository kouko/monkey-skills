#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["sqlglot>=25.0"]
# ///
"""Classify each changed dbt model as material vs cosmetic, maintain logic_sha cache.

dbt-wiki's rescan needs to know which changed models actually changed their
logic/structure (material — the wiki page must be re-distilled) versus which
only had a comment or whitespace edit (cosmetic — the page can be left alone).

Per model:
  added / removed        -> always material.
  modified               -> material if ANY of:
                              column-name-set changed,
                              depends_on set changed,
                              materialization changed,
                              logic_sha drifted from the cached baseline,
                              logic_sha fell back to regex (parse failed),
                              or there is no cached baseline for the uid.
                            else cosmetic.

The cache maps uid -> {"sha", "method"} (the prior run's logic_sha). It is never
mutated in place: a NEW dict is returned with added/modified uids seeded from the
newly computed fingerprint, removed uids dropped, and all others carried over.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from logic_sha import compute_logic_sha  # noqa: E402


def _is_material_modified(entry, new_logic, cache):
    """True if a modified model's change touches logic or structure."""
    old, new = entry["old"], entry["new"]
    uid = entry["uid"]
    if set(old["columns"]) != set(new["columns"]):
        return True
    if set(old["depends_on"]) != set(new["depends_on"]):
        return True
    if old["materialization"] != new["materialization"]:
        return True
    if uid not in cache:
        return True
    if new_logic["method"] == "regex":
        return True
    if new_logic["sha"] != cache.get(uid, {}).get("sha"):
        return True
    return False


def classify_changed_models(changed, cache, dialect="redshift"):
    """Classify changed models, return (materiality_map, updated_cache).

    changed: list of {"uid", "status", "old", "new"} dicts (see module doc).
    cache:   {uid: {"sha", "method"}} prior-run baseline; may be empty / partial.
    dialect: sqlglot read dialect threaded into compute_logic_sha.

    Returns:
      materiality_map: {uid: "material" | "cosmetic"}
      updated_cache:   NEW dict; input cache is never mutated.
    """
    materiality_map = {}
    updated_cache = dict(cache)

    for entry in changed:
        uid = entry["uid"]
        status = entry["status"]

        if status == "removed":
            materiality_map[uid] = "material"
            updated_cache.pop(uid, None)
            continue

        new_logic = compute_logic_sha(entry["new"]["compiled_sql"], dialect)

        if status == "added":
            materiality_map[uid] = "material"
        elif status == "modified":
            materiality_map[uid] = (
                "material" if _is_material_modified(entry, new_logic, cache)
                else "cosmetic")
        else:
            raise ValueError(f"unknown status {status!r} for uid {uid!r}")

        updated_cache[uid] = {"sha": new_logic["sha"],
                              "method": new_logic["method"]}

    return materiality_map, updated_cache
