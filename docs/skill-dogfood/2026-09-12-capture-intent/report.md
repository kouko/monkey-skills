# Dogfood report — `capture-intent`

## Metadata

| Field | Value |
|---|---|
| Skill path | `loom-design/skills/capture-intent/` |
| Skill version | `1.0.0` |
| Date | `2026-09-12` |
| Passes run | activation · executor+auditor · cold-reader |
| Model pinned | Claude Sonnet 5 via Claude Code 2.1.268 |
| Activation fidelity | real-harness sandbox |

## Probe matrix

- Should fire: a new product idea, a newly reported recurring bug, or an engineering change with no intent.
- Should not fire: refining an existing confirmed intent, writing a spec, writing a plan, implementing a plan, reviewing a completed change, or maintaining an incident already routed to an intent.
- Workflow bar: use existing context first; ask only missing intent-field content; keep Acceptance outcome-level; require explicit answers for material outcome/scope forks; run one altitude pass; never invent IDs, spec behaviour, plan method, or a review loop.
- Highest-risk untested axis: multi-turn product ambiguity. Prediction: an executor may either over-question after fields are sufficient or silently promote a plausible visible behaviour instead of keeping the intent open.

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 0 |
| **Total** | 4 |

## Findings

### Activation probe — reduced first pass

The reduced pass ran each of 26 prompts once before spending quota on
repetition. All six negative controls routed to their expected neighboring
skill. Of the twenty prompts originally labelled positive, fifteen explicitly
loaded `capture-intent`, two loaded `maintain`, and three asked intake questions
without loading any skill.

The two `maintain` routes (`t02`, `t12`) are not reliable evidence of a skill
defect: both prompts describe recurring incidents, and the repository contract
assigns incident intake to `maintain`. They expose a corpus-labelling defect and
will be treated as negative controls in the corrected score.

With that correction, strict explicit routing is 23/26 overall (88.5%):

- true positive: 15/18 (83.3%);
- true negative: 8/8 (100%);
- false positive: 0/8 (0%);
- three behaviorally plausible but implicit intake responses (`t06`, `t14`,
  `t20`) did not load `capture-intent` and therefore remain trigger misses.

The three misses are materially different. `t14` first asks for the missing
rough request and is a reasonable precondition check. `t06` asks two broad
questions with multiple suggested branches, and `t20` asks three intent fields
at once; those two bypass the candidate skill's narrow, one-material-gap
interview behavior. Repetition should target these three misses plus selected
boundary controls rather than all 26 prompts.

Follow-up changed that interpretation. Across three total runs, `t06` loaded
`capture-intent` once and bypassed it twice. In one bypass it also claimed that
the Loom skill was external and could be executed but not modified. This is a
**high-severity activation defect** because an actionable but underspecified
change request can miss the station that owns clarification, and the fallback
can give a false capability boundary.

By contrast, `t14` and `t20` never supplied an actual change to capture. Their
three non-activations each are reasonable precondition handling, not reliable
false negatives. Together with the recurring-incident cases `t02` and `t12`,
this is a **medium-severity corpus defect**: four of twenty original positive
labels did not match the repository's routing contract or lacked the minimum
object needed to start an intent.

### Executor and blind auditors

The executor correctly used supplied context, asked one material channel
question, kept Acceptance outcome-level, preserved in-app notifications, kept
unmute out of scope, and invented no UI, persistence, errors, state machine,
files, IDs, or implementation. It also did not consume the simulated future
publication opt-out prematurely.

The literal cold-repository setup then forced the product-principles prerequisite
before the combined intent confirmation. The executor stopped honestly with an
open artifact. This created a **medium-severity scenario-coverage defect**: the
probe did not reach the confirmation or publication branch it was intended to
test, so those candidate behaviors remain unverified.

Two blind auditors split 1–1. One marked FAIL because it treated the principles
interview as an unrelated second pass; the other marked PASS because it treated
the missing principles as a legitimate prerequisite blocker. This is a
**medium-severity contract-observability defect** for this evidence package:
without the hidden workflow contract, the output does not make the relationship
between the prerequisite and the promised single decision point unambiguous.
Adding a third vote would hide the ambiguity rather than resolve it.

