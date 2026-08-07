# Complexity-prune runbook — the loom family's periodic mechanism-slim recipe

**Proposal-only.** This runbook never edits a mechanism. Every arm it
describes is read-only, and the only output is a dated audit doc plus
backlog entries — a human (or a separately-dispatched implementer arc,
reviewed the normal way) decides whether to act on any finding. Nothing
here mutates a skill, agent, rubric, or script.

**Deliberately NOT a skill.** The audit that produced this recipe
(item E3, `docs/loom/audits/2026-08-07-family-complexity-audit.md`)
considered and rejected building a new skill for it: a skill is new
standing machinery — another mandatory-happy-path candidate, another
surface to keep in sync — for something that fires human-invoked,
maybe quarterly. A runbook you read and follow by hand carries none of
that weight. If this recipe is ever run so often that hand-following
it becomes the friction, that itself is the signal to reconsider — not
a reason to pre-build the skill now.

## When to run

Human-invoked, not scheduled or hooked into any CI gate. Two triggers,
either is sufficient:

- **Felt growth** — a session notices mechanism accretion while doing
  unrelated work (a SKILL.md near its word cap, a checklist gaining a
  new "ONCE per X" sub-block, a duplicated block spotted across files)
  and it's worth stepping back to look at the whole family rather than
  patching the one spot.
