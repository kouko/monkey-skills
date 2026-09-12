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
   recap**. It contains the full L3 template, the section rules, and the five
   principles. Do not render from memory.

2. Keep planning internal. Before writing, identify the current purpose,
   spec-critical phrases, useful visual forms, the most recent agent question,
   and the expected next step. Never output `<thinking>` or `<recap>` tags,
   their closing tags, or any planning scratchpad. Never expose `Block N` labels.
   Address the user directly under natural headings in the conversation language,
   following this order:

   ### Purpose and current position
   ### Essential background
   ### Gap and current assessment
   ### Why confirmation is needed now
   ### Pending work
   ### Align purpose and next step

   Adapt these headings naturally rather than translating them word for word.
   The structure is fixed; its internal names are not user-visible labels.

   The current purpose is mandatory; ground it in explicit conversation evidence.
   State the broader purpose only when explicitly established by the user or a
   confirmed goal or intent, and do not invent short-, medium-, or long-term goals
   to fill a hierarchy. If the evidence does not establish the
   current purpose, say that the purpose is not yet aligned and make that the
   only question in the final section.

3. Apply the Goal-Grounded Alignment Loop through the six sections:

   - **Purpose and current position**: state the grounded current purpose,
     any explicitly established broader purpose, and where the work stands
     relative to that purpose.
   - **Essential background**: give 3–5 bullets with decisions, rejected
     options, and critical strings. Preserve spec-critical user phrases
     verbatim: file paths, error messages, named constraints, exact tool names and
     command names.
   - **Gap and current assessment**: name what remains between the current
     position and purpose, the working assumption, confidence, and unknown or
     blocker. Gap and assessment defaults to 2-col key:value form.
   - **Why confirmation is needed now**: explain the most recent agent
     question, why it matters, and the options and trade-offs. If there is no
     pending question, say so briefly; do not invent one.
   - **Pending work**: list unfinished work that closes the stated gap.
   - **Align purpose and next step**: restate the purpose, current position, and proposed next step,
     then ask the user to confirm or redirect.

   A full user-message dump adds no signal for an in-session reader. If a user
   phrase affects behavior, retain it exactly in Essential background instead.

4. Apply the five principles defined in the schema:

   - **structured-schema**: use the fixed six-section L3 structure, never a
     free-form substitute.
   - **quote-not-paraphrase**: Essential background carries original
     spec-critical strings exactly.
   - **all-user-messages**: dormant at L3. Do not dump every user turn. If
     explicitly requested, list messages outside this schema.
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

5. Wait. Do not continue until the user responds to the final alignment check. Any clear
   confirmation (`yes`, `對`, `go`, `continue`, `繼続`, `はい`, `proceed`) opens
   this soft gate. If the user redirects, follow the redirect.

The Synthesis-check is a soft gate, not a ritual closing line. Do not render
the recap and immediately start a tool call, edit, or analysis based on the
agent's expected direction. A brief confirmation is enough; no special keyword
is required. A correction replaces the expected direction and should be
handled as the user's current instruction.

## Visual aids

Use tables or diagrams only when they compress information:

- Gap and assessment defaults to 2-col key:value.
- Why confirmation is needed now uses a comparison table for 2+ options.
- Pending work uses a table when items have metadata; otherwise use a checklist.
- The opening and final sections stay concise prose.
- Use a diagram only for real topology such as a pipeline, dependency graph,
  or state machine. When the client is known to render Mermaid, prefer
  Mermaid; for an unknown or terminal client, use ASCII. An explicit user
  format request overrides this fallback.

Do not add decorative visuals. Tables must flatten ≥3 sub-items or
compare ≥2 options; a one-row table or boxes around an unrelated list add cost.

Section defaults matter: the opening and alignment check are direct prose;
Essential background is normally bullets; Gap and current assessment is a
compact table; the confirmation explanation becomes a table only for a real
comparison; Pending work remains a checklist unless metadata would be lost.
Mermaid and ASCII are for spatial relationships, never a list with arrows.

## Hard boundaries

- Chat only: do not write the recap to a file.
- Current session only: cross-session work belongs to HANDOFF.
- Do not replace the built-in `/recap` away-summary.
- Do not dump all user messages at L3. Put necessary direct quotes in Essential background.
- Do not paraphrase spec-critical user phrases in Essential background.
- Do not continue after the recap; wait for the Synthesis-check response.

A free-form paragraph that covers similar facts is not equivalent to the six
sections: predictable placement is what makes re-orientation fast. Likewise, do
not resurrect the user-message dump when the user asks for message history. Supply that
listing separately, leaving the recap schema unchanged. Never weaken verbatim
preservation to make the prose sound smoother; invisible drift in a path,
error, constraint, or command is more damaging than a slightly abrupt quote.

## See also

- `references/seven-block-schema.md` — authoritative template, block rules,
  principles, visual guidance, and examples. Read it before rendering every
  recap.
