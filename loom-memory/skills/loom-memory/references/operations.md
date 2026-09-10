# Operations — detailed procedure

This file expands the four operations named in `SKILL.md`. Read it when
the compact steps there are not enough, not on every invocation.

## Recall

1. Locate the store. Its absence is a normal no-memory result — report it
   and move on; never treat a missing store as an error to fix.
2. If the store exists but has concept files with no `index.md`, that is
   structural corruption, not a normal miss. Stop, name it explicitly, and
   direct the user to `loom-memory/scripts/loom_memory.py validate
   <store>` or, when the store is the pre-OKF legacy shape, the explicit
   migration operation. Do not fall back to scanning concept files
   directly — that defeats the bounded-load property the index exists
   for.
3. Read `index.md`. Its grouped, one-line-per-entry shape is enough to
   decide which entries might match without opening anything else.
4. Open only the entries whose description plausibly matches the current
   need. An empty match set is a normal no-memory result.
5. For every entry opened, verify every file, flag, skill, or command it
   names by its own trigger or correct-path text still exists in the
   repository before treating the lesson as actionable. A lesson naming a
   file that is gone is stale — surface that explicitly rather than
   silently acting on outdated advice.
6. Report findings point-first, citing the concept file, not a raw
   frontmatter dump.

## Record

1. Classify the candidate against this filter before anything else. It
   must be a durable repository lesson — knowledge that stays true and
   useful after this change is long forgotten. It fails the filter, and
   is not recorded here, when it is instead:
   - an open task or TODO,
   - a narrative of what changed in this session,
   - a verification or test-run record,
   - a decision whose relevance is bound to one commit or PR (`git-memory`
     owns that), or
   - a personal preference unrelated to the repository.
2. Read `index.md` and search matching or nearby entries for one that
   already says this, or says something this would contradict or narrow.
   A match routes to Reconcile — never create a second concept for the
   same subject.
3. Choose `type`, a filename (the concept's `name` must equal its stem),
   and write the frontmatter: `type`, `name`, `description` (one
   standalone durable relevance rule), `sources` with at least one
   `resource`.
4. Write the body: `Trigger`, `Correct path`, `Why`, and `Limits` only
   for a real non-applicability boundary — see `references/okf-profile.md`.
5. Run `loom-memory/scripts/loom_memory.py regenerate-index <store>` then
   `validate <store>`. Do not consider Record complete until validation
   is clean.

## Reconcile

1. Reconcile activates when a new lesson contradicts or narrows a current
   entry found during Recall or Record's search step — never as a
   separate discovery pass.
2. Locate the exact current entry through `index.md`; do not guess at a
   filename.
3. Decide: does the new lesson replace the old one outright, or narrow it
   (the old lesson still holds in a smaller set of cases)? Either way, the
   result is exactly one current concept for the subject — editing the
   existing file in place, or replacing its content wholesale. Never
   leave both the old and the new as separate live entries.
4. Preserve every `sources[].resource` already on the entry; add the
   source for the new evidence rather than dropping the old provenance.
5. Regenerate and validate the index.

## Retire

1. Retire activates when an entry is no longer true and nothing currently
   replaces its value (a plain repeal, not a narrowing — that is
   Reconcile).
2. State the entry and why it no longer holds, in the user's language.
3. Require explicit user approval before deleting anything. Retire never
   deletes on the agent's own judgement alone, unlike Recall, Record, and
   Reconcile, which the agent may perform on its own judgement of need.
4. On approval, delete the concept file. Rely on Git history, not a
   `log.md`, as the archive of what it said and why it was retired.
5. Regenerate and validate the index after deletion; a stale link left in
   `index.md` is exactly the broken-index-target failure the validator
   already catches.

## Legacy stores

A legacy README-indexed store — one predating this profile, whose
"index" is hand-written prose in `README.md` rather than a generated
`index.md`, and whose concept files may carry a legacy `origin` field
instead of `sources` — is out of scope for every operation above. Detect
it (concept files present, no generated `index.md`, at least one concept
file lacking a `sources` entry) and report that an explicit migration is
required, without modifying any file. This skill never reads or writes
that legacy format itself; migration is a separate, explicit operation
performed on request, never an implicit side effect of installation,
session start, Recall, or any other station.
