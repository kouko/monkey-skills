---
name: review
description: |
  Runs one checkpoint review of a change: two or more fresh-context reviewers, a blind run and an adversarial pass over the delta since reviewed_sha, merged into docs/loom/<change-id>/review.json. Called by write-spec (or write-plan for a minimal spec) for the spec lens, by build after a task or wave, by ship at branch end, or when asked to review the change in progress.
version: 1.0.0
---

## What this station does

Every other gate in loom recomputes something already written down. This
one is where a judgement is made for the first time, and it is the only
source of quality in the flow: the user is not asked to grade a diff, a
spec or a plan, so if the machines do not catch it, nobody does.

A checkpoint is three verification actions over one delta — **read**,
**blind run**, **adversarial** — plus the package tests, merged into a
single verdict and written to `docs/loom/<change-id>/review.json`. Which of
the three run depends on what kind of artifact the delta is (step 1).

Two rules hold across the whole station and everything below is downstream
of them:

- **Whoever wrote it does not verify it.** No reviewer, blind-runner or
  adversary may be an agent that appears in `dispatch[]` as an
  `implementer` for this change. The checker recomputes this at push
  (`push.reviewer-ne-implementer`).
- **Fresh context, not a summary.** Every reviewing agent is a new process
  given file paths. Never hand one a transcript, your own reading of the
  change, or a list of what you think it should look at.

| Host | Command prefix |
|---|---|
| Claude Code | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py` |
| Codex CLI | `python3 .codex/hooks/loom_checker.py` |

The Claude Code form is written out below; on Codex substitute the other
prefix and nothing else changes.

## 0. Contract check, and the file you are writing

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py contract --require 1.0
```

Exit 0 continue; non-zero stop and report the mismatch (`contract.requires`).

On Codex, if `.codex/hooks/loom_checker.py` does not exist, **stop**: run
`loom-code:write-plan` step 0b (the scaffold and its trust probe; that station
writes the procedure out in `codex-first-contact.md`, under its `references/`)
first. Do not produce any
artifact without the checker. The file existing is not proof the hook runs:
an untrusted Codex hook is skipped in silence, and step 0b's trust probe is
what tells the two apart.

The record is `docs/loom/<change-id>/review.json`, in version control. At
the first checkpoint of a change it does not exist yet: copy
`contract/templates/review.json` and set `reviewed_sha` to the merge-base
with the trunk —

```
git merge-base HEAD <trunk>
```

— because nothing before the branch started is this change's to answer for.
`<trunk>` is the **first** of `origin/main`, `main`, `origin/master`,
`master` that `git rev-parse --verify <name>` resolves; a repo with no
remote is fine, the local branch answers. If none of the four resolves, say
so and ask the user which ref is the trunk — do not guess.

If `HEAD` **is** the trunk, **stop**: create the change branch first and
come back. A merge-base of a branch with itself is the branch tip, which
would make the delta empty and the checkpoint vacuous — this is the same
condition the checker refuses.

If `build` already created the file for its dispatch records, use that one;
never start a second.

There is one `review.json` per change and it accumulates. Each checkpoint
appends its verdicts, probes and findings under a new `round`, and only
`reviewed_sha` moves.

## 1. Scope and artifact type

State the scope in one token and write it on every verdict and probe of
this round:

| `scope` | Called by | Delta |
|---|---|---|
| `spec` | write-spec (or write-plan, for the code-only minimal spec) | the spec file only |
| `after-task:<id>` | build, right after that task's commit | that task's commits |
| `wave-end:<n>` | build, when the wave closes | `<reviewed_sha>..HEAD` |
| `branch-end` | ship | `<reviewed_sha>..HEAD` |

The delta itself is always

```
git diff --stat <reviewed_sha>..HEAD
```

Classify every changed path by the type mapping in
`contract/manifest.yaml` (`artifact_types:`) — a `KICKOFF-DEFAULTS.md`
line `artifact-types: <glob>=<type>` overrides it. Then run the actions the
type asks for:

