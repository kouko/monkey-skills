# goal-create — two decision experiments

> **Date**: 2026-08-27
> **Purpose**: resolve the two open questions in `../specs/2026-08-27-goal-create.md`.
> **Status**: complete. Both questions resolved; the brief was updated from these results.

Raw artifacts lived in a session scratchpad and are gone. What survives is
recorded here, including the numbers that argue against the conclusions.

---

## Experiment 1 — does a ruled SESSION mode beat asking the host directly?

**Why it was run.** OpenAI documents the conversational goal-setting flow as
native: "ask Codex to help: start by having a conversation about what you want
to build, then ask it to directly set a goal and start working." If a bare host
drafts goals as well as a ruled skill does, SESSION mode should not ship.

**Design.** Four conversation records. Two arms, same model (`sonnet`) and same
seeds. Arm A received the seed and one instruction: write the goal you would
paste into `/goal`. Arm B received the same seed plus the protocol — four
fields, the decidable-and-false bar, provenance tags, and the two-slot input
floor with its refusal rule. Neither arm saw the brief.

**Seeds.** Seed 1 was a condensed record of this arc's own discussion, ending
before any decision. Seeds 2 and 3 were the discussion-only sections (Problem,
Users, Alternatives) of two real briefs, with their end-state and decision
sections withheld. Seed 4 was a short session about a genuinely open task —
making one `check_north_star_link.py` message point somewhere.

**Results.**

| | Arm A (bare) | Arm B (ruled) |
|---|---|---|
| Produced a goal | 4 of 4 | 1 of 4 |
| Refused | 0 | 3, each with a repo-verified reason |
| Targeted work already merged or overturned | 2 of 4 | 0 |
| Over the 4,000-character limit | 1 of 4 (4,228) | 0 |
| Carried the four fields | 0 of 4 | 1 of 1 |
| Carried any stop clause | 1 of 4 | 1 of 1 |

Arm B's three refusals were checked against the repository rather than taken on
trust. Seed 2's decision is merged and live — the arm cited `git-guard.py`,
`check_onramp_choice.py` and two commits, which matches this repo's own record
of that arc shipping. Seed 3 was an excerpt of a spec overturned the same day it
was written, whose follow-on extraction is parked on a Rule-of-Three trigger
that has not fired; the backlog entry says so. Seed 1's fork was genuinely left
open by its participants.

Arm A's failure is not fluency. Its seed-2 goal opens "Implement the design-side
on-ramp decision fix already settled" — an instruction to build something that
already exists — and its seed-3 goal revives a decision that was reversed. Both
read as competent work.

On seed 4, where the task was real, Arm B did not over-refuse. It produced a
goal naming the two functions whose message text must change, tagged each field
with its source, and — unprompted — used `git diff` as a second verification so
the constraint could be checked, not only the outcome.

**Conclusion.** SESSION mode ships. Its value is not drafting, which the bare
host does fluently; it is refusing when there is nothing to draft, and the
fields that make a goal checkable once there is.

**What argues against this conclusion.** Four seeds, one model per arm, and
three of the four seeds turned out to be non-actionable — a property of how the
seeds were chosen, not a measured property of real conversations. Both arms
could read the repository; a host that cannot would not have caught seeds 2 and
3 under either arm. Arm B produced exactly one goal, so its drafting quality
rests on a single case.

---

## Experiment 2 — can the quality bar be a script?

**Why it was run.** The bar currently has the agent judge a condition it just
wrote. This repository has already measured that shape failing: prose that
requires judgment loses on weaker models, prose that points at a checkable
action holds.

**Design.** A `goal_lint.py` was written against the bar alone, by an author who
had not seen the test cases. Cases were written by separate agents who had not
seen the script. Round 1 was five cases; round 2 was eight fresh cases from a
different author, deliberately mixed across Traditional Chinese, English and
Japanese, with four distinct violation types.

**Round 1 — discarded.** The first run scored 0 of 5: every case failed the same
check. The cause was that the checks were written in English and the cases were
in Chinese, so "把完整輸出貼在對話裡" was invisible. After adding Chinese
patterns the run scored 5 of 5, but that tuning happened after the answer key
was visible, so the round proves nothing.

**Round 2 — clean.** Eight blind cases against the intent-matching version:

| | Result |
|---|---|
| Verdicts correct | 6 of 8 |
| False positives (a good goal failed) | 2 — one English, one Japanese |
| Correct verdict reached by the wrong reason | 1 (Japanese) |

The two false positives have the same root cause. One case ran `k6`, which was
not in the runner whitelist. Two Japanese cases said "会話にそのまま貼り付ける
こと", which the surfacing pattern did not cover. Matching prose intent by regex
is whitelist maintenance: every unknown tool name and every unknown phrasing
becomes a false failure, and a false failure is the worst outcome for a gate,
because it blocks correct work and teaches its user to ignore it.

**The change that survived.** Hard checks were rewritten to be syntactic, so
they depend on neither language nor tool vocabulary: the four field labels must
be present and non-empty, a stop clause must exist, the Verification field must
quote at least one command in backticks, and the text must fit the character
limit. Everything that requires reading intent — undecidable wording, dependence
on a person — was demoted to a warning. On the same eight cases this version
produced no false positives at all, hard-failed the structural violation, and
warned on the rest, one of them for the wrong reason.

**Conclusion.** The lint ships as a floor, not as the bar. It fails only what can
be decided syntactically and warns on the rest; the judgment half stays prose and
stays honest about being judgment.

**What argues against this conclusion.** The syntactic version was written after
the answer key was seen. It introduces no whitelist entries, which is why it is
reported as a design conclusion rather than a score, but a third blind round
would be needed to certify it. As a floor it also catches less: of four bad
goals it hard-fails one and only warns on three.

**Carried finding, independent of both conclusions.** A mechanical check over
goal text is language-bound, and its failure is silent — it does not error, it
passes everything or fails everything. Any such check in this family must cover
the languages its users actually write in, and must be tested in each of them.
