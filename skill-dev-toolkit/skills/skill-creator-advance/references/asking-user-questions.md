# Asking User Questions — The Hardened Pattern

When a skill needs structured user input via Anthropic's `AskUserQuestion`
tool (Claude Code main agent only), apply the empirically-validated pattern
below to maximize tool invocation reliability and prevent silent-default
failure modes.

This pattern is a project convention; copy it into any new skill that has
a user-input step. Skills with no user-input steps are exempt.

## Background — what fails

Three documented failure modes in industry practice:

1. **Inline fallback** — Claude renders the question as plain text instead
   of invoking the tool (loses UI buttons, breaks conversational flow).
2. **Silent default** — Claude assumes a "recommended default" and skips
   asking entirely. Documented in Anthropic's own retrospective on the
   first two `AskUserQuestion` design iterations
   ([Seeing like an agent](https://claude.com/blog/seeing-like-an-agent)).
3. **Tool unavailable** — In subagent / web-client / sandbox contexts,
   `AskUserQuestion` is not loaded. Without explicit fallback, skills
   silently default or skip.

The hardenings below close all three failure modes.

## The Thariq canonical phrase (load-bearing)

@trq212 (Anthropic) documented this as the most reliable trigger pattern:

> Use AskUserQuestion to interview the user about [X]. Make sure questions
> are not obvious — surface the real trade-off.

Three load-bearing tokens:

- **`AskUserQuestion`** literal name (not "ask the user", not "user prompt",
  not "user input")
- **interview** (signals multi-round, not one-shot Q&A)
- **not obvious** (triggers Anthropic's built-in question-quality filter
  documented in the AskUserQuestion system prompt)

## The 4 hardenings

### 1. MUST verb (not "Use")

`Use AskUserQuestion` reads as a soft suggestion. Empirical A/B tests show
the model treats it as "prefer this mechanism if convenient" rather than a
binding instruction. Use stronger phrasing:

```markdown
You MUST call the AskUserQuestion tool to interview...
```

Or with a gate clause:

```markdown
This step is mandatory. Do not proceed to STEP X+1 without explicit user
selection gathered through AskUserQuestion.
```

### 2. Args-schema example (not prose Q&A template)

A fenced block in the format:

```
Question: "Which folder?"
Options:
1. daily
2. inbox
```

…visually resembles **output the model should write**, not arguments to
pass into a tool. The model can shortcut the tool and just emit this as
message text.

Replace with a JSON-shape example showing the actual tool call structure:

````markdown
You MUST call AskUserQuestion with arguments matching this schema:

```json
{
  "questions": [
    {
      "question": "<non-obvious question that surfaces a real trade-off>",
      "header": "<≤12 char chip label>",
      "multiSelect": false,
      "options": [
        {"label": "X (Recommended)", "description": "<one-sentence trade-off>"},
        {"label": "Y", "description": "<one-sentence trade-off>"}
      ]
    }
  ]
}
```
````

The `json` code-fence visually signals "this is data going into a function"
rather than "this is text to write back".

### 3. Fallback contract

Add an explicit fallback for environments where `AskUserQuestion` is not
loaded (subagents, claude.ai web, sandboxed runners):

```markdown
### Fallback contract

If AskUserQuestion is unavailable in your environment (subagent context,
web client, sandbox), inline the question as plain text with the same
options. Do NOT silently default to any preset. Do NOT skip the step.
The user-as-gate contract must be honored regardless of UI mechanism.
```

Without this clause, the failure mode in tool-unavailable environments is
silent default — the most invisible bug class.

### 4. (Recommended) marker on first option

Per [Anthropic's official AskUserQuestion guidance](https://platform.claude.com/docs/en/agent-sdk/user-input),
mark the preferred option:

```json
{"label": "X (Recommended)", "description": "..."}
```

This anchors user choice and prevents flat-options confusion. It also
signals to the model that taking a position is required, rather than
presenting options as flat alternatives.

## Mandatory-gate template

Copy this stanza into any STEP that needs user disambiguation:

````markdown
## STEP X — [name] (mandatory)

This step is mandatory. Do not proceed to STEP X+1 without explicit user
selection gathered through AskUserQuestion.

You MUST call the AskUserQuestion tool with arguments matching:

```json
{
  "questions": [
    {
      "question": "<non-obvious question that surfaces a real trade-off>",
      "header": "<≤12 char label>",
      "multiSelect": false,
      "options": [
        {"label": "<concise label> (Recommended)", "description": "<trade-off>"},
        {"label": "<...>", "description": "<...>"}
      ]
    }
  ]
}
```

Generate 2-4 options yourself based on the user's context. Cover at least
these dimensions: [list dimensions specific to your skill — e.g.,
"data-source folders", "exclusion patterns", "approval workflow"].

Do not ask obvious meta-questions ("is this ok?", "should I proceed?").
Surface the real trade-off between the options.

### Fallback contract

If AskUserQuestion is unavailable, inline as plain text with same options.
Do NOT silently default. Do NOT skip the step.
````

## Anti-patterns to avoid

| Anti-pattern | Why it fails |
|---|---|
| `Use AskUserQuestion` (soft verb) | Model treats as suggestion, not binding |
| Pre-baked "(recommended default)" prose label | Invites silent default — model thinks "user accepts default = no need to ask" |
| Fenced block with `Question: / Options:` format | Looks like message-text template, not tool args |
| `Is the plan ready?` / `Should I proceed?` | Anthropic system prompt routes these to `ExitPlanMode`, not `AskUserQuestion` |
| No fallback contract | Subagent / web-client contexts silently default |
| Options without `(Recommended)` marker | Flat-options confusion; model may inline-list or skip |
| Combining AskUserQuestion + another tool in same step | Documented Anthropic failure mode (their first two iterations both failed this way) |

## Limitations

- `AskUserQuestion` is **main agent only** in Claude Code. Subagents
  spawned via the Agent / Task tool do not have access. The fallback
  contract handles this.
- Soft-cap: ~4-6 questions per session before the model starts batching
  or deferring. Cap your skill at ≤3 questions per invocation.
- 60-second timeout; design with a reasonable default selection in mind.
- Not currently exposed in the public Anthropic API — only Claude Code.
  ([anthropic-sdk-typescript#836](https://github.com/anthropics/anthropic-sdk-typescript/issues/836))

## When to skip this pattern

Don't apply this pattern when:

- The skill is purely deterministic (no user-input branch points)
- The skill is single-shot generation (formatter, transformer, lint)
- The user-input is free-form text (not a discrete choice from 2-4 options)
- The skill runs in a context where blocking the user is unacceptable
  (autonomous agent, batch job)

For free-form text input, consider a different mechanism (chat prompt,
filesystem watch, etc.).

## References

- [Seeing like an agent — Anthropic engineering](https://claude.com/blog/seeing-like-an-agent) — official Anthropic retrospective on the failure modes that led to the dedicated tool design
- [Handle approvals and user input — Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/user-input) — official Anthropic doc with `(Recommended)` guidance
- [Thariq's canonical interview prompt (gist)](https://gist.github.com/robzolkos/40b70ed2dd045603149c6b3eed4649ad)
- [neonwatty.com — Interview skills with AskUserQuestion](https://neonwatty.com/posts/interview-skills-claude-code/) — practitioner walk-through of mandatory-gate patterns
- [ClaudeLog — AskUserQuestion FAQ](https://claudelog.com/faqs/what-is-ask-user-question-tool-in-claude-code/)
- [GitHub: claude-code#9846 — AskUserQuestion inert until plan mode toggled](https://github.com/anthropics/claude-code/issues/9846) — known bug requiring plan-mode framing

---

## Empty-Prompt Onboarding (companion intake pattern, moved from SKILL.md body)

A related user-interaction-at-intake pattern — recommended for conversational / multi-workflow skills. When a user invokes a skill with no prompt or a very sparse prompt, consider including a "surface orientation" behavior so the skill can introduce itself, explain how it works with the user, and ask for the minimum inputs needed. This is an opt-in pattern — single-shot utility skills (file transforms, fixed-format generators) don't need it; conversational or multi-workflow skills benefit significantly.

**Recommended pattern** (adapt to your skill's shape):

1. **Surface orientation** — present the user with:
   - What the skill does (top 3 triggers from the description's "Use when" clause)
   - What it doesn't do (delegation hints for adjacent skills)
   - How the interaction will unfold (intake questions + workflow phases + delivery)
   - What inputs help most (2-3 prerequisite bullets)
2. **Route to intake** — either invoke a dedicated brainstorming protocol OR ask 2-3 bootstrap questions covering scope / inputs / output expectation
3. **Sufficient-context skip** — bypass orientation when any context source already provides an actionable brief. Check **all** of these, not just the current prompt:
   - (a) Current-turn prompt ≥50 chars with a concrete ask
   - (b) Prior conversation turns state scope / artifact / output expectation
   - (c) IDE context (`<ide_selection>`, opened files) identifies the target
   - (d) Referenced plan / memory file encodes the brief
   - (e) Upstream skill handoff (main agent provided a prior skill's output)

**Common pitfall**: triggering orientation on "empty current prompt" alone creates friction for returning users — Claude's context often already carries the brief. Always check the full context, not just the current prompt's length.

For domain-team skills (which follow a stricter structural-gate convention), this pattern is a hard requirement encoded in the CHK-SKL-013 gate — consult your domain-team plugin's structure standard for the rigorous version (Empty Invocation Fallback Rules + a Surface Orientation Format skeleton, with a hard-gate exception for skills with mandatory intake).
