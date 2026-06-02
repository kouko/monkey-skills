# Decompiled source — CC built-in `deep-research` (v2.1.159)

Verbatim reference for the Python port. Extracted from
`~/.local/share/claude/versions/2.1.159`. **Port these byte-for-byte**
(prompt text, schema shapes, quorum rule, ranking maps). The orchestration
shell (Workflow primitives) is replaced by asyncio; the content below is NOT.

## Constants

```
VOTES_PER_CLAIM = 3
REFUTATIONS_REQUIRED = 2
MAX_FETCH = 15
MAX_VERIFY_CLAIMS = 25
```

## Ranking maps

```
relRank  = { high: 0, medium: 1, low: 2 }                                  # search relevance
impRank   = { central: 0, supporting: 1, tangential: 2 }                   # claim importance
qualRank  = { primary: 0, secondary: 1, blog: 2, forum: 3, unreliable: 4 } # source quality
confRank  = { high: 0, medium: 1, low: 2 }                                 # verifier confidence
```

Ranked claims sort key: `(impRank[importance], qualRank[sourceQuality])`, then slice to `MAX_VERIFY_CLAIMS`.

## URL normalization (dedup key)

```js
const normURL = u => {
  try {
    const p = new URL(u)
    return (p.hostname.replace(/^www\./, "") + p.pathname.replace(/\/$/, "")).toLowerCase()
  } catch { return u.toLowerCase() }
}
```
Python: strip leading `www.` from hostname, strip trailing `/` from path, lowercase the `host+path`. On parse failure, lowercase the raw string.

## Quorum rule (verify survival)

```js
const valid = verdicts.filter(Boolean)            // drop null votes (abstain)
const refuted = valid.filter(v => v.refuted).length
const abstained = VOTES_PER_CLAIM - valid.length
const survives = valid.length >= REFUTATIONS_REQUIRED && refuted < REFUTATIONS_REQUIRED
```
Survive ONLY if: ≥2 valid votes AND fewer than 2 refuting. All-abstain or
1-valid-only → killed (unadjudicated). This guards the "all-abstain →
refuted=0 → false survive" bug.

## Schemas (verbatim)

```js
const SCOPE_SCHEMA = {
  type: "object", required: ["question", "angles", "summary"],
  properties: {
    question: { type: "string" },
    summary: { type: "string" },
    angles: { type: "array", minItems: 3, maxItems: 6, items: {
      type: "object", required: ["label", "query"],
      properties: { label: {type:"string"}, query: {type:"string"}, rationale: {type:"string"} },
    }},
  },
}
const SEARCH_SCHEMA = {
  type: "object", required: ["results"],
  properties: {
    results: { type: "array", maxItems: 6, items: {
      type: "object", required: ["url", "title", "relevance"],
      properties: { url:{type:"string"}, title:{type:"string"}, snippet:{type:"string"},
                    relevance: { enum: ["high","medium","low"] } },
    }},
  },
}
const EXTRACT_SCHEMA = {
  type: "object", required: ["claims", "sourceQuality"],
  properties: {
    sourceQuality: { enum: ["primary","secondary","blog","forum","unreliable"] },
    publishDate: { type: "string" },
    claims: { type: "array", maxItems: 5, items: {
      type: "object", required: ["claim", "quote", "importance"],
      properties: { claim:{type:"string"}, quote:{type:"string"},
                    importance: { enum: ["central","supporting","tangential"] } },
    }},
  },
}
const VERDICT_SCHEMA = {
  type: "object", required: ["refuted", "evidence", "confidence"],
  properties: {
    refuted: { type: "boolean" },
    evidence: { type: "string" },
    confidence: { enum: ["high","medium","low"] },
    counterSource: { type: "string" },
  },
}
const REPORT_SCHEMA = {
  type: "object", required: ["summary", "findings", "caveats"],
  properties: {
    summary: { type: "string" },
    findings: { type: "array", items: {
      type: "object", required: ["claim","confidence","sources","evidence"],
      properties: { claim:{type:"string"}, confidence:{enum:["high","medium","low"]},
                    sources:{type:"array",items:{type:"string"}}, evidence:{type:"string"},
                    vote:{type:"string"} },
    }},
    caveats: { type: "string" },
    openQuestions: { type: "array", items: { type: "string" } },
  },
}
```

## Prompts (verbatim)

