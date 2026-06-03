"""Claim ranking and quorum survival logic.

Pure functions; stdlib only; no schemas import (L1 leaf module —
operates on generic dicts).  Ported verbatim from decompiled-source.md
§Quorum rule + §Ranking maps.

CLI (consumed by SKILL.md over stdin/stdout JSON):
    python rank.py           # stdin: claims JSON array  → stdout: ranked (≤25) JSON
    python rank.py quorum    # stdin: verdicts JSON array → stdout: `true` / `false`
"""

from __future__ import annotations

from typing import Any

_DEFAULT_IMP_RANK: dict[str, int] = {
    "central": 0,
    "supporting": 1,
    "tangential": 2,
}

_DEFAULT_QUAL_RANK: dict[str, int] = {
    "primary": 0,
    "secondary": 1,
    "blog": 2,
    "forum": 3,
    "unreliable": 4,
}


def rank_claims(
    claims: list[dict[str, Any]],
    imp_rank: dict[str, int] | None = None,
    qual_rank: dict[str, int] | None = None,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Stable-sort claims by (importance, sourceQuality) then slice to limit.

    Sort key: (imp_rank[c["importance"]], qual_rank[c["sourceQuality"]]).
    Lower values rank higher (0 = best).  Python's sort is stable, so
    ties preserve input order.
    """
    if imp_rank is None:
        imp_rank = _DEFAULT_IMP_RANK
    if qual_rank is None:
        qual_rank = _DEFAULT_QUAL_RANK

    ranked = sorted(
        claims,
        key=lambda c: (
            imp_rank.get(c.get("importance", ""), 99),
            qual_rank.get(c.get("sourceQuality", ""), 99),
        ),
    )
    return ranked[:limit]


def quorum_survives(
    verdicts: list[dict[str, Any] | None],
    votes_per_claim: int = 3,
    refutations_required: int = 2,
) -> bool:
    """Return True only if the claim survives adversarial quorum.

    Port of the JS quorum rule (decompiled-source.md §Quorum rule):

        valid = verdicts.filter(Boolean)           # None = abstain, dropped
        refuted = valid.filter(v => v.refuted).length
        survives = valid.length >= REFUTATIONS_REQUIRED
                   and refuted < REFUTATIONS_REQUIRED

    Guards the all-abstain → refuted=0 → false-survive bug:
    the valid-count check must gate before the refuted check.
    """
    valid = [v for v in verdicts if v is not None]
    refuted = sum(1 for v in valid if v["refuted"])
    return len(valid) >= refutations_required and refuted < refutations_required


if __name__ == "__main__":
    import json
    import sys

    data = json.load(sys.stdin)
    if len(sys.argv) > 1 and sys.argv[1] == "quorum":
        print(json.dumps(quorum_survives(data)))
    else:
        print(json.dumps(rank_claims(data)))