| Artifact type | Lens | Read | Blind run | Adversarial |
|---|---|---|---|---|
| code | code (11 dimensions) | yes | yes | yes |
| spec | docs + spec-conformance + design-conformance + principles-conformance + user-judgment-leak | yes | cold reader walks the Acceptance scenarios | red-team the spec |
| plan, docs, memory, map, evidence | docs (5 dimensions) | yes | no | no |
| skill (`SKILL.md`, `agents/*.md`) | skill | yes | a cold agent performs a real task from the file alone | gate-attack catalogue |
| gate (`hooks/**`, `scripts/check_*`) | code + skill | yes | yes | yes — attacks are the point of the file |
| standing (`PRINCIPLES.md`, `DESIGN.md`) | principles / design | yes | no | no |
| intent | docs + user-judgment-leak | yes | no | no |

A delta that spans types runs the union: one reviewer may carry two lenses,
but every type present must be covered by some lens. The dimension
definitions live in `references/lenses.md`; hand reviewers that path.

**Lane.** The checker recomputes `small | full` from the same classified
delta — never asked for, never chosen by an agent. A change is `small`
when every changed path falls in a pre-authorised class (tests only;
docs only; CI/config/dependency declarations; version and manifest sync;
a clean revert), the delta touches no `interface-surfaces` glob, touches
no `gate` or `skill` artifact type, includes no non-test `code`-typed
path, and every changed path sits under one top-level plugin directory
(or none). One line of non-test code, one `gate` or `skill` file, or a
second plugin makes the whole delta `full` — a smaller diff never buys a
smaller lane.

| Lane | Checkpoint |
|---|---|
| `small` | one fresh-context reviewer, package tests, adversarial probes; the blind run runs only when an Acceptance line of the intent is not mechanical — cannot be settled by "run the command, compare the number" |
| `full` | unchanged — two or more fresh-context reviewers, blind run, adversarial |

## 2. Read — reviewers, by lane

<!-- gate: review.two-fresh-reviewers -->
Dispatch in two stages. First the adversary (§4) and, in the full lane,
the blind-runner (§3) — each in its own message so the two run
concurrently; their probes and report are committed before any reviewer
starts, because a verdict's `sha` must name the commit that becomes
`reviewed_sha`, and dispatching reviewers first would let a later commit
move that target out from under them. Then dispatch fresh-context
reviewers: **two or more, in one message so they run concurrently and
cannot see each other's findings, in the full lane**; **exactly one, in
the small lane** (§1). One reviewer in the full lane is not a review: it
is an opinion with nothing to disagree with, and `push.verdicts-ge-2`
refuses the push below the lane's floor.
<!-- /gate -->

Each gets the contract `agents/reviewer.md` and this input:

```
### Lens
<code | docs | spec | design | principles | skill>

### Resource paths
- repo root, and `git diff <reviewed_sha>..HEAD` as the delta
- changed paths, by name
- ground truth: intent docs/loom/intent/<change-id>.md; spec and plan when they exist
- dimensions: loom-code/skills/review/references/lenses.md
- reviewed_sha: <sha>
- HEAD at dispatch, what this verdict reviews and what becomes the next
  `reviewed_sha`: <sha>

### Return
verdict PASS | PASS_WITH_NOTES | NEEDS_REVISION, dimension_scores, findings
(severity fatal | important | nit; anchor file:line; text; fix), sha — the
HEAD value above, copied onto the verdict
```

**Second vendor.** Read `docs/loom/KICKOFF-DEFAULTS.md`. If it carries
`second-vendor: <cli>`, one of the two legs runs on that command-line tool,
non-interactively — for Codex:

```
codex exec --sandbox read-only -o <out-file> "<the reviewer prompt above>" < /dev/null
```

Before dispatching to that tool, check it is actually there:

```
command -v <cli> && <cli> --version
```

