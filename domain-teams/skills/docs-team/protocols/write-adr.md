# Write ADR Protocol (Architecture Decision Record)

Write an Architecture Decision Record following the Nygard template
(with optional MADR extensions). ADRs are short, immutable records of
significant architectural decisions, capturing context, decision, and
consequences at the time the decision was made.

**Primary sources**:
- [Michael Nygard — Documenting Architecture Decisions (2011)](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [MADR — Markdown Architecture Decision Records](https://adr.github.io/madr/)

## When to Write an ADR

Write an ADR when:

- A decision affects the architecture (module boundaries, data flow, dependencies)
- The decision has non-obvious trade-offs that future readers will need to understand
- The decision constrains future work (e.g., "we can't use X because this decision chose Y")
- The decision is hard to reverse

Do **not** write an ADR for:

- Code style preferences (use `standards/style-conventions.md` instead)
- Implementation details that don't affect architecture
- Decisions that are easily reversible and low-impact

## ADR vs Explanation

ADRs are adjacent to the Explanation quadrant but differ in three ways:

| ADR | Explanation |
|-----|-------------|
| **Immutable once accepted** | Revisable as understanding evolves |
| **Fixed template** (Nygard/MADR) | Flexible structure |
| **Has a lifecycle** (proposed → accepted → superseded) | No status |
| **Single decision per file** | May cover broader topics |

When a decision is rejected or later reversed, write a **new ADR** that
supersedes the old one. Do not edit the old ADR.

## Phase 0: Context Discovery

1. **Verify the decision is architectural** — does it affect module boundaries,
   data flow, dependencies, or future flexibility? If not, consider if an
   Explanation doc or comment is more appropriate.
2. **Check for prior ADRs** — is there an existing ADR on this topic? If so,
   the new ADR might supersede it rather than be independent.
3. **Find the next ADR number** — ADRs are sequentially numbered starting from
   `0001`. Look at `docs/adr/` for the highest existing number.
4. **Identify deciders** — who is involved in the decision? Name them in the
   ADR metadata (MADR extension).

## Phase 1: Fill the Nygard Template

The canonical Nygard template has five sections:

### Title

Short noun phrase describing the decision. Format: `ADR-NNNN: <decision>`.

Good: `ADR-0042: Use PostgreSQL for event store`
Bad: `ADR-0042: Database stuff`

### Status

One of:
- **Proposed** — under discussion, not yet accepted
- **Accepted** — decision made, in effect
- **Deprecated** — no longer the recommended approach, but not yet replaced
- **Superseded by ADR-NNNN** — replaced by a newer decision

Once an ADR is Accepted, its Status and Body are immutable except for the
Status field (which can transition to Deprecated or Superseded).

### Context

State the forces at play in neutral, fact-based language. Forces include:
technological constraints, team constraints, business constraints, time
pressure, regulatory requirements.

**Do not advocate for the decision in the Context.** Context describes the
situation; Decision describes the response. Mixing them makes the ADR feel
biased.

### Decision

State the response in full sentences, active voice, imperative tone:
**"We will..."** or **"We choose..."**. A reader should be able to implement
the decision from this section alone.

### Consequences

List **all** resulting consequences — positive and negative (and optionally
neutral). Do not hide the costs. Future readers need to see both sides.

## Phase 2: MADR Extensions (Optional)

If the decision has significant alternatives considered, add MADR extension
fields between Context and Decision:

- **Date** — ISO 8601 date the decision was made
- **Deciders** — named individuals or roles involved
- **Alternatives considered** — for each rejected alternative: Name, Pros,
  Cons, Why rejected. This makes reasoning visible to future readers who
  might otherwise reopen settled questions.

## Phase 3: File and Storage

ADRs live at `docs/adr/NNNN-title.md`:

- **Sequential numbering** starting at `0001`
- **Never reuse or renumber** — a superseded ADR keeps its number
- **Kebab-case title** — `0042-use-postgresql-for-event-store.md`
- **Zero-padded to 4 digits** — `0042`, not `42` (for sort order)

## Rules

- **Immutable once Accepted.** Do not edit the Context, Decision, or
  Consequences after acceptance. Only Status can change.
- **Supersede, don't revise.** When a decision changes, write a new ADR
  with `Supersedes: ADR-NNNN` and update the old ADR's Status to
  `Superseded by ADR-MMMM`.
- **One decision per ADR.** If multiple decisions are being made together,
  write multiple ADRs.
- **Short.** Nygard's original guidance: 1-2 pages. Long ADRs are harder
  to read and often indicate multiple decisions bundled together.
- **Active voice, "We will..."** The Decision section sets the policy.
- **Balanced Consequences.** Always list both positive and negative.

## Output Structure

```markdown
# ADR-NNNN: {Decision title}

## Status

{Proposed | Accepted | Deprecated | Superseded by ADR-MMMM}

## Date

{YYYY-MM-DD}

## Deciders

{Names or roles}

## Context

{Neutral description of forces at play}

## Alternatives considered (MADR extension)

### {Alternative 1}
- **Pros**: ...
- **Cons**: ...
- **Rejected because**: ...

## Decision

We will... / We choose...

## Consequences

**Positive**
- ...

**Negative**
- ...

**Neutral**
- ...
```

## Structure Check

This ADR passes the ADR Structure MUST gate if:

- Title is `ADR-NNNN: <decision>` format with 4-digit number
- Status is one of the valid values
- Context is neutral (no advocacy)
- Decision is imperative ("We will...")
- Consequences lists both positive and negative
- The file is at `docs/adr/NNNN-title.md`

## Sources

- [Michael Nygard — Documenting Architecture Decisions (2011)](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — original template
- [MADR — Markdown Architecture Decision Records](https://adr.github.io/madr/) — Markdown extensions
- [adr.github.io](https://adr.github.io/) — central ADR resource hub
- [Martin Fowler — Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html) — adoption commentary
