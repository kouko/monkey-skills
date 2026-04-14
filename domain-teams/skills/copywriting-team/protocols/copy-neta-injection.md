# Protocol: Copy Neta Injection（Phase A-D post-production layer for cultural-reference injection）

**When to use**: When a brief has been pre-approved for neta (pop culture / subculture / meme / 流行語) injection during intake (`copywriting-brainstorming.md` neta opt-in Level 2 field = Yes), AND a base-framework copy draft has been produced by `write-short-form-copy.md`, `write-long-form-copy.md`, `write-mid-form-copy.md`, or similar. This protocol applies neta injection as a **post-production layer** on top of already-structured copy.

**When NOT to use**:
- Brand voice or channel policy forbids neta injection (confirmed at intake)
- Base-framework copy is not yet drafted (neta injection is post-production, not initial drafting)
- Brief is for evergreen copy with >6-month shelf life (meme half-life is 4-6 months per Shifman 2014; current memes will expire — prefer evergreen references only, i.e., Technique 1 Reversal on classics or Technique 4 Cross-domain Mapping)
- Audience profile is broad / general-public (Technique 3 Subcultural Capital / tribal signal reference would alienate adjacent audiences; other techniques require recognition that broad audiences may not share)

**Output**: Copy draft with neta injection applied, annotated with (a) reference source URL, (b) technique used per `neta-injection-techniques.md`, (c) neta-safety-gate verdict.

**Grounds on**:
- `../standards/neta-injection-techniques.md` — 4 techniques (Reversal / Substitution / Subcultural Capital / Cross-domain Mapping)
- `../standards/neta-websearch-pipeline.md` — Phase A-D pipeline definition
- `../standards/persuasion-ethics.md` — for dark-pattern + 景品表示法 cross-check
- `../rubrics/neta-safety-gate.md` — SHOULD gate at Phase D

## Pre-Phase: Opt-in Verification

Before executing Phase A-D, verify:

1. Intake Understanding Summary (`copywriting-brainstorming.md` output) contains explicit "neta 使用許可 = Yes" (neta opt-in Level 2 field)
2. Base-framework draft exists (copy structure from short-form / mid-form / long-form / light-action already produced)
3. Shelf-life requirement is compatible (copy not intended for >6-month evergreen use, unless using evergreen-only techniques)
4. Audience profile is sufficiently specific to enable Phase A retrieval

If any check fails: return BLOCKED to main worker with specific gap identified.

## Phase A: Audience Context Retrieval

Retrieve up-to-date cultural context via WebSearch (site-locked) per `neta-websearch-pipeline.md` §Phase A.

1. **Parse intake audience profile**: age band, platform presence, subcultural affiliations. From `copywriting-brainstorming.md` Q3 Target audience output.

2. **Select domain allow-list** from the Tier 2 standard's table:
   - SNS-native youth: X JP, TikTok, niconico / Reddit, Twitter/X, TikTok
   - Anime/manga fandom: 2ch, X JP, pixiv / Reddit r/anime, Crunchyroll forums
   - Business / adult professional: はてなブックマーク, NewsPicks / LinkedIn, FT, WSJ
   - Gaming: ふたば, niconico 実況 / Reddit r/games, Steam forums
   - Custom: combine or narrow based on specific audience segment

3. **Execute site-locked WebSearch queries** using Google `site:` operator (documented in Google Search Central):
   ```
   site:twitter.com OR site:x.com [topic] lang:ja after:2026-01-01
   site:reddit.com/r/[relevant_subreddit] [topic]
   site:niconico.jp [topic]
   ```
   Adjust `after:` date to approximate meme half-life (6 months back).

4. **Build candidate catalog**: 5-15 candidate references with:
   - Source URL
   - Post date (for recency)
   - Recognition assessment (how widely known within target audience)
   - In-group context (which subculture/platform originated)

5. **Recency filter**: prefer ≤6 months old. References 6-12 months old require re-verification of continued currency. References >12 months either qualify as "classic" (evergreen) or are expired — do NOT use as "current."