### Cold-reader audit

The cold reader found the core field interview executable, but identified
several under-specified operational terms and boundaries: installed-plugin path
discovery, the mapping of “small lane” to declared lane values, version ordering
for “newest,” incident routing versus direct capture, the undefined threshold
for a weak product-value answer, and second-vendor wording that can conflict
with the host rule. Most predate this candidate and are not counted again as
new functional findings, but they prevent a clean whole-skill self-contained
PASS.

## Verdict

**FAIL — do not claim the candidate is fully dogfooded yet.** The candidate's
field-level behavior was strong in the executor probe and negative routing had
no false positives, but activation remains unstable on one realistic vague
change request. The end-to-end scenario also failed to exercise confirmation
and publication because its cold-repository prerequisite intercepted the flow.

### Post-fix verification

After adding station-local vocabulary boundaries and expanding the
`capture-intent` discovery description, the targeted follow-up still failed its
predeclared bar:

- `t06` explicitly loaded `capture-intent` in 0/3 runs; all three responses
  bypassed the skill and directly opened a broad clarification interview.
- The context-free negative control (`幫我想想。`) did not load a skill and
  correctly asked for a subject.
- The full-flow simulation loaded `capture-intent`, resolved the notification
  channel, kept the intent outcome-level, honored the automatic-PR opt-out, and
  handed the product change to `write-spec`.
- That simulation nevertheless invented a “mute switch” in the `needs-design`
  reason even though no UI control had been authorized. This violates the
  probe's explicit no-UI-invention condition.

The post-fix result confirms that discovery prose alone does not reliably
control automatic routing for a vague change whose object is only “this
process.” Stop prompt tuning here. The local decision-boundary prose may still
help after a skill is loaded, but it has not earned an activation-success claim.
Do not proceed to closing Review on this evidence.

### Station-boundary A/B

A final targeted A/B removed routing from the experiment: Claude explicitly
loaded each station once against the same synthetic input, using the pre-change
skill at `4e7c359ce` and the candidate skill with its local decision-boundary
section. The comparison found no demonstrated boundary improvement:

- **capture-intent — baseline FAIL, candidate FAIL.** Both invented a
  notification-settings surface in `needs-design`, and both expanded the
  supplied boundary into a guarantee that other projects remain unaffected.
- **write-spec — baseline FAIL, candidate FAIL.** The baseline converted
  “unmute is out of scope” into a requirement that the system provide no
  unmute path. The candidate converted it into “no reverse flow exists.” Both
  promoted an exclusion from this change into affirmative product behaviour.
- **write-plan — baseline PASS, candidate PASS.** Neither added product
  behaviour. The candidate was more explicit about unavailable repository
  evidence, but one run cannot attribute that difference to the vocabulary
  section.

The A/B therefore does not support shipping the added prose as an effective
anti-expansion mechanism. Its definitions are conceptually accurate, but the
observed outputs did not improve and the added prompt cost is not earned by
this evidence. Further wording iteration is outside the stopping rule for this
experiment.

### Claim-admission follow-up

A reduced follow-up reused the same three station fixtures and the prior
baseline outputs. The candidate added one internal author pass only: admit a
new product claim when the upstream artifact directly supports it or when the
station is authorized to make that necessary transformation; otherwise ask,
neutralize, or delete it. It also stated that an exclusion is not an affirmative
product prohibition. The pass prohibited persistent provenance labels, new
IDs, checker output, and additional review steps.

Three fresh Claude Code runs completed successfully. Two blind reviewers, given
only the fixtures, A/B outputs, and a fixed authorization rubric, independently
reached the same station-level result:

| Station | Baseline | Claim-admission candidate | Observed change |
|---|---|---|---|
| `capture-intent` | FAIL | FAIL | Candidate stopped claiming that unmute is absent or one-way, but still invented a notification-settings surface, a distinct muted-email state, a single-project-at-a-time constraint, and guarantees for other projects. |
| `write-spec` | FAIL | PASS | Candidate did not turn “unmute is out of scope” into a requirement that no unmute path exist. It added no UI placement, persistence, or error presentation. |
| `write-plan` | FAIL | FAIL | Candidate still promoted unverified implementation assumptions into current-state facts, including an existing per-project mute state and an existing action that already writes it. |

