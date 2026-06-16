"""Core angle selection for the Verbalized-Sampling (vs) scope variant.

Deterministic, stdlib-only, no network. Turns a pool of typicality-tiered,
relevance-scored candidate angles (from SCOPE_VS_SCHEMA) into the small set
of research angles that feed the UNCHANGED Stage-2 SCOPE_SCHEMA shape.

Pipeline (this module):
  1. relevance floor — drop any candidate below RELEVANCE_FLOOR (i.e. drop "low").
  2. tier sort       — order survivors most-typical -> least-typical
                       (most-obvious -> mid -> least-obvious), stable within a tier.
  2b. dedup (④)      — collapse candidates with the same case-folded label OR
                       normalized query key; keep the first (most-typical) one.
  3. head / tail     — head = the head_k most-typical survivors;
                       tail = the tail_k least-typical survivors, with lexical
                       mutual-exclusion (⑤): a tail pick near-identical to one
                       already in the tail is skipped for the next distinct one;
                       distinct (no double-count when the pool is small).
  4. cap             — total selected <= MAX_ANGLES (6).
  5. strip           — each angle reduced to {label, query, rationale} so it
                       matches the existing SCOPE_SCHEMA angle shape.

CLI (__main__): reads a JSON object from stdin
  {candidates: [...], head_k?: int, tail_k?: int}
and prints to stdout
  {angles: [...]}
where each angle is stripped to {label, query, rationale}.

Note: named vs_select.py (NOT select.py). A module named `select.py` on
sys.path shadows the stdlib `select` module; because pytest.ini sets
`pythonpath = .`, that shadow breaks pytest's own startup imports
(pygments -> socket -> selectors -> select.select), taking down the WHOLE
suite. `vs_select` avoids the clash. (Deviation from the plan's `select.py`
filename — see implementer report; CLI surface / Task 12 must use this name.)
"""
from __future__ import annotations

import difflib
import json
import sys

from dedup import norm_url

# Module-local fallbacks for the scope_vs constants. Defined here (not imported
# from scope_vs) to keep this module self-contained and avoid a cross-file
# import race in the parallel build wave.
HEAD_K = 3
TAIL_K = 2
RELEVANCE_FLOOR = "medium"
MAX_ANGLES = 6

# Relevance rank: lower number = more relevant. Matches dedup.py's convention.
_REL_RANK = {"high": 0, "medium": 1, "low": 2}

# Tier order, most-typical -> least-typical.
_TIER_ORDER = ["most-obvious", "mid", "least-obvious"]
_TIER_RANK = {tier: i for i, tier in enumerate(_TIER_ORDER)}

# Tail (⑤): two "surprise" slots that are near-identical waste a slot. A new
# tail candidate whose label+query is >= this SequenceMatcher ratio to one
# already chosen for the tail is skipped in favour of the next distinct one.
TAIL_SIM_THRESHOLD = 0.8


def _dedup_key(candidate: dict) -> tuple[str, str]:
    """Identity key for ④ dedup: (case-folded label, normalized query).

    Query is normalized via norm_url for URL-shaped queries; otherwise
    casefold+strip. norm_url falls back to .lower() on non-URL input, but we
    only route through it when the query looks URL-shaped so plain queries keep
    their internal spacing semantics under a simple casefold.
    """
    label = candidate.get("label", "").casefold().strip()
    query = candidate.get("query", "")
    if "://" in query or query.startswith("//"):
        qkey = norm_url(query)
    else:
        qkey = query.casefold().strip()
    return (label, qkey)


def _tail_text(candidate: dict) -> str:
    """Lexical signature for ⑤ tail near-duplicate detection."""
    return f"{candidate.get('label', '')} {candidate.get('query', '')}".casefold().strip()


def _strip(candidate: dict) -> dict:
    """Reduce a candidate to the SCOPE_SCHEMA angle shape {label, query, rationale}.

    rationale is preserved if present; otherwise the key is omitted (search_prompt
    tolerates this via angle.get("rationale", "")).
    """
    angle = {"label": candidate["label"], "query": candidate["query"]}
    rationale = candidate.get("rationale")
    if rationale:
        angle["rationale"] = rationale
    return angle


