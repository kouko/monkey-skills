# A/B protocol — prose-edit self-sweep (implementer rule 14)

Date: 2026-09-01 · Scope: `docs/loom/plans/2026-09-01-prose-edit-self-sweep.md` Task 4.
Registered before any run. Nothing below reports a result — see
`## Interpretation notes` for the no-effectiveness-claim binding.

## Arms

- **Arm A** (control) — `loom-code/agents/implementer.md` pinned at
  `3ef8922a72932991b39f67702eb33fec31ade2b0` (the commit immediately before
  Task 2's rule-14 commit `3291e4d1bf1fa48f975bb6e67be060ed5df5973f`; resolved
  via `git rev-parse 3291e4d1~1`). Rules 1–13 present, rule 14 "Prose-edit
  self-sweep" absent — confirmed via `git show 3ef8922a:loom-code/agents/implementer.md
  | grep -c "Prose-edit self-sweep"` → `0`.
- **Arm B** (treatment) — `loom-code/agents/implementer.md` at
  `3291e4d1bf1fa48f975bb6e67be060ed5df5973f` or later on this branch. Rule 14
  present — confirmed via the same grep → `1`.
- Implementer model: fixed **sonnet** in both arms (no model-tier variance
  introduced).
- Judge: unchanged `loom-code:docs-reviewer` (the reviewer contract is not
  touched by this arc — brief "Do NOT build").
- Reps: **2 per arm per case** (4 cases × 2 arms × 2 reps = 16 runs).

## Blind cause-labelling step

The person or process assigning a `cause` code (A–K) to each
`docs-reviewer` gating finding does so from the finding text and the diff
alone — **without** being told which arm (A or B) produced the draft under
review. Arm identity is stripped from the record before labelling and
reattached only afterward, by run id, for tallying. This mirrors the
finding-cause mining method already used in
`docs/loom/audits/2026-09-01-docs-review-finding-causes.md`.

## Registered metrics

Decided in advance; nothing else is scored:

1. **First-round preventable gating findings** — `docs-reviewer` findings
   from the first review round only, `class: instruction`, that a silent
   self-sweep action (grep restatement / re-run self-referential claim /
   walk reading path / check instruction-vs-schema) could plausibly have
   caught before the round ran.
2. **Review rounds** — count of `docs-reviewer` dispatch rounds until a
   non-blocking (`PASS` / `PASS_WITH_NOTES`) verdict.
3. **Draft token/time delta** — implementer generation token count and
   wall-clock time for the initial draft, arm A vs arm B.
4. **Hedge marks + fabricated-evidence count** — count of hedging language
   ("should", "likely", "I believe") and count of findings classed as
   fabricated/unverified evidence in the draft, per
   `docs/loom/audits/2026-09-01-docs-review-finding-causes.md`'s cause taxonomy.

## Registered non-metric

**"More complete-looking sections" is NOT success.** A draft that reads as
more thorough, longer, or more heavily cross-referenced is not scored as
better by this protocol unless it moves one of the four registered metrics
above. This guards against rule 14 optimizing for review-proof prose
theater rather than actually-caught defects.

## Tally command

Task 3's CLI, quoted verbatim from `loom-code/scripts/prose_selfsweep_tally.py`'s
own docstring:

```
CLI: `python3 prose_selfsweep_tally.py <input.json>`. Stdlib only.
```

Run from the repo root as:

```
python3 loom-code/scripts/prose_selfsweep_tally.py <input.json>
```

Input JSON record shape (from the same docstring):

```
{
    "case_id": str,
    "arm": "A" | "B",
    "rep": int,
    "gating_findings": [{"cause": "A".."K", "class": "instruction" | "evidence"}],
    "hedge_marks": int,
    "draft_tokens": int,
    "review_rounds": int,
}
```

Validation, fail loud (per the script): every `arm` must be one of `"A"` /
`"B"`; every `cause` must be in the closed A–K set; every
`(case_id, arm, rep)` triple must be unique. Any violation exits non-zero
naming the offending record. Output is per-arm totals only — no verdict
line, no "improved"/"worse" wording; interpretation stays human and stays
in this document's `## Interpretation notes`, produced only after the run.

Probe `tally-cli-runs` (this task): a 2-record inline fixture (one Arm A
record, one Arm B record) was run against this exact command and exited 0
with a rendered table — confirming the CLI shape above is current and
executable, not just a documented spec.

## Interpretation notes

No effectiveness claim is made in this document or anywhere else in this
branch before the A/B run's results exist (brief: "Branch stays unmerged
until A/B results exist; effectiveness is NOT claimed in any shipped
prose"). If the run later shows no measurable difference between arms on
the registered metrics, candidate explanations to consider — decided now,
before the data can bias the choice — include, but are not limited to:

- **List-position attention decay** — rule 14 is rule 14 of 14 in
  `implementer.md`'s hand-written Role-contract section; an implementer
  reading the contract top-to-bottom may give a late-listed rule less
  weight than an early one, independent of the rule's content.
- **Naming placement-variant (e)** — moving the self-sweep actions out of
  the numbered rule list into a separate `## Prose-task duties` section
  (a structurally distinct location, not just a renumbering) is the
  follow-up experiment this no-effect branch points to, not something
  tried in this run.

Neither explanation is evidence of anything yet; they are pre-registered
candidates to reach for if and when the numbers come back flat, so that
post-hoc rationalizing is constrained to this list plus whatever the data
itself surfaces.

## Isolation clause

- No case in `cases.md` may be drawn from the sibling worktree's baseline
  corpus (the corpus `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`
  and related baseline-experiment material use as their own control
  population) — this A/B's 4 cases are drawn fresh from kumiko-zaiku-app-icons
  and monkey-skills git history, per `cases.md`.
- Reviewer prompts (`loom-code/agents/docs-reviewer.md` and
  `loom-code/skills/requesting-docs-review/`) are never modified for this
  run, in either arm. Only `loom-code/agents/implementer.md` varies across
  arms.
