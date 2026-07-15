# Relay phrasing — the three gates for surfacing a review verdict

> Companion to [`../SKILL.md`](../SKILL.md) §Asking the user. Load this file
> BEFORE composing any verdict relay or hand-off to the user (SKILL.md
> §Process Step 5, or §Push-as-trigger steps 4-6). The reader is a
> warm-but-interrupted human, not the `code-reviewer` subagent.

## ① Whether to ask — tier by reversibility × cost

Every question spends the user's attention; asking on autopilot is confirmation fatigue. Before surfacing a decision, tier it:

- **Reversible and inferable from context** → just do it, mention it after. Under a standing "just finish it" authorization, do not re-confirm each step.
- **Irreversible, outward-facing, or costly** → always confirm first. The push-as-trigger actions (`git push` / `gh pr create` / `gh pr merge`) are exactly this case: they publish to teammates / CI / production, so they are never auto-run — confirm before each one.
- **Genuine taste, scope, or un-inferable** → ask, per gate ②.

## ② What to bring — a recommendation, not an open question

This skill mostly relays a verdict and asks the user to choose: fix the findings now, defer them, or merge anyway. Whichever you ask, **lead with a scoped `(Recommended)` option and one line of why** — never hand the user an open-ended punt they have to fill in themselves. Research industry practice first for design/strategy calls ([`using-loom-code`](../../using-loom-code/SKILL.md) router rule #5 / `brainstorming`'s Axis-4 — point to them, do not re-implement the protocol here). *(Grounded: Horvitz, Principles of Mixed-Initiative User Interfaces, CHI 1999.)*

**Complex remediation fork → brief before you ask.** A finding can open a genuine design fork (e.g. an architectural 🔴 with two viable remediations). When that fork is complex (≥3 trade-offs, ≥2 implementation paths, or architectural blast radius), do not compress it into a fix/defer/merge ask — run `dev-workflow:brief-before-asking` (6-block briefing, Mental Model first) before the `AskUserQuestion`. Same trigger as `brainstorming`'s rule — `brainstorming` carries the canonical trigger rule; `dev-workflow:brief-before-asking` owns the 6-block format.

## ③ How to phrase

Seven rules:

1. **Outcome, not mechanism.** Each finding says what it *means for the user* and what they should do ("this branch ships a circular dependency — fix before merge"), not just the rule name it tripped ("violates arch-gate D3").
2. **Translate jargon; expand acronyms on first use.** Replace or gloss internal terms (`implementer`, `spec-reviewer`, 🟡/🟢, `Wave 1 = T1+T3`). **Exception**: terms the user introduced *this session* are fine as-is.
3. **Numbers and symbols carry their meaning.** Translate `🔴/🟡/🟢`, `PASS_WITH_NOTES`, and the Beck / Martin / OWASP / 徳丸本 citations into one plain sentence ("nothing blocking, two things worth a look before merge") — don't dump the raw verdict block at the user.
4. **Open with a one-line state anchor** (一句話現況): *I reviewed the whole branch; here's what I found.* Never lead with a bare verdict token (`NEEDS_REVISION` alone is the failure) — give the reader the situation before the symbol. When you follow up with an `AskUserQuestion`, put the anchor **inside its `question` field**, not only in chat prose above the call — the user reads the rendered question, not your preamble. Always populate the `questions` array with fully-drafted question text; an empty `{}` payload causes InputValidationError at dispatch time.
5. **≤4 options** (AskUserQuestion hard cap). Never add an explicit "Other" — the tool auto-injects it. End **open** design questions with a free-form invite; for **closed** factual questions, don't.
6. **Compound asks only when sub-questions share one topic** or are jointly judgeable. Split unrelated decisions into separate rounds.
7. **Relay via the shared family card.** Open the relay with the family rollup card per `loom-pipeline/hooks/family-relay.md §Family relay discipline` — don't restate its rules here. Walk findings at the user's pace, not as a dump; ≥2 remediation options default to a markdown comparison table.

## Worked example — the built-in `/recap` style is the target

```
✅ Standard (outcome-framed, no jargon, plain status, term-explained-on-use):
   "I reviewed the whole branch — nothing blocks the merge, but two things are worth a look
    first: a query that could be slow on large tables, and a missing test for the empty-input
    case. Want me to fix them now, or merge and follow up?"

❌ Avoid (jargon-dense status-report style):
   "Verdict: PASS_WITH_NOTES. 🔴 0 / 🟡 2 / 🟢 8. perf D2 (Fowler), tests D5 (Beck). See findings[]. Ready to merge?"
```

This ✅ example is the calibration target for every verdict-relay and hand-off the skill surfaces.
