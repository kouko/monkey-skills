"""Pure synthesis helpers: prompt blocks + stats + markdown render.

Extracted verbatim from the deep-research pipeline (core.py synthesis
helpers + cli.py markdown renderer). Flat imports — this module lives in
scripts/ and is invoked directly (NOT as deep_research.synthesis).

CLI (__main__):
  synthesis.py blocks  — payload {ranked_claims, vote_results, verdicts_per_claim}
                         → stdout {confirmed_block, killed_block}
  synthesis.py report  — payload {report, ranked_claims, angles, all_claims,
                                 confirmed, killed, verdicts_per_claim}
                         → stdout {stats, markdown}

  Payload source: stdin JSON (default), or per-key file flags (repeatable;
  when ANY flag is present, stdin is NOT read):
    --key NAME=FILE      payload[NAME] = JSON value parsed from FILE
    --key-dir NAME=DIR   payload[NAME] = concatenation of all *.json arrays
                         in DIR, filename-sorted
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Synthesis helpers
# ---------------------------------------------------------------------------

_CONF_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}


def _source_url(claim: dict) -> str:
    """Read a claim's source URL, tolerating either key name.

    Extraction is documented to emit `sourceUrl` (SKILL.md Stage 3), but a
    claim keyed `url` instead must not silently lose its source at this
    stage — mirrors the same fallback `prompts.py`'s `verify_prompt()` uses.
    """
    return claim.get("sourceUrl") or claim.get("url", "")


def _is_opinion_verdicts(verdicts: list[dict]) -> bool:
    """True when `verdicts` is Stage 5b's one-element attribution-verdict list.

    Discriminator: the attribution-verdict shape carries `attributionConfirmed`
    (schemas.ATTRIBUTION_VERDICT_SCHEMA) and never `refuted`/`confidence` — the
    fact-path verdict shape (schemas.VERDICT_SCHEMA). Checking key presence
    (rather than list length) stays correct even though both are, by design,
    "a list of verdict dicts" (SKILL.md Stage 5 Merge: "never a bare boolean").
    """
    return any(v and "attributionConfirmed" in v for v in verdicts)


def _confirmed_block(
    ranked_claims: list[dict],
    vote_results: list[bool],
    verdicts_per_claim: list[list[dict]],
) -> str:
    """Build the confirmed-claims block for the synthesis prompt.

    Fact-shaped claims (spec §SYNTHESIS {block}):
      ### [i] {claim}
      Vote: {valid-refuted}-{refuted} · Source: {url} ({quality})
      Quote: "{quote}"
      Verifier evidence ({confidence}): {evidence}

    Opinion-shaped claims (Stage 5b attribution-confirmation, single verdict,
    no refuted/confidence keys — must NOT be rendered with fact vocabulary):
      ### [i] {claim}
      Attributed opinion · Source: {url} ({quality})
      Quote: "{quote}"
      Attribution evidence: {evidence}
      Attributed to: {heldBy}   (only when heldBy is present)
    """
    lines: list[str] = []
    for i, (claim, survived, verdicts) in enumerate(
        zip(ranked_claims, vote_results, verdicts_per_claim)
    ):
        if not survived:
            continue
        if _is_opinion_verdicts(verdicts):
            verdict = verdicts[0] if verdicts else {}
            evidence = verdict.get("evidence", "") if verdict else ""
            held_by = claim.get("heldBy", "")
            block = (
                f"### [{i}] {claim['claim']}\n"
                f"Attributed opinion · "
                f"Source: {_source_url(claim)} ({claim.get('sourceQuality', '')})\n"
                f"Quote: \"{claim.get('quote', '')}\"\n"
                f"Attribution evidence: {evidence}"
            )
            if held_by:
                block += f"\nAttributed to: {held_by}"
            lines.append(block)
            continue
        # None entries are abstentions (Stage 5: "A voter that fails or
        # returns nothing ... record its vote as null") — must be dropped
        # before counting, matching rank.py's quorum_survives convention
        # (`[v for v in verdicts if v is not None]`), or an abstention
        # renders as a phantom non-refuting vote.
        valid_verdicts = [v for v in verdicts if v is not None]
        valid = len(valid_verdicts)
        refuted_count = sum(1 for v in valid_verdicts if v.get("refuted"))
        non_refuting = [v for v in valid_verdicts if not v.get("refuted")]
        best = min(
            non_refuting,
            key=lambda v: _CONF_RANK.get(v.get("confidence", "low"), 2),
            default=None,
        )
        conf = best.get("confidence", "low") if best else "low"
        evidence = best.get("evidence", "") if best else ""
        lines.append(
            f"### [{i}] {claim['claim']}\n"
            f"Vote: {valid - refuted_count}-{refuted_count} · "
            f"Source: {_source_url(claim)} ({claim.get('sourceQuality', '')})\n"
            f"Quote: \"{claim.get('quote', '')}\"\n"
            f"Verifier evidence ({conf}): {evidence}"
        )
    return "\n".join(lines)


def _killed_block(ranked_claims: list[dict], vote_results: list[bool]) -> str:
    """Build the refuted-claims block for the synthesis prompt."""
    lines: list[str] = ["## Refuted claims (for transparency)"]
    for claim, survived in zip(ranked_claims, vote_results):
        if not survived:
            lines.append(
                f"- \"{claim['claim']}\" "
                f"({_source_url(claim)})"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Collect + stats helpers
# ---------------------------------------------------------------------------

def _collect_sources(ranked_claims: list[dict]) -> list[str]:
    """Return unique source URLs in ranked-claim insertion order."""
    sources: list[str] = []
    seen_sources: set[str] = set()
    for claim in ranked_claims:
        url = _source_url(claim)
        if url and url not in seen_sources:
            sources.append(url)
            seen_sources.add(url)
    return sources


def _build_stats(
    angles: list[dict],
    sources: list[str],
    all_claims: list[dict],
    ranked_claims: list[dict],
    confirmed: list[dict],
    killed: list[dict],
    verdicts_per_claim: list[list[dict]],
) -> dict[str, int]:
    """Compute pipeline stats dict.

    agentCalls formula: 1 + angles + sources + verify_calls + 1, where
    verify_calls = sum(len(v) for v in verdicts_per_claim). A fact-routed
    claim's verdict list has VOTES_PER_CLAIM(3) elements (SKILL.md Stage
    5a's 3-voter quorum); an opinion-routed claim's has exactly 1 (Stage
    5b's single attribution-confirmation check). Reading the per-claim
    call cost off the actual verdict-list length — rather than assuming
    every verified claim cost a uniform VOTES_PER_CLAIM — is what makes
    this correct for a mixed fact+opinion claim set.
    """
    n_verified = len(ranked_claims)
    verify_calls = sum(len(v) for v in verdicts_per_claim)
    return {
        "angles": len(angles),
        "sourcesFetched": len(sources),
        "claimsExtracted": len(all_claims),
        "claimsVerified": n_verified,
        "confirmed": len(confirmed),
        "killed": len(killed),
        "agentCalls": 1 + len(angles) + len(sources) + verify_calls + 1,
    }


# ---------------------------------------------------------------------------
# Markdown renderer (extracted from cli.py)
# ---------------------------------------------------------------------------

def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"# {report.get('question', 'Research Report')}\n")

    summary = report.get("summary", "")
    if summary:
        lines.append("## Summary\n")
        lines.append(summary + "\n")

    findings = report.get("findings", [])
    if findings:
        lines.append("## Findings\n")
        for f in findings:
            confidence = f.get("confidence", "")
            claim = f.get("claim", "")
            sources = f.get("sources", [])
            evidence = f.get("evidence", "")
            lines.append(f"- **{claim}** *(confidence: {confidence})*")
            for src in sources:
                lines.append(f"  - <{src}>")
            if evidence:
                lines.append(f"  - Evidence: {evidence}")

    caveats = report.get("caveats", "")
    if isinstance(caveats, list):
        caveats = "\n".join(caveats)
    if caveats:
        lines.append("\n## Caveats\n")
        lines.append(caveats)

    open_qs = report.get("openQuestions", [])
    if open_qs:
        lines.append("\n## Open Questions\n")
        for q in open_qs:
            lines.append(f"- {q}")

    refuted = report.get("refuted", [])
    if refuted:
        lines.append("\n## Refuted Claims\n")
        for r in refuted:
            lines.append(f"- {r.get('claim', '')}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _run_blocks(payload: dict) -> dict:
    confirmed_block = _confirmed_block(
        payload["ranked_claims"],
        payload["vote_results"],
        payload["verdicts_per_claim"],
    )
    killed_block = _killed_block(payload["ranked_claims"], payload["vote_results"])
    return {"confirmed_block": confirmed_block, "killed_block": killed_block}


def _run_report(payload: dict) -> dict:
    ranked_claims = payload["ranked_claims"]
    sources = _collect_sources(ranked_claims)
    stats = _build_stats(
        payload["angles"],
        sources,
        payload["all_claims"],
        ranked_claims,
        payload["confirmed"],
        payload["killed"],
        payload["verdicts_per_claim"],
    )
    markdown = _render_markdown(payload["report"])
    return {"stats": stats, "markdown": markdown}


def _load_json_file(flag: str, name: str, path: Path) -> Any:
    """Parse one JSON file (bytes → RFC 8259 UTF-8 auto-detect).

    Read/parse failures re-raise as ValueError naming the offender, so
    main()'s handler prints a clean one-line stderr message (no traceback).
    """
    try:
        return json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{flag} {name}: {path}: {exc}") from exc


def _payload_from_flags(flag_args: list[str]) -> dict:
    """Assemble the payload dict from repeatable --key / --key-dir flags."""
    payload: dict = {}
    i = 0
    while i < len(flag_args):
        flag = flag_args[i]
        if flag not in ("--key", "--key-dir") or i + 1 >= len(flag_args):
            raise ValueError(
                f"expected --key NAME=FILE or --key-dir NAME=DIR, got {flag!r}"
            )
        name, sep, path = flag_args[i + 1].partition("=")
        if not (name and sep and path):
            raise ValueError(
                f"malformed {flag} argument {flag_args[i + 1]!r} (expected NAME=PATH)"
            )
        if flag == "--key":
            payload[name] = _load_json_file(flag, name, Path(path))
        else:
            dir_path = Path(path)
            if not dir_path.is_dir():
                raise ValueError(f"--key-dir {name}: not a directory: {path}")
            merged: list = []
            for part in sorted(dir_path.glob("*.json")):
                value = _load_json_file(flag, name, part)
                if not isinstance(value, list):
                    raise ValueError(
                        f"--key-dir {name}: {part} is not a JSON array"
                    )
                merged.extend(value)
            payload[name] = merged
        i += 2
    return payload


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] not in ("blocks", "report"):
        name = args[0] if args else "(none)"
        print(
            f"unknown subcommand {name!r}; expected one of {{blocks|report}}",
            file=sys.stderr,
        )
        return 1
    if args[1:]:
        try:
            payload = _payload_from_flags(args[1:])
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        payload = json.load(sys.stdin)
    result = _run_blocks(payload) if args[0] == "blocks" else _run_report(payload)
    json.dump(result, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
