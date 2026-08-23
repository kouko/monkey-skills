# Requirement identifiers — the `REQ-<n>` convention

> Companion to [`../SKILL.md`](../SKILL.md). This is the single-source-of-truth
> convention for a requirement's identifier — the `REQ-<n>` twin of
> the brief-item identifier contract exposed by `loom-code:brainstorming`.
> Every parser and every skill passage that talks about a
> requirement id points here rather than restating the rule.

A requirement gets its identity where it is born — a change-folder's
`specs/<capability>/spec.md` — and that same id is what every downstream
consumer (a plan's `Brief item covered`, a `# @req:` tag, the coverage
checker's join key, the living-spec CI namespace) reads back, unchanged, for
the life of the requirement.

## Form

A requirement header carries its id, if any, first: `### Requirement:
REQ-<n> — <name>` — id-first. The header shape is `REQ-<n> — <name>`;
the id itself is `REQ-<n>` (the literal prefix `REQ`, a hyphen, a
decimal number). The header carries the id followed by one space, an
em dash U+2014, one space, then the human-readable name. The optional
status suffix (`[active]` / `[deferred]`) stays after the name, unchanged by
this convention: `### Requirement: REQ-<n> — <name> [deferred]`.

`REQ1`, `req-1`, and `R-1` are not this form — no hyphen, wrong case, and a
non-`REQ` prefix respectively. A header carrying one of these near-misses
is flagged, not silently accepted as an id.

## Authored, never derived

The spec author types the number. It is never slugified, hashed, or
otherwise generated from the requirement's name — deriving it would desync
the id from its requirement the moment the name is reworded, exactly as
`BI-<n>`'s authored-not-derived rule exists to prevent for brief items.

## Monotonic, never renumbered, never reused

A new requirement takes the next unused number — the highest `REQ-<n>` ever
used across the whole repo (live change-folders + archive + the living-spec
root), plus one — regardless of where in the file the requirement sits. A
requirement already carrying an id keeps it and is never renumbered;
inserting a requirement above `REQ-3` does not renumber `REQ-3`. When a
requirement is deleted, its number is retired and never reused: no later
requirement may carry it.

**Minting**: run `--next-req-id`, exposed by loom-code's living-spec
structural gate when that plugin is installed, or grep the three namespace roots yourself — live
change-folders, the archive, and the living-spec root (see §Monotonic
above) — for the highest `REQ-<n>` in use and take the next number. Never
guess a number that looks free without checking all three roots — a
collision across parallel change-folders is exactly what the
merge-boundary checker exists to reject.

`--next-req-id` computes "highest number among headers PRESENT, plus one",
not "highest number ever minted, plus one" — it has no memory of a
declaration once it is deleted, so the two coincide only for as long as no
requirement is ever deleted; if one is, its retired number stops being
excluded from re-minting and the author must keep tracking retirement by
hand.

**Split and merge retires both sides.** When one requirement is split into
two, the original number is retired and both halves take new numbers —
neither half inherits it. When two requirements are merged into one, both
numbers are retired and the merged requirement takes a new number. This is
what keeps a downstream citation (a plan task, an `@req` tag) from silently
re-pointing at a requirement whose scope has since narrowed or widened; the
stale citation fails loudly against a retired number instead.

## Scope

Change-folder `specs/*/spec.md` and living-spec `spec.md` share the grammar
— one grammar, implemented by each parser. The only difference: a living-spec
header may omit the ` — <name>` half and carry the bare `### Requirement:
REQ-<n>` form, since a living-spec requirement's name lives in its own
prose body rather than the header line. A change-folder header may not omit
the name half — an id with no name in a change-folder is a near-miss, not a
valid id-form header.

## Adoption is all-or-nothing per spec file

Adoption is all-or-nothing per spec file: declaring even one `REQ-<n>` id in
a spec file switches that FILE into id-mode, and from that point every
`### Requirement:` header in the same file must carry an id — a bare-prose
header in an id-mode file is an error, not a tolerated mix. A file with zero ids stays in legacy mode — every current
behavior (prose-keyed coverage, no CI namespace membership) continues
unchanged, indefinitely. Legacy mode is not deprecated: migrating an
existing legacy file to id-mode is a separate, deliberate one-pass task, not
something this convention requires or nudges toward.

## Language

The id and the name are machine-executed precision content — a plan cites
the id verbatim, a test's `@req` tag cites it verbatim, a checker parses it
byte-for-byte — so both are written in English, regardless of the
conversation language the surrounding spec prose uses.

## Parsers

These three parsers are the id's actual consumers. Read the file at its
path for the current regex — this document names the parser, never restates
its pattern (a restated regex is a second copy that can drift from the
real one):

- **Validator** — `validate_spec_output.py` in loom-design's public spec
  validation command surface.
- **Coverage checker** — `check_scenario_coverage.py` in loom-code's public
  plan-verification command surface.
- **Living-spec index** — `living_spec_index.py`, with namespace membership
  enforced by loom-code's public `check-living-spec-index.py` structural gate.

## Anti-patterns

- ❌ **Skipping an id in an id-mode file.** Once one requirement in a file
  carries `REQ-<n>`, every requirement in that file must. A bare-prose
  header left behind in an otherwise id-mode file is not "still legacy" —
  it is an error.
- ❌ **Renumbering on insert.** Inserting a requirement above `REQ-3` and
  shifting existing requirements down makes every already-written citation
  (a plan task, an `@req` tag) point at the wrong requirement, silently.
  The new requirement takes the next unused number wherever it sits.
- ❌ **Reusing a retired number.** A deleted requirement's number stays
  dead. Handing `REQ-3` to a new requirement makes an old citation resolve
  — to something the citing plan or test never meant.
- ❌ **Deriving the id from the name.** A slug or hash of the requirement's
  name (`REQ-narrative-freshness`, `REQ-a1b2c3`) desyncs the moment the name
  is reworded. The author types the number.
- ❌ **Minting an id from inside an implementer.** An implementer working a
  plan task resolves an existing `REQ-<n>` id; it never mints a new one. A
  new id is authored by whoever writes the spec header, not by whoever later
  writes the code that satisfies it.

## See also

- `loom-code:brainstorming` — exposes the `BI-<n>` convention this document
  mirrors; this conceptual reference does not require its plugin files to be
  present.
- [`../SKILL.md`](../SKILL.md) — the requirement header skeleton this
  convention governs.
