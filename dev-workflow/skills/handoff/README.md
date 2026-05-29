# Handoff

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> End a session by writing a 10-block HANDOFF file to `.claude/handoffs/`.
> Start the next session by loading that file, running every verification
> command verbatim, and synthesising before acting. Cold AI restart,
> zero context loss.

---

## Overview — what this skill does

This skill handles cross-session state preservation. When you finish a
work session and want a future AI agent to resume exactly where you left
off — without rebuilding context from memory or chat history — this skill
writes a structured 10-block HANDOFF file to `.claude/handoffs/`.

Two modes:

- **Prepare mode** — end of session. The agent runs `git rev-parse HEAD`,
  `git status --short`, `git log --oneline -5`, and `claude --version` via
  Bash, then writes `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md`
  with all 10 blocks per `references/handoff-schema.md`. The output is
  precision-first: exact paths, full error messages, verbatim user turns,
  runnable verification commands.

- **Resume mode** — start of session. The agent finds the latest file via
  `ls -t .claude/handoffs/ | head -1`, reads it fully, runs every
  Verification Command (Block 9) via Bash and reports verbatim output, and
  refuses to continue if any output mismatches expected. After all
  verifications pass, it produces a 3–5 bullet Synthesis-check and asks the
  user to confirm before acting.

The HANDOFF file targets a cold AI reader — a new session with zero prior
context. Precision beats readability: technical paths, exact identifiers,
complete command output.

---

## When to use vs sister `recap`

Both skills help you re-orient, but they target different situations:

| Situation | Skill |
|---|---|
| Lost the thread **mid-session** (you're still in the conversation) | `dev-workflow:recap-state` (L3 in-session re-orientation, chat output only) |
| **Ending a session**; want a cold AI to resume later | `dev-workflow:handoff` prepare mode |
| **Starting a new session**; loading prior state | `dev-workflow:handoff` resume mode |
| You returned to an open session after being away (built-in) | Claude Code built-in `/recap` (away summary) |
| Delegating a sub-task to a parallel agent | OpenAI Agents SDK or similar (different problem) |

`dev-workflow:recap-state` is L3 — it writes nothing to disk, targets a warm human
reader still inside the session, and produces a 7-block chat summary.

`dev-workflow:handoff` is L2 — it writes a file to `.claude/handoffs/`,
targets a cold AI reader in a future session, and enforces runnable
verification before acting.

The two skills coexist and complement each other.

---

## Example invocation phrases

### Prepare mode — say any of these at session end

- "wrap up"
- "save state"
- "save progress"
- "I'm done for today"
- "let's stop here"
- "end session"
- "record where we are"
- "write a handoff"

### Resume mode — say any of these at session start

- "pick up where we left off"
- "load handoff"
- "load the latest handoff"
- "resume from last session"
- "continue where we stopped"
- "read the handoff file"
- "continue from yesterday"

The skill reads all multilingual trigger phrases from its frontmatter —
Japanese and Traditional Chinese phrases also fire the appropriate mode.

---

## `.gitignore` recommendation

`dev-workflow:handoff` always writes HANDOFF files to `.claude/handoffs/`.
Whether you commit them to git is your policy choice:

**Opt-in (don't commit)** — add to `.gitignore`:
```
.claude/handoffs/
```
Use this if handoff files contain sensitive context (auth tokens, internal
paths, private task details) or if you don't want session artifacts in git
history.

**Opt-out (keep in git history)** — leave `.claude/handoffs/` out of
`.gitignore`. HANDOFF files then travel with the branch; teammates or your
future self on a different machine can `git checkout` and resume from a
known-good state.

v0.1 is path-prescriptive: the skill always writes to `.claude/handoffs/`
and the resume-mode discovery command (`ls -t .claude/handoffs/ | head -1`)
depends on that path. Git-tracking is user-neutral — the skill does not
add or modify `.gitignore`.

---

## What's deferred to v0.2

These are deliberate omissions from v0.1:

- **Forced-handoff trigger detection** — recognising implicit session-end
  signals (context pressure, long silence, user says "bye") without an
  explicit trigger phrase. v0.1 requires explicit invocation.
- **Interruption Snapshot block** — a dedicated Block 11 for mid-task
  interruptions (not session-end). v0.1 uses the existing 10-block schema
  for all cases.
- **Per-tool init-prompt variants** — Codex / Cursor / Gemini have
  different write paths; v0.1 uses Claude Code's Write tool as the only
  write path. Reading a HANDOFF file (resume mode) is already cross-tool
  (any tool that can `read` markdown works).
- **`test-prompts.json` + `trigger-eval.json` scaffolding** — structured
  eval for trigger accuracy and schema completeness. Coming once real-session
  dogfood establishes a quality baseline.

---

## Files

```
handoff/
├── README.md           <- English (this file)
├── README.ja.md        <- 日本語
├── README.zh-TW.md     <- 繁體中文
├── SKILL.md            <- operational file (for Claude)
└── references/
    └── handoff-schema.md  <- 10-block template + 5 core principles
```
