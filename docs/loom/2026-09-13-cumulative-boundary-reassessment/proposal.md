# Cumulative boundary reassessment at Write Plan

## Executive finding

Loom should add a two-tier, change-scoped boundary-validity pass to Write Plan.
Every feature gets a short screen over the likely code, callers, tests, and
bounded history metadata. Only a concrete warning loads a bundled detailed
reference and permits targeted diff inspection. Neither tier should score
modularity, scan the whole repository, or treat length or churn as a
refactoring command.

The decision needs two kinds of evidence:

1. the requested feature introduces or extends a responsibility that is
   meaningfully different from the boundary's current responsibility; and
2. at least one observable consequence shows that the boundary no longer keeps
   change local: dependency ripple, repeated unrelated co-change, unrelated
   test setup, shared mutable state, or a broad relevant-context set.

Only when both are present should Write Plan schedule behavior
characterization and extraction before the feature task. Otherwise it should
preserve the current structure. This is a better fit for Write Plan than a new
skill because Write Plan already owns current-state investigation, task
boundaries, dependencies, and risk decisions.

## Research question

Can every new feature plan cheaply detect when a previously reasonable module
boundary has eroded through accumulated changes, while avoiding speculative
refactoring and false positives from long files, frequent edits, renames, or
formatting?

This proposal concerns planning-time reassessment of the feature's likely
change area. It does not define a repository-wide architecture audit, a
background monitor, or an automatic refactoring engine.

## What current Loom does and misses

Write Plan currently tells the agent to follow existing module boundaries when
the choice is internal to the code (`loom-code/skills/write-plan/SKILL.md:274`)
and requires each task to touch one module boundary and remain independently
executable (`loom-code/skills/write-plan/SKILL.md:404`). The implementer blocks
rather than silently crossing the planned boundary
(`loom-code/agents/implementer.md:27`). Build runs focused checks after each
task and one integration pass over the cumulative branch
(`loom-code/skills/build/SKILL.md:51`). Closing Review already evaluates
responsibilities, dependency direction, duplication, cross-task coherence, and
deletion-first alternatives
(`loom-code/skills/review/references/lenses.md:39`).

This division is sound after a boundary decision has been made. The missing
step is before task construction: Write Plan has no instruction to ask whether
the existing boundary is still valid after several earlier, individually
reasonable changes. "Follow the existing boundary" can therefore preserve
historical erosion until implementation is blocked or Closing Review sees the
whole delta.

The previous boundary experiment does not solve this. Its one-shot cases made
both baseline and candidate choose correctly, so it established no incremental
benefit for more general modularity prose
(`docs/skill-dogfood/2026-09-13-replaceable-boundary-standard/report.md:49`).
That negative result points to a different test population: sequential histories
where the first changes fit and a later feature is the point at which the
boundary ceases to keep change local.

The repository also contains a positive historical example of this evidence
shape. Six git wrappers and five sibling loaders had accumulated duplicate,
divergent behavior; the extraction plan used characterization tests and shared
helpers so a later fix would reach every site
(`docs/loom/plans/2026-08-31-loom-code-script-helper-extraction.md:1`). The
useful evidence was not line count. It was repeated copies, divergent failure
behavior, and a fix-ripple problem.

## Evidence synthesis

### Software evolution: history is a warning, not a verdict

Change history can reveal dependencies that the static file layout hides.
Research over 14 open-source projects and about 20,000 commits found that
co-changing file pairs often preceded detected architectural smells; the
authors explicitly frame co-change as a possible early symptom rather than a
complete diagnosis.[^1] This supports looking at recent co-change while a new
feature is being planned.

It does not support a universal "N commits means split" rule. Co-change can be
caused by a cohesive cross-cutting policy, generated files, mass formatting,
renames, or test updates. History must be joined to present code structure,
dependency direction, and the reason for the requested change. A bounded
history sample is therefore an observation budget, not a quality threshold.

ISO/IEC 25010:2023 supplies a lifecycle quality model intended for specifying,
measuring, and evaluating software quality.[^2] It supports treating
maintainability as an evaluable product concern, but it does not provide a
language-independent file-size or churn threshold for this Loom decision.

### AI coding: relevant context matters more than file count

