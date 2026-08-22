# Brief: a shipped contract cites only what ships with it

Date: 2026-08-22
Author: kouko (session)

## Design-side on-ramp

not fired — a portability defect in shipped contract text, found by inspecting the deployed bundle; no product-shaped or user-facing surface

## Problem

When a repository that is not `monkey-skills` installs loom, I want every
skill and agent contract it loads to be applicable on its own, so that the
rules arrive intact instead of deferring to development records that repo
does not have and will never have.

## Users

Two readers, with different reach. A dispatched agent holds `agents/*.md` in
an injected system prompt and reads files from whatever repository it is
working in — so a citation of `docs/loom/specs/…` resolves in `monkey-skills`
and nowhere else. A human maintainer editing a rule needs the opposite: the
provenance, to avoid re-litigating a settled decision. Today both are served
from the same sentence, which is why it fails one of them.

## Smallest End State

A rule, a mechanical check that enforces it going forward, the one genuinely
functional citation moved inside the skill tree, and the bootstrap gap closed.

BI-1 — the rule, written where the repo's other authoring conventions live: a
runtime prose contract under `loom-code/skills/**`, `loom-code/agents/`,
`loom-design/skills/**` must not cite one of THIS repository's development
records under `docs/`. A path loom defines for every host repo is exempt
whatever its shape — a store directory or a protocol filename alike.

BI-2 — the functional citation moved: `code-as-spec-writing-rule.md`
§Decision is cited as SSOT at three sites in two agent contracts. Its
operative sentence is inlined so the rule stands without the document.

BI-3 — a checker that fails when a runtime prose contract cites one of this
repository's records, carrying an explicit debt list of the files that violate
it today. The list may only shrink; a new violation anywhere fails immediately.

BI-4 — `agents/*.md` cleared of its remaining citations, since an agent
contract is the reader with the least recourse.

BI-5 — `loom_init.py` scaffolds `docs/loom/memory/`, which loom skills
instruct a reader to consult and which the bootstrap does not create.

## Current State Evidence

- **Forward** — of 145 prose files under `loom-code/skills`,
  `loom-code/agents` and `loom-design/skills`, a substantial minority cite a
  named file under `docs/loom/`. No count is stated here on purpose: three
  independent hand-counts returned 32, 36 and 46, differing only in the regex
  used, so the membership question is the checker's to answer and BI-3's debt
  list is the only authority on it.

- **Corrected during Task 1.** This brief first counted the three
  `references/design-evidence.md` files as already compliant because each
  declares itself author-facing. The rule as written grants no such exemption,
  and the implementer put them on the debt list rather than special-casing them
  to match this brief — the right call, twice over. A rule the implementer
  patches to fit the author's expectation is not a rule. And an exemption a
  file can claim by writing a line about itself is self-signed: any file could
  escape by adding the same sentence, which is the failure this repo has
  already recorded for judgment-shaped waivers. They stay on the list.
- **Reverse** — the compliant pattern is not new and is already enforced:
  `test_rcr_extraction_pointers.py`, `test_wp_extraction_pointers.py` and
  `test_rdr_extraction_pointers.py` guard the extraction pointers for the three
  skills that use it. This brief generalises a tested local pattern rather than
  inventing a convention.
- **Error** — the failure is invisible in `monkey-skills`: a docs-reviewer on
  this branch opened `docs/loom/specs/2026-08-22-code-as-spec-lens-no-op-bar.md`
  and checked a claim against it successfully, because the file was there. The
  same contract in a foreign repo silently loses its authority.
- **Data** — the citations were classified by the role their own sentence
  gives them. No counts are stated: the classification was a manual read that
  no script reproduces, so a number here would carry more authority than the
  method earns. Qualitatively, a small minority are AUTHORITY — the reader
  cannot apply the rule without the document — and the clear majority are
  provenance. Within the AUTHORITY set, three sites cite one decision
  paragraph and are inlinable, one sits in a file declaring itself never
  loaded at runtime, and the rest are lookups of stores this rule exempts.
- **Boundary** — the plugin bundle is the whole plugin directory: 388 files
  under `loom-code/` against 376 in the deployed cache at
  `~/.claude/plugins/cache/monkey-skills/loom-code/0.94.0`, and no `docs/loom`
  directory there. Content under `loom-code/**` travels; the repository's
  `docs/` does not.

## Decision

A runtime prose contract cites only what ships with it. Where a citation is
functional — the reader cannot apply the rule without it — the content moves
inside the skill tree or is inlined. Where it is provenance, it leaves the
runtime file for the author-facing sibling this repo already uses.

The line is protocol versus record, not directory versus filename. That
distinction was got wrong in this brief's first draft and the plan-document
reviewer found what it cost: `code-reviewer.md` reads `docs/loom/PRINCIPLES.md`
at its `principles-conformance` row as a conditional self-check against whatever
repo the agent landed in, and a filename-based ban would have deleted that
mechanism. No count is given: the figure first written here reproduced under no
command, which is the fifth such slip this session and the reason counts now
live only where a script produces them.

Exempt, as loom's schema for any adopting repository: the store directories
`docs/loom/{backlog,plans,specs,memory}/`, and the protocol filenames a host
repo owns — `PRINCIPLES.md`, `PURPOSE.md`, `KICKOFF-DEFAULTS.md`, `INDEX.md`,
`DESIGN.md`, `QUEUE.toml`, `spec/MODEL.md`, a store's own `README.md`,
`ui-flows.md`. The list is closed and lives in the checker.

Banned, as this repository's own records: a dated entry under `specs/`,
`plans/` or `audits/`, and a named entry under `memory/`.

Also out of scope: provenance comments inside `.py` and `.sh` files. No model
reads a script comment unless it opens the file, so those are author-facing by
construction.

The checker ships with a debt list rather than scoped to the files this arc
cleans. A list that may only shrink blocks new violations everywhere from the
first commit and leaves the remaining files visible; a checker scoped to
`agents/` would let the rest keep accreting silently.

Only `agents/*.md` is cleaned here. The rest are a follow-up, held by the
checker. One arc rewriting every violating prose file at once is how this repo
ships prose defects — the branch that preceded this one produced a 🔴 doing
exactly that at a scale of two files.

## Alternatives Considered

- **Clean every violating file in one arc.** Rejected on the evidence of the immediately
  preceding branch, where a two-file mirrored edit shipped a dangling referent
  that two reviewers caught and the author did not.
- **Move the cited documents into the plugin tree.** Rejected for the AUTHORITY
  set as it stands: the three inlinable citations name a frozen dated spec, and
  copying a historical record into a shipped tree changes what it is. Inlining
  the operative sentence keeps the record frozen and the rule self-contained.
- **Ban `docs/` mentions outright, including store paths.** Rejected: it would
  remove backlog, memory and plan lookups, which are functional and which
  loom's own bootstrap creates.
- **Leave it and rely on a foreign-repo probe to find these later.** Rejected:
  the probe is already filed and open, and it would rediscover by experiment
  what inspection has already established.

## Out of Scope

- Every violating file outside `agents/`, held by the checker's debt list.
- `.py` and `.sh` provenance comments.
- The second leg of the parent bet — line numbers rotting — which shares the
  rule's shape but not its remedy.
- Any change to what `docs/loom/` stores are or where they live.

## Queue relation

in-queue: 2026-08-22-line-cites-should-be-anchor-primary-across-the-loom-institutions

## Open Questions

N/A — no unresolved question: the rule's boundary was settled with the user, and its protocol-versus-record form was corrected after plan review.