This is a real but local improvement, not a chain-wide pass. The evidence
supports retaining the narrow semantic rule that an exclusion cannot become a
negative product requirement. It does not yet support shipping the generic
two-way “upstream-supported or station-authorized” test: “station-authorized”
left too much room for the author to label invented state and implementation
facts as necessary transformations.

The next candidate, if tested, should replace that broad branch with explicit
station-local allowed transformations rather than adding identifiers or another
review loop:

- `capture-intent`: compress and restate only; no new product nouns, states,
  surfaces, guarantees, or scope dimensions;
- `write-spec`: decompose confirmed outcomes into observable conditions and
  scenarios; an exclusion remains a non-goal, never a negative requirement;
- `write-plan`: select implementation only from repository evidence; an
  unverified current-state claim is a gap to inspect, not an assumption to
  write into the plan.

Verdict: **PARTIAL — positive effect demonstrated at `write-spec`, but do not
implement the generic candidate across all three stations yet.**

### Cross-model follow-up — Codex executor

A second reduced A/B used fresh Codex executors on the same fixtures. Each
station produced one pre-rule baseline and one claim-admission candidate;
station order was alternated to reduce a uniform first-output bias. Two new
blind Codex reviewers received only the fixture, outputs, and authorization
rubric. Neither received the candidate rule or this report.

Both reviewers agreed on the material result:

| Station | Baseline | Claim-admission candidate | Codex observation |
|---|---|---|---|
| `capture-intent` | FAIL | FAIL | Candidate correctly changed “unmute is not supported” to “this change does not cover unmuting” and removed several invented behavior details. Both variants still placed automatic-PR opt-out under product `Constraints`, confusing workflow authorization with product intent. |
| `write-spec` | FAIL | PASS | Baseline invented a no-unmute requirement, persistent muted state, and missing UI action. Candidate retained only the three confirmed outcomes and did not add UI, persistence, errors, or implementation. |
| `write-plan` | FAIL | FAIL | Both variants asserted unsupported existing file/test-file names and introduced test labels despite the fixture providing only component and dispatch-path existence. Candidate wording was slightly more conservative but did not solve evidence admission. |

This cross-model check strengthens one conclusion: the exclusion rule is not a
Claude-only accident. Both Claude and Codex changed `write-spec` from FAIL to
PASS when told that out-of-scope is not an absent, forbidden, or one-way product
capability. It also strengthens the stopping condition: a generic claim rule is
not enough for `capture-intent` metadata separation or `write-plan` repository
evidence. Those need narrow station-local rules, not another generic wording
iteration.

Cross-model verdict: **PARTIAL on both executors. Implement only after the
candidate is split into station-specific allowed transformations and the same
fixtures are rerun.**

### Minimal station-rule probe

A final small Codex probe tested the reshaped proposal only at
`capture-intent` and `write-spec`; routing, `write-plan`, external runners,
new IDs, and new checker behavior were excluded. The baseline was reused. One
fresh executor produced each candidate artifact and two blind reviewers judged
only the fixture and raw outputs.

Both reviewers returned FAIL:

- `capture-intent` correctly kept publication opt-out outside the product
  fields and described unmute only as excluded from this change. It then wrote
  `needs-design: no` because no surface or multi-object behavior was established
  and handed the product change directly to `write-plan`. Avoiding an invented
  surface therefore suppressed the necessary behavior-specification boundary.
- `write-spec` correctly avoided an unmute prohibition, UI placement,
  persistence mechanism, and error behavior. It nevertheless used `WHILE a
  project is muted`, promoting the user action into a persistent named state,
  and combined two Acceptance owners under one trace suffix. One reviewer also
  flagged the `Project notifications` UI-flow label as a surface name not
  supplied by the fixture.

