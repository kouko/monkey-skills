# Protocol: Copy Neta Injection（Phase A-D post-production layer for cultural-reference injection）

**When to use**: When a brief has been pre-approved for neta (cultural reference) injection during intake (`copywriting-brainstorming.md` neta opt-in Level 2 field = Yes), AND a base-framework copy draft has been produced by `write-short-form-copy.md`, `write-long-form-copy.md`, `write-mid-form-copy.md`, or similar. This protocol applies neta injection as a **post-production layer** on top of already-structured copy.

**When NOT to use**:
- Brand voice or channel policy forbids neta injection (confirmed at intake)
- Base-framework copy is not yet drafted (neta injection is post-production, not initial drafting)
- Brief is for evergreen copy with >6-month shelf life AND source type is SNS/Meme (meme half-life is 4-6 months per Shifman 2014). Literary sources (Classical Lit, Modern Lit, Quotes) are inherently evergreen-compatible and CAN be used for long-lived copy.
- Audience profile is broad / general-public AND source type is SNS/Meme (Technique 3 Subcultural Capital / tribal signal reference would alienate adjacent audiences). Literary sources may still work for broad audiences if the reference operates on Bourdieu's cultural capital axis (education-based recognition).

**Output**: Copy draft with neta injection applied, annotated with (a) reference source URL, (b) technique used per `neta-injection-techniques.md`, (c) neta-safety-gate verdict.

**Grounds on**:
- `../standards/neta-injection-techniques.md` — 4 techniques (Reversal / Substitution / Subcultural Capital / Cross-domain Mapping)
- `../standards/neta-source-taxonomy.md` — 5 source categories + retrieval path routing
- `../standards/neta-websearch-pipeline.md` — Phase A-D pipeline definition (Path A-1 / A-2)
- `../standards/persuasion-ethics.md` — for dark-pattern + 景品表示法 cross-check
- `../rubrics/neta-safety-gate.md` — SHOULD gate at Phase D

## Pre-Phase: Opt-in Verification

Before executing Phase A-D, verify:

1. Intake Understanding Summary (`copywriting-brainstorming.md` output) contains explicit `neta_opt_in: Yes`
2. `neta_source_type_preference` is recorded (default: `all`)
3. Base-framework draft exists (copy structure from short-form / mid-form / long-form / light-action already produced)
4. Shelf-life requirement is compatible: if >6-month evergreen AND source type is `sns-meme` only → BLOCKED. Literary sources (`literary`, `all`, `mixed`) are inherently evergreen-compatible.
5. Audience profile is sufficiently specific to enable Phase A retrieval

If any check fails: return BLOCKED to main worker with specific gap identified.

## Phase A: Audience Context Retrieval

Retrieve cultural context per `neta-websearch-pipeline.md` §Phase A,
routing by source type.

### Source-type routing

Check `neta_source_type_preference` from intake:
- `sns-meme` → **Path A-1 only** (WebSearch-first)
- `literary` → **Path A-2 only** (parametric-first)
- `all` or `mixed` → both paths; merge candidate catalogs

### Path A-1 (SNS/Meme, Contemporary Culture)

1. **Parse intake audience profile**: age band, platform presence,
   subcultural affiliations. From `copywriting-brainstorming.md` Q3.

2. **Select SNS domain allow-list** from pipeline standard's table.

3. **Execute site-locked WebSearch queries** using `site:` operator:
   ```
   site:twitter.com OR site:x.com [topic] lang:ja after:2026-01-01
   site:reddit.com/r/[relevant_subreddit] [topic]
   site:niconico.jp [topic]
   ```

4. **Recency filter**: prefer ≤6 months. 6-12 months = re-verify.
   >12 months = expired unless "classic."

5. **Build candidate catalog**: 5-15 references with source URL,
   date, recognition assessment, in-group context.

### Path A-2 (Classical Lit, Modern Lit, Quotes)

1. **Parse intake audience profile**: education level, cultural
   literacy band, generational reading patterns, cross-cultural canon
   overlap (e.g., 漢詩 for JP, Shakespeare for EN).

2. **Parametric candidate enumeration**: generate 5-15 candidate
   references from LLM knowledge matching product domain + audience.

3. **Attribution verification via WebSearch** against 3-language
   literary verification allow-list (JP: 青空文庫, NDL, J-STAGE;
   EN: Project Gutenberg, Perseus, Internet Archive; ZH: ctext.org,
   維基文庫, 成語典). Verify: correct author, exact wording, context.

4. **Audience-recognition check** (replaces currency check): does
   the audience's education/cultural profile include this reference?

5. **Build candidate catalog**: 5-15 references with source text,
   verified attribution, audience-recognition assessment, source type.

### Failure handling

- Zero results (A-1): audience profile too narrow; BLOCKED
- Outdated-only results (A-1): redirect to literary sources or
  evergreen-only techniques (Reversal / Cross-domain Mapping)
- Attribution unverifiable (A-2): do NOT use — misquotation cringe
- Audience-recognition gap (A-2): discard candidate; classical ≠
  universally known

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
4. **Timeliness verified per source type**: SNS/Meme = WebSearch-confirmed within meme half-life window; Literary = audience-recognition check per `neta-source-taxonomy.md`; Quotes = cliché index + attribution accuracy verified.
5. **ステマ risk**: could this be mistaken for authentic organic UGC? (If yes, brand disclosure must be explicit elsewhere.)

If any answer is uncertain, revise the draft before launching the gate.

### Gate launch

Launch `evaluator` agent with:
- `gate_file`: `{base_path}/rubrics/neta-safety-gate.md`
- `standards`: all 18 copywriting-team standards (see SKILL.md Resource Manifest)
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

- **Always execute Phase A before Phase B**. For Path A-1 (SNS/Meme): do not use pre-training memory as a substitute for WebSearch. For Path A-2 (Literary): parametric discovery is acceptable but attribution verification via WebSearch is mandatory.
- **One technique per piece**. Density greater than one technique per キャッチコピー / one per opener block in long-form produces cringe rather than elegance (`jp-copy-craft-lineage.md` §眞木 principle).
- **Strict Replacement Rule is non-negotiable**. If a template doesn't fit the product's slot-grammar, pick a different template; do not bend structure.
- **Phase D hard legal vetoes are non-fungible**. Copyright + ステマ reds block delivery regardless of other dimensions.
- **Source-type-aware timeliness**. SNS/Meme sources: only safe for copy with ≤6-month shelf life (evergreen-only techniques excepted). Literary sources (Classical Lit, Modern Lit, Quotes): inherently evergreen-compatible for any shelf life.
- **Currency verification requires 2+ independent sources** (Path A-1). Attribution verification requires allow-list source confirmation (Path A-2).
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
