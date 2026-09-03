# Dogfood: request-derived authorization — five-leg haiku cold-read probe

Date: 2026-08-05
Branch: feat-request-derived-authorization (probes ran by-path against
the edited working tree at the T5 commit, ff8313ea)
Probe tier: haiku (weak-reader acceptance instrument), one fresh
context per leg, written exercises (no command execution)
Verdict: **5/5 CLEAN**

| Leg | Surface | Scenario | Verdict |
|---|---|---|---|
| a | finishing Step 11 | endpoint-named kickoff, all gates passed | CLEAN |
| b | router §Continuous mode | unnamed vs named kickoff + escape hatch | CLEAN |
| c | rcr push-as-trigger 4-6 | PASS / PASS_WITH_NOTES / NEEDS_REVISION / mid-flow question | CLEAN |
| d | SDD gate ① | checkable fact + once-clause + always-confirm list + SSOT | CLEAN |
| e | finishing §When to use | ambiguous "I'm done here" trigger | CLEAN |

## Leg a — endpoint-named request at close-out

Q1 (ask before `gh pr create`?): **NO**, quoting the shipped lead
verbatim: "Open the PR — no ask: the authorization arrived with the
request (every §When to use trigger names the close-out endpoint; the
one ambiguous row confirmed at entry)." Q2: reports loudly, and the
probe independently pulled the both-merge-paths duty (web URL +
ready-to-run `gh pr merge <N> --squash` framed for the human). Q3
(may you merge?): **NO** — "The orchestrator prepares the command,
never runs it — no auto-merge."

## Leg b — recognition fires only on a named endpoint

Scenario A (「幫我修掉這個 timezone bug」): **not opted in** — "A
request naming no endpoint never triggers this." Scenario B ("ship it
— run this branch to a PR"): **opted in**, with the recording duty
quoted ("endpoint named: yes → continuous" in the plan header;
downstream stations read the recording, never re-judge). Mid-arc
「一站一站來」: "restores human-pumped mode from that point, and the
recording flips."

## Leg c — rcr push-trigger verdict routing

PASS → "the push WAS the request — execute it (branch-qualified form)
and report loudly what was pushed. Do not re-ask." PASS_WITH_NOTES →
push carrying every finding verbatim into the report; "Do NOT fix
findings inline silently." NEEDS_REVISION → "do NOT push." Mid-flow
question → runs the ask-vs-resolve triage at SDD §Asking the user
gate ① (the cross-skill SSOT) before it reaches the user.

## Leg d — decision-side triage + once-clause

Repo-checkable fixture question: **not surfaced** — "fact checkable
within the task's own sources → look it up, never ask." Close-out push
re-confirm after "run this branch to a PR": **no** — the once-clause
quoted in full. Always-confirm list intact: "`gh pr merge`, deploy,
delete, and paid runs always confirm regardless." SSOT sentence
recited verbatim.

## Leg e — the one endpoint-unnamed trigger

"I'm done here, what's next?" routes to close-out WITH the entry
confirmation ("closing out = review → verify → commit → push → PR —
proceeding?"), correctly identified as unique to that row; after the
entry yes, Step 11 does not re-ask; "finish this branch" needs no
entry confirmation because the phrase itself names the endpoint. The
probe articulated the request-carries-authorization principle
unprompted.

## Reading

The two failure directions the plan feared — an over-eager reader
auto-pushing on an unnamed request, and an over-cautious reader
re-asking after a named one — both came back correctly refused at the
haiku tier, each answer anchored to a verbatim shipped sentence. The
merge invariant held in every leg that touched it (a, d).
