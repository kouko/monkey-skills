---
name: critique
description: |
  Judge a proposal before it is built, through one of two lenses. `mode: proposal` triages a list, plan, or prose recommendation into KEEP / DEFER / DROP by evidence grounding and YAGNI. `mode: complexity` weighs one specific change deletion-first: before/after lines, what it obsoletes, and whether a smaller end state exists. Use for 'critique this', 'over-engineered?', 'can this be simpler?', 'worth the lines?', 'what can we delete?', 'should we build this?', '業界證實', '可以簡化嗎'.
---

# Critique

A user-invoked gate that turns a proposal into a decision. Two lenses, one
skill; pick the mode before anything else and say which one you picked.

## Choosing the mode

| The thing in front of you | Mode |
|---|---|
| A list, plan, or P0/P1/P2 backlog | `proposal` |
| Prose advocating one recommendation through two or more supporting claims | `proposal` |
| One specific proposed change — refactor, feature on existing code, debt cleanup, named greenfield feature | `complexity` |

Three or more distinct proposals: run `proposal` first, then run `complexity`
separately on each survivor. The single-change boundary is semantic, not
document-shaped: several edits that jointly create one outcome are one change;
independent outcomes that could each ship alone are a multi-item collection.
Never average a strong item and a weak item into one verdict.

Neither mode fires on: simple Q&A or a single factual answer; explanatory
bullets with no advocated action; a trivial rename, comment, or one-line fix;
an already-written change whose diff you want smaller (use the host's
code-simplification workflow); pre-completion verification (use the host's
verification workflow). This skill judges the proposal text — it does no
primary-source research, writes no implementation, and verifies no completed
execution. Hand a survivor to those capabilities after the verdict, never
instead of it.

## Shared discipline

Both modes obey these:

- **Assertion is not evidence.** "Industry standard," "best practice," or
  "clean architecture," with no source, measurement, or documented failure
  mode behind it, carries no weight in either lens.
- **Uncertainty is stated, never invented.** Prefer real counts and real
  citations from the affected paths; otherwise give labeled estimates, name
  the assumption, and say which verdict flips if it proves false. Ask for a
  missing artifact only when it could change the choice.
- **No silent softening.** Do not convert DROP into DEFER, or a code increase
  into a bare approval, to make the answer more comfortable. The cost stays
  visible in the output.
- **The gate is yours to run.** Do not hand the triage or the three questions
  back to the user; that judgement is what this skill exists to provide.

---

## Mode: proposal

An untriaged list, plan, or prose recommendation is a draft: every item must
earn its place through evidence grounding and necessity.

```
NO MULTI-ITEM PROPOSAL SHIPS WITHOUT TRIAGE
```

Do not call every item a good idea or hide unneeded work behind priorities.
The output is a decision surface, not the original proposal annotated in
place.

### Gate function

Run these five steps in order:

1. **ENUMERATE-OR-DECOMPOSE.** Surface every concrete item.
   - **List or plan:** each numbered item, bullet, or P0/P1/P2 entry is one
     target.
   - **Prose:** extract the recommendation and each supporting claim. The main
     verb phrase is usually the recommendation; clauses introduced by
     "because," "since," "given," or "so that" are supporting claims. Split
     compound claims before judging them.

2. **GROUND.** Assign one evidence-grounding value to every item:
   - `GROUNDED` — supported by a citation, measurement, or documented failure
     mode.
   - `HEURISTIC-OK` — uncited, but its mechanism is industry-known.
   - `SPECULATIVE` — intuition or a novel claim without support.

3. **ESSENTIAL?** Assign one necessity value:
   - `ESSENTIAL` — load-bearing for the stated goal; removal breaks the
     proposal.
   - `SPECULATIVE` — future-proofing, "nice to have," or optimization for a
     hypothetical case.

4. **TRIAGE.** Map the two values through the matrix below, then apply the
   DEFER fall-through rule.

5. **PRESENT.** Show three buckets — KEEP, DEFER, DROP — with a one-line
   reason per item. Put `KEEP-WITH-CAVEAT` items in KEEP and state the caveat.
   Do not intermix the full original list with verdicts.

### The triage matrix

| Grounding | ESSENTIAL | SPECULATIVE necessity |
|---|---|---|
| **GROUNDED** | KEEP | DEFER |
| **HEURISTIC-OK** | KEEP-WITH-CAVEAT | DEFER |
| **SPECULATIVE** | KEEP-WITH-CAVEAT | DROP |

- **KEEP** — ship as-is.
- **KEEP-WITH-CAVEAT** — ship, but expose weak grounding such as "n=1,"
  "industry intuition," or "no benchmark yet."