### SCOPE
```
Decompose this research question into complementary search angles.

## Question
{QUESTION}

## Task
Generate 5 distinct web search queries that together cover the question from different angles. Pick angles that suit the question's domain. Examples:
- broad/primary  · academic/technical  · recent news  · contrarian/skeptical  · practitioner/implementation
- For medical: anatomy · common causes · serious differentials · authoritative refs · red flags
- For tech: state-of-art · benchmarks · limitations · industry adoption · cost/tradeoffs

Make queries specific enough to surface high-signal results. Avoid redundancy.
Return: the question (verbatim or lightly normalized), a 1-2 sentence decomposition strategy, and the angles.

Structured output only.
```

### SEARCH  (per angle)
```
## Web Searcher: {angle.label}

Research question: "{QUESTION}"

Your angle: **{angle.label}** — {angle.rationale}
Search query: `{angle.query}`

## Task
Use WebSearch with the query above (or a refined version). Return the top 4-6 most relevant results.
Rank by relevance to the ORIGINAL question, not just the search query. Skip obvious SEO spam/content farms.
Include a short snippet capturing why each result is relevant.

Structured output only.
```

### FETCH  (per source)
```
## Source Extractor

Research question: "{QUESTION}"

Fetch and extract key claims from this source:
**URL:** {source.url}
**Title:** {source.title}
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

Structured output only.
```

### VERIFY  (per claim, per voter)
```
## Adversarial Claim Verifier (voter {v+1}/{VOTES_PER_CLAIM})

Be SKEPTICAL. Try to REFUTE this claim. ≥{REFUTATIONS_REQUIRED}/{VOTES_PER_CLAIM} refutations kill it.

## Research question
{QUESTION}

## Claim under review
"{claim.claim}"

**Source:** {claim.sourceUrl} ({claim.sourceQuality})
**Supporting quote:** "{claim.quote}"

## Checklist
1. Is the claim actually supported by the quote, or is it an overreach/misread?
2. WebSearch for contradicting evidence — does any credible source dispute or heavily qualify this?
3. Is the source quality sufficient for the claim's strength? (extraordinary claims need primary sources)
4. Is the claim outdated? (check dates — old claims about fast-moving fields are suspect)
5. Is this a marketing claim / press release / cherry-picked benchmark / forum speculation?

**refuted=true** if: unsupported by quote / contradicted / low-quality source for strong claim / outdated / marketing fluff.
**refuted=false** ONLY if: claim is well-supported, current, and source quality matches claim strength.
Default to refuted=true if uncertain.

Structured output only. Evidence MUST be specific.
```

### SYNTHESIS
```
## Synthesis: research report

**Question:** {QUESTION}

{N} claims survived {VOTES_PER_CLAIM}-vote adversarial verification. Merge semantic duplicates and synthesize.

## Confirmed claims
{block}   # per claim: "### [i] {claim}\nVote: {x}-{y} · Source: {url} ({quality})\nQuote: \"{quote}\"\nVerifier evidence ({confidence}): {evidence}\n"
{killedBlock}  # "## Refuted claims (for transparency)\n- \"{claim}\" ({url}, vote {x}-{y})"

## Instructions
1. Identify claims that say the same thing — merge them, combine their sources.
2. Group related claims into coherent findings. Each finding should directly address the research question.
3. Assign confidence per finding: high (multiple primary sources, unanimous votes), medium (secondary sources or split votes), low (single source or blog-quality).
4. Write a 3-5 sentence executive summary answering the research question.
5. Note caveats: what's uncertain, what sources were weak, what time-sensitivity applies.
6. List 2-4 open questions that emerged but weren't answered.

Structured output only.
```

## Pipeline shape (for core.py orchestration)

- **Scope**: 1 llm call → angles[]
- **Search → dedup → Fetch**: `pipeline(angles, search_stage, fetch_stage)` — NO barrier
  (each angle's results stream into dedup+fetch as they complete). dedup mutates
  shared `seen` Map + `fetchSlots` budget across angles.
- **Rank**: barrier — full claim pool assembled, then sort + slice top 25.
- **Verify**: `parallel(rankedClaims.map(claim => parallel(3 voters)))` — barrier.
- **Synthesize**: 1 llm call → Report.
- Fallback returns: 0 claims / all-refuted / synthesis-None each return a
  salvage dict (see brief §Error and core degradation task T10).
- agentCalls stat = 1 + angles + sources + (verified × VOTES_PER_CLAIM) + 1.
