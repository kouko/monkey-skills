# Brief — docs-review 0.49.0 adjudicated defect fixes

Date: 2026-08-04
Branch: `fix-docs-review-0490-adjudicated-defects` (from `f61837ed` == origin/main)
Origin: two-stage independent review this session — one blind adversarial reviewer
(fresh context, no defect list) + one claim adjudicator (given both prior reviews'
divergent claims). User authorized the fix batch and the direction
("retract-claim over add-mechanism for the two carrier gaps") after a
complexity assessment.

## Problem

The shipped 0.49.0 docs-review convergence mechanism contains sentences that
state the opposite of what the code does, or promise mechanisms that do not
exist. A reader or executor acting on those sentences silently breaks the
convergence guarantees the mechanism shipped to provide: the authorized
verification round cannot receive the findings it exists to verify, the
oscillation stop can never fire, a self-resolved sha can silently narrow the
next round's review range, and "recorded" deferrals evaporate. The defect
class is the arc's own recurring shape: a claim with no carrier, or a claim
contradicting a neighbour — this time surviving into the shipped release.

## Users

- Future orchestrators (any model tier, including weak ones) executing
  `requesting-docs-review/SKILL.md` literally.
- Dispatched `docs-reviewer` panel arms executing `agents/docs-reviewer.md`
  literally ("treat unspecified sections as empty").
- Future sessions and research reading the origin ledger or the backlog and
  trusting their self-descriptions.

## Smallest End State

Ten fixes, five defects + five improvements, grouped so each claim's every
copy is edited together. NO new persistence mechanism anywhere (user
decision): where prose promises a carrier that does not exist, the prose is
retracted to what is true, and the mechanism idea goes to
`docs/loom/backlog/` as an entry.

### D1 — prior-findings carrier generalized to every round after round 1 (was: "round 2 only")