- **~Quarterly cadence** — absent a felt trigger, run it roughly every
  three months so patches that individually looked justified don't
  silently compound (the 2026-08-07 audit's headline finding: the
  pathology is not "too big", it's "patches accumulate and are never
  pruned back into the base flow").

## The four-arm read-only audit recipe

Run four arms in parallel, each a separate read-only pass over a
disjoint slice of the family. Every arm returns **file:line-grounded
findings** — a claim with no `file:line` citation is not a finding,
it's an impression, and does not enter the triage step below.

1. **Core-chain arm** — the mandatory happy-path skills a plain bug
   fix walks through (the plugin owning the fix's most-loaded chain;
   in the 2026-08-07 instance: loom-code's using-loom-code →
   brainstorming → tdd-iron-law → verification-before-completion →
   requesting-code-review → finishing-a-development-branch). Measure
   SKILL.md word counts against the cap, and flag any block that reads
   as several stacked incident-patches rather than one coherent
   mechanism.
2. **Support-surface arm** — the same plugin's non-mandatory skills,
   support markdown (references/, checklists/, standards/), and
   scripts. This is usually the largest population by file count and
   the one most likely to hide duplication (the same rule hand-copied
   into two places instead of one SSOT).
3. **Sibling-plugins arm** — every other plugin in the family, one
   arm covering all of them together (not one arm per plugin — the
   goal is a family-wide read, not a plugin-by-plugin repeat of arm 1
   and 2's method). Looks for the same accretion pattern outside the
   heaviest plugin, and for near-duplicate prose across plugin
   boundaries (e.g. a shared trigger sentence copied into multiple
   router SKILL.md files).
4. **Glue-layer arm** — the machinery that holds the family together
   rather than any one plugin's content: session-start cards, hook
   files, the memory store, backlog/audit doc conventions, any
   SSOT/distribute tooling. This is where a duplication's *governance*
   lives or is missing (is there a drift-guard test, or is it a
   silent hand-copy nobody re-syncs).

**State the counting population for every figure, in the finding
itself — never just a bare number.** A count with no stated population
looks precise and is not verifiable; the reader cannot tell whether
"111 support files" means all markdown in the family or one plugin's
slice. Cite the scope alongside every figure (e.g. "111 support md
files (md under `*/skills/*/` excl. SKILL.md), 191 scripts (py+sh
under `loom-*/`, excl. `__pycache__`)" — the 2026-08-07 audit's
Quantitative baseline table does this for every row). This is the
population-discipline lesson from
`docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`:
a finding-list is a sample of what the arm happened to reach, not
proof of the population, and a total that includes the sentence
stating it is never stable — state the partition (what's covered, what
isn't), not an unverifiable grand total.

## Load-bearing — do-not-touch discipline

Before any arm's findings become a slimming proposal, check whether
the mechanism under discussion is **load-bearing**: does an incident
or a dedicated audit stand behind its current shape? If yes, it is
exempt from simplification proposals — the finding may still be
recorded (for visibility), but it does not get a KEEP/DEFER/DROP
candidate slot, and a runbook run must never propose stripping it back
to what looks simpler on paper.

The 2026-08-07 audit's load-bearing list (illustrative, not
exhaustive — re-derive per run, don't just copy this list forward):

- finishing-a-development-branch's memory-timing check (PR #519/#520)
  and commit-carrier verify gate (#445)
- requesting-docs-review's convergence contract semantics (9-round
  loop audit, `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`)
- ui-verification's premise (2026-07-03 dogfood: 28/28 green with a
  broken UI)
- systematic-debugging's anchored-thinking WebSearch gate (2026-05-27
  case)
- product-principles' exemption cluster; spec-expansion's Phase ③
  matrix
- the distribute.py SSOT machinery itself

Each entry names the incident or audit that justifies the current
shape — a mechanism with no incident behind it is a slimming
*candidate*, not automatically exempt; a mechanism with an incident
behind it is exempt regardless of how heavy it looks.

## Proposal-critique triage

Every candidate that survives the do-not-touch filter goes through
`dev-workflow:proposal-critique`'s grounding × necessity matrix,
sorted into exactly one of:

- **KEEP** — grounded and necessary; execute directly (still as its
  own reviewed change, never inside the audit run itself).
- **KEEP-WITH-CAVEAT** — worth doing, but the write-up must record the
  specific constraint that keeps it safe (what must be preserved
  unchanged, what re-adds the removed behavior if it turns out
  needed).
- **DEFER** — plausible but not now; becomes a `PARKED` backlog entry
  under `docs/loom/backlog/` whose `start:` field states the concrete
  re-trigger condition (an event or a measurable threshold — never
  "later" or "when convenient"). A DEFER with no `start:` re-trigger
  is not a valid triage outcome.
- **DROP** — the audit itself states why the item does not clear the
  bar (e.g. zero session-facing benefit for the risk, or the
  verification cost of removing it exceeds the saving) so the same
  candidate isn't re-litigated from scratch on the next run.

## Outputs

A run produces exactly two kinds of artifact, both dated, both
committed the normal way (proposed via a reviewed PR, not written
directly by the audit):

1. **A dated audit doc** under `docs/loom/audits/YYYY-MM-DD-<slug>.md`
   — the four arms' findings, the load-bearing list, the triage
   table (KEEP / KEEP-WITH-CAVEAT / DEFER / DROP), and an execution
   order for whatever gets actioned.
2. **Backlog entries** under `docs/loom/backlog/` for every DEFER,
   each with a `start:` re-trigger, plus one `OPEN` backlog entry
   tracking execution of the KEEP + KEEP-WITH-CAVEAT lanes if they are
   not actioned in the same PR as the audit.

## Worked example

The 2026-08-07 run is the reference instance for this recipe, spanning
two arcs:

- **Audit doc**: `docs/loom/audits/2026-08-07-family-complexity-audit.md`
  — the four-arm run (core-chain / support-surface / sibling-plugins /
  glue-layer), the load-bearing list, and the full KEEP (5) /
  KEEP-WITH-CAVEAT (5) / DEFER (5) / DROP (2) triage table this
  runbook's sections above are distilled from.
- **Arc 1** (PR #670, merged) — the mechanical-dedup lane: executed
  KEEP item B1 and KEEP-WITH-CAVEAT items C2/D2 as drift-guard tests
  pinning existing duplication rather than relocating it into an SSOT
  (recon found the copies were not byte-identical, so relocation would
  have rewritten rendered prose); found B2 already covered by existing
  distribute.py machinery, so it shipped as a doc correction with no
  code change.
- **Arc 2** (this branch) — the legislation lane: executes KEEP item
  E1 (a deletion-first review dimension added to both code reviewers)
  and KEEP-WITH-CAVEAT item E3 — this runbook itself, shipped in its
  minimal form exactly as E3 specified: a human-triggered, proposal-only
  document, explicitly not a new skill.

Every DEFER item from the 2026-08-07 triage (A4, C1, C3, D4, E2) is
tracked as a `PARKED` backlog entry under `docs/loom/backlog/2026-08-07-*.md`
with its re-trigger in `start:` — consult those before starting a new
run to avoid re-discovering a candidate already triaged.
