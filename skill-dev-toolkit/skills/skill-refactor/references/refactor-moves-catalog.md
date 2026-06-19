# Refactor Moves Catalog

Catalog of refactor-hat-safe moves for `skill-refactor`. Each move
is a behavior-preserving transformation that should pass the
equivalence check. Inspired by Fowler's *Refactoring* catalog
applied to SKILL.md prose / structure.

## Move classification

| Tier | Risk | When safe |
|---|---|---|
| **Low** | Behavior preservation almost certain | Most moves |
| **Medium** | Test rigorously; behavior change possible if move misapplied | Cross-section moves |
| **High** | Don't do these without explicit user opt-in | Cosmetic or load-bearing edits |

## Low-risk moves

### Dedupe Prose

Same statement appears in multiple places → consolidate to one
canonical location, reference from others.

**Example**:
- Before: "Read SKILL.md before editing" appears in §1 and §3
- After: stated once in §1, §3 says "(see §1)"

**Equivalence risk**: low if the cross-reference is clear.

### Tighten Phrasing

Verbose constructions → terser equivalents without information
loss.

**Examples**:
- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "make sure that you" → (just imperative)

**Equivalence risk**: low. These phrasings are well-known
boilerplate.

### Inline Single-Use Definition

A term defined inline once, used once → just inline the meaning.

**Example**:
- Before: "An invariant (a property that must hold across all
  rounds) is..."
- After: "A property that must hold across all rounds is..."

**Equivalence risk**: low.

### Compress Repeated Lists into Tables

Three bullet lists with identical structure → one table.

**Example**: see Verdict / Tier section in `SKILL.md` — three
bullet patterns compressed to a table reduces ~20% volume.

**Equivalence risk**: low; same content reorganized.

### Remove Redundant ALWAYS / NEVER Caps

When prose can carry the meaning, the caps add token cost without
behavioral signal. Per `skill-creator-advance/SKILL.md` writing
style note: "if you find yourself writing ALWAYS or NEVER in all
caps, that's a yellow flag — reframe and explain the reasoning".

**Equivalence risk**: low–medium. Test carefully on edge cases.
Caps sometimes carry "this is a hard rule" semantic that prose
loses.

## Medium-risk moves

### Extract to references/

Move a self-contained section (e.g. a worked example, a detailed
protocol) from SKILL.md body to a `references/` file. SKILL.md body
gets a one-line pointer.

**Constraint**: the reference must be loaded on demand by the
skill's flow (mentioned in the right place); otherwise behavior
breaks because Claude won't see the content when relevant.

**Equivalence risk**: medium. Test the use case that the extracted
section served — is it still triggered correctly?

**Example**: extracting "Description Optimization" section (~700
words) to `references/description-optimization.md`, with a pointer
"see references/description-optimization.md when user asks to
optimize description triggering".

### Move Worked Examples to Companion File

When a protocol has 3+ worked examples, extract per the structural convention gates'
companion-file convention to `{protocol-name}-examples.md`.

**Constraint**: keep 1-2 examples inline as quick-mode pattern
anchor (per domain-team structural convention).

**Equivalence risk**: medium. Quick-mode runs may behave
differently if companion file doesn't load. Test both modes.

### Reorder Sections (No Content Change)

Move a section earlier/later in the file. Useful when current
order causes Claude to miss a section because of where it falls in
the prompt.

**Equivalence risk**: medium. Order matters for some Claude
behaviors; test if the section's effect changes.

## High-risk moves (require explicit user opt-in)

### Remove Section Considered Redundant

If a section appears redundant with another, remove it.

**Risk**: redundancy might be deliberate emphasis. The first
mention plants the concept; the repeat reinforces. Removal can
cause Claude to miss the rule.

**Mitigation**: don't auto-remove. Surface to user as "section X
seems redundant with section Y; OK to remove?" before doing it.

### Compress Numbered List to Prose

A 5-item numbered list → a single paragraph.

**Risk**: numbered lists give Claude clear "follow these in order"
semantic. Prose loses ordering hints.

**Mitigation**: only do this if the items are not order-sensitive,
and verify in test prompts.

### Replace Specific with Abstract

Specific instructions ("write X to file Y at line Z") → abstract
("save the result").

**Risk**: removes load-bearing specificity. Often a behavior
change disguised as refactor.

**Mitigation**: avoid this entirely in refactor scope. If
specificity is the problem, that's a redesign — go to
skill-creator-advance.

## Out-of-scope moves (do NOT do in refactor)

These are not refactors. If proposed, route elsewhere:

| Proposed move | Why out of scope | Where it should go |
|---|---|---|
| Add a new phase | New behavior | `skill-creator-advance` |
| Remove a fallback / edge case handler | Behavior change | `skill-creator-advance` (with explicit user decision) |
| Change input/output format | Contract change | `skill-creator-advance` |
| Reword for "clarity" with judgment call | Taste, not refactor | `skill-tuning` |
| Remove "deprecated" instruction | Behavior change | `skill-creator-advance` |
| Add example / pattern | Additive | `skill-creator-advance` (or just direct edit if trivial) |
| Strengthen / weaken a constraint | Behavior change | `skill-creator-advance` |

## Move stacking

A single refactor round should ideally apply **one move at a
time**. This keeps Q1's diagnosis clean: if equivalence fails, you
know which move broke it.

When the user wants several moves in sequence, each move is its
own round. Q1/Q2/Q3 run independently for each.

## Ratchet implications

If a move reduces tokens but its equivalence check is moderate
confidence (Layer 1 + 2/3 ensemble), it can still PROCEED — but
this becomes the new baseline for subsequent rounds. Stacking
moderate-confidence rounds builds compound risk.

After 3 consecutive moderate-confidence PROCEEDs, automatically
flag for human review of the cumulative diff regardless of
individual round verdicts. The aggregate behavior may have drifted
even if each round individually passed.

## Summary table

| Move | Tier | Auto / User-confirm |
|---|---|---|
| Dedupe prose | Low | Auto |
| Tighten phrasing | Low | Auto |
| Inline single-use definition | Low | Auto |
| Compress lists to tables | Low | Auto |
| Remove redundant caps | Low | Auto |
| Extract to references/ | Medium | Auto with extra Q1 scrutiny |
| Move examples to companion | Medium | Auto with extra Q1 scrutiny |
| Reorder sections | Medium | User-confirm before |
| Remove redundant section | High | User-confirm explicitly |
| Compress list to prose | High | User-confirm explicitly |
| Replace specific with abstract | Out-of-scope | Don't |
| Add new content | Out-of-scope | Don't |
| Remove fallback / handler | Out-of-scope | Don't |
| Change format / contract | Out-of-scope | Don't |