Repository-level coding research consistently treats localization, dependency
analysis, and staged planning as core problems. CodePlan plans chains of edits
using repository context, previous changes, incremental dependency analysis,
and change-impact analysis; in its evaluated multi-file tasks it passed
validity checks for five of seven repositories while its stated baselines
passed none.[^3] RepoCoder found repository information scattered across files
and improved over an in-file completion baseline by more than 10% in its code
completion settings.[^4] LocAgent likewise reports gains from a lightweight
graph of code structure and dependencies for code localization.[^5]

These results do not prove that splitting a long file improves a Loom agent.
They support a narrower inference: planning should identify the smallest
dependency-complete context for the requested change. A new file that still
shares state, callers, and tests has not reduced that context.

General long-context research also shows that merely fitting information in a
context window does not guarantee robust use of it; performance can vary with
where relevant information appears.[^6] Because that study is not a coding
agent benchmark, it is supporting evidence for context locality, not a basis
for any line or token limit.

SWE-agent further shows that the interface offered to a coding agent affects
repository navigation, editing, and test execution.[^7] For Loom, that argues
for a concrete inspection procedure and evidence carrier rather than a broad
instruction to "be modular."

## Proposed mechanism

### Ownership across the existing flow

| Stage | Responsibility | New mechanism? |
|---|---|---|
| Write Plan | Always run the fast screen; load the bundled detailed reference only on a concrete warning; encode any decision in existing evidence, task, and Risk fields | Small entrypoint plus conditional reference |
| Build / implementer | Follow the plan and retain its existing block-on-boundary-crossing contract | No change |
| Closing Review | Verify that the planned boundary still holds across the cumulative branch using existing architecture, refactoring, cross-task-coherence, and deletion-first lenses | No new lens |

There should be no new user question. Boundary placement remains an internal
engineering decision. There should also be no new skill, score, persistent
debt ledger, checker rule, or mandatory artifact in the first version.

### Bounded inspection protocol

Run the following after Write Plan has identified the likely implementation
surface but before it constructs the task DAG.

**Phase A — always-run fast screen**

1. **Name the current boundary.** State its present responsibility, likely
   changed symbols/files, direct callers or consumers, state owner, and focused
   tests. If that set cannot be named, gather more current-state evidence before
   making a structural decision.
2. **Sample metadata, not patches.** Inspect at most the latest 20 unique
   commits across the whole likely target set, including names, subjects,
   rename information, and changed-path summaries. Twenty is a collection
   ceiling, never a refactoring threshold. Do not read raw diffs in this phase.
3. **Check present locality.** Trace whether the requested feature can be
   understood, modified, and tested with the named local set. Record concrete
   dependency ripple, shared state, unrelated fixtures, or unrelated regions
   that must be read or changed.

Stop here and preserve the current boundary unless the metadata suggests a
distinct reason to change, or the present locality check exposes dependency,
state, test, or relevant-context ripple.

**Phase B — conditional detailed reference**

4. **Classify the warning.** Load the bundled reference. Exclude renames,
   formatting, generated updates, dependency bumps, and mass edits. If the
   warning depends on patch content, inspect no more than three target-only
   diffs selected from the bounded commit set.
5. **Apply the causal rule.** Extract only when responsibility divergence and a
   locality consequence are both supported. If evidence is missing or noisy,
   preserve the boundary.
6. **Carry the decision in the existing plan.** Put the relevant evidence and
   the preserve/extract reason in Current State Evidence and the affected
   task's Risk line. If extraction is required, plan characterization and
   behavior-preserving extraction before the feature task.

The protocol may suggest commands such as `git log --follow -- <path>`,
`git show --name-only <commit>`, symbol search, caller search, and focused-test
discovery. It should not require a language parser or trust a numeric result as
a verdict.

### Runtime and context budget

Local measurements over three representative repository paths show why the
two tiers matter. A 20-entry metadata summary was only 155–2,323 bytes and the
Git commands took roughly 18–318 ms. Reading all 20 patches ranged from 24,868
to 645,417 bytes—roughly 6,000 to 161,000 tokens at a conservative four
bytes per token—while three target-only diffs were 12,946–27,651 bytes.

The expected agent cost is therefore dominated by reading and reasoning, not
Git execution:

