# distill-sessions proposals — 2026-07-02

**Target SKILL.md**: `/Users/kouko/.supacode/repos/monkey-skills/obsidian-skill-r1/obsidian/skills/daily-news-digest/SKILL.md`
**Counts**: 0 addition(s), 0 modification(s), 0 anchor mismatch(es), 7 pending cross-session evidence, 0 deferred to v0.2.

> No silent writes — review the proposals below, then run `python -m apply --approved ...` to commit the diff.

## Proposed additions

_(none)_

## Proposed modifications

_(none)_

## Anchor mismatch — needs review

_(none)_

## Cross-session evidence pending

_These items were observed in only 1 session and did not reach the minimum cross-session evidence threshold (min_n=2). They are NOT auto-applied — re-run after more sessions accumulate to promote them._

### Enumerate cot_mermaid.py's valid role tokens explicitly
_Agent guessed role 'mechanism' instead of 'mech' → tool error + inspect.getsource round-trip; the sample shows one 'mech' but never states the closed enum; compaction had dropped the detail._

Add one line near the STEP 6 code block: valid role values are exactly trigger / mech / result / concl — do not use full words like 'mechanism'.

_Observed in 1 session: `67e7733c-a238-472d-b452-d9355a5568c5` — re-run after more session evidence accumulates._

### Keep the full stem→label dict live through to the Write call
_All 5 digests shipped broken links from truncated/re-typed titles (agent's own stem[:60] triage prints, memory-typed punctuation) — the existing Hard-rule warning only covers the printed manifest view._

Strengthen the Hard-rules truncation callout: build one full stem→label dict from the untruncated JSON and keep it live (e.g. dump to a file consulted at Write time); never re-type titles from any earlier truncated print, including the agent's own triage listings.

_Observed in 1 session: `67e7733c-a238-472d-b452-d9355a5568c5` — re-run after more session evidence accumulates._

### Multi-day batch requests need per-day sessions or checkpoints
_'把最近幾天都整理一下' → 5 heavy days (57/68/51/35/29 candidates) in one run → API Overloaded + three context-exhaustion compactions, each losing resolved details (e.g. cot_mermaid role vocabulary)._

Add under STEP 0 — Pre-flight: when a request spans multiple dates, recommend processing heavy days (≥40 candidates) in separate invocations/sessions, or checkpoint per-day (scratch progress file) so a mid-batch compaction doesn't force rediscovering already-resolved details.

_Observed in 1 session: `67e7733c-a238-472d-b452-d9355a5568c5` — re-run after more session evidence accumulates._

### Open source notes via the manifest's exact path field, never shell-embedded filenames
_Filenames containing & and full-width ｜ embedded in Bash/sed returned empty output with no error; fix was Python open() on the manifest's stored path field._

In STEP 4 point 1, add: always open notes via the collector manifest's exact path field through a native file API (Read tool / Python open()), never by retyping or shell-embedding the filename — YouTube-derived names routinely contain characters that break shell reads silently.

_Observed in 1 session: `9e195a61-343d-47a0-845f-ee60bd999517` — re-run after more session evidence accumulates._

### Dispatch STEP 4 story subagents blocking, not run_in_background
_Six research subagents dispatched with run_in_background:true + ScheduleWakeup → eight consecutive turns of 'Stop hook feedback: Background subagents are still running' after the digest was already written; TaskOutput returned 'No task found'; ps/CronList/CronDelete diagnostics needed to end the turn._

Add to STEP 4's execution-model callout: dispatch story-cluster subagents as blocking Agent calls (not run_in_background) — STEP 6 assembly can't start until every subagent returns, so background dispatch buys nothing and creates stop-hook contention. If a ScheduleWakeup/cron was used, cancel it once results are collected, before declaring done.

_Observed in 1 session: `e716583b-aa11-4c2a-b088-d375362f637d` — re-run after more session evidence accumulates._

### Resolve an absolute vault-root path before the STEP 6 Write call
_After cd-ing into a /tmp scratch dir for Mermaid JSON (per STEP 6's own pattern), the Write used relative 'news/2026-07-02 每日新聞.md' and silently landed in /private/tmp/...; self-checks failed FileNotFoundError; find/mv recovery needed._

Change STEP 6's file-creation instruction to require an absolute path resolved from the vault root (established at pre-flight) immediately before the Write call, so an earlier scratch-directory cd can't silently redirect the digest.

_Observed in 1 session: `e716583b-aa11-4c2a-b088-d375362f637d` — re-run after more session evidence accumulates._

### Route scratch Mermaid JSON through a mktemp session dir, not bare /tmp literals
_Following the literal 'cat > /tmp/cot_chain.json' example created fixed /tmp dirs whose cleanup was blocked twice (permission denial + dcg rm-rf guard), leaving debris and wasted turns._

Change STEP 6's example to write scratch JSON into a mktemp -d session-scoped dir; mark cleanup optional/best-effort and note bare-/tmp deletion may be blocked by the host's destructive-command guard.

_Observed in 1 session: `e716583b-aa11-4c2a-b088-d375362f637d` — re-run after more session evidence accumulates._

## Marked for v0.2

_(none)_
