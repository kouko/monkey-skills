---
name: process-mechanism-dogfood-via-coldreader-real-commits
description: To dogfood a shipped process RULE (not a whole skill's triggering/output), give a fresh context-blind agent ONLY the rule text + real sandbox git commits (not fabricated data) and ask it to decide+execute each branch — cheaper than a full nested-subagent live run, still catches real misuse
type: process
origin: PR #514 (loom-code Review-weight: mechanical) dogfood, 2026-07-08
---

`skill-dev-toolkit:dogfood-skill-testing`'s three probes are built to
test a whole skill's triggering + output quality. Testing a single
shipped PROCESS RULE inside an existing skill (e.g. SDD's new
mechanical-review-weight skip branch) doesn't need a full live SDD run
with real subagent reviewer dispatch — the rule's value lives entirely
in one decision branch, not in producing an artifact.

**How it was done:** built a real (not fabricated) git sandbox with
three commit states — (a) a mechanical edit that genuinely matches its
declared exact-spec across its declared files, (b) an ordinary logic
change with no exemption marker, (c) a mechanical edit that matches
content-wise but also touches a file outside its declared scope. A
fresh, context-blind `general-purpose` agent was given ONLY the target
SKILL.md section (full file) + a plain-language description of each
plan-task + implementer-DONE report, and told to decide and actually
EXECUTE (grep / git diff) what the rule says to do next for each,
citing the exact sentence that justified each decision.

**Why:** rule text that reads fine to its own author can still be
mis-applied by a genuinely fresh reader — the same "cold agent executes
it blind" bar as any prompt/skill text (per this machine's
`judgment-rubrics.md` §5 quality-floor row). This variant is far
cheaper than a full nested-subagent SDD dogfood (no real reviewer
dispatch needed) while still being a live behavioral test, not a
self-read.

**How to apply:** for any single shipped process rule (not a whole
skill), reuse this shape — real sandbox commits, a blind agent given
only the rule text + scenario descriptions, required to cite + execute,
not summarize. Judge success by whether it catches the "looks compliant
but actually violates" case (in this instance: a mechanical marker
whose commit slipped in an out-of-scope file — the agent correctly
recomputed the scope-check and fell back to full review instead of
trusting the surface-level content match).
