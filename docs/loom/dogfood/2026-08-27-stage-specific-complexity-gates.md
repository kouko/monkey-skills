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
- loom-design candidate SHA-256: `805fd790d45fe6dc0e8465daa8322caed4e28d1e3e8b00651a051768c8f4754a`
- loom-code candidate SHA-256: `32790c3fa1bf19211ac47d8fcf1ef548326a706aef3937db9a8ccb4c2dbc3ee5`

These are the **final cold-install candidate bytes** for both plugin packages;
the report and its root-level test do not alter either package tree.

Raw transcripts and normalized comparisons are session-local evidence under
`/tmp/loom-complexity-live.SRPuAf/`. They are intentionally not committed
because they contain verbose host traces and disposable authentication homes.

## Hard-case results

| Case | Baseline observation | Final candidate observation | Result |
|---|---|---|---|
| `no-upstream` business burden | Claude and Codex asked for Why-now evidence and did not complete an artifact within the bounded run. | Codex 2/2 produced a validated `NEEDS-MORE-RESEARCH` artifact naming burden, conditional worth, avoidable work, and downstream risk. Claude 2/2 retained the existing evidence-first questioning behavior. | PASS with host divergence recorded; absence of upstream evidence did not weaken the candidate verdict. |
| `no-upstream` architecture plan | Baseline Codex 2/2 refused to invent a valid handoff without a brief; baseline Claude produced provisional shapes. | Candidate Codex 2/2 created a brief and plan with a complete local four-part assessment; candidate Claude either produced an exemplar assessment or requested the missing Smallest End State. | PASS; local judgment occurred and existing brief discipline was not silently bypassed. |
| `trivial-exempt` visual typo | Baseline produced a reasoned visual N/A in three gradeable runs; one Claude replicate was contaminated by unrelated workspace orientation. | Claude 2/2 and Codex 2/2 returned a reasoned N/A because no token, variant, state, vocabulary, or exception changed. | PASS; the visual lens did not over-fire into design regeneration. |
| `misleading-upstream` architecture claim | Baseline hosts already challenged the unsupported `complexity: none` statement using general planning judgment. | Claude 2/2 and Codex 2/2 ignored the unsupported conclusion and independently recorded added migration/dependency cost, worth, avoidance, and risk. | PASS; optional evidence never replaced local assessment. |
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
| `business-complexity-lens` | live hard case | PASS |
| `visual-complexity-lens` | live hard case | PASS |
| `interaction-complexity-lens` | live hard case | PASS |
| `behavioral-complexity-lens` | contract test | PASS |
| `architecture-complexity-lens` | live hard case | PASS |
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
