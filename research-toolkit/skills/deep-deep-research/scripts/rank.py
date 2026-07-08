"""Claim ranking and quorum survival logic.

Pure functions; stdlib only; no schemas import (L1 leaf module —
operates on generic dicts).  Ported verbatim from decompiled-source.md
§Quorum rule + §Ranking maps.

CLI (consumed by SKILL.md over stdin/stdout JSON):
    python rank.py                   # stdin: claims JSON array  → stdout: ranked (≤25) JSON
    python rank.py --claims-dir DIR  # merge every *.json in DIR (filename-sorted;
                                     #   each file = claims JSON array); stdin is
                                     #   NOT read → stdout: ranked (≤25) JSON
    python rank.py quorum            # stdin: verdicts JSON array → stdout: `true` / `false`
    python rank.py attribution-check # stdin: one verdict JSON object → stdout: `true` / `false`

--claims-dir and stdin are mutually exclusive: when the flag is given,
stdin is never read.  The quorum and attribution-check subcommands
take no --claims-dir.
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


def attribution_survives(verdict: dict[str, Any] | None) -> bool:
    """Return True only if the single attribution-confirmation check passed.

    Structurally parallels quorum_survives but for ONE opinion-attribution
    verdict, not a 3-vote adversarial quorum: an opinion claim gets one
    attribution-confirmation check (does the cited source actually hold
    this view?), not adversarial voting.  A missing key, an explicit
    null value, OR a None verdict (the checker abstained — failed or
    returned nothing) all fail closed, mirroring quorum_survives's
    None-filtering for the same convention. ``dict.get(key, default)``
    only applies its default when the key is ABSENT, not when the key
    is present with value None -- ``bool(...)`` closes that gap so an
    explicit ``{"attributionConfirmed": null}`` (plausible from an LLM
    checker expressing uncertainty) fails closed instead of returning
    None and breaking this function's bool contract.
    """
    if verdict is None:
        return False
    return bool(verdict.get("attributionConfirmed", False))


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    args = sys.argv[1:]
    if args and args[0] == "quorum":
        print(json.dumps(quorum_survives(json.load(sys.stdin))))
    elif args and args[0] == "attribution-check":
        print(json.dumps(attribution_survives(json.load(sys.stdin))))
    elif args and args[0] == "--claims-dir":
        if len(args) < 2:
            sys.exit("--claims-dir requires a directory argument")
        claims_dir = Path(args[1])
        if not claims_dir.is_dir():
            sys.exit(f"--claims-dir: not a directory: {claims_dir}")
        claims: list[dict[str, Any]] = []
        for path in sorted(claims_dir.glob("*.json")):
            try:
                # read_bytes: json auto-detects UTF-8 per RFC 8259,
                # immune to the host locale's preferred encoding.
                loaded = json.loads(path.read_bytes())
            except json.JSONDecodeError as e:
                sys.exit(f"--claims-dir: invalid JSON in {path}: {e}")
            if not isinstance(loaded, list):
                sys.exit(
                    f"--claims-dir: expected a JSON array in {path}, "
                    f"got {type(loaded).__name__}"
                )
            claims.extend(loaded)
        print(json.dumps(rank_claims(claims)))
    else:
        print(json.dumps(rank_claims(json.load(sys.stdin))))