def select_angles(
    candidates: list[dict],
    head_k: int = HEAD_K,
    tail_k: int = TAIL_K,
) -> list[dict]:
    """Select head/tail angles from scored candidates. See module docstring.

    Each candidate is {label, query, rationale?, relevance, typicality_tier}.
    Returns a list of angles stripped to {label, query, rationale}, head-first
    then tail, capped at MAX_ANGLES, with no duplicate candidate counted twice.
    """
    # 1. relevance floor: keep candidates at or above RELEVANCE_FLOOR.
    floor = _REL_RANK[RELEVANCE_FLOOR]
    survivors = []
    for c in candidates:
        missing = [k for k in ("label", "query", "relevance", "typicality_tier") if k not in c]
        if missing:
            raise ValueError(
                f"candidate missing required key(s): {missing!r} — got {list(c.keys())!r}"
            )
        if c["relevance"] not in _REL_RANK:
            raise ValueError(
                f"candidate has unknown relevance {c['relevance']!r}; "
                f"expected one of {list(_REL_RANK.keys())!r}"
            )
        if c["typicality_tier"] not in _TIER_RANK:
            raise ValueError(
                f"candidate has unknown typicality_tier {c['typicality_tier']!r}; "
                f"expected one of {_TIER_ORDER!r}"
            )
        if _REL_RANK[c["relevance"]] <= floor:
            survivors.append(c)

    # 2. tier sort: stable sort most-typical -> least-typical. Python's sort is
    #    stable, so input order is preserved within a tier.
    ordered = sorted(survivors, key=lambda c: _TIER_RANK[c["typicality_tier"]])

    # 2b. dedup (④): collapse candidates with the same case-folded label OR the
    #     same normalized query key. Keep the first occurrence — which, after the
    #     tier sort, is the most-typical of the duplicate set (most-typical wins).
    deduped = []
    seen_keys: set[tuple[str, str]] = set()
    for c in ordered:
        label_key, query_key = _dedup_key(c)
        if label_key in seen_keys or ("q", query_key) in seen_keys:
            continue
        seen_keys.add(label_key)
        seen_keys.add(("q", query_key))
        deduped.append(c)

    # 3. head / tail picked from the deduped relevance-passing pool only.
    head = deduped[:head_k]

    # tail (⑤): walk least-typical-first, skipping candidates already in head
    # AND candidates lexically near-identical to one already chosen for the tail
    # (so the two "surprise" slots aren't redundant). Pull the next distinct
    # least-typical relevance-passing candidate instead.
    head_ids = {id(c) for c in head}
    tail: list[dict] = []
    if tail_k > 0:
        for c in reversed(deduped):
            if len(tail) >= tail_k:
                break
            if id(c) in head_ids:
                continue
            ctext = _tail_text(c)
            if any(
                difflib.SequenceMatcher(None, ctext, _tail_text(t)).ratio()
                >= TAIL_SIM_THRESHOLD
                for t in tail
            ):
                continue
            tail.append(c)
        tail.reverse()  # restore least-typical-first -> most-typical order within tail

    # distinct: append tail entries not already chosen for head (small-pool
    # overlap is already excluded above, but keep the guard for cap-order safety).
    selected = list(head)
    seen = set(head_ids)
    for c in tail:
        if id(c) not in seen:
            selected.append(c)
            seen.add(id(c))

    # 4. cap total at MAX_ANGLES.
    selected = selected[:MAX_ANGLES]

    # 5. strip to SCOPE_SCHEMA angle shape.
    return [_strip(c) for c in selected]


def main() -> None:
    payload = json.load(sys.stdin)
    head_k = payload.get("head_k", HEAD_K)
    tail_k = payload.get("tail_k", TAIL_K)
    angles = select_angles(payload["candidates"], head_k=head_k, tail_k=tail_k)
    json.dump({"angles": angles}, sys.stdout)


if __name__ == "__main__":
    main()
