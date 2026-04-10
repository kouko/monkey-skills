# Diátaxis Mode Clarity Gate

## Scope Boundary

Review the **Diátaxis mode clarity** of a document: whether it sits cleanly
in exactly one of the four quadrants (Tutorial, How-to, Reference, Explanation)
or, for composite documents like READMEs, whether each labeled section sits
cleanly in its declared mode.

Do NOT review: correctness, completeness, style, or freshness — those belong
to other gates.

**Vocabulary reference**: `standards/diataxis-taxonomy.md`

## When This Gate Runs

| Artifact | Gate behavior |
|----------|---------------|
| Tutorial / How-to / Reference / Explanation | Runs on the whole document |
| README | Runs **per section** — each section's declared mode is checked separately |
| ADR | **Skip** — ADRs have their own Structure gate; they are Explanation-adjacent but follow a fixed template |
| Codebase Assessment report | **Skip** — not a single-quadrant prose document |
| Freshness audit report | **Skip** — metadata output, not prose |

If the artifact is in the skip list, return `PASS` with evidence "Skipped per Mode Clarity gate scope rules."

## Flag Definitions

### Mode Declaration

- 🔴 **Fatal**: The document (or README section) has no mode declared. Frontmatter
  has no `mode:` field and the prose does not make the intended mode obvious.
- 🟡 **Warning**: The mode is declared in frontmatter but the prose style
  contradicts it (e.g., `mode: reference` but the content is narrative).
- 🟢 **Clear**: Mode is declared (frontmatter or section label) and the prose
  matches.

### Mode Consistency

- 🔴 **Fatal**: The document contains substantial content from more than one
  mode. Example: a tutorial with a 20-line reference table embedded, or a
  how-to with a 3-paragraph design rationale section.
- 🟡 **Warning**: Minor mode bleeding — one or two sentences of the wrong
  mode (e.g., a brief "why" aside in a how-to).
- 🟢 **Clear**: Content stays in one mode throughout (or one mode per
  labeled section for README).

### Anti-Pattern Absence

Check against the anti-patterns listed in `standards/diataxis-taxonomy.md`:

- 🔴 **Fatal**: Matches one of the primary Diátaxis anti-patterns
  (Tutorial that teaches concepts, How-to that explains why at length,
  Reference with narrative, Explanation with step-by-step commands,
  README that is one undifferentiated blob).
- 🟡 **Warning**: Borderline — some anti-pattern tendency but within
  tolerable limits.
- 🟢 **Clear**: No anti-patterns detected.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- **Be strict about mode consistency, not mode choice.** Any of the 4 quadrants
  is acceptable if the content stays in it. Do not penalize the author for
  choosing Reference over Tutorial if the content works as Reference.
- **For README, evaluate per section.** Each section declares its expected mode
  (per `protocols/write-readme.md`). Score each section separately and report
  the worst per-section result.
- **Minor bleeding is tolerable.** A how-to guide that says "this works because
  of caching" in one sentence is not broken. A how-to guide with a 3-paragraph
  caching explanation is broken.
- **When issuing NEEDS_REVISION, include a specific fix.** Name the anti-pattern
  and suggest which mode the leaked content should move to.

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Quote the specific line or section that triggered the flag
3. **Fix instruction**: For warning flags, suggest the minimal change. For
   fatal flags, indicate which mode the content should move to (and into what
   file).
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to move and where.

## Sources

- `standards/diataxis-taxonomy.md` — the authoritative Diátaxis taxonomy and anti-patterns
- [diataxis.fr](https://diataxis.fr/) — Daniele Procida's original framework