Both must succeed. A named CLI that is missing, or that fails its version
probe, does **not** stop the checkpoint and is **not** a question for the
user: run both legs here as two same-vendor fresh reviewers, record
`vendors: ["anthropic"]`, and put `fallback: "<cli> missing at <YYYY-MM-DD>"`
on this round's verdicts — that exact shape, naming the CLI that was
declared. The checker matches it (`push.second-vendor-honoured`): a free
string like `n/a`, or one naming a different tool, explains nothing about
the vendor the user chose and does not silence the rule.

Record every vendor used in `vendors:`. If the line says `none`, or is
absent, both legs run here and that is a complete review. **This station
never suggests a second vendor**: that offer is made once per change by
`write-plan`, inside decision point ①, and the answer is remembered.

<!-- gate: review.reviewer-not-implementer -->
Before dispatching, append one `dispatch[]` entry per agent — role
`reviewer`, `blind-runner` or `adversary` — and commit it
(`chore(loom): dispatch review <scope>`). Written afterwards the record is
a reconstruction, and it is the only evidence that the agent who reviewed
is not the agent who wrote. An agent that implemented any task of this
change may not take any of the three reviewing roles.
<!-- /gate -->

## 3. Blind run

The blind run is not a smoke test; it is the acceptance interface the user
reads at decision point ③. Dispatch `agents/blind-runner.md` — an agent
that appears nowhere in `dispatch[]` as an implementer for this change.

- **code**: clone or `git worktree add` a clean tree at `HEAD`, install,
  build, run. Walk every Acceptance line of the intent in order; for a
  product change also walk every UI flow of the spec. Capture screenshots
  or command output as evidence.
- **spec**: a cold reader takes the spec alone and walks its Acceptance
  scenarios, saying at each step what they would do and what they expect.
- **skill**: a cold agent performs one real task using only the `SKILL.md`,
  and reports where it had to guess.

The result is `docs/loom/<change-id>/blind-run-report.md`, written to the
structure in `references/blind-run-report.md` — per Acceptance line: how it
was tried, what happened, the evidence; then the fixed line about what the
change did to data the user already had; then the section listing what the
agent decided on the user's behalf, including every dismissal of severity
`important` or worse; then the open questions. Record it as a probe with
`kind: blind-run` and the report path as `artifact`.

## 4. Adversarial

Dispatch `agents/adversary.md` — again never an implementer of this change.

- **code**: if the repo declares mutation or fuzz tooling, run it. If it
  declares none, the adversary **writes at least three executable abuse or
  boundary cases** — empty input, hostile input, the state the change
  forgot — runs them, and records each as a probe.
- **spec**: red-team it — read each requirement for the behaviour it fails
  to forbid.
- **skill / gate**: work the six classes of
  `references/attack-catalogue.md` against the file, one attempt per
  class.

Recipes and the probe shape are in `references/adversarial.md`. Whatever
the adversary finds enters `findings` like any other finding; whatever it
ran enters `probes[]` with `kind: adversarial` and this round's `scope`.

Each such probe names, in `artifact`, the **committed file** the case now
lives in, and its `command` runs that file. The checker re-runs each one
itself at push and refuses a probe whose command never mentions its
artifact, or is a shell builtin: `true` exits 0 without attacking
anything, and three of those used to pass for a red team
(`push.probes-adversarial`). A case that is not a file in the tree is not
a regression eval — it is a claim.

## 5. Package tests

Run the repo's own test command at `HEAD` and record it:

```json
{"kind": "package-tests", "command": "python3 -m pytest loom-code/scripts/ -q", "sha": "<HEAD>", "result": "pass", "artifact": "", "scope": "wave-end:1"}
```

`build` supplies the command (a `package-tests:` line in
`KICKOFF-DEFAULTS.md`, else detected from the repo) and it is recorded
byte for byte — the checker compares it against the repo's own command and
refuses a substitute. When `build` reports that the repo has no suite at
all, the `package-tests: none — <why>` line it wrote is the record; note
the gap in this round's findings so it is visible rather than absent, and
record no run.

Your `result` is a record and nothing more: at push the checker runs the
command itself in a clean tree and believes only the exit code it sees
(`push.probes-package-tests`).

