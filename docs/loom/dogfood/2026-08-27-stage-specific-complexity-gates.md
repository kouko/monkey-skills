# Stage-specific complexity gates — behavioral evidence

Date: 2026-08-27

## Evidence binding

The immutable pre-edit snapshot at `/tmp/loom-complexity-baseline.xt9viD` was
captured before lens edits and checked against base commit `0a7dcde2`. It was
used only to run the original comparison. The durable identities below are
recomputed from that commit's tracked plugin archives; candidate identities are
recomputed from tracked cold-package files, so ignored caches cannot affect
either result and CI does not depend on the machine-local directory.

- loom-design baseline SHA-256: `0e63efae0f07c92c3e98c657d821b5a03d171d0049570508ad745e0a19aef486`
- loom-code baseline SHA-256: `e2a861d4028c2837de7a32596a7c4299cd0792fdc27e4b7f278f9856745df6bc`
- loom-design candidate SHA-256: `2c26a91e2a72114800344ce8dd649ef8ec7d1760a95fe90c681d499d6c5d2c17`
- loom-code candidate SHA-256: `eda1e76408fdf3ac447dda7a645134b798d83fbdaabcc76a23c7b260b05208a3`
- loom-design hard-case behavior SHA-256: `afa3b1dca93ab1a078cd5ddc495bd03c613da81e645c894625bce753a05e6241`
- loom-code hard-case behavior SHA-256: `6ce0976774f213d4c6e7d4c60727a2fb6e7f2270edafbdf9c43fd41564c415c5`

These are the **final cold-install candidate bytes** for both plugin packages;
the report and its root-level test do not alter either package tree.

The candidate fingerprints cover the whole cold-install package, so they move
for a release bump that changes no instruction. The **hard-case behavior**
fingerprints above cover only the instruction surface the hard cases could
observe — every tracked `.md` under each plugin's `skills/` and `agents/`,
excluding READMEs and changelogs — measured at commit `7af88b70`, the last
commit the live runs saw.

The loom-design candidate fingerprint above was refreshed on the
`loom-script-refactor-phase3` branch, after that branch's last change to a
tracked `loom-design/` file. That branch split
`loom-design/scripts/pipeline/batch_queue.py` into `queue_commands.py` and
`queue_core.py` and bumped the plugin version; it changed no tracked `.md`
under `loom-design/skills/` or `loom-design/agents/`, and no file in
`_LENS_PATHS`. It is therefore exactly the release-bump case the paragraph
above describes — the package bytes moved, the instruction surface the hard
cases observed did not, and the results below still hold. The loom-code
candidate fingerprint was unaffected and is unchanged.

`7af88b70` was a commit on the pre-rebase branch. Rebasing this work onto the
mainline replaced it, and no reachable commit carries those bytes, so the two
hard-case numbers can no longer be recomputed from a clone; they stand as a
recorded measurement. What remains checkable is the part that matters going
forward: `scripts/test_stage_specific_complexity_behavior_evidence.py` records
the files that had already changed by `acd5a846` (the round-4 fixes as merged)
and reads every later change straight from git, so an edit landing on the
instruction surface after that anchor cannot reach this report without being
named in the section below.

## Instruction-surface changes after the hard cases

Round-4 whole-branch review returned `NEEDS_REVISION` (two fatal findings) and
the remediation edited the instruction surface. The hard-case results below
therefore describe the surface at `7af88b70`, **not** the shipped bytes, for
these seven files:

- `loom-code/agents/code-reviewer.md` — the no-planned-evidence fallback was widened from downstream risk alone to the whole assessment, and the worth question was added.
- `loom-code/skills/requesting-code-review/references/implementation-complexity-lens.md` — added the fourth handoff meaning (whether the landed burden is worth its maintenance cost), which this lens alone had dropped.
- `loom-code/skills/requesting-code-review/references/design-evidence.md` — a heading inserted in an earlier round had orphaned the deletion-first evidence tail; the sections were reordered. Author-facing, not loaded at runtime.
- `loom-code/skills/writing-plans/SKILL.md` — the plan skeleton gained the `## Complexity assessment` slot it mandates, and the lens paragraph now names that section and links the schema.
- `loom-code/skills/writing-plans/references/plan-format.md` — both worked examples gained the mandated section (the CSV plan in full, the mechanical backfill plan as the reasoned exemption), and a dangling heading anchor was repointed.
- `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md` — Check 21 now states how it interacts with Check 18(b), whose hedge scan covers the region the new section occupies.
- `loom-design/skills/business-value/assets/business-value-template.md` — the reasoned-N/A placeholder now says it replaces the four slots rather than joining them.

One later edit, from the `goal-create` branch and outside the complexity work,
moved the surface once more:

- `loom-code/skills/finishing-a-development-branch/SKILL.md` — the offer made when `docs/loom/PURPOSE.md` is absent now names `loom-workflow:goal-create` as one way to answer it. It adds no lens, changes no verdict enum, and alters no stage's required outcome, so the results below are unaffected by it.