The blind review's top defect. `resurfaced` means "reappeared after being
fix-verified"; fix-verification first happens at round 2; therefore
`resurfaced` is unreachable at round 2 — the only round whose packet may
carry `prior_findings_check`. Directive 3's trigger and its carrier never
coexist. Fix: every "round 2 only / omit on round 1" label on the
prior-findings carrier becomes "every round after round 1"; the round-2
handoff rule becomes a round-N handoff (round N's packet carries round
N-1's surviving findings verbatim); Directive 1 option (a)'s authorized
verification round explicitly receives the surviving findings it verifies.
Sites (verify at edit time; line numbers drift): SKILL.md §Directive 2
round-2 handoff sentence, SKILL.md verdict-schema comment
(`# round 2 only; omit on round 1`), docs-reviewer.md input-contract
section `### Prior-round findings (round 2 only)`, docs-reviewer.md output
template comment. Run `claim_copy_sweep.py --claim "round 2 only"` and
partition before editing.

### D2 — the ledger-recording contract told three ways; fix both lying sides

Code truth (`loom_gate_markers.py` `_record_origin_ledger_round` called
before the exit-3/4 early returns): the ledger is written on EVERY
`review-pass` INVOCATION — not on every mint, and not on every review round
(exit-4 fix/rerun retries append again; mixed-branch docs rounds never
invoke the CLI at all).
- Fix SKILL.md §Directive 2 "it holds only the last **minted** round" →
  state invocation semantics correctly (an entry can still be stale for a
  different reason: rounds that never invoke the CLI append nothing).
- Fix the script docstring's purpose clause "so the sample of recorded
  findings is never biased by which rounds happened to pass" → state it as
  a capability conditional on invocation, and name the shipped reality:
  nothing obliges invoking `review-pass` on a round already known
  NEEDS_REVISION, so the recorded sample IS invocation-skewed (the branch
  measured in `docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`
  had 2 ledger rows against more review rounds than that).
- Fix that same backlog entry's "records mint attempts" wording to
  invocation semantics (same misreading, third copy).

### D3 — retract "round accounting continues, it does not reset"

SKILL.md §Already-reviewed-branch bullet asserts cross-session round
continuity that nothing carries (the ledger `round` field is an invocation
counter, not a review-round counter, and no step tells a resuming
orchestrator to read anything). Retract to the truth: round accounting is
session-scoped; across a session boundary the count restarts and the
2-round cap guards each session independently, which is weaker than it
sounds — state that plainly. Extend the existing backlog entry
(`2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`) to
cover round-count resume alongside sha resume (same carrier gap, same
future mechanism), rather than opening a duplicate entry.

### D4 — reviewed_sha fallback goes fail-closed; input template gets the field

docs-reviewer.md output contract currently says: take the sha from the
dispatch packet; "if the packet did not state one, resolve it yourself."
Self-resolving fails in exactly the direction SKILL.md §Directive 2
forbids ("never a guessed range" / a wrong range "suppresses findings…
leaves nothing behind to notice"): a late-resolved sha becomes the left
endpoint of the next round's range and silently excludes commits. Fix:
replace the fallback with fail-closed — report `reviewed_sha: unresolved`;
the consuming rule in SKILL.md already maps "no prior reviewed_sha" to an
unbounded next round. Also add the missing `HEAD sha` slot to
docs-reviewer.md's input-contract template (SKILL.md Step 3 requires the
packet to state it; the template has no field — the blind review's
improvement 1), which removes the fallback's trigger.

### D5 — retract "deferred on the record" for out_of_scope

`out_of_scope:` entries carry no `severity:` so they can never match the
ledger's finding regex; nothing re-injects them into round N+1; the verdict
text goes to a temp file. "On the record" = said once in chat. Fix SKILL.md
§out_of_scope sentence and docs-reviewer.md's "recorded so it is not lost"
to the truth: surfaced to the user with the verdict, persisted nowhere —
deferral survives only if the user or orchestrator acts on it. Keep
docs-reviewer.md's completeness counter-instruction. New backlog entry
proposing the mechanism (a severity-less ledger block type; the
every-invocation append pipeline already exists) so the retract is not the
end of the story.

### I1 — panel union: recompute dimension_scores from the union

Both copies of the aggregation parenthetical ("per-dimension score = the
worse of the two arms' scores") allow verdict/dimension_scores
contradiction (two different 🟡 instruction findings in the same dimension
from different arms → union verdict NEEDS_REVISION while worse-of-arms says
PASS_WITH_NOTES). Fix in requesting-docs-review/SKILL.md Step 4 AND
requesting-code-review/SKILL.md (the source copy): re-run the aggregation
rule on the union for dimension scores too.

### I2 — restatement in prior_findings_check must not be ledger-parseable

The round-N template asks findings to be restated "verbatim"; a verbatim
`- severity:` block nested under `finding:` matches `_FINDING_RE` at any
indent and lands in the origin ledger a second time as a later-round
finding, contaminating the population partition the ledger exists to keep
clean. Fix the template wording in SKILL.md + docs-reviewer.md: restate as
a one-line scalar (`finding: <one-line summary>`), never the original
`- severity:` block. Interacts with D1 (same template block — edit once,
correctly).

### I3 — delete or source the two unsourced figures

SKILL.md's delta-scope rationale sentence carries "round 1's fixes were a
broad rewrite" and "round 2's were four one-to-two-sentence edits" — the
cited audit (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`)
carries neither. By the skill's own missing-population dimension these lack
their source. Fix: rewrite the sentence to carry only what the audit
records (or drop the magnitudes; direction over magnitude — see memory
`a-passage-that-describes-itself-decays-on-every-edit`).

### I4 — one-sentence docs-specific threshold rationale

SKILL.md §Aggregation states thresholds are inherited "unchanged" from
requesting-code-review but no sentence says why the 2-🟡 bar is right
without a passing test suite beneath it. Add one honest sentence: either a
docs-specific rationale or an explicit "inherited unexamined; revisit if
the docs arm's false-positive economics prove different" marker. No
threshold change.

### I5 — judged-vs-defaulted class provenance marker (adjudicator's residual from the refuted F6)

The finding schema cannot distinguish "judged instruction" from
"fail-closed defaulted to instruction", and the reviewer knows which at tag
time. Smallest fix: allow an optional `class: instruction (defaulted)`
annotation in the finding schema (SKILL.md + docs-reviewer.md), surfaced so
a user deciding Directive 1 option (c) can see which findings are
instruction-class only by default. No aggregation change — defaulted still
gates (fail-closed preserved).

## Current State Evidence

All five sub-lenses were walked by two fresh-context reviewers this session
against the live files; their quotes were re-verified by the adjudicator at
current file state. Line numbers below were current at f61837ed and drift
under edit — implementers re-locate by quoted text, never by line number.

- **Forward** (who executes the edited text): orchestrator reads
  `loom-code/skills/requesting-docs-review/SKILL.md` Steps 1-5 +
  Directives 1-4; panel arms execute `loom-code/agents/docs-reviewer.md`
  (input contract ~:314-369, output contract ~:370-449, baseline rules
  ~:240-242, severity ladder ~:461-462). Subagents load the INSTALLED
  plugin contract (cache 0.49.0), not the branch copy — behavioral
  verification of agent-contract edits is impossible in-session (memory:
  `agent-contract-edits-do-not-reach-this-sessions-subagents`).
- **Reverse** (what the edited claims describe):
  `loom-code/scripts/loom_gate_markers.py` — docstring :45-51 (ledger
  written on EVERY invocation), `_FINDING_RE` :153 (`- severity:` at any
  indent), `"round": len(rounds) + 1` :738 (invocation counter),
  `validate_verdict_text` :763-793 (no reviewed_sha check),
  `_record_origin_ledger_round` call :1278 before exit-3/4 returns.
- **Error** (failure paths the fixes touch): exit-3 (NEEDS_REVISION
  refuses mint), exit-4 (schema failure refuses mint, fix/rerun retries
  re-append ledger rows), fail-closed unbounded round on unresolvable
  range (SKILL.md §Directive 2).
- **Data**: `<git-common-dir>/loom/origin-ledger.json` (per-branch rows,
  survives sessions, invocation-keyed); verdict text lives in a temp file
  (SKILL.md Step 4 "save the panel verdict text to a temp file") — nothing
  persists it.
- **Boundary**: mixed-branch path — docs arm returns verdict to the
  requesting-code-review orchestrator and does NOT mint (SKILL.md Step 4 /
  requesting-code-review Step 1); those rounds never touch the CLI or
  ledger. i18n READMEs and router cards may quote edited rules
  (memory: `core-rule-removal-needs-plugin-wide-sweep`) — plugin-wide grep
  per claim is a task obligation.

Evidence paths: `loom-code/skills/requesting-docs-review/SKILL.md`,
`loom-code/agents/docs-reviewer.md`, `loom-code/scripts/loom_gate_markers.py`,
`loom-code/skills/requesting-code-review/SKILL.md`,
`docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`,
`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`.

## Decision

Fix all ten items in one branch, prose-first, mechanism-free (the two
carrier gaps are closed by retracting the claim and opening/extending a
backlog entry — user decision, consistent with #646's deliberate
in-session-half boundary). Bump loom-code to 0.50.0 (contract semantics
change: round-N handoff, fail-closed sha, class provenance). We will NOT
build: round-count persistence, out_of_scope persistence, reviewed_sha
schema validation in `loom_gate_markers.py` (would contradict the
retract-not-add direction this batch commits to; candidate for the next
mechanism arc alongside the backlog entries), any threshold change.

## Out of Scope

- Cross-session round/sha/finding persistence mechanisms (backlog).
- `validate_verdict_text` gaining a `reviewed_sha` check (backlog note in
  D4/D5 entry; requires deciding mixed-branch semantics first).
- PASS_WITH_NOTES threshold retuning (I4 adds rationale prose only).
- The standing pre-existing-pool sweep (Directive on round-1 unboundedness
  stays provisional as shipped).
- The citation pre-pass advisory-context mechanization (blind review
  improvement 6 — noted, not built).
- Any change to `scripts/claim_copy_sweep.py` or `check_doc_citations.py`.

## What Becomes Obsolete

- docs-reviewer.md's self-resolve sha fallback sentence (deleted, replaced
  by fail-closed reporting).
- The "round 2 only" labels on the prior-findings carrier (replaced by
  round≥2 monotonic labels).
- The false claims themselves: "holds only the last minted round",
  "round accounting continues, it does not reset", "deferred on the
  record" / "recorded so it is not lost", the docstring's unconditional
  "never biased" clause, the two unsourced magnitude figures.

## Constraints (bind every task)

- SKILL.md sits at ~4,125 words against the repo's ~4,500-word soft cap:
  net word growth must stay near zero — retractions shorten, D1/I5 may
  lengthen; measure with `wc -w` before and after; if over the soft
  target, note the one-line justification in the PR per repo convention.
- Before editing ANY claim: `python3 scripts/claim_copy_sweep.py --claim
  "<distinctive phrase>"` and record the operative/frozen partition in the
  task artifact; name the synonym leak (memory:
  `enumerate-every-copy-before-editing-a-claim-and-name-the-leaks`).
- Prose edits are pinned by grep-window tests under `loom-code/scripts/`
  (and possibly `scripts/`): locate the pinning test per claim FIRST, flip
  it RED against the new wording, then edit (TDD for prose; memory:
  `grep-tests-scope-to-measured-neighborhood` — windowed anchors, RED via
  `git show HEAD:<file>`).
- No self-referential magnitudes in edited prose (memory:
  `a-passage-that-describes-itself-decays-on-every-edit`).
- Agent-contract edits are behaviorally unverifiable this session — the
  ship gate is static: diff review + the skill↔agent pairing check; state
  this in the PR. Before ship, run the evidence-class trap probe (memory:
  `docs-review-dogfood-must-probe-the-evidence-class-trap`, recipe in
  `docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md` §D3) —
  it exercises the INSTALLED contract, so its role is regression (the
  changed wording must not break the trap when it ships), and the probe
  result must be labeled with which contract version actually ran.
- Version bump: `loom-code/.claude-plugin/plugin.json` → 0.50.0 (+ any
  marketplace/manifest sync the repo's CI checks).

## Design-side on-ramp

Skipped silently — defect-fix increment (Axis 0 negative guard).

## Sign-off

User authorized scope + direction this session (「好 就照你的建議開分支修吧」)
after the ranked defect report and the complexity assessment. Committed
interpretation stated in-chat: D5 takes the retract direction (option ②);
correctable before implementation if the user prefers the ledger mechanism.
