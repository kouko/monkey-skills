---
name: a-checkpoint-interrupted-after-dispatch-resumes-under-the-committed-agent-ids
description: When a session dies between the `chore(loom): dispatch review` commit and the verdicts (a /clear, a crash), the dispatched agents are gone but their `dispatch[]` entries are already committed — re-dispatch fresh agents under the SAME agent_ids and the same HEAD rather than appending new entries; and read review.json's template placeholders (`<agent id>`, `PASS|PASS_WITH_NOTES|NEEDS_REVISION`) as "round not yet written", not as a corrupted record — §7 writes verdicts, probes and open_findings together at the end of the round, so a review.json with only `dispatch[]` filled is the normal mid-round state
type: process
origin: branch reviewer-adversary-positioning (2026-09-04) — session /clear'd between the two-reader dispatch commit and their verdicts; checker showed six BLOCKs on the placeholders which read as a hole but was the expected mid-round state
---

A review checkpoint has two commits: the dispatch record first
(`chore(loom): dispatch review <scope>`), the verdict record last
(`chore(loom): checkpoint review — <scope> <verdict>`). Between them the
agents run and nothing is written. If the session is interrupted there:

1. `ListAgents` shows no subagent of yours — the readers are gone and
   will never report. Their `dispatch[]` entries are already committed
   under agent_ids; re-dispatch fresh agents **under those same ids**
   with the same `HEAD at dispatch`. Appending new entries for the
   re-dispatch invents a second dispatch that never verified anything.
2. `review.json` still carries the scaffold's template rows in
   `verdicts[]`, `probes[]`, `open_findings[]` (`<agent id>`,
   `PASS|PASS_WITH_NOTES|NEEDS_REVISION`, `<id>`). `loom_checker push`
   BLOCKs on every one of them. That is not damage — §7 of the review
   station writes those three arrays together at the end of the round,
   so a record with only `dispatch[]` real is the normal mid-round shape.
   Replace the template rows when writing the round; do not "repair"
   them first.
3. Probes that already ran this round (blind run, adversary files,
   package tests) were never recorded either — record them in the same
   §7 write, with `sha` = the HEAD the readers were given.

**Why:** the six BLOCKs together with an interrupted session read as a
corrupted record and invite a repair pass or a fresh checkpoint from
scratch; both waste a round. The record is append-only by design, and the
dispatch commit is the evidence that survives the interruption.

**How to apply:** on resuming, run `ListAgents`, then `git log -- review.json`;
if the last commit is a dispatch record, re-dispatch under its agent_ids
and finish §7 — nothing else.
