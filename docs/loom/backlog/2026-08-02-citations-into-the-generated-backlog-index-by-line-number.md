---
name: 2026-08-02-citations-into-the-generated-backlog-index-by-line-number
description: six documents still cite docs/loom/BACKLOG.md by line number, which is now a generated file whose line numbers move on every regeneration
status: OPEN
origin: whole-branch review of the docs-backlog-one-entry-per-file arc, 2026-08-02 — the arc repointed every citation whose anchor had already gone out of range, and left these, which resolve today
start: whenever a batch of entries is added or archived, since that is what shifts the line numbers and turns these from correct into silently wrong
---

Before the one-entry-per-file split, `docs/loom/BACKLOG.md` was a
hand-maintained 2,545-line document, and citing it by line range was
reasonable. It is now **generated output**, 89 lines, rebuilt from the
entry files on every `--write`. Adding one entry or archiving one
shifts every line below it.

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

The fix is the same one the sweep applied elsewhere: repoint each at
the entry file under `docs/loom/backlog/` that now owns the cited
content, without a line number — entry files are short and are the
stable identity. Find them with:

```
grep -rn "BACKLOG\.md:[0-9]" --exclude-dir=.git . | grep -v '^./docs/loom/archive/'
```

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
