---
name: recap-state
version: 0.1.0
description: |
  in-session re-orientation: produce a structured recap ending with a Synthesis-check when the user loses the thread. Use for "where were we", "I'm lost", "我們剛剛在幹嘛", "剛剛講到哪", "我跟丟了", "ちょっと振り返って", "今どこだっけ", "振り返り", or similar requests. The built-in /recap is an away-summary; for cross-session continuation use handoff.
---

# Recap

Re-orient the user inside the current conversation, then pause for confirmation.
This is **in-session re-orientation**. The built-in `/recap` is an
`away-summary`; `HANDOFF` handles cross-session continuation. Do not replace
either sibling workflow.

## What to do

1. Read `references/seven-block-schema.md` fully before rendering **every
   recap**. It contains the full V1 template, the block rules, and the five
   principles. Do not render from memory.

2. Output exactly two sibling top-level tags:

   The first output character is `<`. Do not add prose before `<thinking>` or
   after `</recap>`. Do not wrap either tag in a Markdown fence.

   <thinking>
   [Private planning: identify spec-critical phrases, useful visual forms,
   the most recent agent question, and the expected next step.]
   </thinking>

   <recap>
   [Conversational explanation addressed to the user.]

   ### Block 1 — Situation
   ### Block 2 — Background
   ### Block 3 — Assessment
   ### Block 5 — Why-this-question
   ### Block 6 — Pending
   ### Block 7 — Synthesis-check
   </recap>

   `<thinking>` is planning; `<recap>` is the user-facing explanation. Do not
   blend their tones or content. At L3 render these six blocks in this order.
   Block 4 is L2-only and must not appear inside the recap.

   In `<thinking>`, make a short extraction pass before writing the recap:

   - Locate exact user wording that controls the work. Prioritize paths,
     errors, named constraints, and command or tool names; these belong in
     Block 2 without normalization.
   - Identify the agent's most recent question. That question, rather than a
     generic status update, determines Block 5.
   - Infer the next step the agent currently expects. Treat it as an
     assumption to check, not authorization to continue.
   - Choose a table or diagram only if the schema's compression threshold is
     met. Do not let visual planning delay a short recap.

   The user can see `<thinking>`, but it remains telegraphic agent-to-self
   planning. Switch deliberately to explanation-style prose inside `<recap>`.
   This tag boundary prevents internal shorthand from leaking into the text
   meant to restore the user's mental model.

3. Render the six L3 blocks:

   - **Block 1 — Situation**: one sentence locating the work and current snag.
   - **Block 2 — Background**: 3–5 bullets with decisions, rejected options,
     and critical strings. Preserve spec-critical user phrases verbatim:
     file paths, error messages, named constraints, exact tool names and
     command names. Quote directly; do not rewrite.
   - **Block 3 — Assessment**: current assumption, confidence, and unknown or
     blocker. Block 3 Assessment defaults to 2-col key:value form.
   - **Block 5 — Why-this-question**: explain the most recent agent question,
     why it matters, and the user's options and trade-offs.
   - **Block 6 — Pending**: checklist of unfinished work.
   - **Block 7 — Synthesis-check**: state the expected next direction in one
     sentence, then ask the user to confirm or redirect.

   Block 4 is skipped because an in-session human already remembers their own
   turns. A full message dump pushes the useful question and pending work out
   of view. If a user phrase affects behavior, retain that exact phrase in
   Block 2 instead. The displayed numbering remains 1, 2, 3, 5, 6, 7; do not
   renumber the six blocks to hide the deliberate L3/L2 distinction.

4. Apply the five principles defined in the schema:

   - **structured-schema**: use the fixed six-block L3 structure, never a
     free-form substitute.
   - **quote-not-paraphrase**: Block 2 carries original spec-critical strings
     exactly. At L3, it performs the preservation duty that Block 4 performs
     at L2.
   - **all-user-messages**: dormant at L3. Do not render Block 4 or dump every
     user turn. If explicitly requested, list messages outside this schema.
   - **synthesis-check**: finish with a directed question; the agent
     does not continue until user responds.
   - **plain-language**: explain TO the user in conversational second-person
     language, not status-report shorthand. Use technical terms only when the
     user introduced them; expand acronyms, prefer short sentences, and keep
     one fact per bullet.

   Plain language changes the relationship, not merely the vocabulary. Prefer
   “you were debugging X; we chose Y because Z” over “Current state: X.
   Decision: Y. Rationale: Z.” The latter still makes the user decode a report.
   Preserve a user-introduced technical term when precision depends on it;
   plain-language is not permission to paraphrase exact strings.

5. Wait. Do not continue until the user responds to Block 7. Any clear
   confirmation (`yes`, `對`, `go`, `continue`, `繼続`, `はい`, `proceed`) opens
   this soft gate. If the user redirects, follow the redirect.

The Synthesis-check is a soft gate, not a ritual closing line. Do not render
the recap and immediately start a tool call, edit, or analysis based on the
agent's expected direction. A brief confirmation is enough; no special keyword
is required. A correction replaces the expected direction and should be
handled as the user's current instruction.

## Visual aids

Use tables or ASCII only when they compress information:

- Block 3 Assessment defaults to 2-col key:value.
- Block 5 uses a comparison table for 2+ options.
- Block 6 uses a table when items have metadata; otherwise use a checklist.
- Blocks 1 and 7 stay one-sentence prose.
- Use ASCII only for real topology such as a pipeline, dependency graph, or
  state machine.

Do not add decorative visuals. Tables must flatten ≥3 sub-items or
compare ≥2 options; a one-row table or boxes around an unrelated list add cost.

Block-specific defaults matter: Situation and Synthesis-check are direct prose;
Background is normally bullets; Assessment is normally a compact table;
Why-this-question becomes a table only for a real comparison; Pending remains
a checklist unless owner, priority, dependency, or due-date metadata would be
lost. ASCII is for spatial relationships, never a list with arrows added.

## Hard boundaries

- Chat only: do not write the recap to a file.
- Current session only: cross-session work belongs to HANDOFF.
- Do not replace the built-in `/recap` away-summary.
- Do not render Block 4 at L3. Put necessary direct quotes in Block 2.
- Do not paraphrase spec-critical user phrases in Block 2.
- Do not continue after the recap; wait for the Synthesis-check response.

A free-form paragraph that covers similar facts is not equivalent to the six
blocks: predictable placement is what makes re-orientation fast. Likewise, do
not resurrect Block 4 when the user asks for message history. Supply that
listing separately, leaving the recap schema unchanged. Never weaken verbatim
preservation to make the prose sound smoother; invisible drift in a path,
error, constraint, or command is more damaging than a slightly abrupt quote.

## See also

- `references/seven-block-schema.md` — authoritative template, block rules,
  principles, visual guidance, and examples. Read it before rendering every
  recap.
