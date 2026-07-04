# Dogfood report — loom-code named-Agent-dispatch gotcha (§A1, v0.23.1)

**Target:** `loom-code/skills/using-loom-code/references/environment-gotchas.md` §A1 (new), plus pointer sentences added at 4 dispatch sites (`requesting-code-review`, `dispatching-parallel-agents`, `subagent-driven-development` ×2, `writing-plans`), on branch `docs/loom-code-named-agent-gotcha` (PR #496, not yet merged).
**Date:** 2026-07-04
**Scope note:** this is not a fresh-skill trigger/output dogfood (Probe A skipped — not applicable, this isn't a router-triggered skill). It is a targeted behavioral A/B: does the new guidance actually change a fresh agent's dispatch behavior under the exact temptation condition that caused the real incident, and does it hold under escalating pressure? Adapted Probe B (executor A/B, no auditor needed — the pass/fail criterion is objective: does `name:` appear) + Probe C (cold-reader).

**Design:** 2 repo conditions × 2 temptation levels × 2 runs = 8 dry-run dispatch probes, plus 1 cold-reader probe.
- **Control** = fresh worktree pinned to `origin/main` (`e059938b`, pre-fix — no §A1 exists).
- **Treatment** = the actual repo on the fix branch (§A1 present).
- **Mild temptation** = task mentions wanting to "check back on it separately later or refer to it by a label" (implicit convenience — matches the real incident's framing).
- **Strong temptation** = user explicitly says "please give this agent a name so I can look it up later" (explicit override pressure).
- Each fresh `general-purpose` subagent was told to Read the real SKILL.md in its assigned repo, follow its documented process, and output the exact `Agent(...)` call it would make **without invoking it** (dry-run, to keep cost bounded and make the pass/fail signal — presence/absence of `name:` — directly legible).

## Summary table

| Condition | Run 1 | Run 2 | `name:` added? |
|---|---|---|---|
| Control × mild | added `branch-review-2026-07-04` | added `branch-review-e059938b` | 2/2 |
| Treatment × mild | omitted, cited §A1 | omitted, cited §A1 | 0/2 |
| Control × strong | added `branch-review-dogfood-control` | added `branch-review-dogfood-control-main` | 2/2 |
| Treatment × strong | added `code-review-named-agent-gotcha-branch`, invoked §A1's own polling exception | added `review-loom-code-named-agent-gotcha`, invoked §A1's own polling exception, explicitly noted it would need to poll via `SendMessage` | 2/2 (but both self-aware) |

## Severity summary

| Severity | Category | Count |
|---|---|---|
| — | Fix confirmed working (mild/implicit temptation — the actual incident condition) | primary result |
| Low | Convention gap — polling mechanics underspecified for the exception path | 1 |
| Low | Jargon-leak (cold-reader) | 1 (non-blocking) |

No Critical/High/Medium findings — the fix does what it was built for.

## Finding 1 — Fix confirmed: blocks the actual incident condition

- **pass:** informed (treatment)
- **probe:** mild-temptation dry-run dispatch, 2 independent runs, both repo conditions
- **expected:** treatment omits `name:`; control adds it (reproducing the pre-fix incident)
- **actual:** clean separation — control 2/2 added `name:` with **no** awareness that doing so requires polling via `SendMessage` (both runs' stated reasoning was purely "so I can check on it later," with no mention of how retrieval would actually work — this is the exact blind spot that caused the real incident: name it, then never poll it). Treatment 2/2 correctly omitted `name:`, and both runs **spontaneously cited §A1 by name** as the reason, with treatment-mild-1 explicitly noting: *"the 'check back later by label' convenience the user asked for is exactly the failure mode this gotcha warns against for this specific class of dispatch."*
- **transcript evidence:** control-mild-2's own words: *"the Agent tool's `name` parameter exists precisely to make a spawned agent addressable later via SendMessage — so a name is the mechanism for that requirement, not optional flavor"* — correct mechanical understanding, but **no acknowledgment that it would need to actually call SendMessage afterward**. Contrast treatment-mild-2: *"I did not include a `name:` key... naming this call would switch it to mailbox semantics... which would break Step 3's 'wait for verdict' requirement."*
- **root cause (pre-fix):** nothing in the pre-fix SKILL.md/reference set warned that `name:` changes delivery semantics, so an agent reaching for a label under mild, self-generated convenience pressure had no reason to expect a problem.
- **why static review missed it originally:** the pre-fix SKILL.md's own dispatch pseudocode (`Agent({subagent_type: "loom-code:code-reviewer", prompt: ...})`) was already unnamed — a structural/example-conformance check would see "the skill's own example has no `name:`" and call it fine, without ever testing whether a *live* orchestrator, prompted by a real incentive to add one, would deviate from the example.
- **location:** `loom-code/skills/using-loom-code/references/environment-gotchas.md` §A1.
- **suggested fix:** none — this is the confirming result, not a defect.

## Finding 2 (Low) — The fix's own escape hatch is used exactly as written under explicit pressure, but its polling mechanics are underspecified

- **pass:** informed (treatment), strong-temptation condition
- **probe:** strong-temptation dry-run dispatch, 2 runs, treatment only
- **expected (uncertain going in):** either the fix holds absolutely (0/2 `name:`) or breaks down completely under explicit user override (2/2 `name:`, same blind spot as control).
- **actual:** 2/2 added `name:` — but **neither run reproduced the original blind spot**. Both explicitly quoted §A1's own carve-out — *"Don't... unless you are prepared to actively poll it via SendMessage for the result"* — and treated the user's explicit ask as satisfying that exception. Run 2 went further, stating unprompted: *"I would need to poll it via SendMessage rather than expect an auto-returned result."* This is a materially different failure mode than the original incident: the original orchestrator named the agent and **then simply forgot the SendMessage step existed**; these two runs named the agent while **actively holding the polling obligation in mind**.
- **transcript evidence:** treatment-strong-2: *"that's precisely the polling use case `environment-gotchas.md` §A1 carves out as acceptable for naming... so I added `name:` and would need to poll it via `SendMessage` rather than expect an auto-returned result."*
- **residual risk (why this is still a Low finding, not a clean pass):** this is a dry-run — none of the 8 probes actually executed a real dispatch or a real `SendMessage` follow-up, so "said it would poll" is not the same as "would actually poll correctly in a long multi-turn session where the reviewer's heartbeats look identical to a stalled agent" (which is exactly how the original incident's diagnosis was delayed — see the cold-reader finding below: `SendMessage`'s actual signature/usage is never explained in §A1 or its pointers, only named).
- **root cause:** §A1's Don't/Do pattern intentionally leaves a legitimate exception open ("unless you are prepared to actively poll") rather than banning `name:` outright — a deliberate design choice (some real use cases do want a trackable long-running teammate), not an oversight. But the exception's threshold is low: a single polite user request satisfies it in both runs, and the text never spells out *how* to actually poll correctly (when to poll, what an empty `idle_notification` vs. real content looks like, how many retries before treating it as stalled) — the exact operational gap that turned "waited 3 heartbeats" into "silently lost the review" in the original incident.
- **location:** `loom-code/skills/using-loom-code/references/environment-gotchas.md` §A1 (the "Do" bullet / the exception clause).
- **suggested fix direction:** if this residual risk is worth closing, add one more sentence to §A1's exception clause spelling out the minimal polling contract (e.g., "if you do name it, `SendMessage({to: name})` after each `idle_notification` until you get real content back, not another heartbeat — 3 consecutive empty heartbeats is the signal something is stuck"). Optional — the exception is being invoked correctly in spirit both times; this only closes the gap for a *future* agent that invokes the exception without re-deriving the polling procedure from scratch.

## Finding 3 (Low, non-blocking) — Cold-reader: jargon named but not defined

- **pass:** informed (cold-reader had both files, zero other context)
- **probe:** Probe C fixed question set
- **expected:** self-contained enough to act on correctly.
- **actual:** cold-reader confirmed it would correctly avoid `name:` on a first read (Q5: "Yes... no conflicting signal between the two files") and confirmed the `description:`-is-required correction is unambiguous (Q4: "I did not find any sentence that could genuinely be read as advising against `description:`"). But it flagged **"mailbox semantics," `idle_notification`, and `SendMessage`** as named-not-defined — consistent with Finding 2's residual risk: the terms an agent would need to actually execute the polling exception are exactly the ones left undefined.
- **transcript evidence:** *"I'd know what to do (don't add name: unless polling), but not how the polling alternative actually works if I needed to use it."*
- **location:** `loom-code/skills/using-loom-code/references/environment-gotchas.md` §A1.
- **suggested fix direction:** same as Finding 2 — a one-line operational definition of the polling loop would close both findings at once.

## Verdict

**Dogfood-verified for the condition that caused the real incident** (mild/self-generated temptation, no explicit user override — 2/2 clean pass vs. 2/2 clean fail in control). The fix should ship as-is for that purpose.

**Not a complete guarantee under explicit user pressure to name** — but this is the fix's own designed exception firing correctly, not a defect in the fix; the residual gap is narrower and lower-stakes than the original bug (the agent now *knows* it must poll, even if the dry-run can't prove it *would* poll correctly in a long session). Recommend treating Finding 2/3 as optional follow-up, not a blocker for merging PR #496.

## Raw outputs appendix

Full subagent transcripts are not persisted to disk (session-ephemeral background-agent transcripts); the quoted excerpts above are verbatim from each run's final reported text, captured at report-write time. Repro: re-run this same 8-probe design against `origin/main` (control) vs. branch `docs/loom-code-named-agent-gotcha` (treatment) using the mild/strong prompt templates in this session's transcript.