- **DEFER** — exclude from the current proposal and record the event that
  would make it relevant.
- **DROP** — remove it; the assumption does not justify the cost.

**DEFER fall-through.** DEFER is valid only with an **articulable re-trigger
condition**: a concrete observation or event that could change the verdict. If
none exists, **fall through DEFER to DROP**. "Do it later," a lower priority,
gradual ecosystem change, or an unspecified future need is not a re-trigger.
This keeps DEFER from becoming a parking lot that disguises "ship everything."

### Judgment rules

- "Future-proofing," "in case we need it," and "nice to have" are
  `SPECULATIVE` necessity unless tied to the present goal.
- A weak source does not automatically mean DROP: an essential item may be
  KEEP-WITH-CAVEAT.
- A grounded item is not automatically necessary: GROUNDED × SPECULATIVE maps
  to DEFER and still needs a re-trigger.
- P0/P1/P2 ranks do not replace triage. A low-priority promise remains work
  unless it becomes DEFER with a re-trigger or DROP.
- Judge each claim of compound prose separately. One grounded clause lends no
  evidence to its neighbors.
- If five or more items survive without a DROP, recheck whether necessity
  judgments were too charitable; this is a diagnostic, not a quota.

### Output contract

```markdown
## KEEP
- Item — verdict inputs and why it is load-bearing.
- Item (caveat: weak grounding) — why it still survives.

## DEFER
- Item — re-trigger: <observable condition>.

## DROP
- Item — unsupported, unnecessary, or no valid re-trigger.
```

Name both the grounding and the necessity result in the reason whenever
ambiguity matters.

**Compact example.** For "rewrite auth to JWT because it is stateless, scales
better, and is the industry standard," first decompose the recommendation and
its three claims. A cited statelessness claim may be GROUNDED × ESSENTIAL →
KEEP. The rewrite may be HEURISTIC-OK × ESSENTIAL → KEEP-WITH-CAVEAT. A
scalability claim may be GROUNDED × SPECULATIVE → DEFER with "when this
workload is benchmarked" as its re-trigger. An uncited "industry standard"
claim is SPECULATIVE × SPECULATIVE → DROP. The example illustrates the
process; do not copy its verdicts when the evidence or stated goal differs.

Automatic self-triggering on the assistant's own proposed backlog is deferred.
Reconsider only after at least ten successful user-triggered audits and an
explicit user request for self-firing.

---

## Mode: complexity

Judge the smallest resulting codebase, not the smallest diff or the easiest
implementation.

**Iron law: no change ships without a named mindset and all three questions,
in order.**

### Required mindset

Before Q1:

1. List the four files under this skill's `references/` directory.
2. Read each opening section and choose the mindset relevant to the proposal.
3. **Load at least one** by reading its full file.
4. Tell the user which mindset you loaded and summarize its core principle in
   one sentence.

Do not proceed without a named mindset. The bundled references make this mode
standalone:

- [Data over abstractions](references/mindset-data-over-abstractions.md): use
  when debating a class, type, or wrapper.
- [Design is taking apart](references/mindset-design-is-taking-apart.md): use
  when concerns may be complected; default when unsure.
- [Expensive to add later](references/mindset-expensive-to-add-later.md): use
  when "we might need this later" invokes PAGNI rather than YAGNI.
- [Simplicity versus easy](references/mindset-simplicity-vs-easy.md): use when
  a familiar option may be easier but less simple.

The bundled copies track canonical versions at
`domain-teams:code-team/standards/mindset-*.md`: edits land in the canonical
standards first and the bundled copies are updated to match in the same PR.
Adding a fifth mindset is governed by that same standards directory's
`mindset-extension-standard.md`.

### Q1. What is the smallest end state that solves this?

Ask what the codebase should look like after the change, not how little work
alters today's code.

- Could fewer functions, files, types, or features satisfy the requirement?
- Could the feature be deleted or declined entirely?
- Starting fresh with only the current requirement, what would you build?

State the smallest-end-state alternative even when it differs from the
proposal. Start from the requirement rather than the current architecture:
existing abstractions are evidence about today's cost, not constraints that
automatically survive. Describe the end state concretely enough to compare —
name the surviving responsibilities and the files, functions, or interfaces
that disappear. If deletion would remove user-visible behavior, say so and
confirm whether that behavior belongs to the requirement; do not disguise a
scope cut as simplification.

Test alternatives against the same outcome. A smaller design that drops
required safety, compatibility, or observability is not equivalent.
Conversely, do not preserve incidental behavior solely because code already
implements it.

### Q2. Does the change result in less total code?

Count lines, functions, and files before and after:

| Result | Interpretation |
|---|---|
| after > before | **RESHAPE** or **REJECT** per §Verdict; **PROCEED-WITH-CAVEAT** only when the added volume is explicitly justified and costed — never a silent PROCEED |
| after = before | Net-neutral; continue to Q3 |
| after < before | Strong signal in favor |

Organization, flexibility, separation, patterns, and type safety do not
automatically justify growth. When a benefit is worth more code, quantify and
name the trade-off, such as "compile-time exhaustiveness costs about 30
lines."

Count generated code separately because its maintenance cost differs, but do
not hide hand-maintained schemas, adapters, tests, or configuration the
proposal needs. Include code the new design requires elsewhere, not just the
most flattering module. Volume is a decision aid, not a claim that every line
has identical value: security checks, explicit failure handling,
accessibility, and compatibility may justify growth. The discipline is to
expose that exchange — the benefit, its approximate added surface, and why a
smaller alternative cannot deliver it.

**Pure greenfield handling:** without a `before` baseline, substitute: *what
is the smallest code that ships this feature, and is "0 lines = decline to
build" on the table?* Q1 and Q3 still apply; preserve deletion bias in the
build decision.

### Q3. What can we delete?

Identify what the change makes obsolete:

- What exists only because of the component being replaced?
- What is the maximum safe removal bundled with this change?
- What compatibility layer, duplicate path, function, or file can disappear?

Measure end-state volume, not effort or diff neatness. An addition that
deletes more than it adds can be a win; retaining many old parts to avoid a
smaller replacement is not.

Deletion must be real and included in the proposal, not promised for an
unspecified later cleanup. Account for temporary compatibility code
explicitly: if a migration requires two paths for a bounded period, name the
removal condition and compare both the transitional and final states. A
permanent duplicate path counts against the end state even when the initial
patch is easy to review.

Look beyond direct replacement. New shared behavior may obsolete caller-side
checks, configuration switches, documentation branches, fixtures, or bespoke
adapters. Do not claim deletions without checking their consumers. When
nothing can safely disappear, write "none"; that fact is important evidence
for the verdict.

### Verdict

After Q1, Q2, and Q3, emit exactly one:

- **PROCEED** — the change reduces total code and has an adequate end-state
  justification.
- **PROCEED-WITH-CAVEAT** — net-neutral or marginally larger; name the
  trade-off and its approximate code cost.
- **RESHAPE** — it adds more than it removes; propose Q1's smallest-end-state
  alternative.
- **REJECT** — it adds code without sufficient end-state justification;
  redirect to deletion or Q1's alternative.

Choose the verdict from the whole gate, not LOC alone. A net reduction that
destroys a required property does not merit PROCEED. A modest increase can
merit PROCEED-WITH-CAVEAT when its benefit is explicit and alternatives were
tested. RESHAPE means the goal is valid but the proposed form is not; REJECT
means the addition lacks enough end-state value to pursue now.

### Rationalization check

Stop and revisit the questions when the reasoning relies on any of these:

- "Keep what exists" — status quo does not justify end-state volume.
- "We might need it" — use the PAGNI reference's high bar.
- "It is cleaner / more flexible / standard" — name the concrete benefit and
  line cost.
- "The diff is clean" — Q1 evaluates the result, not the patch.
- "We can refactor later" — later does not erase today's added complexity.

Also challenge asymmetric comparisons. Do not compare a production-ready
proposal with a toy alternative, or count the proposal's tests while omitting
equivalent tests from the alternative. Do not treat moving code to another
package or dependency as deletion without naming the transferred operational
and maintenance cost. The goal is a smaller system boundary the team must own,
not a smaller local file achieved by hiding complexity.

### Response shape

1. **Mindset** — selected reference and its principle.
2. **Q1** — smallest end state.
3. **Q2** — before/after estimates or the greenfield substitution.
4. **Q3** — concrete deletions or an explicit "none."
5. **Verdict** — one of the four terms above, including the named trade-off
   whenever code grows.

For Q2, a compact table is often enough: current, proposed, smallest
alternative, and net change for lines/functions/files. For Q3, distinguish
deletions verified from the repository from candidates that still need
consumer checks. Keep the response proportionate; the gate should sharpen a
decision, not become a design document.

### Handoffs

- No specific proposal yet → define one with `loom-design:capture-intent`
  (or `loom-code:write-plan` for code-only work) first.
- A named greenfield proposal → stay here and use the Q2 substitution above.
- Approved refactor needing safe mechanics →
  `domain-teams:code-team/protocols/refactoring.md` when available.
- Structure mandated by an external API → state the constraint; do not invent
  alternatives that cannot exist.

These are handoffs, not automatic invocations.

The end state is the metric. Bias toward deletion. Name the trade-off when
choosing to add.
