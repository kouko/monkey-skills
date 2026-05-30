---
name: handoff
version: 0.1.1
description: >-
  Cross-session continuation skill. When a work session ends and the user
  wants to save state so a future AI agent can resume without losing context —
  produce a structured 10-block HANDOFF file in `.claude/handoffs/` (prepare
  mode), or load and verify a prior HANDOFF file before resuming work (resume
  mode). Not the same as `dev-workflow:recap-state` (L3 in-session re-orientation
  for a human reader still in the session). Not agent-to-agent delegation
  (not the OpenAI Agents SDK handoff_<id>_tool pattern — that is a different
  problem). This skill is cross-session L2: cold AI reader, new session, zero
  prior context.

  Prepare-mode triggers (fire when you recognise any of these):
  - **zh-TW**: 「收尾」「明天繼續」「保存狀態」「先這樣」「記錄一下進度」「今天先到這」
  - **ja**: 「今日はここまで」「引き継ぎ」「状態を保存して」「セッションを終わる」
  - **en**: "wrap up" / "save state" / "I'm done for today" / "let's stop here"
    / "save progress" / "end session"

  Resume-mode triggers (fire when you recognise any of these):
  - **zh-TW**: 「繼續上次」「從上次說到哪裡」「載入狀態」「接著做」
  - **ja**: 「前回の続きから」「引き継ぎを読んで」「再開して」
  - **en**: "pick up where we left off" / "load handoff" / "resume from last
    session" / "continue where we stopped"

  Disambiguation: `dev-workflow:recap-state` is L3 in-session (human warm reader,
  current session, chat output only). `dev-workflow:handoff` is L2
  cross-session (cold AI reader, new session, file output). The two coexist.
  Not agent-to-agent delegation — that is OpenAI Agents SDK or similar
  (different problem). クロスセッション引き継ぎ・セッション終了時保存・再開時ロード。
  跨對話接續・保存狀態・冷啟動恢復。
---

# Handoff

## What this skill does

Produces or consumes a structured 10-block HANDOFF file in
`.claude/handoffs/`. Two modes:

- **Prepare mode** — end of session. Gather live git state via Bash,
  then Write a file named `HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md` under
  `.claude/handoffs/`. All 10 blocks per `references/handoff-schema.md`.
- **Resume mode** — start of session. Find the latest HANDOFF file, Read it,
  run every Verification Command via Bash, report verbatim output, and surface
  any mismatch before acting.

The HANDOFF file is for a cold AI reader (new session, zero context). It is
not a human-readable summary — precision beats readability here (see
`technical-precision` principle below).

## When to fire

Fire when you recognise any prepare-mode or resume-mode trigger from the
frontmatter. When in doubt: if the user is ending a session → prepare mode;
if the user is starting work and mentions a prior session → resume mode.

**Layer table** — choose the right skill:

| Situation | Skill |
|---|---|
| Lost thread mid-session (human still in conversation) | `dev-workflow:recap-state` (L3 in-session) |
| Ending session; want cold AI to resume later | `dev-workflow:handoff` prepare mode (L2 cross-session) |
| Starting new session; loading prior state | `dev-workflow:handoff` resume mode (L2 cross-session) |
| User returns to a session after being away (built-in) | Claude Code `/recap` away-summary (built-in, different tool) |
| Delegating a sub-task to a parallel agent | OpenAI Agents SDK `handoff_<id>_tool` or similar (not this skill) |

## Prepare mode — what to do

**HARD-GATE: do not skip these Bash steps. State gathered here is the ground
truth for the future cold AI reader.**

1. Run via Bash (report all output verbatim in the HANDOFF file):
   ```
   git rev-parse HEAD
   git rev-parse --abbrev-ref HEAD
   git status --short
   git log --oneline -5
   claude --version
   ```

2. Use Write to create `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md`
   where `<slug>` is a short kebab-case description of the work (e.g.
   `handoff-skill-t2`, `auth-refactor-session-3`).

3. Author all 10 blocks per `references/handoff-schema.md`:
   1. Frontmatter (YAML — git.head, git.dirty, tools.claude_code)
   2. Situation (one sentence — exact present state)
   3. Background (decisions + rejected paths + critical paths, verbatim)
   4. All user messages (every turn verbatim — no filtering)
   5. Recent decisions (Decision / WHY / Rejected alternative triples)
   6. Pending (checklist with P1/P2/P3 priority)
   7. Critical files (path + why-it-matters + recently-modified)
   8. Do Not Touch (explicit guardrails — exact paths + reasons)
   9. Verification commands (runnable shell assertions + expected output)
   10. Confidence flags (per-block ✅/⚠️/❓ table)