| Path | Expected added time | Expected added context |
|---|---:|---:|
| Fast screen, no warning | 20–60 seconds | 500–1,500 tokens |
| Conditional detailed check | 1–3 minutes | 3,000–8,000 tokens |
| Rejected full-patch approach | 3–10+ minutes | 6,000–161,000 tokens |

The entrypoint should target 60–90 net words and the bundled reference
250–400 words. With a 70-word entrypoint and 300-word reference, conditional
loading uses fewer contract words on average than a 150-word inline rule only
when fewer than about 27% of plans load the reference; at 400 reference words,
the break-even rate is 20%. The evaluation must therefore measure reference
load rate instead of assuming that file separation saves context.

### Decision rule

| Current evidence | Historical evidence | Decision |
|---|---|---|
| Feature fits the same responsibility and remains locally testable | Any amount of cohesive churn | Preserve |
| Distinct responsibility appears, but no dependency/test/context consequence is shown | Noisy or ambiguous co-change | Preserve; record uncertainty only if it affects delivery risk |
| Locality is broad, but the feature does not introduce or extend a distinct responsibility | Large cohesive policy or shared infrastructure | Preserve; consider task decomposition, not module extraction |
| Distinct responsibility plus dependency, state, test, co-change, or relevant-context ripple | Repeated purpose-divergent changes strengthen the causal account | Characterize, extract, then implement the feature |
| Files were already split, but shared state and repeated co-change remain | Physical separation did not reduce the relevant set | Do not add another file split; plan the smallest correction that restores ownership |

This rule intentionally has no summed score. A score could let several weak
proxies overrule one strong counterexample, such as a heavily edited but
cohesive policy module.

### Definition of "boundary has failed"

For this mechanism, a boundary has failed only when the new feature exposes a
distinct reason to change **and** at least one of these consequences is
observable:

- a change to one responsibility requires editing callers or internals owned by
  another responsibility;
- two otherwise independent concerns share mutable state or dependency
  direction that prevents isolated change;
- focused verification for the feature requires unrelated fixtures, setup, or
  assertions;
- recent purpose-divergent changes repeatedly touch the same symbol or coupled
  set, after noise is excluded;
- the agent cannot form a small dependency-complete relevant-context set
  without reading unrelated regions.

Duplication is additional direct evidence when a rule or behavior has reached
the repository's existing Rule-of-Three threshold. File length, raw token
count, number of functions, commit count, age, and churn are warnings only.

## Failure modes and controls

| Failure mode | Control |
|---|---|
| Every popular file is flagged | Require distinct responsibility plus a locality consequence; churn alone preserves |
| Rename or formatter history looks like coupling | Classify and exclude non-behavioral mass changes before deciding |
| A "module" is only another file | Require smaller state/dependency/test/relevant-context scope, not physical separation |
| The check becomes a repository audit | Start from likely feature paths and direct neighbors; cap history collection |
| The agent refactors unrelated legacy code | Extraction must be necessary for the accepted feature and be the smallest behavior-preserving prerequisite |
| Prompt cost grows without behavioral gain | Cap the entrypoint at 60–90 words, load the detailed reference only on warning, and measure its load rate |
| Implementation reveals the plan was wrong | The existing implementer contract blocks boundary crossing and returns a smaller decomposition; do not duplicate that rule |
| Review duplicates planning | Review checks the resulting cumulative branch with existing lenses; it does not repeat the history scan by default |

## Evaluation design

The evaluation must model accumulation. One-shot prompts are not an adequate
population because the previous experiment already showed that both baseline
and candidate could handle obvious static cases.

### Frozen longitudinal cases

Build small real Git repositories with identical commit histories for baseline
and candidate runs:

1. **L1 — accumulated responsibility divergence.** Changes one and two fit one
   module. Change three introduces a separate caller or state owner. The
   candidate must plan characterization and extraction before the feature; the
   baseline must demonstrably miss or mishandle that need for the experiment to
   establish incremental value.
2. **L2 — high churn, cohesive boundary.** Many behavior changes affect the
   same policy and focused tests, but ownership and dependency direction remain
   local. The candidate must preserve the boundary.
3. **L3 — shallow historical split.** Prior commits separated files while
   shared state and co-change remained. The candidate must avoid another
   physical split and choose the smallest ownership correction, if any.