6. **Failure handling**:
   - Zero results: audience profile too narrow; return BLOCKED asking user to broaden or redirect to evergreen-only techniques
   - Outdated-only results: signal user that Technique 3 Subcultural Capital with current memes is not viable; propose Techniques 1 / 2 / 4 (Reversal / Substitution / Cross-domain Mapping) on evergreen references

## Phase B: Structural Deconstruction (Chain-of-Thought)

For each promising candidate from Phase A, apply Chain-of-Thought prompting (Wei et al. 2022, arXiv:2201.11903) with ReAct interleaving (Yao et al. 2022, arXiv:2210.03629).

1. **For each candidate, reason through**:

   ```
   Thought 1: What is this reference's exact canonical form?
     [original phrase / visual / structural pattern]

   Thought 2: Which element is the recognition hook?
     [the specific phrase / frame / visual token that makes it recognizable]

   Thought 3: Which technique does this map to?
     - Technique 1: Reversal (subvertising) if subvertible
     - Technique 2: Substitution (snowclone / 大喜利) if template-based
     - Technique 3: Subcultural Capital (tribal signal / 界隈消費) if in-group code
     - Technique 4: Cross-domain Mapping (conceptual simplification / 次元降下) if analog mapping

   Thought 4: What is the reusable template (slots + fixed parts)?
     [template with [X], [Y], [Z] slots and non-swappable frame]

   Thought 5: What reader cognition will it trigger?
     [what reader recognizes + what incongruity they resolve]
   ```

2. **Invoke ReAct for uncertainty**: when a candidate's currency or in-group scope is uncertain, interleave WebSearch:

   ```
   Thought: Is this reference currency verified?
   Act: site:[platform] [reference] 2026
   Observation: [WebSearch results]
   Thought: [continue reasoning based on results]
   ```

3. **Output per candidate**: structured deconstruction record `{canonical form, recognition hook, technique mapping, reusable template, predicted reader cognition, currency verification status}`.

4. **Shortlist**: select 2-3 strongest candidates for Phase C parameter stitching. Discard weaker candidates with brief note explaining why (for audit trail).

## Phase C: Parameter Stitching (Strict Replacement Rule)

Apply the Strict Replacement Rule from `neta-websearch-pipeline.md` §Phase C.

1. **For each shortlisted candidate**:
   - Start from the reusable template from Phase B
   - Enumerate what each slot must encode for the product message
   - Fill slots with minimum-drift parameters (prefer syllable / mora count matching; prefer similar grammatical category)
   - Preserve ALL non-slot elements verbatim

2. **Post-fill validation**:
   - Re-read the filled version against the Phase B canonical form
   - Confirm recognition hook is intact
   - Confirm the product message maps onto the template's rhetorical force

3. **Iteration discipline**:
   - If a single parameter feels wrong, iterate ONLY on that parameter
   - Do NOT relax the Strict Replacement Rule by modifying multiple slots or bending template structure
   - If no parameter fits, the candidate is a **bad fit** — discard and try next candidate

4. **Output**: 2-3 draft versions of copy with neta injection applied, each annotated with (a) reference source URL, (b) technique used, (c) slot-fill rationale.

## Phase D: Vibe & Safety Check

Run `../rubrics/neta-safety-gate.md` SHOULD gate on each draft.

### Pre-gate SELF Check (worker-side)

Before launching evaluator, verify:

1. **Recognition hook preserved**: can the reference still be recognized at full fidelity?
2. **Fallback readability**: can a reader who misses the reference still parse the copy's surface meaning?
3. **Load-bearing neta**: does the reference carry product meaning, or is it decorative?
4. **Currency verified**: has the reference been WebSearch-confirmed within meme half-life window?
5. **ステマ risk**: could this be mistaken for authentic organic UGC? (If yes, brand disclosure must be explicit elsewhere.)

If any answer is uncertain, revise the draft before launching the gate.

### Gate launch

Launch `evaluator` agent with:
- `gate_file`: `{base_path}/rubrics/neta-safety-gate.md`
- `standards`: all 17 copywriting-team standards (see SKILL.md Resource Manifest)
- `artifact`: the neta-injected draft(s)
- `requirements`: original user brief + neta opt-in context + technique used

