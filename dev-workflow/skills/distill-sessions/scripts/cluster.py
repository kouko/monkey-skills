"""cluster.py — pure-function clustering of memory items by cross-session evidence.

Public API
----------
cluster_memory_items(items, min_n=2) -> tuple[list[dict], list[dict]]
    Partition memory items into ``promoted`` (multi-session patterns) and
    ``pending`` (single-session / below-threshold observations).

Design notes
------------
- Normalization key: (title_norm, anchor_norm) where norm = lowercase +
  whitespace-collapse + strip leading/trailing punctuation from allowlist.
- Promotion criterion: number of *distinct* session_ids in a group >= min_n.
- Pure function: no I/O; input dicts are not mutated (copies built as needed).
- Stdlib-only: no embeddings, no third-party deps.

Locked decision Q-v0.3-1 = A (Filter):
    N=1 items go to pending (not silently dropped) so the §Cross-session
    evidence pending bucket renderer (Task 2) can surface them.
"""

import copy
import string
from collections import defaultdict

# Characters stripped from the leading/trailing positions of normalized strings.
# Internal punctuation is preserved (e.g. hyphens in compound words).
_STRIP_CHARS = set(".,;:!?'\"" + string.whitespace)


def _normalize(text: str) -> str:
    """Lowercase, collapse internal whitespace, strip leading/trailing punctuation.

    Stripping uses an allowlist of punctuation chars (.,;:!?'"") plus
    whitespace.  Internal punctuation is intentionally preserved so that
    "Read/Write" and "ReadWrite" do not accidentally merge.
    """
    # Collapse internal whitespace first, then strip boundaries.
    collapsed = " ".join(text.split())
    # Strip one character at a time from each end until no strip-chars remain.
    result = collapsed.lower()
    # lstrip / rstrip accept a *string* of chars to strip (set of chars, not substring).
    strip_str = "".join(_STRIP_CHARS)
    result = result.strip(strip_str)
    return result


def cluster_memory_items(
    items: list[dict],
    min_n: int = 2,
) -> tuple[list[dict], list[dict]]:
    """Partition memory items into promoted patterns and pending observations.

    Args:
        items:  Flat list of memory item dicts.  Each must contain at least
                ``title``, ``section_anchor``, and ``session_id`` keys.
        min_n:  Minimum number of *distinct* session_ids required for a group
                to be promoted.  Default 2.

    Returns:
        A ``(promoted, pending)`` tuple.

        promoted:
            One representative dict per group that reached min_n distinct
            sessions.  The representative is a shallow copy of the *first*
            item in the group (input order) with a new ``supporting_sessions``
            key added — an alphabetically-sorted list of distinct session_ids.
            Sorted by group size descending; ties broken alphabetically by
            normalized title.

        pending:
            All items whose group did not reach min_n distinct sessions,
            returned individually in their original shape (no
            ``supporting_sessions`` added).  Sorted by session_id then by
            normalized title.

    Notes:
        - Does not mutate input dicts or the input list.
        - Items from the *same* session with the same (title, anchor) do not
          contribute more than one vote toward the distinct-session count.
    """
    if not items:
        return [], []

    # -----------------------------------------------------------------------
    # Phase 1: group items by normalized (title, anchor) key.
    # Each bucket holds a list of (norm_title, item) pairs so we can sort
    # pending later without re-normalizing.
    # -----------------------------------------------------------------------
    # groups: key -> list of (item_copy, norm_title)
    groups: dict[tuple[str, str], list[tuple[dict, str]]] = defaultdict(list)

    for item in items:
        norm_title = _normalize(item.get("title", ""))
        norm_anchor = _normalize(item.get("section_anchor", ""))
        key = (norm_title, norm_anchor)
        item_copy = copy.copy(item)  # shallow copy — values are strings, safe
        groups[key].append((item_copy, norm_title))

    # -----------------------------------------------------------------------
    # Phase 2: split groups into promoted / pending based on distinct sessions.
    # -----------------------------------------------------------------------
    promoted_entries: list[tuple[int, str, dict]] = []  # (size, norm_title, rep)
    pending_entries: list[tuple[str, str, dict]] = []  # (session_id, norm_title, item)

    for (norm_title, _norm_anchor), bucket in groups.items():
        # Count distinct session_ids in this bucket.
        seen_sessions: set[str] = set()
        for item_copy, _ in bucket:
            seen_sessions.add(item_copy.get("session_id", ""))

        if len(seen_sessions) >= min_n:
            # Build representative from the first item in the bucket.
            rep = copy.copy(bucket[0][0])
            rep["supporting_sessions"] = sorted(seen_sessions)
            promoted_entries.append((len(seen_sessions), norm_title, rep))
        else:
            for item_copy, nt in bucket:
                session_id = item_copy.get("session_id", "")
                pending_entries.append((session_id, nt, item_copy))

    # -----------------------------------------------------------------------
    # Phase 3: sort and extract final lists.
    # -----------------------------------------------------------------------
    # promoted: group size descending, then alphabetic by normalized title
    promoted_entries.sort(key=lambda e: (-e[0], e[1]))
    promoted = [e[2] for e in promoted_entries]

    # pending: session_id ascending, then normalized title ascending
    pending_entries.sort(key=lambda e: (e[0], e[1]))
    pending = [e[2] for e in pending_entries]

    return promoted, pending
