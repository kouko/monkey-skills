"""URL deduplication and fetch-budget filtering.

Port of the JS dedup logic from the deep-research pipeline:
  norm_url  — canonical key for seen-set deduplication
  filter_novel — classify results into novel / dupes / budget_dropped

CLI (__main__): reads a JSON object from stdin with keys
  {results: [...], seen: {...}, fetch_slots: int}
and prints a JSON object to stdout
  {novel: [...], seen: {...}, slots: int}
where `seen` is the mutated seen-map and `slots` is the remaining budget.
"""

import json
import sys
from urllib.parse import urlparse

_DEFAULT_REL_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}


def norm_url(u: str) -> str:
    """Return canonical dedup key: hostname (no leading www.) + path (no trailing /), lowercased.

    On parse failure, return u.lower().
    """
    try:
        p = urlparse(u)
        host = p.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        path = p.path.rstrip("/")
        return (host + path).lower()
    except Exception:
        return u.lower()


def filter_novel(
    results: list[dict],
    seen: dict,
    fetch_slots: int,
    rel_rank: dict | None = None,
) -> tuple[list, list, list, int]:
    """Classify results into novel, dupes, and budget_dropped.

    Parameters
    ----------
    results:     search results pre-sorted by relevance (caller's responsibility).
    seen:        shared dict mapping norm_url key -> True; mutated in-place.
    fetch_slots: remaining fetch budget; decremented for each novel result.
    rel_rank:    relevance rank map; defaults to {"high":0,"medium":1,"low":2}.

    Returns
    -------
    (novel, dupes, budget_dropped, fetch_slots)
    """
    if rel_rank is None:
        rel_rank = _DEFAULT_REL_RANK

    novel: list[dict] = []
    dupes: list[dict] = []
    budget_dropped: list[dict] = []

    for result in results:
        missing = [k for k in ("url", "relevance") if k not in result]
        if missing:
            raise ValueError(
                f"search result missing required key(s): {missing!r} — got {list(result.keys())!r}"
            )
        if result["relevance"] not in rel_rank:
            raise ValueError(
                f"search result has unknown relevance {result['relevance']!r}; "
                f"expected one of {list(rel_rank.keys())!r}"
            )
        key = norm_url(result["url"])
        if key in seen:
            dupes.append({**result, "dupOf": key})
        elif fetch_slots <= 0 and rel_rank[result["relevance"]] >= 1:
            budget_dropped.append(result)
        else:
            seen[key] = True
            fetch_slots -= 1
            novel.append(result)

    return novel, dupes, budget_dropped, fetch_slots


def main() -> None:
    payload = json.load(sys.stdin)
    seen = payload.get("seen") or {}
    novel, _dupes, _budget_dropped, slots = filter_novel(
        payload["results"],
        seen,
        payload["fetch_slots"],
    )
    json.dump({"novel": novel, "seen": seen, "slots": slots}, sys.stdout)


if __name__ == "__main__":
    main()
