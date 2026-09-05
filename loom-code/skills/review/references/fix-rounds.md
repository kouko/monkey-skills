# Fix rounds — a `NEEDS_REVISION` checkpoint finishing itself

A round that comes back `NEEDS_REVISION` is not a new checkpoint; it is
the same checkpoint continuing until it converges. This file is the
procedure for that continuation — `SKILL.md` §8 points here.

## Delta: fix commits only

The next round's delta is `git diff <this round's reviewed commit>..HEAD`
— the fix commits that landed after this round's verdict, never the whole
checkpoint again from an earlier `reviewed_sha`. A finding already closed
in an earlier round is not re-opened by re-reading unrelated history.

## Resume, do not replace, the reader

The readers who raised the still-open findings are **resumed** for the
next round — the same agent, its own context, not a fresh one. A reader
who raised none keeps its previous PASS standing when every path the fix
touched sits inside the anchors of the returning readers' findings;
when the fix reached outside those anchors, that reader is resumed too,
and the floor is the whole previous round (`push.verdicts-ge-2`
recomputes this from `open_findings[].anchor` and the fix delta, and a
standing reader must appear in `dispatch[]` as a reviewing role).
Dispatch a resumed reader with:

```
### Your previous findings
<the findings list this agent raised last round>

### Fix delta
git diff <previous reviewed commit>..HEAD
```

The resumed reader marks each of its own previous findings `fixed` or
`unfixed` against the fix delta. It raises no finding outside that delta
unless the fix itself broke something the delta touches — a fix round
re-reads a finding list, it does not re-review the checkpoint.

## Probes are not re-run here

The resumed reader does not re-run `probes[]`; `push` re-runs every probe
itself in a clean tree and is the check that actually gates the merge.
Re-running them inside a fix round buys nothing but a slower loop.

When a reader's `important` finding can be written as a runnable case,
this fix round's adversary encodes it into this change's probe file, runs
it once here, and records one `probes[]` entry (`kind: adversarial`, this
round's scope) — done inside the fix round, no hand-off. This adds and
runs one new probe; it does not re-run existing ones.

## Rebuttal

The orchestrator may attach evidence disputing a finding instead of
fixing it. The resumed reader either accepts it — mark the finding
`dismissed: <reason> by <agent_id>` — or holds its ground and says why in
one line. A dismissal by anyone holding an `implementer` role for this
change is refused (`push.dismissed-by-reviewer`); it must come from the
reviewing role that raised or is resuming the finding.

## Third round: stop fixing, look at the design

A third round on the **same checkpoint** — the same `scope`, not a new
one — means the fix-and-reread loop is not converging: hand the full
finding history (every round's findings, fixed/unfixed/dismissed) to a
higher-tier agent for one design question — is the shape of the change
itself wrong, not just its wording — before dispatching any further fix.
Do not iterate a fourth round on the same finding without that check.

These two rules — no finding outside the fix delta, and the third-round
design re-look — are reader-trusted, not checker-enforced; no push rule
reads a finding's anchor against the delta or counts rounds. They are
enforced the way `dispatch[].fresh_context` is: by the record and the
next reader.
