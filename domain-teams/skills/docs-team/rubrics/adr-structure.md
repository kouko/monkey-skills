# ADR Structure Gate

## Scope Boundary

Review the **structural compliance** of an Architecture Decision Record
against the Nygard template (with optional MADR extensions). Do NOT review
the quality of the decision itself, only whether the ADR is correctly
structured, dated, and formatted.

**Protocol reference**: `protocols/write-adr.md`

## Flag Definitions

### Section Completeness

- 🔴 **Fatal**: Any Nygard core section is missing: Title, Status, Context,
  Decision, or Consequences. The ADR is structurally incomplete.
- 🟡 **Warning**: MADR extension sections are missing where they would add value
  (e.g., no "Alternatives considered" on an ADR that obviously involved choice).
- 🟢 **Clear**: All Nygard core sections present; MADR extensions used where relevant.

### Status Validity

- 🔴 **Fatal**: Status is missing or uses a non-standard value (not one of:
  Proposed, Accepted, Deprecated, `Superseded by ADR-NNNN`).
- 🟡 **Warning**: Status is valid but ambiguous — e.g., `Accepted` on an ADR
  dated 3 years ago with no review since, or `Deprecated` with no pointer to
  the replacement.
- 🟢 **Clear**: Status is valid and unambiguous.

### Decision Actionability

- 🔴 **Fatal**: The Decision section is vague or passive — e.g., "We should
  consider using PostgreSQL" instead of "We will use PostgreSQL." A future
  reader cannot determine what the team committed to.
- 🟡 **Warning**: Decision is active voice but lacks specificity about scope
  or implementation boundary.
- 🟢 **Clear**: Decision uses "We will..." or equivalent imperative voice with
  sufficient specificity for implementation.

### Consequences Balance

- 🔴 **Fatal**: The Consequences section lists only positive outcomes. Nygard
  explicitly requires **all** consequences, including negative ones. A one-
  sided Consequences section hides costs from future readers.
- 🟡 **Warning**: Consequences lists both sides but the negative consequences
  are perfunctory or obviously underweighted.
- 🟢 **Clear**: Consequences lists both positive and negative outcomes with
  honest assessment.

### File and Naming

- 🔴 **Fatal**: File is not located at `docs/adr/` or the filename does not
  follow `NNNN-title.md` format with 4-digit zero-padded sequential numbering.
- 🟡 **Warning**: File location is correct but the title slug is poorly chosen
  (e.g., `0042-database-stuff.md` instead of `0042-use-postgresql-for-event-store.md`).
- 🟢 **Clear**: File at `docs/adr/NNNN-title.md` with descriptive kebab-case title.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- **Do not grade the decision itself.** If the team decides to use PostgreSQL,
  this gate does not evaluate whether PostgreSQL was a good choice. It only
  checks that the ADR captures the decision in the correct format.
- **Immutability is a protocol concern, not a gate concern.** This gate does
  not check whether an Accepted ADR has been edited. That is enforced by the
  `write-adr.md` protocol's rules.
- **Supersession pointer required on Deprecated/Superseded status.** If Status
  is Deprecated or Superseded, the `Superseded by ADR-NNNN` pointer must be
  explicit.

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Quote the specific section or metadata that triggered the flag
3. **Fix instruction**: Specific correction needed
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

## Source

- [Michael Nygard — Documenting Architecture Decisions (2011)](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — template definition
- [MADR](https://adr.github.io/madr/) — Markdown extensions and directory convention
