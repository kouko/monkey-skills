"""Prompt builder functions for deep-research.

All prompt text is verbatim from:
  docs/code-toolkit/specs/deep-research-decompiled-source.md §Prompts

Do NOT paraphrase. Reviewers diff against the reference.
"""

from deep_research.schemas import VOTES_PER_CLAIM, REFUTATIONS_REQUIRED


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
3. Extract 2-5 FALSIFIABLE claims that bear on the research question. Each claim must:
   - be a concrete, checkable statement (not vague generalities)
   - include a direct quote from the source as support
   - be rated central/supporting/tangential to the research question
4. Note publish date if available.

If the fetch fails or the page is irrelevant/paywalled, return claims: [] and sourceQuality: "unreliable".

Structured output only."""


def verify_prompt(claim: dict, voter_idx: int, question: str) -> str:
    """Return the VERIFY prompt for one voter on one claim.

    claim must have keys: claim, sourceUrl, sourceQuality, quote
    voter_idx is 0-based; displayed as voter_idx+1/{VOTES_PER_CLAIM}
    """
    v = voter_idx + 1
    claim_text = claim["claim"]
    source_url = claim["sourceUrl"]
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
