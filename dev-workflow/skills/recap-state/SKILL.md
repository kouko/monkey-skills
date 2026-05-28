---
name: recap-state
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

2. Produce a single in-chat message (no file output) with **6 blocks** in
   order. (Block 4 from the bundle is L2-only and is skipped at L3 — see
   `references/seven-block-schema.md` §"Block ↔ Audience map".)

   - **Block 1 — Situation**: one sentence, present moment, where we are stuck.
   - **Block 2 — Background**: 3–5 bullets; key decisions + rejected options +
     critical file names / error strings. Quote directly — do not rewrite.
     **This is where spec-critical user phrases land at L3** (since Block 4
     does not render).
   - **Block 3 — Assessment**: current assumption + confidence level + what is
     unknown or blocking.
   - *(Block 4 — User messages — **skipped at L3.** L2-only; the future
     HANDOFF sister skill renders it verbatim for a cold AI reader. At L3
     the human reader already remembers their own turns; dumping them adds
     no signal.)*
   - **Block 5 — Why-this-question**: explain the agent's most recent question:
     what is being asked, why it matters, what options the user has.
   - **Block 6 — Pending**: checklist of tasks not yet done.
   - **Block 7 — Synthesis-check**: one sentence stating the expected next step,
     then ask the user to confirm or redirect.

3. Apply all 5 共通核心原則 throughout (4 of the 5 fire at L3; the 5th
   `all-user-messages` is L2-only and dormant here — kept named in the
   principle list as the canonical SSOT for the future HANDOFF sister skill):

   - **structured-schema**: use the fixed block structure every time. No
     free-form paragraphs substituted for blocks. At L3 = 6 blocks (skip
     Block 4).
   - **quote-not-paraphrase**: block 2 (and block 4 at L2) reproduces original
     strings exactly — file paths, error messages, command names, user
     wording. **At L3 this principle does the work Block 4 used to do** —
     spec-critical user phrases land in Block 2's quote-not-paraphrase
     enforcement.
   - **all-user-messages** *(L2-only — dormant at L3)*: at L2 HANDOFF block 4
     lists every user turn verbatim. At L3 (this skill) the principle does
     not fire; Block 4 is skipped entirely. Anchor preserved here as SSOT
     for HANDOFF.
   - **synthesis-check**: block 7 always ends with a directed question; agent
     does not continue until user responds.
   - **plain-language**: each block **explains TO the user** in plain everyday
     language — write as if speaking to them ("you were debugging X" / "we
     picked Y because Z"), NOT reporting at them ("Current state: X.
     Decisions: Y, rationale: Z."). Use second-person framing where natural.
     Only use a technical term if the user introduced it in this session.
     Expand acronyms on first mention. Short sentences. One fact per bullet.
     See `references/seven-block-schema.md` §plain-language for the
     report-style vs explanation-style failure-mode contrast.

4. **Visual aids** (tables / ASCII diagrams): permitted **only when they
   compress information**, not as decoration. See `references/seven-block-schema.md`
   §1.5 for per-block guidance. Block 3 (Assessment) defaults to a 2-col
   key:value table. Block 5 (Why-this-question) and Block 6 (Pending) use
   tables when there are 2+ options or per-item metadata, prose otherwise.
   Skip tables for blocks 1 + 7 (single sentence). Reach for ASCII only when
   real topology exists (pipeline / dependency / state machine).

5. After producing the 6 L3 blocks (Block 4 skipped), wait. Do not continue
   until the user responds to the Synthesis-check question in block 7.

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
- **Do not produce a free-form summary instead of the 6 L3 blocks**: the schema is
  the user-visible value. A paragraph that "covers the same ground" is not
  equivalent — it breaks the structured-schema principle.
- **Do not render Block 4 at L3**: that block is L2-only (for the future
  HANDOFF sister skill's cold AI reader). At L3 the human reader already
  remembers their own turns. If you find yourself listing user messages,
  stop and ask whether the content actually belongs in Block 2 Background.
- **Do not paraphrase spec-critical phrases in Block 2**: file paths, error
  messages, named constraints, exact tool / command names stay verbatim.
  At L3 Block 2 is the only place spec-critical user phrases land (since
  Block 4 is skipped) — losing those quotes here is invisible intent loss.
- **If the user actually asks for verbatim user-message listing at L3**:
  produce it as a separate response outside the recap schema, not as a
  ressurected Block 4. The 6-block recap stays focused.
- **Do not add decorative tables / ASCII**: a 1-row table, a 2-row table whose
  rows are unrelated, or an ASCII chart for a 3-item list adds framing without
  compressing. Per `references/seven-block-schema.md` §1.5, tables fire only
  when they flatten ≥3 sub-items or compare ≥2 options.

## See also

- `references/seven-block-schema.md` — SSOT for the V1 7-block template,
  5 共通核心原則 definitions, good-example / bad-example pair.