## 6. Merging the verdicts

<!-- gate: review.no-averaging -->
There is **no averaging and no tie-break**. Every verdict is stored whole in
`verdicts[]`, disagreements included — two reviewers who disagree are the
finding. The round's outcome is `NEEDS_REVISION` if any reviewer says so;
otherwise `PASS_WITH_NOTES` if any says that; otherwise `PASS`.
<!-- /gate -->

Every finding of severity `important` or worse becomes an `open_findings`
entry with id `<scope>-<nn>`, its anchor, `origin_sha` and `raised_by`.
Findings already open from an earlier round must each be closed before
`reviewed_sha` moves:

- `resolved: <evidence>` — the commit or test that closed it, and
- `dismissed: <reason> by <agent_id>` — where that agent holds a
  reviewing role in `dispatch[]`. An implementer may never dismiss a
  finding about their own work (`push.dismissed-by-reviewer`), and every
  dismissal of `important` or worse is listed in the blind-run report so
  the user sees what was waved through.

`push.open-findings-closed` refuses a push while any entry is neither.

**Severity is by consequence, not by wording.** `important` means a reader
following the text would act wrongly, or a fact the checker or CI relies
on is wrong; everything else — wording, terminology, units, the same fact
stated two ways, readability — is `nit`, even where it is literally
incorrect (`references/lenses.md` "Severity and verdict" is the full
rule). `nit`s never open a round: they never become an `open_findings`
entry, and `ship` folds every open one into a single commit before push,
confirmed by the reader who raised it in one line — no new round.

## 7. Write the record

Write `review.json` — verdicts, probes, findings and vendors of this round
— and commit it **alone**. On a round whose `scope` is `spec`, every verdict
also carries `spec_sha`: the first seven characters of
`git hash-object docs/loom/<change-id>/spec.md` as reviewed. It is what
lets a later reader tell whether the spec the user confirmed
(`confirmed-behavior: <date> @<spec sha7>`) is the spec that was reviewed. Add to what is there; never drop a key another
station wrote (`dispatch[]` from `build`, `questions[]` from a decision
point), and never rewrite an earlier round:

At the **first** checkpoint of a change, also fill `questions[]`, one entry
each as `{decision_point, text, type}`. Those questions were asked at
decision point ① before `review.json` existed, so they arrive from
elsewhere; leaving them there makes the flow look quieter than it was.
Where to take them from depends on whether a plan exists yet:

- **A plan exists** — copy the plan's `## Questions asked` section, and add
  anything the hand-off message carries that the section does not.
- **Scope `spec`, no plan yet** — the plan has not been written, so the
  only carrier is `write-spec`'s hand-off message, which is required to
  list the questions verbatim. Take them from there. If that message
  carries none and decision points did happen, say so in the round's notes
  rather than writing an empty `questions[]` as if none were asked.

A later checkpoint does not re-copy: `questions[]` accumulates, it is never
rewritten.

```
git add docs/loom/<change-id>/review.json
git commit -m "chore(loom): checkpoint review — <scope> <verdict>"
```

<!-- gate: review.review-only-commit -->
That commit touches one file and no other. On `PASS` or
`PASS_WITH_NOTES`, set `reviewed_sha` to `HEAD^` — the commit whose tree was
actually reviewed — in the same commit that carries the verdict, so the
reviewed tree and the pushed tree are the same object
(`push.review-only-head`, `push.reviewed-sha`, `push.review-schema`).
On `NEEDS_REVISION`, `reviewed_sha` does not move at all.
<!-- /gate -->

**A wave-end round that is also the branch end.** When this checkpoint is
the plan's last wave and nothing is committed after it, there is no delta
left for a separate `branch-end` round to read, and reviewing an unchanged
tree twice buys nothing. Record `scope: branch-end` on this round rather
than adding an empty one — that is what `ship` step 1 looks for, and it
still counts as one checkpoint, not two. If anything but `review.json` is
committed afterwards, the exemption is gone and a real `branch-end` round
is owed.

A worked record:

