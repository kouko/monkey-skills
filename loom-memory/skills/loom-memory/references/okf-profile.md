# OKF v0.2 compatibility profile

This is the compatibility surface `loom-memory` pins from Open Knowledge
Format v0.2's generic bundle rules, implemented in full in
`${CLAUDE_PLUGIN_ROOT}/scripts/loom_memory.py` (the `scripts/loom_memory.py`
file inside this plugin's own directory). It is not a restatement of the
upstream specification — only the six clauses this profile actually
depends on, frozen at a fixed point so a later upstream edit has no effect
until a separate change adopts it:

1. Every non-reserved Markdown document in the store carries parseable
   YAML-ish frontmatter. The store is flat: a concept file lives directly
   under the store's root directory, never in a nested subdirectory — the
   validator walks the bundle recursively and reports a nested `.md` file
   as a violation naming that path, matching this repository's own
   one-fact-per-file charter for the store. Concept identity itself stays
   flat: a nested document is never treated as a concept, only ever as an
   offender.
2. Each such frontmatter has a non-empty `type`.
3. A present reserved file (`index.md` or `log.md`) follows its reserved
   structure.
4. Missing optional metadata, an unknown `type`, and unrecognized extra
   frontmatter keys never make a bundle nonconformant on their own — they
   round-trip untouched.
5. A profile may layer its own required fields on top of the generic
   rules — this is where the Loom minimum concept schema below comes
   from.
6. The bundle-root `index.md` carries exactly `okf_version: "0.2"` as its
   only frontmatter.

Calling the result an "OKF v0.2-compatible Loom memory profile" is
deliberate: it claims conformance with this pinned generic surface, never
implementation of OKF's optional trust, lifecycle, or computation
services, and never a future OKF version.

## The Loom minimum concept schema

Every concept file (every non-reserved Markdown file in the store) must
carry:

| Field | Rule |
|---|---|
| `type` | non-empty string |
| `name` | must equal the filename stem |
| `description` | a standalone durable relevance rule — readable and actionable with no other context loaded |
| `sources` | a sequence with at least one entry; every entry has a non-empty `resource` |

`sources[].resource` follows OKF v0.2 provenance structure: a string
naming where the lesson came from — an introducing commit, a URL, a prior
document. Optional or unrecognized OKF metadata on a concept file is
preserved on every read, migration, and round-trip write; it never turns
into a Loom-profile failure by itself, and Loom does not add field-
specific validation for it ahead of the change that makes some operation
here actually emit that field.

## The lesson body contract

Record and Reconcile author one durable lesson body with exactly these
sections:

- **Trigger** — the concrete situation that makes this lesson relevant.
- **Correct path** — what to do instead, stated as an action.
- **Why** — the constraint or failure mode that makes the correct path
  necessary.
- **Limits** — included only when a real non-applicability boundary
  exists; omit it rather than pad the lesson with a boundary nobody would
  hit.

This is a skill-output obligation, checked by what Record and Reconcile
actually author — not a structural invariant the validator enforces —
and migrating a legacy body does not retroactively rewrite it into this
shape.

## Why there is no `log.md`

OKF v0.2 makes both `index.md` and `log.md` optional reserved files. This
profile omits `log.md` because Git is already the authoritative update
history for every concept file: every add, edit, reconcile, and retire is
a commit, `git log` already answers "when and why did this change", and a
second hand- or agent-maintained chronological file would only duplicate
that history and eventually drift from it. Omitting `log.md` stays fully
conformant — OKF v0.2 never requires it.
