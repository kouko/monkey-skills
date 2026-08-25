---
name: git-memory
description: |
  Mandatory gate before every git commit / gh pr create / gh pr merge — the skill decides whether memory trailers (Decision/Learning/Gotcha) apply; don't pre-judge a commit 'routine'. Also recalls past decisions: 'why did we…', '為什麼', an old branch.
---

# Git Memory

Durable lessons live in the repo's committed memory store
(`docs/loom/memory/` here), the authoritative carrier. Git artifacts provide
commit-bound capture: best-effort, secondary, and never the retrieval path a
durable lesson depends on.

## Invocation policy

> **This skill is an invocation gate, not a trailer gate.**

Two decisions must remain separate:

| Decision | Owner | Rule |
|---|---|---|
| Invoke this skill? | Caller | Before `git commit` / `gh pr create` / `gh pr merge`: always yes in an agent session |
| Add memory content? | This skill | Classify inside the skill; routine commits exit cleanly with no trailers |

Never let the caller's pre-judgment replace the classification logic. The gate
must run even when its result is “no memory needed.” `gh pr merge`, especially
with `--squash`, is the last checkpoint before the branch closes and the final
chance to catch an empty memory-worthy branch.

## Carrier hierarchy

Use the committed memory store for durable knowledge. Use git artifacts to
capture the why at the change boundary so any git-capable tool or human can
recover it without a vendor-specific database. These layers complement, rather
than replace, user-level agent memory.

| Layer | Scope | Retrieval |
|---|---|---|
| Committed memory store | Durable repo lesson | Repository files and their index |
| Commit messages + PR bodies | Change-bound capture | `git log`, PR history, and `scripts/memory-grep.sh` |
| Agent-native memory | User preferences across projects | Host-managed, session-loaded memory |

Do not distill all git-memory into an always-loaded context file. Project
decisions are pulled on demand; user preferences can remain pushed by the host.

## What to capture

The diff already shows what changed. Capture why it changed when at least one
of these applies:

- **Decision** — a non-obvious choice had a real alternative.
- **Learning** — the work revealed a surprising constraint or behavior.
- **Gotcha** — a concrete trap would otherwise catch a future contributor.

Use the minimum earned set of structured trailers:

- `Decision:` — why this approach won over the alternative.
- `Learning:` — the specific discovery worth retaining.
- `Gotcha:` — the misleading surface and the correct path.
- `Related:` — an earlier PR whose context this change extends.
- `Supersedes:` — the earlier live decision this change replaces.

Routine typo, formatting, version-bump, and obvious implementation commits
produce no trailers. Do not record restatements of the diff, generic advice,
or user preferences unrelated to the repository. The full schema, wrapping,
liveness rules, and examples live in `standards/memory-conventions.md`.

### Classification discipline

Ask whether the work made a choice future readers could reasonably reopen,
discovered a constraint they cannot infer from the code, or exposed a named
failure mode. Any yes makes the change memory-worthy. All no means the correct
output is empty. This classification happens separately for a commit and its
PR: a sequence of ordinary commits can still produce a memory-worthy PR when
their combined architecture or policy matters.

Do not fill every field as a completeness ritual. One precise `Decision:` is
better than three vague trailers. A useful entry remains actionable after the
working context disappears: it names the rejected alternative, the observed
constraint, or the recognizable trap. `Related:` links supporting context;
`Supersedes:` declares replacement and lets recall hide the retired decision by
default. Validate either relationship as required by the commit protocol so an
immutable pointer does not silently lead to a carrier with no memory.

## Compose at each git boundary

### Commit

Before authoring or finalizing a commit, read
`protocols/compose-commit.md`. It owns the memory-worthiness filters, trailer
composition, `Related:`/`Supersedes:` validation, diagram venue, confirmation,
and delegated close-out exception. Compose concise why-focused prose, then the
minimum useful trailers.

### PR create

Before `gh pr create`, read `protocols/compose-pr.md`. For a memory-worthy PR,
both carriers are mandatory:

1. a rendered `## Memory` section after the standard test-plan content and
   before the generated-attribution footer; and
2. an unbolded raw `Decision:`/`Learning:`/`Gotcha:` footer as the absolute
   last authored block.

For a routine PR, omit both. Do not alter the standard Summary or Test plan to
smuggle memory content into them.

The rendered section and raw footer serve different readers. The section can
explain alternatives, learnings, gotchas, and architecture in readable prose.
The raw footer keeps short keys available to git retrieval. Memory-worthy means
both are required; neither substitutes for the other. Place Mermaid diagrams
in PR prose when architecture, data flow, or state changes justify one. Commit
messages may use a small ASCII diagram, but routine changes need no diagram.

### Merge and capture verification

Before a memory-worthy PR closes, verify the capture rather than assuming the
authoring step worked:

- Run `scripts/memory-grep.sh --verify <ref>` for the commit carrier. Exit `0`
  means at least one memory key is text-retrievable; exit `4` means empty.
- Confirm the PR `## Memory` section is present.
- Use `--verify-merged <ref>` after merge to catch a heading whose keys were
  silently dropped, including a title-only squash result.
- Use `--verify-strict <ref>` only as a footer-parse diagnostic; it is not the
  durable-lesson path.