```json
{
  "reviewed_sha": "be19b9612b0d4c7a9f0e21c3d8a5b6e7f0123456",
  "scope": "wave-end:1",
  "vendors": ["anthropic"],
  "verdicts": [
    {"round": 1, "scope": "wave-end:1", "reviewer": "rev-w1-a", "vendor": "anthropic",
     "model": "sonnet", "lens": "code", "verdict": "PASS_WITH_NOTES",
     "sha": "be19b9612b0d4c7a9f0e21c3d8a5b6e7f0123456",
     "fallback": "codex missing at 2026-09-02",
     "dimension_scores": {"security": "PASS", "tests": "PASS_WITH_NOTES"},
     "findings": [{"severity": "important", "anchor": "loom-code/scripts/x.py:41",
                   "text": "the empty-input path is untested",
                   "fix": "add a case asserting the empty list returns []"}]}
  ],
  "probes": [
    {"kind": "package-tests", "command": "python3 -m pytest loom-code/scripts/ -q",
     "sha": "be19b9612b0d4c7a9f0e21c3d8a5b6e7f0123456", "result": "pass",
     "artifact": "", "scope": "wave-end:1"}
  ],
  "open_findings": [
    {"id": "wave-end:1-01", "anchor": "loom-code/scripts/x.py:41",
     "origin_sha": "be19b9612b0d4c7a9f0e21c3d8a5b6e7f0123456", "raised_by": "rev-w1-a",
     "resolved": "closed by 4f1c2ab — test_empty_input"}
  ],
  "dispatch": [
    {"task": "wave-end:1", "role": "reviewer", "agent_id": "rev-w1-a", "model": "sonnet",
     "started": "2026-09-02T14:05:00+08:00", "fresh_context": true}
  ]
}
```

## 8. Hand back

- **`NEEDS_REVISION`** — hand the findings to `loom-code:build` as fix
  work, one commit per finding, then run this station again as the next
  `round` of the same checkpoint (§8a). **Fix rounds do not count** against
  the five-checkpoint cap; they are one checkpoint finishing.
- **`PASS` / `PASS_WITH_NOTES`, waves remaining** — back to
  `loom-code:build` for the next wave.
- **`PASS` / `PASS_WITH_NOTES`, `branch-end`** — to `loom-code:ship`, which
  runs the memory step, the push and decision point ③. The user reads the
  blind-run report there, never the diff.

## 8a. Fix rounds

A `NEEDS_REVISION` round is not a new checkpoint starting over — it is the
same checkpoint continuing. The full procedure — a fix-commits-only delta,
resuming the same reader with its own previous findings, no probe re-run,
rebuttal-to-dismissed, and the third-round design re-look — is
`references/fix-rounds.md`; hand reviewers that path on every round after
the first.

## Lenses at a glance

| Lens | Dimensions |
|---|---|
| code | security, architecture, correctness, naming, tests, refactoring, cross-task-coherence, external-surface-grounding, principles-conformance, deliberate-simplification, deletion-first |
| docs | omission, ambiguity, inconsistency, incorrect-fact, missing-population |
| spec | the five docs dimensions + spec-conformance, design-conformance, principles-conformance, user-judgment-leak |
| design | design-conformance (against `DESIGN.md`) |
| principles | principles-conformance (against `PRINCIPLES.md`) |
| skill | the five docs dimensions + user-judgment-leak |

A conformance dimension with no document to conform to scores `N/A` with
the reason, never a free `PASS`. `user-judgment-leak` is the dimension that
fires when the change asks the user a question they cannot answer — a
question about quality, a task split, or a review outcome, rather than what
they want, what they will see, or whether it is done.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff — commits on the change branch, one `Task: <id>` trailer each | agent-decided | none during build; writes the `dispatch[]` the push rules read | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review — `docs/loom/<change-id>/review.json`, and `docs/loom/<change-id>/blind-run-report.md` from the blind run | fresh-context reviewers, one in the small lane, two or more in the full lane (§1); no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR — the pushed change branch and its pull request | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

