# House standard — SKILL.md `description`

> Status: ADOPTED 2026-06-19 (length target 150 / cap 250). Evidence basis + refuted alternatives:
> `docs/skill-mining/2026-06-19-skill-description-research.md` (deep-research, 9 claims verified).
> This doc is the human-readable SSOT (rationale + evidence). The operative rules are **inlined
> (copied)** into `skill-dev-toolkit:skill-creator-advance` (authoring) and `skill-dev-toolkit:skill-judge`
> (a D4 rubric check), per this repo's self-contained-skill convention — skills cannot resolve a
> cross-plugin reference at runtime. Drift is guarded by
> `skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py`, not by a sync script (only two
> consumers, short rule-set). If a third consumer appears, revisit the canonical+distribute pattern.

## Why this exists

The `description` is the **primary signal** Claude uses to pick a skill (pure LLM reasoning over
the name+description list — no embeddings). With many skills installed, all descriptions share a
budget (~1% of context, ~15k chars; per-entry cap 1536) and **overflow silently drops the
least-used skills**. So a description must be **specific, distinct, and short**.

## The rules

### 1. Length — target **≤150 chars**, hard ceiling **250**; never exceed 1024 (spec/Codex)
- Real shipped skills average ~263; lean collections run 110–150; Anthropic examples ~150–250;
  superpowers averages 140. We have ~184 skills → near the shared budget, so we sit at the
  **lean end: aim ~150, cap 250.** Over-long descriptions evict other skills from what Claude sees.

### 2. Content — **what it does + when to use it** (positive, specific triggers), front-loaded
- Format: a short "what" + "Use when …" with concrete, real-user trigger phrasings.
- **Front-load the most important trigger words** (truncation is from the end).
- Use the words a user actually types ("check this", "查一下"), not formal jargon.
- ❌ Do NOT put the **step-by-step procedure / workflow / grounding citations** in the
  description — those go in the body. (The description gates activation; the body loads in full
  once activated — verified, so a "what+when" summary does NOT cause body-skipping.)

### 3. Disambiguate by **positive specificity**, not negation or pushiness
- To stop a skill firing on the wrong task, make its **positive** triggers precise and distinct
  from siblings. Optionally a light positive redirect ("for X, use skill-Y").
- ❌ Avoid "ALWAYS invoke" / pushy directives — they over-trigger at scale, not Anthropic-endorsed.
- ❌ Avoid heavy "Do NOT do X" behavioral negation — LLMs handle negation unreliably. (A short
  scope note is fine; don't lean on negation for correctness.)

### 4. No CJK redundancy
- Cross-lingual reasoning triggers fine on non-English prompts without translated keyword tails
  (A/B-verified: identical triggering with/without CJK). Appended CJK is also the first thing
  truncated from the end. **Drop the 中/日/英 triple-restate tails.**

### 5. Multi-line / block-scalar is fine (NOT required to be one line)
- Verified: block-scalar (`>`/`|`) and multi-line descriptions load in full in current Claude
  Code. The "one-line only" rule does not apply to us. (Length, not line count, is the limit.)

### 6. Third person, no XML tags, `name` ≤64 chars (lowercase/hyphen)

## Quick template

```yaml
description: <One-line what it does>. Use when <concrete trigger situations / real user phrasings>.
```
Example (good, ~140 chars):
```yaml
description: Reviews the whole-branch diff and flags 🔴/🟡/🟢 issues. Use before any push/merge/PR, or on "review my branch" / "is this ready to merge".
```

## Checklist (for skill-judge / authoring)
- [ ] ≤150 chars (≤250 hard); not over 1024
- [ ] what + when, positive specific triggers, front-loaded
- [ ] procedure / grounding NOT in description (in body)
- [ ] no "ALWAYS invoke", minimal/again no behavioral negation
- [ ] no CJK redundancy
- [ ] third person, no XML tags

## Explicitly NOT adopted (and why) — see research doc §Refuted
- "when-only, never say what" · "ALWAYS invoke" directives · "Do NOT use for X" as a reliability
  lever · the "+18.4pp from wording" and "21% skill-shadowing" citations (misattributed / unverifiable).
