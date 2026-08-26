---
name: complexity-critique
description: |
  Evaluate one proposed change (refactor / feature / tech-debt) via a deletion-first lens: before/after LOC, what it obsoletes. Use for 'worth the lines?', 'what can we delete?', 'should we build this?'. Multi-item → proposal-critique.
---

# Complexity Critique

Apply a deletion-first gate to one specific proposed change before implementation. Judge the smallest resulting codebase, not the smallest diff or easiest implementation.

This includes a refactor, a feature added to existing code, debt cleanup, or a named greenfield feature. It excludes multi-item triage, open-ended ideation, and review of an already-written change.

## Required Mindset

Before Q1:

1. List the four files under this skill's `references/` directory.
2. Read each opening section and choose the mindset relevant to the proposal.
3. **Load at least one** by reading its full file.
4. Tell the user which mindset you loaded and summarize its core principle in one sentence.

Do not proceed without a named mindset. The bundled references make this skill standalone:

- [Data over abstractions](references/mindset-data-over-abstractions.md): use when debating a class, type, or wrapper.
- [Design is taking apart](references/mindset-design-is-taking-apart.md): use when concerns may be complected; default when unsure.
- [Expensive to add later](references/mindset-expensive-to-add-later.md): use when "we might need this later" invokes PAGNI rather than YAGNI.
- [Simplicity versus easy](references/mindset-simplicity-vs-easy.md): use when a familiar option may be easier but less simple.

The bundled copies track canonical versions at `domain-teams:code-team/standards/mindset-*.md`: edits land in the canonical standards first and the bundled copies are updated to match in the same PR. Adding a fifth mindset is governed by that same standards directory's `mindset-extension-standard.md`.

The iron law is: **no change ships without a named mindset and all three questions, in order.**

## Q1. What's the smallest end state that solves this?

Ask what the codebase should look like after the change, not how little work alters today's code.

- Could fewer functions, files, types, or features satisfy the requirement?
- Could the feature be deleted or declined entirely?
- Starting fresh with only the current requirement, what would you build?

State the smallest-end-state alternative even when it differs from the proposal.

Start from the requirement rather than the current architecture. Existing abstractions are evidence about today's cost, not constraints that automatically survive. Describe the end state concretely enough to compare: name the surviving responsibilities and the files, functions, or interfaces that disappear. If deletion would remove user-visible behavior, say so and confirm whether that behavior belongs to the requirement; do not disguise a scope cut as simplification.

Test alternatives against the same outcome. A smaller design that drops required safety, compatibility, or observability is not equivalent. Conversely, do not preserve incidental behavior solely because code already implements it. Separate required outcomes from historical implementation choices, then compare only alternatives that satisfy the required outcomes.

## Q2. Does the proposed change result in less total code?

Count lines, functions, and files before and after:

| Result | Interpretation |
|---|---|
| after > before | **RESHAPE** or **REJECT** per §Verdict; **PROCEED-WITH-CAVEAT** only when the added volume is explicitly justified and costed — never a silent PROCEED |
| after = before | Net-neutral; continue to Q3 |
| after < before | Strong signal in favor |

Organization, flexibility, separation, patterns, and type safety do not automatically justify growth. When a benefit is worth more code, quantify and name the trade-off, such as "compile-time exhaustiveness costs about 30 lines."

Use available repository evidence rather than invented precision. Prefer actual counts from the affected paths; otherwise give labeled estimates and state what remains uncertain. Count generated code separately because its maintenance cost differs, but do not hide hand-maintained schemas, adapters, tests, or configuration needed by the proposal. Include code that the new design requires elsewhere, not just the most flattering module.

Volume is a decision aid, not a claim that every line has identical value. Security checks, explicit failure handling, accessibility, and compatibility may justify growth. The discipline is to expose that exchange: identify the benefit, its approximate added surface, and why a smaller alternative cannot deliver it. "Best practice" or "clean architecture" alone is not evidence.

**Pure greenfield handling:** without a `before` baseline, substitute: *what's the smallest code that ships this feature, and is "0 lines = decline to build" on the table?* Q1 and Q3 still apply; preserve deletion bias in the build decision.

## Q3. What can we delete?

Identify what the change makes obsolete:

- What exists only because of the component being replaced?
- What is the maximum safe removal bundled with this change?
- What compatibility layer, duplicate path, function, or file can disappear?

