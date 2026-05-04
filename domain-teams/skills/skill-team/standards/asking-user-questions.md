# Standard: Asking User Questions — The Hardened Pattern

When a domain-team skill needs structured user input via Anthropic's
`AskUserQuestion` tool (Claude Code main agent only), apply the
empirically-validated pattern below to maximize tool invocation
reliability and prevent silent-default failure modes.

This standard is enforced by **CHK-SKL-014** in
[`checklists/skill-completeness-checklist.md`](../checklists/skill-completeness-checklist.md).

## Why this standard exists

Three documented failure modes in industry practice:

1. **Inline fallback** — Claude renders the question as plain text instead
   of invoking the tool (loses UI buttons, breaks conversational flow).
2. **Silent default** — Claude assumes a "recommended default" and skips
   asking entirely. Documented in Anthropic's own retrospective
   ([Seeing like an agent](https://claude.com/blog/seeing-like-an-agent)).
3. **Tool unavailable** — In subagent / web-client / sandbox contexts,
   `AskUserQuestion` is not loaded; without explicit fallback, skills
   silently default.

The 4 hardenings codified below close all three.

## The Thariq canonical phrase (load-bearing)

@trq212 (Anthropic) documented this as the most reliable trigger pattern:

> Use AskUserQuestion to interview the user about [X]. Make sure questions
> are not obvious — surface the real trade-off.

Three load-bearing tokens:

- **`AskUserQuestion`** literal name (not "ask the user", not "user prompt")
- **interview** (signals multi-round, not one-shot Q&A)
- **not obvious** (triggers Anthropic's built-in question-quality filter)

## The 4 hardenings (MUST in CHK-SKL-014)

### 1. MUST verb (not "Use")

| Weak | Strong |
|---|---|
| `Use AskUserQuestion to confirm...` | `MUST call the AskUserQuestion tool to interview...` |

Or with explicit gate clause:

```markdown
This step is mandatory. Do not proceed to STEP X+1 without explicit user
selection gathered through AskUserQuestion.
```

### 2. Args-schema example (not prose Q&A template)

A fenced block in `Question: / Options:` format visually resembles
**output the model should write**, not arguments to pass into a tool.
Replace with a JSON-shape example:

````markdown
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

### 4. (Recommended) marker on first option

Per [Anthropic's official AskUserQuestion guidance](https://platform.claude.com/docs/en/agent-sdk/user-input),
mark the preferred option:

```json
{"label": "X (Recommended)", "description": "..."}
```

This anchors user choice and signals the model that taking a position is
required, rather than presenting options as flat alternatives.

## Mandatory-gate template (copy-paste into SKILL.md)

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
these dimensions: [list dimensions specific to your skill].

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
| Pre-baked "(recommended default)" prose label | Invites silent default |
| Fenced block with `Question: / Options:` format | Looks like message-text template, not tool args |
| `Is the plan ready?` / `Should I proceed?` | Anthropic system prompt routes to `ExitPlanMode` |
| No fallback contract | Subagent / web-client contexts silently default |
| Options without `(Recommended)` marker | Flat-options confusion |
| AskUserQuestion + another tool in same step | Documented Anthropic failure mode |

## Limitations

- **Main agent only** in Claude Code. Subagents have no access. Fallback contract handles this.
- **Soft cap ~4-6 questions per session**. Keep skill ≤3 questions per invocation.
- **60-second timeout**. Design with reasonable default in mind.
- **Not in public Anthropic API yet** — Claude Code only.

## When skills are exempt from CHK-SKL-014

A skill is exempt when it has **no user-input branching steps**. Examples:

- Pure deterministic skills (formatters, transformers, lint)
- Single-shot generation (one prompt → one output, no decision points)
- Skills where user input is already gathered upstream (e.g., orchestrated by another skill)
- Skills where input is free-form text rather than discrete choice

Record "no user-input steps" in the CHK-SKL-014 evidence field for exempt
skills.

## References

- [Seeing like an agent — Anthropic engineering](https://claude.com/blog/seeing-like-an-agent)
- [Handle approvals and user input — Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/user-input)
- [Thariq's canonical interview prompt (gist)](https://gist.github.com/robzolkos/40b70ed2dd045603149c6b3eed4649ad)
- [neonwatty.com — Interview skills with AskUserQuestion](https://neonwatty.com/posts/interview-skills-claude-code/)
- [GitHub: claude-code#9846 — AskUserQuestion plan-mode bug](https://github.com/anthropics/claude-code/issues/9846)