This exposes a missing distinction in the proposed rule: an author must be able
to state an ongoing observable result without inventing its internal state or
persistence mechanism. It also must not interpret “surface not yet chosen” as
“no behavior specification required.” A product action with visible effects may
require `write-spec` precisely because its surface is still undecided.

Verdict: **FAIL — the reduced proposal is smaller, but not ready to implement.
Its capture rule needs a surface-unknown routing clause, and its spec rule needs
surface-neutral temporal wording plus exact Acceptance ownership.**

### Integrated minimal station-rule probe v3

The prior probe used independently authored capture and spec fixtures, which
made its Acceptance-number failure partly a harness defect: capture emitted
four Acceptance lines while the spec executor was preloaded with a different
three-line input. The corrected probe executed the chain in order. The exact
capture artifact, including its three Acceptance lines, became the sole product
input to the fresh spec executor.

The candidate added only the missing narrow clauses:

- an unknown surface does not mean design is unnecessary; a user-invoked
  product action with visible effects and no existing spec routes to
  `write-spec` with a surface-neutral reason;
- workflow authorization stays out of product fields but must still be
  preserved in its existing frontmatter or handoff representation;
- a continuing observable result may use temporal language, but may not invent
  a named state, lifecycle, storage, or persistence mechanism;
- spec Requirements preserve the exact upstream Acceptance count, order, and
  owner number.

Two fresh blind reviewers independently returned:

| Artifact | Reviewer 1 | Reviewer 2 | Evidence |
|---|---|---|---|
| `capture-intent` | PASS | PASS | Product claims stayed inside the supplied scope; `needs-design: yes` used only visible effects plus missing spec; publication opt-out remained outside product fields and was preserved in the handoff. |
| `write-spec` | PASS | PASS | Three Requirements mapped one-to-one to Acceptance #1–#3; temporal email suppression introduced no named state or persistence; UI flow stayed `N/A` because no surface was authorized; unmute remained excluded rather than prohibited. |
| integrated chain | PASS | PASS | No semantic claim was added, dropped, renumbered, or promoted across the station boundary. |

Both reviewers noted only non-blocking caveats: decision point ② was correctly
shown as awaiting the user's spec confirmation, and the handoff's historical
publication question could be phrased more compactly after an opt-out.

Verdict: **CONCEPT PASS — this one-case Codex probe is sufficient to plan the
small station-local edit, but not to claim broad behavioral or cross-model
validation. Formal dogfood still needs at least a second semantic shape and a
Claude executor after implementation.**

## Raw outputs appendix

The `raw/` streams below are local to the authoring environment and deliberately
not committed; these paths name the local run, not repository content.

### A. Activation runs

Raw stream JSONL files and the machine-readable summary are under `raw/`:

- `activation-summary.json`
- `activation-<case>-run1.jsonl` for all 26 cases

Observed list-price telemetry reported by the harness was approximately
USD 3.03, 1,029,170 input-plus-cache tokens, and 6,327 output tokens. This is
provider telemetry, not an invoice; subscription charging may differ.

### B. Cold-reader audit

Completed. The audit found the field interview mostly executable and the
operational ambiguities summarized above. The complete agent response remains
available in the originating dogfood task transcript; it was not used as a
blind workflow verdict.

### C. Executor artifacts

See `raw/executor-output.md`. The executor produced an open draft and correctly
refused to fabricate a confirmed artifact after hitting the missing-principles
prerequisite.

### D. Executor trajectory

Captured in `raw/executor-output.md`, including the exact stopping point and
the behaviors deliberately not invented.

### E. Auditor judgment

The two independent blind outputs are:

- `raw/blind-auditor-1.txt` — FAIL, one high finding about a second interview
  replacing the intent confirmation;
- `raw/blind-auditor-2.txt` — PASS, treating that interview as a legitimate
  prerequisite blocker.

Their full stream transcripts are preserved as `raw/blind-auditor-1.jsonl`
and `raw/blind-auditor-2.jsonl`.

### F. Post-fix runs

The machine-readable summary is `raw/postfix-summary.json`. Each of the five
runs is preserved as `raw/postfix-*.jsonl`, with extracted final text in the
matching `raw/postfix-*.txt` file.

### G. Station-boundary A/B

