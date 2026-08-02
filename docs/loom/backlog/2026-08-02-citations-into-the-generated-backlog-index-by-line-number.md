---
name: 2026-08-02-citations-into-the-generated-backlog-index-by-line-number
description: documents still cite docs/loom/BACKLOG.md by line number or heading anchor, both of which are invalidated by the generated file — six by line number (resolve silently wrong), eleven more by a §-heading the generated index has no headings for
status: OPEN
origin: whole-branch review of the docs-backlog-one-entry-per-file arc, 2026-08-02 — the arc repointed every citation whose anchor had already gone out of range, and left these, which resolve today
start: whenever a batch of entries is added or archived, since that is what shifts the line numbers and turns these from correct into silently wrong
---

Before the one-entry-per-file split, `docs/loom/BACKLOG.md` was a
hand-maintained 2,545-line document, and citing it by line range was
reasonable. It is now **generated output** — a small fraction of that
size, rebuilt from the entry files on every `--write`. Adding one
entry or archiving one shifts every line below it (do not cite this
entry's own line count either: the same class of decay applies to any
number stated about a container this entry itself lives inside — see
`docs/loom/memory/a-passage-that-describes-itself-decays-on-every-edit.md`).

The arc's reference sweep repointed the citations whose anchors had
already gone out of range. These six still cite a line number that
resolves **today**, which is precisely why the sweep did not catch
them — and why they will go wrong silently rather than loudly:

```
docs/loom/plans/2026-07-06-loom-memory-store.md
docs/loom/plans/2026-07-07-loom-user-communication-overhaul-tasks.md
docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
docs/loom/specs/2026-07-06-loom-memory-store.md
docs/loom/specs/2026-07-11-principles-replay-l3-loop.md
docs/loom/specs/2026-07-19-jnj-restatement-axis-signature.md
```

(`loom-code/scripts/check_doc_citations.py` also matches the grep, but
its hit is a docstring example of the citation syntax, not a citation.)

**The recipe below returns more hits than that list — the extras are
deliberate, not missed.** Running it at the arc's final commit also
surfaces this entry's own prose, plus four lines the arc's own
remediation rounds *added on purpose*, each naming the pre-migration
monolith as a historical fact rather than as a live pointer:

```
docs/loom/specs/2026-07-25-kpi-id-injective-identity.md      (the dropped-anchor note)
docs/loom/plans/2026-07-22-kpi-observation-history.md        (dated correction note)
docs/loom/plans/2026-07-25-company-total-revenue.md ×2       (restored historical anchor)
```

Do **not** repoint those four. Two review rounds went into establishing
that a completed task block records what was true on the day it ran, and
that a measurement whose original anchor pointed at a section header has
no owner to be repointed to. Repointing them would fabricate provenance
— the specific defect the rest of this entry exists to prevent.

The fix is the same one the sweep applied elsewhere: repoint each at
the entry file under `docs/loom/backlog/` that now owns the cited
content, without a line number — entry files are short and are the
stable identity. Find the line-number class with:

```
grep -rn "BACKLOG\.md:[0-9]" --exclude-dir=.git . | grep -v '^./docs/loom/archive/'
```

## A second, wider class: heading-anchor citations

`BACKLOG.md §<heading>` citations are the same defect one step removed:
no line number to go stale, but the generated index has no per-entry
headings at all — a `§"..."` anchor into `docs/loom/BACKLOG.md` today
resolves to nothing. Widened recipe (a whole-branch reviewer's
suggestion), re-run 2026-08-02:

```
grep -rnP 'BACKLOG\.md[^a-zA-Z0-9]{0,4}§' --exclude-dir=.git .
```

This over-matches and needs manual filtering: it also catches a
generic template example (`docs/loom/plans/2026-07-06-loom-memory-store.md:218`,
`"→ docs/loom/BACKLOG.md §<entry>"` — a placeholder, not a citation, the
same shape as `check_doc_citations.py`'s docstring example above) and
`investing-toolkit/CHANGELOG.md:10`, which *describes* an already-completed
repoint, not a live one. After filtering both out, **eleven files, twelve
citation lines** remain unrepointed:

```
loom-product-principles/CHANGELOG.md:42
docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md:326
docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md:110
docs/loom/specs/2026-07-19-8k-earnings-kpi-intake.md:4
docs/loom/specs/2026-07-25-company-total-revenue.md:180
docs/loom/plans/2026-07-30-copywriting-convergence-modernization.md:379
docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md:200,227
docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md:185
docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md:98
docs/loom/plans/2026-08-01-declared-vs-actual-files-touched-check.md:89
docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md:154
```

Four further instances of this same class —
`docs/loom/plans/2026-07-22-kpi-observation-history.md:143` and three
lines in `docs/loom/plans/2026-07-25-company-total-revenue.md` (`:423`,
`:440`, `:464`) — are **not** in this list: all are inside one
already-completed task block per file, and are already addressed in
place by a dated correction note on that task (2026-08-02,
whole-branch review remediation), which explains why they still
correctly name the pre-migration monolith and should not be repointed.

Also expect the recipe to match this entry's own prose above (it names
the `§<heading>` shape to explain it) — that is self-reference, not a
citation, same exclusion reason as the template-example filter above.
Re-run this same recipe before closing this entry — the count above is
a 2026-08-02 measurement, not a ceiling.

## One carve-out that has no owner

`docs/loom/specs/2026-07-11-escalation-interface-contracts.md`, lines
5 and 104, cite `BACKLOG.md:111-149` for a heading titled
"Designer/PM loop — escalation interface". That heading was added in
`de8992ff` and **deleted** — not archived — in `d8793b56` when PR #537
shipped the feature, under the pre-migration delete-on-completion
practice, weeks before this store existed. No entry owns it, live or
archived; `grep -rl "Designer/PM loop" docs/loom/backlog/` returns
nothing. These two citations are therefore unrepointable and are
recorded here as a defended carve-out rather than left as a silent
skip. They are also the concrete argument for this store's
archive-over-delete rule: the content is only unrecoverable because
the old policy deleted it.
