---
name: an-absence-claim-in-a-plan-is-a-hypothesis-not-a-fact
description: A plan-time claim that "no X exists" (no cap test, no guard, no consumer) is a hypothesis one failed grep can silently found — an abbreviated filename dodges a skill-name grep — so encode the claim as an in-task tripwire (hidden X fires → STOP, report, fall back to a rule the brief pre-recorded) and verify absence by running the candidate edit against the suite, never by name-grep alone
type: practice
origin: 2026-08-07 stage-owner-and-blocked-enum arc, T4 rider descope (branch feat-stage-owner-blocked-enum)
---

The plan and the plan-document-reviewer both recorded "no rdr word-cap
test exists" — the fact-check grep searched scripts for the skill's full
name, but the test lived in `test_rdr_extraction_pointers.py`
(abbreviated prefix) and pinned a 4430-word ceiling. The claim shipped
into the plan as a frozen fact. What saved the arc: the task's
acceptance carried a tripwire clause ("if a hidden cap test goes red,
STOP and report — do not trim other prose to fit"), and the brief had
pre-recorded the fallback rule ("cap blown → skip the rider"). The
implementer hit the ceiling, stopped per the tripwire, and the recorded
rule resolved the fork without re-scoping or asking.

**Why:** absence is the one claim a grep cannot prove — a miss is
indistinguishable from a bad pattern (abbreviations, renames, indirect
references all dodge name-greps). A frozen "no X exists" fact in a plan
silently authorizes work that X forbids; the failure surfaces mid-task,
at the worst time, unless the plan planned for its own fact being wrong.

**How to apply:** when a plan leans on an absence claim, do three
things: (1) state it as a hypothesis, not a fact; (2) attach an in-task
tripwire — the concrete symptom that falsifies it and the STOP action;
(3) pre-record the fallback rule in the brief (skip / widen scope /
escalate) so the tripwire firing resolves mechanically. To actually
test absence, run the candidate edit against the full suite in a
scratch copy — the suite knows every pin by behavior, not by name.
Composes with [[a-rule-edit-falsifies-the-unchanged-prose-composed-with-it]]
(recorded facts going stale) — this entry covers facts that were never
true to begin with.