The six explicit-invocation runs are under `raw/station-boundary-ab/`:

- `summary.json` — routes, return codes, extracted outputs, and provider cost;
- `baseline-<station>.txt` and `candidate-<station>.txt` — readable outputs;
- matching `.jsonl` files — raw Claude Code streams.

### H. Claim-admission follow-up

The three candidate runs are under `raw/claim-admission/`:

- `summary.json` — routes, return codes, outputs, and provider telemetry;
- `candidate-<station>.txt` — readable station outputs;
- matching `.jsonl` files — raw Claude Code streams.

All three runs returned zero and explicitly loaded the intended station. Their
reported list-price telemetry totals approximately USD 0.64. This is provider
telemetry, not an invoice; subscription charging may differ. The baseline was
reused from section G, so this follow-up did not spend quota regenerating it.

### I. Codex executor A/B

The six Codex executor artifacts are under `raw/claim-admission-codex/`:

- `capture-ab.md` — baseline and candidate intent artifacts;
- `spec-ab.md` — candidate and baseline product-behaviour specs;
- `plan-ab.md` — baseline and candidate plans.

The two blind reviews agreed on all station pass/fail outcomes. One reviewer
described the candidate capture result as admissible apart from the shared
publication-classification defect; under the predeclared strict rubric, that
defect keeps the station at FAIL. No external provider-cost telemetry applies
to these Codex subagent runs.

### J. Minimal station-rule probe

The two raw candidates are under `raw/minimal-station-rules/`:

- `candidate-capture.md`;
- `candidate-spec.md`.

No external provider cost applies. The two independent reviews agreed on the
intent-to-spec bypass and unauthorized persistent-state wording.

### K. Integrated minimal station-rule probe v3

The corrected sequential artifacts are under
`raw/integrated-station-rules-v3/`:

- `capture.md` — first-stage output and publication-preserving handoff;
- `spec.md` — generated from that exact capture Acceptance list.

Two independent blind reviews returned PASS/PASS for both artifacts and the
integrated boundary. No external provider cost applies.

### L. Post-implementation dual-host chain — `354ca9207`

After the final functional digest, fresh Codex and sandbox-outside Claude Code
each read only `capture-intent/SKILL.md`, `capture-intent/references/interview.md`,
and `write-spec/SKILL.md`. Each executor ran the same confirmed GUI and CLI
fixtures through capture-intent and then write-spec in memory. The capture
artifact was the sole product input to its spec. Neither run inspected this
report or an earlier output.

| Executor | Fixture | Acceptance mapping | Unauthorised state or mechanism | Out-of-scope promotion | Result |
|---|---|---:|---|---|---|
| Codex `gpt-5.6-sol`, ephemeral/read-only, session `01a095d3-ba2a-7ac1-85b0-de7a3e42851b` | GUI project-email mute | 3 → 3, ordered | none | none | PASS |
| Codex `gpt-5.6-sol`, same session | CLI `sync --dry-run` | 3 → 3, ordered | none | none | PASS |
| Claude Code, sandbox-outside runner | GUI project-email mute | 3 → 3, ordered | none | none | PASS |
| Claude Code, same run | CLI `sync --dry-run` | 3 → 3, ordered | none | none | PASS |

The GUI outputs retained the supplied Settings-page control without inventing
its type, label, status display, storage, lifecycle, or a named muted state.
The continuing result stayed attached to the original mute action. Unmuting
and mobile UI remained not designed or implemented in this change, not absent,
prohibited, irreversible, or one-way.

The CLI outputs retained `sync --dry-run`, stdout, the existing human-readable
format, and the no-file-modification result. They introduced no preview state,
transaction, rollback, temporary copy, exit code, output ordering, or broader
side-effect guarantee. Applying changes, JSON output, and another output format
remained outside this change rather than prohibited.

Both executors put unsupplied GUI/error/empty reactions in Open questions or
marked them N/A instead of inventing visible behaviour. Publication opt-out
remained workflow context and did not enter the product fields. This closes the
earlier concept-only limitation at line 299: the result above exercises the
post-implementation skill text on both hosts and both semantic shapes.
