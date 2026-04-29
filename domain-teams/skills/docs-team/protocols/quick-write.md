# Quick-Write Protocol (Cost-Saving Mode)

Cost-optimized documentation writing executed **directly in the main
agent** without worker / evaluator dispatch. Trades full gate enforcement
for ~4× lower token cost.

**Vocabulary reference**: `standards/diataxis-taxonomy.md`
**Style reference**: `standards/style-conventions.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md`

## When to Use

Quick mode applies when **all** of the following are true:

- The artifact is **low-stakes** (personal note, draft, internal scratch, iteration on existing doc)
- The user has not asked for **gate verdicts**
- The artifact is **NOT** in the hard-block list below

## Hard Block List (Always Use Full Mode)

These artifact types require full-mode gate enforcement and MUST NOT use
quick mode regardless of triggers:

| Artifact | Reason |
|----------|--------|
| **ADR** (Architecture Decision Record) | Decisions are immutable once accepted; structure errors are unrecoverable |
| **API Reference** | Reader contract requires mechanical consistency across all entries |
| **Public-facing release README** | First-impression artifact; gate verdict is the audit trail |
| **Architecture documentation** | Component spec / data flow drift causes downstream confusion |
| User explicitly says "production", "for clients", "team review", "release" | Stated stakes |

If the request matches the hard-block list, refuse quick mode and explain
why; route to the full workflow instead.

## Trigger Signals

Quick mode is appropriate when **any** of these signals are present:

- User says: "quick", "draft", "rough", "簡單", "草稿", "ざっくり", "ラフ"
- Target file path is in a personal vault / scratch directory
- Iteration on an existing doc the user is actively editing (small touch-up)
- User explicitly requests: `--quick`, `quick mode`, `cost-saving`

## Execution Model

Unlike full mode, quick-write runs entirely in the main agent's context.
**Do NOT launch worker or evaluator subagents.**

### Phase 0: Pre-Writing Checklist (mandatory)

Read `standards/pre-writing-checklist.md` and apply every item. Quick mode
skips gates, so this defensive step is the only safeguard against the
default-assumption failures (wrong package manager, invented license,
mismatched file naming, etc.).

### Phase 1: Read the Selected Protocol

Identify the Diátaxis quadrant from the request and read **only one** of:

- `protocols/write-tutorial.md`
- `protocols/write-how-to.md`
- `protocols/write-reference.md`
- `protocols/write-explanation.md`
- `protocols/write-readme.md`

Do NOT read multiple protocols. If the request is ambiguous, ask the user
to clarify the mode rather than reading all of them.

#### No Companion Load Rule

Some protocols have a companion `*-examples.md` file in `protocols/`
(currently: `write-readme-examples.md`, `write-architecture-examples.md`).
**Quick mode MUST NOT load these companion files.** They exist
specifically to defer worked examples out of quick mode's token budget;
loading them defeats the cost-saving purpose.

If you need the breadth of examples, that signals the task is not
actually quick mode — fall back to full mode and let the worker load
the companion via `additional:`.

The current rule is: **no file path matching `protocols/*-examples.md`
may be Read in any quick-mode phase.**

### Phase 2: Read Minimal Standards

Read **exactly two** standards:

- `standards/diataxis-taxonomy.md` — mode characteristics
- `standards/style-conventions.md` — prose rules

Skip the other standards (`docs-as-code.md`, `freshness-metadata.md`,
`api-reference-structure.md`) unless the protocol explicitly requires them.

### Phase 3: Write the Artifact

Apply the protocol's phases directly. Stay in the chosen Diátaxis quadrant.
Apply style conventions inline.

### Phase 4: SELF Check (mandatory)

Before delivering, run the self-audit defined in `SKILL.md` §SELF Check
against the protocol's `## Mode Clarity Check` (or equivalent) section:

1. Re-read the user's original request
2. List 3-5 things that would make this output unacceptable
3. Check each one against your output
4. Fix any issues found before delivering

The protocol's terminal "Mode Clarity Check" / "Completeness Check" /
"Structure Check" section is your acceptance criteria. Treat each bullet
as a checklist item.

### Phase 5: Deliver With Disclosure

Append a single-line disclosure to the user (NOT to the artifact body):

```
⚠️ Quick mode: gates skipped. Run /docs verify if you want full gate review.
```

This makes the trade-off visible and gives the user a one-step upgrade path.

## Upgrade Path (`/docs verify`)

When the user wants full gate review on a quick-mode artifact:

1. Treat the existing artifact as the input (do NOT rewrite)
2. Skip Phase 1-4 of the relevant `write-*` protocol
3. Launch evaluators for the gates that would normally trigger:
   - MUST: Mode Clarity / README Completeness / ADR Structure (per artifact type)
   - SHOULD: Style Convention / Freshness (if metadata present)
4. Apply standard verdict handling: PASS / PASS_WITH_NOTES (auto-revise) / NEEDS_REVISION (escalate)

The verify path costs roughly 25K tokens (evaluator only — no worker
re-write), versus 46K for full mode from scratch. This makes the total
quick + verify cost (~36K) **still cheaper** than starting in full mode,
while letting the user defer the verification decision until they know
they need it.

## Rules

- **No worker dispatch.** Quick mode runs in main agent context. Launching
  a worker defeats the cost-saving purpose.
- **No evaluator dispatch.** SELF check is the only quality gate.
- **Hard-block list is non-negotiable.** Even if the user explicitly
  requests quick mode for an ADR, refuse and explain.
- **Pre-writing checklist is mandatory.** It is the only defense against
  default-assumption failures when gates are skipped.
- **Always disclose.** The disclosure line is required so the user knows
  the artifact is not gate-verified.

## Anti-Patterns

1. **Silent quick mode** — using quick mode without disclosing it. The
   disclosure is what preserves user trust.
2. **Quick mode for ADR** — the hard-block exists for a reason. ADRs are
   immutable; getting the structure wrong is unrecoverable.
3. **Skipping pre-writing checklist** — without gates, the only safeguard
   left is defensive reading. Skipping both is reckless.
4. **Reading every protocol "to be safe"** — quick mode loads exactly one
   protocol. Reading more is cost-saving theater.
5. **Auto-promoting quick to full** — quick is opt-in for cost. Don't
   silently upgrade unless the user asks.

## Cost Profile (estimate)

| Phase | Token cost (input + output) |
|-------|----------------------------:|
| SKILL.md (already loaded) | ~3,750 |
| 1 protocol | ~1,200-1,500 |
| 2 standards (diataxis + style) | ~3,400 |
| Artifact output | ~2,000-3,000 |
| **Total per task** | **~10,500-11,500** |

Compare to full mode (~46,000 tokens per task) — quick mode is approximately
4× cheaper at the cost of skipping multi-gate enforcement.

## Sources

- `standards/diataxis-taxonomy.md` — mode vocabulary
- `standards/style-conventions.md` — prose rules
- `standards/pre-writing-checklist.md` — defensive pre-writing reading
- `protocols/write-{tutorial,how-to,reference,explanation,readme}.md` — quadrant protocols (one selected per task)