4. **L4 — noisy history.** Rename, formatting, generated, or mass-update commits
   dominate the history. The candidate must not infer boundary failure from
   them.

Each repository should expose source, callers, tests, and Git history to a
fresh runner. The runners receive the same requested feature and differ only in
the frozen baseline/candidate contracts. Two blind auditors judge normalized
plans against a predeclared rubric. Contract hashes, fixture-tree hashes, exact
commands, and normalized final artifacts are committed; raw operational model
streams remain private.

### Execute, do not only propose

At least L1 and L2 should continue through a minimal real implementation in
temporary copies. This prevents a plausible plan from standing in for the
claimed outcome. The evaluation should measure:

- whether the boundary decision is correct under the blind rubric;
- the dependency-complete relevant set needed to make the feature change
  (files and named symbol regions, not a claimed universal token saving);
- changed-file and caller ripple attributable to the feature;
- whether focused tests run without unrelated setup or assertions;
- added planning cost: commands, contract words, and elapsed run time;
- detailed-reference load rate and the resulting average contract context;
- whether the existing mechanism population and session-start word count stay
  non-rising.

The candidate is admitted only if it improves L1 over baseline, has no new
false positive in L2 or L4, handles L3 without shallow splitting, and the real
implementation evidence supports a smaller or clearer dependency-complete
change surface. If it ties the baseline again, creates speculative extraction,
or costs more without an observable decision benefit, revert and keep the
negative result.

No claim about universal agent efficiency, token savings, or all repositories
is permitted from this bounded corpus.

## Implementation options

| Option | Assessment | Decision |
|---|---|---|
| Add general modularity prose to Write Plan | Already tied the baseline in one-shot dogfood; does not force cumulative evidence | Drop |
| Add a fast screen to Write Plan, conditionally load one bundled reference, and reuse existing Build/Review contracts | Stage-owned, change-scoped, context-bounded, and directly testable | **Recommended** |
| Build a deterministic history analyzer and checker rule now | Premature: rename handling, language semantics, and thresholds are not yet validated | Defer until the bounded pass proves signal |
| Create a separate modularity skill | Adds routing and a second planning owner; risks being skipped or duplicating Write Plan | Drop |

## Proposed delivery sequence

This is a planning draft, not the ratified Loom plan.

1. **W0 — freeze evidence and contracts.** Create the four longitudinal Git
   fixtures, blind rubric, exact baseline/candidate identity checks, and a
   failing admission probe before changing runtime prose.
2. **W1 — integrate the smallest contract change.** Add the causal rule and
   existing-plan carrier to a 60–90-word Write Plan screen and a conditionally
   loaded 250–400-word bundled reference. Change no Build or Review contract;
   add zero skills, gates, checker rules, or persistent artifact types.
3. **W2 — run longitudinal dogfood.** Execute matched fresh runs, blind audits,
   and minimal L1/L2 implementations. Measure the reference load rate and
   commit normalized, reproducible evidence.
4. **W3 — admit or revert.** Keep the contract only if the frozen bar is met.
   If admitted, run the ordinary package verification and one Closing Review;
   otherwise publish the negative evidence and restore the baseline contracts.

## Sources

[^1]: Sas et al., “Exploring the Relation Between Co-changes and Architectural Smells,” *SN Computer Science* (2021), https://link.springer.com/article/10.1007/s42979-020-00407-5
[^2]: ISO, “ISO/IEC 25010:2023 — Product quality model,” https://www.iso.org/standard/78176.html
[^3]: Bairi et al., “CodePlan: Repository-level Coding using LLMs and Planning,” *Proceedings of the ACM on Software Engineering* (FSE 2024), https://www.microsoft.com/en-us/research/publication/codeplan-repository-level-coding-using-llms-and-planning-2/
[^4]: Zhang et al., “RepoCoder: Repository-Level Code Completion Through Iterative Retrieval and Generation,” EMNLP 2023, https://aclanthology.org/2023.emnlp-main.151/
[^5]: Chen et al., “LocAgent: Graph-Guided LLM Agents for Code Localization,” ACL 2025, https://aclanthology.org/2025.acl-long.426/
[^6]: Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *TACL* 12 (2024), https://aclanthology.org/2024.tacl-1.9/
[^7]: Yang et al., “SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering,” NeurIPS 2024, https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html
