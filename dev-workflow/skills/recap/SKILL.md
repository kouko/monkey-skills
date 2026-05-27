---
name: recap
version: 0.1.0
description: >-
  In-session re-orientation skill. When the user loses track of what we were
  doing mid-conversation — after a break, a long tool output, or an agent
  question whose premise they can no longer reconstruct — produce a structured
  7-block recap in chat and end with a Synthesis-check before continuing.

  Triggers (fire when you recognise any of these phrases):
  - **zh-TW**: 「我們剛剛在幹嘛」「我們在做什麼」「剛剛講到哪」「帶我回到」「我跟丟了」
  - **ja**: 「ちょっと振り返って」「今どこだっけ」「振り返りをして」「状況を整理して」
  - **en**: "where were we" / "I'm lost" / "recap" / "bring me back" / "what are we doing"
  - **slash**: User types `/recap` inside a skill conversation (NOT the built-in away-summary).

  **Disambiguation**: Claude Code v2.1.108+ ships a built-in `/recap`
  (away-summary) that fires when the user returns to a session after being away.
  That is a cross-context return tool. This skill is different: it is an
  in-session re-orientation tool that the user invokes explicitly while already
  in conversation. The built-in away-summary continues to work as designed;
  this skill fills the gap the built-in does not cover.

  Do NOT use for: new-session continuation (that is HANDOFF, a future skill),
  compacting context to save tokens (use built-in /compact), or replacing the
  built-in away-summary.
  構造化振り返り・会話内リオリエンテーション・セッション途中で迷子になったとき。
  結構化對話重新定位・對話中途迷失・七格式摘要。
---

# Recap

## What this skill does

When you are mid-conversation and lose the thread — because of a break, a long
tool output, or an agent question you can no longer place — this skill stops,
restructures the last N minutes into a fixed 7-block schema, and ends with a
Synthesis-check question. You read yourself back into state in under 60 seconds,
confirm the next step, and then the work continues.

## When to fire

Fire when you recognise any of the trigger phrases listed in the frontmatter
description, or when the user explicitly says something like "where are we" /
"我不知道你在說什麼" / "今どこまで来た".

**This skill is in-session re-orientation.** The built-in `/recap` (away-summary)
handles the cross-context return case — user was away, comes back, gets a summary.
That is different. This skill fires while the user is already in conversation and
has lost the thread. The two coexist; do not replace the built-in away-summary.

## What to do

1. Read `references/seven-block-schema.md` for the full V1 template and the
   5 共通核心原則 definitions.

2. Produce a single in-chat message (no file output) with all 7 blocks in order:

   - **Block 1 — Situation**: one sentence, present moment, where we are stuck.
   - **Block 2 — Background**: 3–5 bullets; key decisions + rejected options +
     critical file names / error strings. Quote directly — do not rewrite.
   - **Block 3 — Assessment**: current assumption + confidence level + what is
     unknown or blocking.
   - **Block 4 — User messages (compressed)**: one-line intent per user turn
     + verbatim quote of any spec-critical phrase (file paths, error messages,
     named constraints, exact tool/command names). No filtering of which turns
     to represent. User can request full verbatim with "show me my original
     messages."
   - **Block 5 — Why-this-question**: explain the agent's most recent question:
     what is being asked, why it matters, what options the user has.
   - **Block 6 — Pending**: checklist of tasks not yet done.
   - **Block 7 — Synthesis-check**: one sentence stating the expected next step,
     then ask the user to confirm or redirect.

3. Apply all 5 共通核心原則 throughout:

   - **structured-schema**: use the fixed 7-block structure every time. No
     free-form paragraphs substituted for blocks.
   - **quote-not-paraphrase**: blocks 2 and 4 reproduce original strings exactly —
     file paths, error messages, command names, user wording.
   - **all-user-messages**: block 4 represents every user turn — compressed
     (one-line intent + verbatim spec-critical phrases) for L3 in-session
     human reader, fully verbatim for L2 cross-session AI reader (future
     HANDOFF skill). No turn is dropped as "unimportant" in either form.
   - **synthesis-check**: block 7 always ends with a directed question; agent
     does not continue until user responds.
   - **plain-language**: write in plain everyday language. Only use a technical
     term if the user introduced it in this session. Expand acronyms on first
     mention. Short sentences. One fact per bullet.

4. After producing the 7 blocks, wait. Do not continue until the user responds
   to the Synthesis-check question in block 7.

## Soft-gate Synthesis-check

Block 7 is a soft gate: any "yes / 對 / go / continue / 繼続 / はい / proceed"
counts as confirmation and the agent continues. The agent does not hard-block on
a specific keyword — any clear confirmation from the user is enough. If the user
redirects instead of confirming, follow the redirect.

The Synthesis-check is **not** a formality. Ending the recap and immediately
continuing without waiting is the failure mode this block exists to prevent —
the agent would resume from its own assumption of alignment, and the user's
correction would only surface 3 turns later.

## What NOT to do

- **No file output**: the 7-block recap goes in chat only. Do not write a file.
- **No cross-session work**: this skill covers the current session only.
  Cross-session continuation is HANDOFF (a future sister skill).
- **Do not replace the built-in `/recap`**: the away-summary is a different
  tool for a different moment. This skill fills the in-session gap.
- **Do not produce a free-form summary instead of the 7 blocks**: the schema is
  the user-visible value. A paragraph that "covers the same ground" is not
  equivalent — it breaks the structured-schema principle.
- **Do not drop user turns**: block 4 represents every user turn in the
  session (compressed: one-line intent + verbatim spec-critical phrases).
  Deciding a turn doesn't matter is the failure mode this rule prevents —
  even routine "go" / "好" turns count as state transitions worth a line.
- **Do not paraphrase spec-critical phrases**: file paths, error messages,
  named constraints, exact tool / command names stay verbatim inside the
  compressed line. Losing those is invisible intent loss.

## See also

- `references/seven-block-schema.md` — SSOT for the V1 7-block template,
  5 共通核心原則 definitions, good-example / bad-example pair.
