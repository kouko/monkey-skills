# Brief — Two-tier token-budget calibration (body-size governance)

**Date:** 2026-07-15 · **Stage:** brainstorming brief (loom-code) · **Lever:** SKILL.md *body* word/token budget (distinct from the description-token lever in `2026-07-14-description-token-economy.md`).

## Problem
(Axis 1 — JTBD)
The repo's house rule caps SKILL.md bodies at ~6,000 tokens / 4,500 words — **20% looser** than the official Anthropic guidance (dual-track: "<500 lines" + "Level 2 Instructions under 5k tokens", platform.claude.com, live-verified 2026-07-15). The job: **align the house governance to the official 5k-token line as a stated soft aim, without forcing deliberately-frozen dense skills to trim under a new hard gate.** Success = a documented two-tier target (soft ≈5k tokens / 3,750 words + justified-exceedance convention; hard stays 6k/4,500) that reviewers and skill-judge apply, with the numbers consistent across every place they appear.

## Users
(Axis 2)
Skill authors + reviewers in this repo (and the skill-judge/coherence-rubric machinery they lean on). Condition: writing or reviewing a new/edited SKILL.md and wanting a target that matches industry practice, not a 20%-looser local exception. Not end-users of any product.

## Current State Evidence
(brownfield — file:line)
- **Forward (the number's SSOT):** `domain-teams/skills/skill-team/standards/skill-md-structure.md:400` §Token Budget **already encodes a two-tier shape** — `Hard cap ~6,000 tokens / ~4,500 words (🔴 rubric)` · `Soft target ~3,000–4,500 tokens` · `Warning zone ~4,500–6,000 tokens (🟡 rubric)`. The 🟡/🔴 refer to the **Skill Coherence rubric**, NOT the checker.
- **Reverse (SSOT direction):** the standard is the SSOT; `check-skill-structure.py:294-298` comment cites it and hard-codes `WORD_HARD_CAP = 4500` for the **hard** tier only. The **soft/warning tier has no machine enforcement today** — it lives purely in the doc + coherence rubric.
- **Error/enforcement path:** `check-skill-structure.py:301-316` — `check_chk_skl_010` returns a `CheckError` (all errors FATAL; no severity concept) only when `word_count > 4500`; `main():547-556` fails (exit 1) if any error exists. CI scope = 5 plugins only (`.github/workflows/skill-structure.yml`: domain-teams + loom-code/spec/interface-design/product-principles).
- **Data (who sits where):** the 4 real over-cap skills (dbt-wiki:init 6,476 / deep-deep-research 5,309 / cld-craft 5,016 / skill-judge 4,533) are **all outside CI scope**. The in-scope skills in the 3,750–4,500 soft-exceed band are SDD 4,152 / copywriting-team 4,098 / writing-plans 4,090 / completeness-critic 3,840 — **all deliberately frozen or dense contracts** (#559 froze SDD + writing-plans).
- **Boundary/other consumers of "4500":** `CLAUDE.md:39` (house-rule line), `skill-completeness-checklist.md:40` (CHK-SKL-010 text), `skill-judge/SKILL.md` D5 (line-based, `<500 lines`; the token number lives in `references/domain-team-adaptation.md`), `loom-product-principles/scripts/improve_loop_verdict.py:55` (`--cap` default 4500). No committed unit test exists for `check-skill-structure.py` (hyphenated filename → would need a loader to test).

## Decision
(the fork — resolved with user)
**Build:** a docs-only two-tier recalibration (Option 1 below) — recalibrate the already-documented soft tier to the official 5k tokens ≈ 3,750 words, add a *justified-exceedance* prose convention, reconcile the words/tokens presentation, and propagate the aligned framing consistently to CLAUDE.md + CHK-SKL-010 checklist wording + skill-judge's token-cap reference. **The checker stays hard-cap-only** (as it is today).
**Do NOT build:** a checker severity system / non-fatal WARN line (Option 2), nor a machine-readable exceedance-suppression marker (Option 3).

## Alternatives Considered
(Axis 4 — industry research done prior session; mechanism fork here)

| | Option 1 — docs-only (REC) | Option 2 — + non-fatal checker WARN | Option 3 — + machine suppression marker |
|---|---|---|---|
| Soft tier home | doc + coherence rubric (as today) | doc + new `WORD_SOFT_CAP` WARN in checker | doc + WARN + frontmatter suppression key |
| Justified-exceedance | prose note in skill's PR/changelog | non-fatal WARN tolerated + prose note | machine key silences the WARN |
| New code | none (edit constants/text only) | severity concept in `CheckError`+`main()`; bootstrap test harness for untested module | + marker parser + tests |
| Ongoing behavior | no CI noise | **fires forever on 4 frozen in-scope skills**; blind to the 4 real over-cap (out of scope); wc-w underestimates CJK | same noise unless every frozen skill gets a marker |
| Matches user "min code / no speculative mechanism" | ✅ | ⚠️ | ❌ (rejected upfront) |

**Why Option 1:** the soft tier is *already* a doc/rubric concept — adding a checker WARN introduces new machinery for a tier that never had it, and it would nag persistently on skills we've deliberately frozen (SDD/writing-plans per #559) while being blind to the real offenders (all out of CI scope). Official 5k alignment is a *governance* change, not an enforcement change.
**Conditional reversal:** if CI scope later expands to all plugins AND we adopt a suppression convention for frozen skills, revisit Option 2 (the WARN becomes actionable rather than noise).

## What Becomes Obsolete
(Axis 5)
- The 20%-looser framing (house 6k vs official 5k) in `CLAUDE.md:39` and the standard — reframed, not deleted, to "hard 6k / soft aim 5k per official".
- The existing muddled `Soft target ~3,000–4,500 tokens` / `Warning zone ~4,500–6,000 tokens` numbers in the standard — replaced by the recalibrated soft/hard framing anchored to 5k/6k tokens with the words-proxy stated once.

## Out of Scope
- Trimming any actual skill (that's slim round 3 — a separate arc).
- The description-token lever (`2026-07-14-description-token-economy.md`).
- Expanding CI scope to unscanned plugins (the `ci-skill-structure-scan-gap-obsidian` memory item; separate).
- Touching SDD / writing-plans frozen contracts.

## Open Questions
- Resolved by user pick: Option 1 vs 2 (Option 3 rejected upfront). Pending confirmation before planning.
