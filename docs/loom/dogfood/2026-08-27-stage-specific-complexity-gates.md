# Stage-specific complexity gates — behavioral evidence

Date: 2026-08-27

## Evidence binding

The immutable pre-edit snapshot at `/tmp/loom-complexity-baseline.xt9viD` was
captured before lens edits and checked against base commit `0a7dcde2`. It was
used only to build isolated baseline plugin roots; the durable identities below
bind the compared trees without making CI depend on that machine-local
directory.

- loom-design baseline SHA-256: `084299e0537bee45a2f2c559472d6a6e4651ce814bebb2755b70daca1a1afe3c`
- loom-code baseline SHA-256: `73c552397959a13770d61769189e2945a6dba7aff74f46774a44b5fd6c3126f5`
- loom-design candidate SHA-256: `9a08a1d477601562a7ba5cd7e744b341820a08e138f8766e0e91fa3d19ca5c20`
- loom-code candidate SHA-256: `d6fa77b78afd9757588edc0875d1867515cd1be2baa6447436e5b962df29b9d3`

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