Every one of the round-4 files adds, widens, or disambiguates an instruction; none removes a
lens, narrows a verdict enum, or changes a stage's required outcome. That is a
reason to expect the results below still hold, **not** evidence that they do —
the live cases were not re-run against the edited surface. Re-running the
`business` and `architecture` lanes is the open item; the other four lenses'
rows are unaffected, because `behavioral-complexity-lens` and
`implementation-complexity-lens` are evidenced by contract test rather than by a
live case, and the `visual` and `interaction` lenses' files did not change.

Raw transcripts and normalized comparisons are session-local evidence under
`/tmp/loom-complexity-live.SRPuAf/`. They are intentionally not committed
because they contain verbose host traces and disposable authentication homes.

## Hard-case results

| Case | Baseline observation | Final candidate observation | Result |
|---|---|---|---|
| `no-upstream` business burden | Claude and Codex asked for Why-now evidence and did not complete an artifact within the bounded run. | Codex 2/2 produced a validated `NEEDS-MORE-RESEARCH` artifact naming burden, conditional worth, avoidable work, and downstream risk. Claude 2/2 retained the existing evidence-first questioning behavior. | PASS at `7af88b70`, not re-run after the round-4 fixes; host divergence recorded, and absence of upstream evidence did not weaken the candidate verdict. |
| `no-upstream` architecture plan | Baseline Codex 2/2 refused to invent a valid handoff without a brief; baseline Claude produced provisional shapes. | Candidate Codex 2/2 created a brief and plan with a complete local four-part assessment; candidate Claude either produced an exemplar assessment or requested the missing Smallest End State. | PASS at `7af88b70`, not re-run after the round-4 fixes; local judgment occurred and existing brief discipline was not silently bypassed. |
| `trivial-exempt` visual typo | Baseline produced a reasoned visual N/A in three gradeable runs; one Claude replicate was contaminated by unrelated workspace orientation. | Claude 2/2 and Codex 2/2 returned a reasoned N/A because no token, variant, state, vocabulary, or exception changed. | PASS; the visual lens did not over-fire into design regeneration. |
| `misleading-upstream` architecture claim | Baseline hosts already challenged the unsupported `complexity: none` statement using general planning judgment. | Claude 2/2 and Codex 2/2 ignored the unsupported conclusion and independently recorded added migration/dependency cost, worth, avoidance, and risk. | PASS at `7af88b70`, not re-run after the round-4 fixes; optional evidence never replaced local assessment. |
| `over-complex` interaction proposal plus misleading upstream | Baseline Claude requested missing project inputs or was blocked by the harness write restriction before producing `ui-flows.md`. | Final-byte Codex 2/2 produced and validated `ui-flows.md`, called the increase substantial, justified survivors against auditable above-threshold purchasing, proposed collapses, and handed risks to spec-expansion. | PASS on Codex; Claude lane UNGRADABLE because the comparison harness permits only `Skill` while this skill must write and validate an artifact. |

The normalized firing comparator returned PASS where tool sequences remained
equivalent and INCONCLUSIVE where the candidate loaded extra local references
or wrote the newly required artifact. INCONCLUSIVE is not treated as a failure
or a pass; the semantic judgments above come from the preserved raw outputs.

## Lens evidence coverage

The live harness exercised the stages for which its bounded tool surface could
produce a gradeable artifact. The remaining two lenses are explicitly scoped
to contract tests rather than being presented as unobserved live results.

| Lens | Evidence kind | Result |
|---|---|---|
| `business-complexity-lens` | live hard case (pre-fix surface; not re-run) | PASS |
| `visual-complexity-lens` | live hard case | PASS |
| `interaction-complexity-lens` | live hard case | PASS |
| `behavioral-complexity-lens` | contract test | PASS |
| `architecture-complexity-lens` | live hard case (pre-fix surface; not re-run) | PASS |
| `implementation-complexity-lens` | contract test | PASS |

## Purpose preservation

The final interaction artifact says each surviving element must support the
stated policy outcome and that losing audit or recovery behavior is a **scope
trade-off**, not a complexity saving. Contract tests independently pin the
same invariant in all six local lenses:

- `business-complexity-lens`: required business outcome
- `visual-complexity-lens`: intended visual outcome
- `interaction-complexity-lens`: required user or operator outcome
- `behavioral-complexity-lens`: required user or system outcome
- `architecture-complexity-lens`: required end state
- `implementation-complexity-lens`: preserves the required outcome

Thus purpose preservation constrains deletion without introducing identical
plugin prose, a shared schema, or a universal score.

## Selectivity and plugin independence

Each lens owns an applicability boundary and a reasoned exemption or local
fallback in its own skill directory. The focused stage tests verify those
boundaries; the cold-package contract verifies every skill resolves only its
local reference; standalone layout and composition tests verify that missing
sibling plugins do not break evaluation and that optional relay uses only
project-owned `docs/loom/` artifacts.

No live result is used to claim more than it observed. In particular, the
Claude interaction lane remains UNGRADABLE rather than being converted into a
false PASS, and the one contaminated trivial baseline replicate is excluded
from the stability claim.

Pre-existing invariant result: PASS — existing value axes, eight-section
`DESIGN.md`, seven flow dimensions, seven-section spec proposal, plan review
gate, and whole-branch review station remain in place; focused tests and the
full package suites are the merge-boundary evidence.
