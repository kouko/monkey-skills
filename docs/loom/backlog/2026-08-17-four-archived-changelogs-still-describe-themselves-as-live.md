---
name: 2026-08-17-four-archived-changelogs-still-describe-themselves-as-live
description: loom-design's four sibling CHANGELOG-*.md archives still open in present or future tense for plugins retired in the 6→2 merge — two of them literally say "will be documented in this file" — so a reader cannot tell they are historical records
status: open
origin: 2026-08-17 review of the CHANGELOG-pipeline.md archival-header fix — the reviewer checked the symmetry that fix claimed to restore and found it never existed; none of the four siblings carries archival framing
start: the next edit to any loom-design/CHANGELOG-*.md, OR a reader/agent misreads one as the live changelog — whichever comes first
---

- Start: the next edit to any loom-design/CHANGELOG-*.md, OR a reader/agent misreads one as the live changelog — whichever comes first

- Origin: 2026-08-17 review of the CHANGELOG-pipeline.md archival-header
  fix — the reviewer checked the symmetry that fix claimed to restore and
  found it never existed; none of the four siblings carries archival
  framing

- Measured state (2026-08-17):
  - `CHANGELOG-discovery.md:3` — "All notable changes to the
    `loom-discovery` plugin **will be** documented in this file"
  - `CHANGELOG-spec.md:3` — same future tense for `loom-spec`
  - `CHANGELOG-interface-design.md:3` and
    `CHANGELOG-product-principles.md:3` — present tense ("are
    documented"), and their `>` notes are 2026-07-02 *reconstruction*
    notes, not archival ones
  - None of the four names the 6→2 merge, says "Archived", or points at
    `CHANGELOG.md`

- Why it matters: all four plugins were retired on 2026-08-17. A file
  promising future entries for a plugin that cannot receive them is
  actively misleading — the same defect that was just fixed in
  `CHANGELOG-pipeline.md`, which is now the only one of five with
  archival framing.

- Why it was not fixed in that branch: the fix was scoped to the file
  whose rename PR #697 had landed without its content edit. Widening the
  diff to four unrelated files would violate surgical-edits, and the
  reviewer explicitly recommended filing over widening.

- Shape of the fix: give each of the four the same treatment
  `CHANGELOG-pipeline.md` now has — tense corrected to "are documented",
  an **Archived** sentence naming the merge and its date, and a pointer
  to `CHANGELOG.md`. Check per file whether any of its skills moved to a
  plugin OTHER than loom-design (the pipeline case did — `loom-memory`
  went to loom-code — and a header naming only one destination sends
  readers to the wrong plugin).

- Already done, do not redo: the INBOUND half of the pointer exists.
  `loom-design/CHANGELOG.md:9-12` already names all five archives ("The
  five plugins this one absorbed keep their own histories alongside") and
  states that their version numbers do not continue. Only the outbound
  half — each archive saying what it is — is missing.

- Open sub-question: where the archival meta-commentary belongs. Three
  live candidates, pick one and make all five match:
  (a) inline in the opening paragraph — what `CHANGELOG-pipeline.md` does
      today;
  (b) a `>` blockquote after the Format/Versioning lines — what the two
      reconstruction-noted siblings do;
  (c) state the convention ONCE at the hub (`CHANGELOG.md:9-12`, which
      already lists all five) and keep the five headers short — avoids
      repeating the same sentence five times, at the cost of a reader who
      opens an archive directly not seeing it.
