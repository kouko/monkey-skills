"""Prompt builder functions for deep-research.

All prompt text is verbatim from:
  docs/loom/specs/deep-research-decompiled-source.md §Prompts

Do NOT paraphrase. Reviewers diff against the reference.

CLI:
  python prompts.py scope     --question Q
  python prompts.py search    --angle JSON --question Q
  python prompts.py fetch     --source JSON --label L --question Q
  python prompts.py verify      --claim JSON --voter-idx N --question Q
  python prompts.py attribution --claim JSON --question Q
  python prompts.py synthesis   --question Q --confirmed-block B \\
                                --killed-block B --confirmed-count N
"""
from __future__ import annotations

from schemas import VOTES_PER_CLAIM, REFUTATIONS_REQUIRED


def scope_prompt(question: str) -> str:
    """Return the SCOPE prompt with {QUESTION} interpolated."""
    return f"""\
Decompose this research question into complementary search angles.

## Question
{question}

## Task
Generate 5 distinct web search queries that together cover the question from different angles. Pick angles that suit the question's domain. Examples:
- broad/primary  · academic/technical  · recent news  · contrarian/skeptical  · practitioner/implementation
- For medical: anatomy · common causes · serious differentials · authoritative refs · red flags
- For tech: state-of-art · benchmarks · limitations · industry adoption · cost/tradeoffs

Make queries specific enough to surface high-signal results. Avoid redundancy.
Return: the question (verbatim or lightly normalized), a 1-2 sentence decomposition strategy, and the angles.

Structured output only."""


def search_prompt(angle: dict, question: str) -> str:
    """Return the SEARCH prompt for one angle.

    angle must have keys: label, query
    angle may have key: rationale (defaults to "")
    """
    label = angle["label"]
    rationale = angle.get("rationale", "")
    query = angle["query"]
    return f"""\
## Web Searcher: {label}

Research question: "{question}"

Your angle: **{label}** — {rationale}
Search query: `{query}`

## Task
Use WebSearch with the query above (or a refined version). Return the top 4-6 most relevant results.
Rank by relevance to the ORIGINAL question, not just the search query. Skip obvious SEO spam/content farms.
Include a short snippet capturing why each result is relevant.

Structured output only."""


def fetch_prompt(source: dict, angle: str, question: str) -> str:
    """Return the FETCH prompt for one source.

    source must have keys: url, title
    angle is the search-angle label string
    """
    url = source["url"]
    title = source["title"]
    return f"""\
## Source Extractor

Research question: "{question}"

Fetch and extract key claims from this source:
**URL:** {url}
**Title:** {title}
**Found via:** {angle} search

## Task
1. Use WebFetch to retrieve the page content.
2. Assess source quality: primary research/institution? secondary reporting? blog/opinion? forum? unreliable?
3. Extract 2-5 claims that bear on the research question. Each claim must:
   - be a concrete statement (not a vague generality)
   - include a direct quote from the source as support
   - be rated central/supporting/tangential to the research question
   - be tagged with claimType: "fact" (a checkable, verifiable proposition) or "opinion" (a viewpoint, judgment, or interpretation)
4. If a single source statement mixes a factual component with an opinion component (e.g. "GDP grew 3%, which proves the policy failed"), decompose it into TWO separate claim objects — one claimType: "fact" claim for the factual component, one claimType: "opinion" claim for the opinion component — rather than emitting one ambiguously-typed claim. If a statement cannot be cleanly decomposed, do not guess: keep it as a single claim and default claimType to "fact" (never default an undecomposable statement to "opinion" — uncertainty always resolves toward the stricter check).
5. Whenever a claim (fact OR opinion) has a natural attributable source — a named person, organization, or institution the claim/view is attributed to — capture it in heldBy. This applies equally to both claimTypes, not just opinions.
6. Note publish date if available.

If the fetch fails or the page is irrelevant/paywalled, return claims: [] and sourceQuality: "unreliable".

Structured output only."""


def verify_prompt(claim: dict, voter_idx: int, question: str) -> str:
    """Return the VERIFY prompt for one voter on one claim.

    claim must have keys: claim, sourceQuality, quote, and one of
    sourceUrl or url (sourceUrl preferred; url is a tolerated fallback)
    voter_idx is 0-based; displayed as voter_idx+1/{VOTES_PER_CLAIM}
    """
    v = voter_idx + 1
    claim_text = claim["claim"]
    source_url = claim.get("sourceUrl") or claim.get("url", "")
    source_quality = claim["sourceQuality"]
    quote = claim["quote"]
    return f"""\
## Adversarial Claim Verifier (voter {v}/{VOTES_PER_CLAIM})

Be SKEPTICAL. Try to REFUTE this claim. ≥{REFUTATIONS_REQUIRED}/{VOTES_PER_CLAIM} refutations kill it.

## Research question
{question}

## Claim under review
"{claim_text}"

**Source:** {source_url} ({source_quality})
**Supporting quote:** "{quote}"

## Checklist
1. Is the claim actually supported by the quote, or is it an overreach/misread?
2. WebSearch for contradicting evidence — does any credible source dispute or heavily qualify this?
3. Is the source quality sufficient for the claim's strength? (extraordinary claims need primary sources)
4. Is the claim outdated? (check dates — old claims about fast-moving fields are suspect)
5. Is this a marketing claim / press release / cherry-picked benchmark / forum speculation?

**refuted=true** if: unsupported by quote / contradicted / low-quality source for strong claim / outdated / marketing fluff.
**refuted=false** ONLY if: claim is well-supported, current, and source quality matches claim strength.
Default to refuted=true if uncertain.

Structured output only. Evidence MUST be specific."""


