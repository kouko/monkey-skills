# Brief — asking-the-user three-gate rollout to brainstorming + router (Pattern ③)

Date: 2026-05-31 · Stage: brainstorming output → `writing-plans`
Approach locked: **Pattern ③ (mirror-principle / audience-tailored)** — each skill
carries its OWN native version; NO cross-skill file reference; NO distribute-script
(the block is audience-tailored, not byte-identical). Concept SSOT = the existing
PR #355 brief (augmented, not duplicated).

## Problem (Axis 1 — JTBD)

The three-gate `## Asking the user` model (① whether to ask · ② bring a researched
recommendation · ③ how to phrase) shipped to SDD + requesting-code-review in PR #355
(v0.13.0). The deferred v0.2 was "roll to brainstorming + router." Job: make
brainstorming's and the router's user-asking *consistent* with the three-gate model
**without** (a) violating Anthropic skill-independence (no cross-skill reference) or
(b) duplicating what brainstorming already encodes.

## Users (Axis 2)

- The **agent** following brainstorming/router (the rule consumer) + **kouko** (asked).
- Same heterogeneous-repo context as PR #355.

## Smallest End State (Axis 3)

Per Pattern ③, the rollout is **much smaller than copying the block** because both
targets already partially encode the gates natively:

1. **brainstorming/SKILL.md** — gates ① and ② are ALREADY native: Axis 1's "confident
   JTBD read → state as committed interpretation, don't re-ask" **is gate ①**; Axis 4's
   research-then-"My take: Recommend / Why / Conditional-reversal" **is gate ②**. The
   only gap is **gate ③ phrasing rules** when an axis-uncertainty `AskUserQuestion`
   *does* fire. Add, natively (tailored to the axis-question context), to the existing
   "ask at most one axis per call" guidance: **state-anchor inside the `question` field**,
   **outcome-not-mechanism**, **numbers carry their meaning**. (brainstorming already has
   ≤4-options + one-axis-per-call + plain-language-summary, so those are NOT re-added.)
   Plus one internal sentence naming that ① lives in Axis 1 and ② in Axis 4, so the
   three gates are discoverable as a coherent set.
2. **using-code-toolkit/SKILL.md** — rule #5 ("Research before asking") IS gate ② at the
   routing level. Add a **one-line pointer** that the full asking-the-user discipline
   (gates ① + ③) is enforced in the downstream skills (brainstorming / SDD /
   requesting-code-review). The router rarely surfaces `AskUserQuestion` itself, so this
   is a discoverability pointer, not a duplicated block.
3. **Concept SSOT** — reuse the existing PR #355 brief
   (`docs/code-toolkit/specs/2026-05-31-asking-the-user-three-gate-redesign.md`); append
   a short "Cross-skill rollout" note recording where each of the 4 skills carries the
   gates + how each tailors them. NO new SSOT doc (deletion-first — it already exists).

## Current State Evidence

- `code-toolkit/skills/brainstorming/SKILL.md` — no `## Asking the user` heading. Axis 1
  (§"5-axis", the "confident JTBD read" paragraph) = gate ①; Axis 4 (the "My take:
  Recommend/Why/Conditional reversal" output format) = gate ②; "ask at most one axis per
  `AskUserQuestion` call" + "≤4 options ... rejected" (in §5-axis intro) + "Plain language
  in the summary message" (§Output Contract) = partial gate ③. **Missing**: state-anchor-
  inside-question-field, outcome-not-mechanism, numbers-carry-meaning.
- `code-toolkit/skills/using-code-toolkit/SKILL.md:20` — rule #5 "Research before asking
  ... Use `brainstorming` Axis 4 protocol." = gate ② at routing level; no other asking
  guidance; router routes, rarely asks directly.
- SDD `## Asking the user` (PR #355) — the 6 gate-③ phrasing rules to mirror (tailored):
  outcome-not-mechanism / translate-jargon / numbers / state-anchor-inside-question /
  ≤4-options / compound-same-topic. brainstorming already has 3 of the 6.
- PR #355 brief — the canonical three-gate definition + §Terminology Provenance; serves
  as the non-skill concept SSOT (mirror-principle escape hatch per
  [[feedback_skill_independence_applies_between_sister_skills]]).

## Decision

Apply Pattern ③ (mirror-principle): brainstorming gets a **native, tailored** gate-③
phrasing addition + an internal ①=Axis-1/②=Axis-4 note; the router gets a one-line
downstream pointer; the existing PR #355 brief is augmented as the concept SSOT. NO
cross-skill file reference, NO distribute-script, NO copied block, NO new SSOT doc. The
gate-③ rules brainstorming already has are NOT re-added (no duplication within the file).

## Alternatives Considered (Axis 4)

Implementation-pattern alternatives (researched against the repo's own precedents):
- **Pattern ① naive duplicate** — copy SDD's block into brainstorming. Rejected:
  duplicates Axis-1/Axis-4 (contradiction + bloat) and the block is audience-tailored.
- **Pattern ② SSOT + distribute.py + verify-drift** (the knowledge-layer model). Rejected:
  requires byte-identical content; the asking-the-user block is deliberately tailored
  (SDD-fuller / code-review-lighter+boundary / brainstorming-Axis-form), so a functional
  copy would erase the tailoring.
- **Pattern ③ mirror-principle** — CHOSEN: each skill native + tailored, concept SSOT in
  a non-skill doc. Fits audience-tailored content; the recap↔handoff precedent + CLAUDE.md
  skill-independence support it.
No external WebSearch — the three-gate model + plain-language were already grounded in
PR #346/#355 (Horvitz / NN-g / ISO 24495-1 / 確連報); this is purely applying it.

## What Becomes Obsolete (Axis 5)

Nothing removed. Purely additive (3 phrasing rules in brainstorming + 1 router line + 1
SSOT-brief note). The "v0.2 rollout deferred" item in the PR #355 brief's Out-of-Scope is
discharged.

## Out of Scope

- SDD + requesting-code-review `## Asking the user` blocks — already shipped (PR #355),
  untouched.
- A distribute-script / byte-identical shared block — explicitly rejected (Pattern ②
  doesn't fit audience-tailored content).
- save-memory global over-confirm (a global behavior, not a code-toolkit skill).
- Re-adding gate-③ rules brainstorming already has (≤4-options / one-axis / plain-summary).

## Open Questions

1. Version bump: minor (0.14.1 → 0.15.0, new guidance in a skill) vs patch (→ 0.14.2,
   small additive). Lean **minor 0.15.0** — consistent with treating asking-the-user
   guidance changes as minor (PR #355 was 0.13.0 minor).
2. Behavioral validation = dogfood + grep diagnostics (no pytest for skill prose); confirm
   the new gate-③ rules don't contradict brainstorming's existing one-axis/≤4 guidance.
