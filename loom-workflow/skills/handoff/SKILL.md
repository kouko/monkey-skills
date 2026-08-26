---
name: handoff
version: 0.3.0
description: |
  Save session state to a structured HANDOFF file so a future agent resumes cleanly, or load/verify a prior HANDOFF. Use for 'wrap up', 'save state', 'done for today', or 'pick up where we left off'. For in-session re-orientation use recap-state.
---

# Handoff

Preserve session state for a cold AI reader in a structured file under
`.claude/handoffs/`. Use **Prepare mode** when a user is ending a session and
**Resume mode** when starting from a prior HANDOFF. For in-session
re-orientation use `loom-workflow:recap-state`; this is not `/recap` or
agent-to-agent delegation.

The artifact is an operational restart record, not a polished human summary.
Its job is to let a new session prove that repository and tool state still
match, recover the user's exact intent, and stop before changing anything.
Completeness and precision therefore outrank narrative flow, but repeated
schema teaching belongs in the reference rather than this always-loaded file.

## Prepare mode

**Before authoring any HANDOFF artifact, read `references/handoff-schema.md` fully.**
It is the unchanged authority for the template, field semantics, and examples.
Do not reconstruct the schema from this entrypoint. Then:

1. Run these state-gathering commands and preserve their output verbatim:
   ```
   git rev-parse HEAD
   git rev-parse --abbrev-ref HEAD
   git status --short
   git log --oneline -5
   claude --version 2>/dev/null || codex --version 2>/dev/null || printf '%s\n' 'N/A — host CLI unavailable'
   ```

2. Write
   `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md`, with a short
   kebab-case slug, using all 10 blocks in schema order:
   1. Frontmatter
   2. Situation
   3. Background
   4. All user messages
   5. Recent decisions
   6. Pending
   7. Critical files
   8. Do Not Touch
   9. Verification commands
   10. Confidence flags

   Populate them according to the schema: frontmatter records
   `conversation_language`, git state, and host version. The
   `tools.claude_code` field holds Claude output, `N/A — Codex <version>`, or
   `N/A — host CLI unavailable`.
   Situation
   is one exact sentence; Background retains decisions, rejected paths, and
   critical paths. All user messages includes every turn verbatim. Recent
   decisions uses Decision / WHY / Rejected alternative triples. Pending is a
   P1/P2/P3 checklist. Critical files names each path, why it matters, and
   whether it changed. Do Not Touch gives exact paths and reasons. Verification
   commands are runnable assertions with expected output. Confidence flags rate
   every block with the schema's ✅/⚠️/❓ vocabulary.

   Set `conversation_language` to the language used with the user, not the
   language returned by a subagent or command. Preserve exact paths,
   identifiers, commands, full error messages, decisions, rejected
   alternatives, and user turns. The reader has zero conversational context;
   vague phrases such as "the usual file" or "tests mostly pass" are invalid.

3. In Block 9 tag every command **[T1] load-bearing** or **[T2] advisory**.
   Use [T1] for facts whose drift makes the saved next action unsafe or wrong,
   such as HEAD, branch, tool version, PR state, or test counts. Use [T2] for
   informative state that can change benignly but still deserves review.
   The new HANDOFF itself may add one untracked `git status --short` entry after
   the initial snapshot. Never make the raw status line count [T1]: either
   re-snapshot after writing or label it [T2] and record this known benign drift.

4. Append a closing `## Resume Launcher` and print the same copy-paste init
   prompt in chat. This launcher is a **thin pointer**, not a context re-dump.
   It must name the exact HANDOFF path, work without this skill installed,
   direct the next session to read the file, run [T1] checks, report [T2] drift,
   perform the Synthesis-check before acting, reply in `conversation_language`,
   and end with a blank `USER DIRECTIVE:` line. Do not reproduce any HANDOFF
   blocks in the launcher: the file remains the single source of truth. Append
   first so the launcher survives the current session, then show the identical
   text to the user for immediate copying.

## Resume mode

**Before interpreting any HANDOFF artifact, read `references/handoff-schema.md` fully.**
This read happens before judging, verifying, summarizing, or acting on the
artifact; do not rely on memory of a prior schema version. Then:

If the schema read is unavailable, fail closed: do not interpret or execute the
artifact. Still report any self-evident missing evidence in the supplied input,
such as a verification command with missing expected output, and request the
schema plus a corrected HANDOFF rather than treating read access as the only
blocker.

1. Find the latest file:
   ```
   ls -t .claude/handoffs/ | head -1
   ```

2. Read that HANDOFF fully. Adopt its `conversation_language` for every
   user-facing reply instead of defaulting to English. Keep subagent and tool
   output in its source language internally, but localize it before surfacing it
   to the user. Do not skim or begin pending work while reading.

3. **run every command** in Block 9. Report verbatim output next to expected
   output; do not collapse several results into a summary:
   ```
   Command: git log --oneline -5
   Expected: abc123 at top
   Actual: abc123 feat(loom-workflow): ...  ← MATCH
   ```

4. Apply the mismatch tiers command by command; an untagged command is treated as [T1], fail-safe.
   - A **[T1]** mismatch in HEAD, branch, version, PR state, test count, or other
     load-bearing state means **REFUSE TO CONTINUE**. Quote command, expected,
     and actual output, explain that state drifted, and ask how to proceed:
     > Load-bearing verification mismatch on `<command>`: expected `<X>`, got
     > `<Y>`. State has changed since the handoff was written. How do you want
     > to proceed?
   - A **[T2]** mismatch must still be reported verbatim and judged. Proceed
     only when it matches a recorded benign cause such as the known benign drift
     from the HANDOFF file itself; otherwise ask the user. Never silently waive
     it or treat every advisory mismatch as a hard stop. For example:
     > Advisory mismatch on `git status --short`: expected 3 untracked lines,
     > got 4 — the extra line is `.claude/handoffs/` itself (the known benign
     > drift). Proceeding.

5. Only after full verification passes, give a 3–5 bullet **Synthesis-check**
   covering situation, pending work, and next step, then ask the user to confirm
   or redirect. **Do not act until the user responds.**

## Invariants

Apply the schema's five principles every time:

- **structured-schema** — use all 10 blocks in order, never a free-form
  narrative substitute.
- **quote-not-paraphrase** — preserve load-bearing strings exactly, especially
  user intent, paths, identifiers, and errors.
- **all-user-messages** — include every user turn without deciding which ones
  seem important; the cold reader has no other user-intent record.
- **synthesis-check** — Resume mode ends at the directed confirmation question
  and waits for the user's answer.
- **technical-precision** — retain exact paths, identifiers, errors, commands,
  and expectations even when plainer wording would sound smoother.

## Boundaries

- Do not author `.claude/handoffs/` outside Prepare mode; other locations break
  the discovery command and this directory is canonical.
- Do not skip or sample Verification commands in Resume mode, even when the
  HANDOFF is recent. Run all of them before synthesis.
- Do not substitute a free-form summary for the 10 blocks or filter Block 4.
- Do not use this for in-session recap, an away-summary, or parallel delegation.
- Do not use `/compact` as a substitute for intentional handoff: compaction does
  not preserve the complete verbatim user-message record.

## See also

- `references/handoff-schema.md` — SSOT for 10-block template, 5 principles
  definitions, good-example / bad-example pair.