def attribution_prompt(claim: dict, question: str) -> str:
    """Return the ATTRIBUTION prompt for one opinion-routed claim.

    Modeled structurally on verify_prompt, but asks a narrower question:
    does the cited source actually hold/express this view, per the quote?
    This is NOT an adversarial-refutation prompt — no "try to refute"
    framing, no counter-evidence WebSearch instruction. Emits a verdict
    conforming to ATTRIBUTION_VERDICT_SCHEMA.

    claim must have keys: claim, quote, and one of sourceUrl or url
    (sourceUrl preferred; url is a tolerated fallback)
    claim may have key: heldBy (who the view is attributed to)
    """
    claim_text = claim["claim"]
    source_url = claim.get("sourceUrl") or claim.get("url", "")
    quote = claim["quote"]
    held_by = claim.get("heldBy", "")
    held_by_line = f"**Attributed to:** {held_by}\n" if held_by else ""
    return f"""\
## Attribution Checker

Confirm whether the cited source actually holds/expresses this view — do NOT try to refute it.

## Research question
{question}

## Claim under review
"{claim_text}"

**Source:** {source_url}
{held_by_line}**Supporting quote:** "{quote}"

## Task
Does the quote show the source actually holding/expressing this view (not the reader's paraphrase or overreach)?

**attributionConfirmed=true** if: the quote clearly shows the source holding/expressing this view.
**attributionConfirmed=false** if: the quote does not support that attribution, is a misread, or overreaches.

Structured output only. Evidence MUST be specific."""


def synthesis_prompt(
    question: str,
    confirmed_block: str,
    killed_block: str,
    n_confirmed: int,
) -> str:
    """Return the SYNTHESIS prompt.

    confirmed_block: pre-formatted block of confirmed claims
    killed_block: pre-formatted block of refuted claims (with header)
    n_confirmed: count of confirmed claims (for the header line)
    """
    return f"""\
## Synthesis: research report

**Question:** {question}

{n_confirmed} claims survived {VOTES_PER_CLAIM}-vote adversarial verification. Merge semantic duplicates and synthesize.

## Confirmed claims
{confirmed_block}
{killed_block}

## Instructions
1. Identify claims that say the same thing — merge them, combine their sources.
2. Group related claims into coherent findings. Each finding should directly address the research question.
3. Assign confidence per finding: high (multiple primary sources, unanimous votes), medium (secondary sources or split votes), low (single source or blog-quality).
4. Write a 3-5 sentence executive summary answering the research question.
5. Note caveats: what's uncertain, what sources were weak, what time-sensitivity applies.
6. List 2-4 open questions that emerged but weren't answered.

Structured output only."""


def _main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Print an assembled deep-research prompt to stdout.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scope = sub.add_parser("scope")
    p_scope.add_argument("--question", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("--angle", required=True, help="JSON: {label, query, rationale?}")
    p_search.add_argument("--question", required=True)

    p_fetch = sub.add_parser("fetch")
    p_fetch.add_argument("--source", required=True, help="JSON: {url, title}")
    p_fetch.add_argument("--label", required=True, help="search-angle label")
    p_fetch.add_argument("--question", required=True)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--claim", required=True, help="JSON: {claim, sourceUrl, sourceQuality, quote}")
    p_verify.add_argument("--voter-idx", type=int, required=True)
    p_verify.add_argument("--question", required=True)

    p_attribution = sub.add_parser("attribution")
    p_attribution.add_argument("--claim", required=True, help="JSON: {claim, sourceUrl, quote, heldBy?}")
    p_attribution.add_argument("--question", required=True)

    p_synth = sub.add_parser("synthesis")
    p_synth.add_argument("--question", required=True)
    p_synth.add_argument("--confirmed-block", required=True)
    p_synth.add_argument("--killed-block", required=True)
    p_synth.add_argument("--confirmed-count", type=int, required=True)

    args = parser.parse_args(argv)

    if args.command == "scope":
        print(scope_prompt(question=args.question))
    elif args.command == "search":
        print(search_prompt(angle=json.loads(args.angle), question=args.question))
    elif args.command == "fetch":
        print(fetch_prompt(source=json.loads(args.source), angle=args.label, question=args.question))
    elif args.command == "verify":
        print(verify_prompt(claim=json.loads(args.claim), voter_idx=args.voter_idx, question=args.question))
    elif args.command == "attribution":
        print(attribution_prompt(claim=json.loads(args.claim), question=args.question))
    elif args.command == "synthesis":
        print(synthesis_prompt(
            question=args.question,
            confirmed_block=args.confirmed_block,
            killed_block=args.killed_block,
            n_confirmed=args.confirmed_count,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