Measure end-state volume, not effort or diff neatness. An addition that deletes more than it adds can be a win; retaining many old parts to avoid a smaller replacement is not.

Deletion must be real and included in the proposal, not promised for an unspecified later cleanup. Account for temporary compatibility code explicitly. If a migration requires two paths for a bounded period, name the removal condition and compare both the transitional and final states. A permanent duplicate path counts against the end state even when the initial patch is easy to review.

Look beyond direct replacement. New shared behavior may obsolete caller-side checks, configuration switches, documentation branches, fixtures, or bespoke adapters. Do not claim deletions without checking their consumers. When nothing can safely disappear, write "none"; that fact is important evidence for the verdict.

## Verdict

After Q1, Q2, and Q3, emit exactly one:

- **PROCEED** — the change reduces total code and has an adequate end-state justification.
- **PROCEED-WITH-CAVEAT** — it is net-neutral or marginally larger; name the trade-off and its approximate code cost.
- **RESHAPE** — it adds more than it removes; propose Q1's smallest-end-state alternative.
- **REJECT** — it adds code without sufficient end-state justification; redirect to deletion or Q1's alternative.

Never silently approve a Q2 increase. A user may choose a justified increase, but the response must make that choice and cost visible.

Choose the verdict from the whole gate, not LOC alone. A net reduction that destroys a required property does not merit PROCEED. A modest increase can merit PROCEED-WITH-CAVEAT when its benefit is explicit and alternatives were tested. RESHAPE means the goal is valid but the proposed form is not; REJECT means the addition lacks enough end-state value to pursue now.

When evidence is incomplete, make the uncertainty visible in the verdict rationale rather than fabricating counts. Ask for a missing artifact only when it can change the choice. Otherwise provide bounded estimates, identify the assumption, and show which verdict would change if the assumption proves false.

## Boundaries and Routing

This skill handles a **single change** before implementation:

- A list, plan, or prose containing three or more distinct proposals → use `proposal-critique`, then apply this skill separately to survivors.
- No specific proposal yet → use `superpowers:brainstorming` to define one first.
- A named greenfield proposal → stay here and use the Q2 substitution above; brainstorming is not mandatory.
- Already implemented and asking whether the diff can shrink → use Anthropic `simplify`.
- Approved refactor needing safe mechanics → use `domain-teams:code-team/protocols/refactoring.md` when available.
- Trivial rename, comment, or one-line fix → skip this gate.
- Structure mandated by an external API → state the constraint; do not invent alternatives that cannot exist.

These are handoffs, not automatic invocations.

The single-change boundary is semantic, not merely document-shaped. A proposal may mention several edits that jointly create one outcome; analyze them together when their costs and deletions are inseparable. Split independent outcomes, each of which could ship alone, and send a multi-item collection through `proposal-critique`. Do not average a strong item and a weak item into one verdict.

For greenfield work, stay in this skill once the feature is specific enough to evaluate. The absence of existing code removes the before/after comparison, not the need to challenge whether the feature should exist or how little must be built. Route to brainstorming only when the desired outcome itself is unresolved.

## Rationalization Check

Stop and revisit the questions when the reasoning relies on any of these:

- "Keep what exists" — status quo does not justify end-state volume.
- "We might need it" — use the PAGNI reference's high bar.
- "It is cleaner / more flexible / standard" — name the concrete benefit and line cost.
- "The diff is clean" — Q1 evaluates the result, not the patch.
- "We can refactor later" — later does not erase today's added complexity.

Also challenge asymmetric comparisons. Do not compare a production-ready proposal with a toy alternative, or count the proposal's tests while omitting equivalent tests from the alternative. Do not treat moving code to another package or dependency as deletion without naming the transferred operational and maintenance cost. The goal is a smaller system boundary the team must own, not a smaller local file achieved by hiding complexity.

## Response Shape

Keep the critique auditable:

1. **Mindset** — selected reference and its principle.
2. **Q1** — smallest end state.
3. **Q2** — before/after estimates or the greenfield substitution.
4. **Q3** — concrete deletions or an explicit "none."
5. **Verdict** — one of the four terms above, including the named trade-off whenever code grows.

For Q2, a compact table is often enough: current, proposed, smallest alternative, and net change for lines/functions/files. For Q3, distinguish deletions verified from the repository from candidates that still need consumer checks. Keep the response proportionate; the gate should sharpen a decision, not become a design document.

The end state is the metric. Bias toward deletion. Name the trade-off when choosing to add.
