# Doc Writing Router Protocol

Entry point for all docs-team writing workflows. Determines which specific
write-* protocol applies, based on the user request and the target artifact
type. Routes to exactly one downstream protocol.

**Vocabulary reference**: `standards/diataxis-taxonomy.md` (4 Diátaxis quadrants)

## When to Use

- Any user request to write documentation where the target mode is not yet clear
- Any request that mentions multiple doc types (the router clarifies and splits)
- As the first phase of every writing workflow (tutorial, how-to, reference, explanation, README, ADR, API reference)

## When NOT to Use

- User explicitly requests a specific mode ("write a tutorial") — skip the
  router and invoke the mode-specific protocol directly
- Codebase assessment workflows — use `codebase-assessment.md` instead

## Phase 0: Mode Selection (Full vs Quick)

Before classifying the request, decide whether full or quick mode applies.

### Quick mode triggers

Use quick mode if **any** of:

- User says: "quick", "draft", "rough", "簡單", "草稿", "ざっくり", "ラフ"
- User explicitly requests: `--quick`, `quick mode`, `cost-saving`
- Target file is in a personal vault / scratch directory
- Iteration on an existing doc the user is actively editing (small touch-up)

### Quick mode hard block

Refuse quick mode (use full mode and explain) if **any** of:

| Artifact / Signal | Reason |
|-------------------|--------|
| Target is an **ADR** | Decisions are immutable; structure errors are unrecoverable |
| Target is an **API reference** | Reader contract requires mechanical consistency |
| Target is a **public-facing release README** or **architecture document** | First-impression / contract artifacts need gate audit trail |
| User states: "production", "for clients", "team review", "release" | Stated stakes |

### Routing decision

- Quick mode triggers + not blocked → hand off to `protocols/quick-write.md`
- Otherwise → continue to Phase 1 below for full-mode classification

## Phase 1: Classify the Request

Read the user request and ask: **what does the reader need?**

| Reader need | Target | Protocol |
|-------------|--------|----------|
| "Teach me how to use this from scratch" | Tutorial | `write-tutorial.md` |
| "I have this specific problem, solve it" | How-to Guide | `write-how-to.md` |
| "Tell me the facts about this API/CLI/config" | Reference | `write-reference.md` |
| "Help me understand why this exists / how it works" | Explanation | `write-explanation.md` |
| "I need a README for this project" | Composite | `write-readme.md` |
| "We need to record this architectural decision" | ADR | `write-adr.md` |
| "Document this API" | Reference sub-case | `write-reference.md` + `api-reference-structure.md` |

If the request genuinely needs multiple modes (e.g., "write tutorial and reference
for feature X"), **split into separate invocations** — one per mode. Do not try
to produce a mixed document.

## Phase 2: Identify the Reader

Before handoff, answer three questions:

1. **Who is the reader?** (beginner / competent user / expert / all of these)
2. **What do they already know?** (their skill level, prior exposure)
3. **What state do they need to be in after reading?** (able to do X, knowing that Y)

These answers feed into the downstream protocol's Phase 0 (Context Discovery).

## Phase 3: Handoff

Invoke the selected downstream protocol with a context summary:

```
### Selected Mode
{tutorial | how-to | reference | explanation | composite-readme | adr | api-reference}

### Execution Mode
{full | quick}  # from Phase 0

### Reader Profile
- Audience: {beginner | competent | expert}
- Prior knowledge: {what they already know}
- Target state: {what they need to do/know after reading}

### Request Context
{The user's original request, verbatim}

### Known Constraints
{Any constraints from the user — length, format, tone, deadline}
```

## Rules

- **Exactly one mode per handoff.** If the request genuinely needs multiple
  modes, return to the user to clarify which one is the priority, or split
  into multiple workflows.
- **No content writing in the router.** This protocol selects; it does not
  write. Content writing happens in the downstream protocol.
- **Default to Explanation if unclear** — most ambiguous requests are about
  understanding, and Explanation is the easiest mode to re-classify later.
- **Cite the reasoning.** When handing off, include a one-sentence rationale
  for why this mode was selected.

## Anti-Patterns

1. **Mixed handoffs** — sending "write a tutorial that also covers the API
   reference" to a downstream protocol. Split the request.
2. **Inventing a new mode** — Diátaxis has 4 quadrants plus a handful of
   composite special cases (README, ADR). Do not create a 5th quadrant.
3. **Skipping reader profiling** — the downstream protocol needs to know who
   the reader is. Router failures often come from missing this step.