### Verdict handling

- **PASS**: deliver with attribution metadata. Proceed to SKILL.md MUST gates (Framework Adherence, Ethics, etc.) on the final copy.
- **PASS_WITH_NOTES** (yellow flags): deliver with explicit disclosure of flagged dimension + mitigation taken. Proceed to MUST gates.
- **NEEDS_REVISION** (red flag OR hard legal veto on copyright/ステマ):
  - Return to Phase C and try next parameter set, OR
  - Return to Phase B and try next candidate from Phase A catalog, OR
  - If all candidates exhausted, return BLOCKED with specific failure reason (recognition gap / legal risk / stale references / in-group mismatch)

**Hard legal vetoes are non-fungible**: a copyright or ステマ hard veto blocks delivery regardless of other PASSes. This is explicit in the rubric.

## Handoff

On successful Phase D completion, hand the neta-injected copy back to the invoking workflow (short-form / mid-form / long-form / light-action) for that workflow's standard MUST gates (Framework Adherence, Ethics). The neta-safety-gate is **in addition to**, not **in replacement of**, the base MUST gates.

Handoff document must include:
- Final neta-injected copy (single chosen version or 2-3 candidates)
- Per-candidate metadata: technique, reference source URL, Phase D verdict with flags
- Currency verification timestamp (so downstream reviewers can assess when the reference was confirmed current)
- Fallback readability note (how the copy reads for audiences who miss the reference)

## Rules

- **Always execute Phase A before Phase B**. Do not use the model's pre-training memory as a substitute for current context retrieval. Meme half-life is 4-6 months; pre-training data is typically older.
- **One technique per piece**. Density greater than one technique per キャッチコピー / one per opener block in long-form produces cringe rather than elegance (`jp-copy-craft-lineage.md` §眞木 principle).
- **Strict Replacement Rule is non-negotiable**. If a template doesn't fit the product's slot-grammar, pick a different template; do not bend structure.
- **Phase D hard legal vetoes are non-fungible**. Copyright + ステマ reds block delivery regardless of other dimensions.
- **Evergreen-only techniques** (Technique 1 Reversal on classics / Technique 4 Cross-domain Mapping) are the only safe choice for copy with >6-month shelf life.
- **Currency verification requires 2+ independent sources**. A single post does not prove a meme is alive; confirm via multiple platforms or references.
- **Route to this protocol only when intake opt-in = Yes**. Do not inject neta into copy whose intake did not authorize it.

## Anti-Patterns

- **Skipping Phase A "because I already know the memes"**. Model pre-training is 6-18 months old; memes from that era are likely expired. WebSearch is mandatory for currency verification.
- **Violating Strict Replacement Rule**. Modifying more than slots breaks recognition. If you're rewriting multiple elements, you've chosen the wrong template.
- **Using Phase D as a formality**. The safety gate is load-bearing — hard legal vetoes are real vetoes, not advisory.
- **Chaining multiple techniques**. Per `neta-injection-techniques.md` §Anti-Patterns: one technique per piece.
- **Running this protocol on copy that hasn't been base-framework drafted**. Neta injection is a post-production layer; without a solid base, it becomes decorative cleverness rather than compression.
- **Applying this protocol when intake opt-in is No**. Brand policy or channel policy may forbid neta; respect the intake decision.
- **Treating "general knowledge memes" as grounded**. Reference currency and in-group fit require WebSearch verification, not model intuition.
- **Declaring "no neta is possible"** when Phase A returns limited results. Evergreen techniques (Technique 1 Reversal on classics, Technique 4 Cross-domain Mapping conceptual metaphor) often still work when current memes are absent.
- **Producing a single candidate and stopping**. Phase C should generate 2-3 candidates so Phase D has choices; a single-candidate pipeline breaks when that one candidate fails gate.
- **Delivering without attribution metadata**. Downstream reviewers / evaluators need source URL + technique + verdict; omitting them breaks audit trail.