4. When authoring Block 9, **tag each verification command [T1] load-bearing or
   [T2] advisory** per `references/handoff-schema.md` §Block 9, and account for
   the self-reference: the HANDOFF file you just wrote adds an untracked entry to
   `git status --short` (the snapshot in step 1 predates the Write), so **never
   encode a raw git-status line count as a [T1] assertion** — keep it [T2] with a
   "+1 for `.claude/handoffs/` itself" benign-drift note, or re-snapshot after
   the Write.

5. Apply `technical-precision` throughout: exact file paths, full error
   messages, precise command names. The reader is a cold AI tool — vague
   descriptions cause wrong-path assumptions.

## Resume mode — what to do

**HARD-GATE: run ALL Verification Commands and report verbatim. A [T1
load-bearing] mismatch means STOP. A [T2 advisory] mismatch is reported and
judged, not an automatic stop — see step 4.**

1. Run via Bash to find the latest HANDOFF:
   ```
   ls -t .claude/handoffs/ | head -1
   ```

2. Read the file. Read it fully — do not skim.

3. Run EACH Verification Command from Block 9 via Bash. Report the verbatim
   output next to the expected output. Example format:
   ```
   Command: git log --oneline -5
   Expected: abc123 at top
   Actual: abc123 feat(dev-workflow): ...  ← MATCH
   ```

4. **Apply the tier rule to each mismatch** (Block 9 tags every command [T1] or
   [T2]; an untagged command is treated as [T1], fail-safe):
   - **[T1] load-bearing mismatch** (HEAD / branch / version / PR state / test
     counts) → **REFUSE TO CONTINUE.** State has drifted since the HANDOFF was
     written. Surface it:
     > "Load-bearing verification mismatch on `<command>`: expected `<X>`, got
     > `<Y>`. State has changed since the handoff was written. How do you want
     > to proceed?"
   - **[T2] advisory mismatch** (e.g. `git status` line count) → **report it
     verbatim, state whether it matches the known benign drift, and proceed only
     if benign.** Do NOT silently wave it through, and do NOT hard-stop on it:
     > "Advisory mismatch on `git status --short`: expected 3 untracked lines,
     > got 4 — the extra line is `.claude/handoffs/` itself (the known benign
     > drift). Proceeding."

5. After all verifications PASS, produce a Synthesis-check (soft gate):
   summarise your understanding of the situation, pending work, and next
   step in 3–5 bullets, then ask the user to confirm or redirect before
   acting. Do not act until the user responds.

## Apply all 5 共通核心原則

See `references/handoff-schema.md` §3 for full definitions. One-line reminder
per principle:

- **structured-schema**: use all 10 blocks every time — no free-form narrative.
- **quote-not-paraphrase**: blocks 3, 4, 5 reproduce exact strings — file
  paths, error messages, user turns verbatim.
- **all-user-messages**: block 4 lists every user turn — no LLM filtering of
  "unimportant" messages (the cold reader has no other source of user intent).
- **synthesis-check**: resume mode always ends with a directed question; agent
  does not continue until the user confirms.
- **technical-precision**: HANDOFF output uses full paths, exact identifiers,
  complete error messages. Reader is a cold AI tool — plain-language softening
  removes load-bearing precision.

## What NOT to do

- **Do not replace the built-in `/recap`** (away-summary). That fires when the
  user returns to a session after being away. This skill fires when the user
  explicitly wants to end a session or resume from a prior one.
- **Do not use this for in-session re-orientation** — that is
  `dev-workflow:recap-state` (L3). If the user is still in the current session and
  just needs a "where were we", use recap.
- **Do not treat this as agent-to-agent delegation** — not the OpenAI
  `handoff_<id>_tool` pattern. That is a parallel-agent orchestration problem;
  this is a cross-session state-preservation problem.
- **Do not skip Verification Commands on resume** (HARD-GATE). Even if the
  HANDOFF looks recent, run the commands. State may have drifted.
- **Do not produce a free-form narrative instead of the 10 blocks** — the
  schema is the cold reader's navigation map; a prose summary with "basically
  we were doing X" is not equivalent.
- **Do not author `.claude/handoffs/` files outside prepare mode** — the
  directory is the canonical storage for HANDOFF files. Other paths break
  the `ls -t .claude/handoffs/ | head -1` discovery command.
- **Do not compact context to "save space" instead of handoff** — compaction
  loses the verbatim user-message record (Block 4). Use this skill for
  intentional state preservation; use built-in `/compact` only when context
  pressure (not session end) forces it.

## See also

- `references/handoff-schema.md` — SSOT for 10-block template, 5 principles
  definitions, good-example / bad-example pair.