An empty result is a flag to fix **before** merge. Branch close-out enforces
this through `loom-code:finishing-a-development-branch`; verification proves
that commit-bound capture landed, not that a durable lesson was filed.

This verification is **enforced as an executable gate by
`loom-code:finishing-a-development-branch`**. The raw-footer mandate itself is
owned by `protocols/compose-pr.md`; the close-out gate verifies its result.

Interpret the checks narrowly. Plain `--verify` proves a key is visible in the
message text, including the mid-body produced by squash. `--verify-merged`
guards the merged carrier against a PR body or Memory section being discarded.
Strict verification asks whether git still recognizes a real trailing footer;
its failure can coexist with successful grep-level capture. None of these
checks promotes a broadly reusable lesson into `docs/loom/memory/`; durable
filing is a separate repository workflow.

## Squash-merge caveat

> **On a squash-merged default branch, `%(trailers)` is unreliable.**

A squash can relocate per-commit trailers into the merged commit's mid-body.
GitHub may also append a divider and `Co-authored-by:` block, or hard-wrap a
line, after the authored PR footer (live-observed on PR #576). Footer-only
parsing through `%(trailers)` or
`git interpret-trailers --parse` can therefore miss valid capture even when
the PR body followed the best-effort placement mandate.

`git log --grep` and `memory-grep.sh --verify` still find keys that begin at a
line start. The PR `## Memory` section remains human-readable on GitHub. Both
are commit-bound evidence; the committed memory store remains authoritative.
Never promise that a raw PR trailer footer guarantees structured parsing. Its
guaranteed floor is grep-level retrieval. A merge commit is also valid when
preserving each commit's real footer matters.

Keep raw trailer lines short and consecutive, separated from preceding prose
by one blank line, with no authored heading, comment, fence, or ordinary text
after them. That placement gives structured parsing its best chance before the
hosting platform performs its own squash transformation. On feature branches,
merge-commit histories, and rebase-merge histories, a genuine footer remains
available to `%(trailers)`; on squash `main`, prefer the robust retrieval paths
above.

## Privacy gate — fail-closed

Git is public-by-default. After composing any commit message or PR body, follow
the exact two-layer privacy gate in its compose protocol:

1. Run `scripts/privacy-scan.py --text-file <composed>`.
2. Dispatch the fresh-context judge specified by
   `protocols/privacy-judge-spec.md` over the same text.
3. Continue only when the deterministic scan is clean and the judge returns a
   conforming `PASS`.

Any finding, judge `BLOCK`, script error, dispatch failure, or malformed judge
result makes the carrier **BLOCKED**. Surface the findings, stop, and escalate
to the human. Delegated close-out consent never overrides this stop. The
commit protocol's optional quality note is advisory only; it cannot turn a
privacy failure into a pass.

Run the gate over the exact final text that would be committed or sent to
GitHub, not an earlier excerpt. Do not manually waive a deterministic match or
replace the fresh judge with the composing agent's own confidence. When the
protocol is delegated from an already-authorized close-out, that authorization
can remove duplicate publication confirmation; it cannot authorize a blocked
carrier or broaden what sensitive material may leave the machine.

Never write secrets or sensitive context into repository history. Use an
appropriate ignored note or secret manager instead.

- **Secrets or sensitive context** — the compose protocols enforce a
  fail-closed privacy gate: `protocols/compose-commit.md` and
  `protocols/compose-pr.md` run `scripts/privacy-scan.py` plus the judge in
  `protocols/privacy-judge-spec.md`. Any failure stops publication.

## Recall routing

Past decisions are **pulled** on demand, not preloaded. Read
`protocols/recall.md` when:

- the user asks why an old decision, branch, or PR exists;
- non-trivial work begins in a concrete file or module; or
- planning weighs an alternative that may already have been rejected.

Recall once with a scoped `--path` or `--match`, cap the result with `--top`,
and accept empty output as normal. Default retrieval is live-only; add
`--history` only to explain a superseded chain. Surface the answer in the
user's language, point-first, citing the PR or commit rather than dumping raw
trailers. If new work intentionally reverses a live decision, say so and treat
it as a candidate `Supersedes:` relation.

For proactive work, use one scoped path recall before changing a non-trivial
area. For alternative analysis, use one topic recall before recommending the
approach. Do not broaden or loop because a query returned nothing; absence is a
normal result, not an operational failure. A live match should prevent silent
re-litigation. A superseded match should be presented with its replacement so
the retired choice is not accidentally revived. Recall supports the current
task; it is not a transcript dump or session-start priming ritual.

## Resource map

- `protocols/compose-commit.md` — commit classification, composition, privacy,
  consent, and relation validation.
- `protocols/compose-pr.md` — PR memory section, footer placement, privacy, and
  confirmation.
- `protocols/privacy-judge-spec.md` — fresh-context privacy judge contract.
- `protocols/recall.md` — scoped pull triggers, commands, liveness, and user
  reporting.
- `standards/memory-conventions.md` — schema, examples, supersession, line
  length, diagram venues, and retrieval doctrine.
- `scripts/memory-grep.sh` — scoped recall plus normal, merged, and strict
  capture verification.
- `scripts/privacy-scan.py` — deterministic first privacy layer.

## License

MIT — see repository root `LICENSE`.
