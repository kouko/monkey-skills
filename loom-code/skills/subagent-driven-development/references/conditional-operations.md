# Conditional operations

Read only the section whose trigger fires. The core SDD loop, review packet,
verdict table, retry caps, ledger rule, model selection, and status routing stay
in `SKILL.md`.

## Capacity-error recovery

When a subagent call returns a usage-limit or `529 Overloaded` error, do not
silently retry. Finish and commit tasks already `DONE` in the wave, then use
`dispatch-hygiene-notes.md` §Capacity-error recovery for the three recovery
options and retrospective reviewer dispatch after capacity returns.

## User-question delivery

Use these rules only when `SKILL.md`'s ask policy says a question is warranted:

1. Describe outcomes, not internal agent mechanics.
2. Translate jargon and expand acronyms on first use; terms introduced by the
   user in this session are fine.
3. Explain numbers (`PASS 12/12` becomes “all 5 tasks checked out”) before
   showing machine detail.
4. Open with one line stating the current state and what the choice changes.
   Put that anchor inside the structured question field. Never offer a CLI
   command before confirming it exists.
5. Offer at most four options; do not add an explicit “Other”. Invite free-form
   input for open design questions, not closed factual questions.
6. Combine questions only when they share one topic and can be judged together.
7. Prefer the host's structured question tool for non-trivial choices. A prose
   question is valid only when its first line contains the same state-and-stakes
   anchor.

For the calibrated good/bad example, read `dispatch-hygiene-notes.md` §Worked
example. For a complex fork, apply `hooks/family-reception.md` §Brief before a
complex fork.

### Progress-card delivery

`python3 scripts/plan_card.py <plan-path> --set-status
"T<N>=<status>"` and `--set-stage "<text>"` print the card after the flip. Use
the repo-root script when present, otherwise the plugin-shipped copy. Relay its
output in the conversation language using `hooks/family-relay.md` §(a2). If
neither script or the relay contract exists, render goal, task table, stage,
and next action inline. Always re-read the plan; never compose the card from
memory or copy its template here.

When the host provides task tools, mirror the plan tasks and update the mirror
with each ledger flip. This is display-only: the plan's `Status` remains the
source of truth. Hosts without task tools skip this silently.

## Review-weight mechanics

Read when a plan declares `Review-weight: mechanical` or `Review-weight:
prose`; otherwise run the full reviewer pair.

### Mechanical self-check

This lane requires implementer `DONE` and all three checks:

1. **Content match.** The Description must name either a literal target/diff or
   a deterministic sync script plus its SSOT. For a literal, confirm the
   post-edit string in every declared file or compare the exact diff. Before
   trusting a sync script, require it to be clean and absent from `Files
   touched`; then re-run it and require zero diff, or run its paired drift test.
2. **Scope match.** The commit diff must be a subset of `Files touched`, with no
   changes outside the exact target.
3. **Suite green.** Run the resolved package test command after the commit.

Any failure or ambiguity falls back to the full reviewer pair. All three
passing resolve the task as `DONE` without reviewer verdicts. The plan-time
eligibility gate is `plan-document-reviewer` Check 16.

### Prose and record-class routing

`Review-weight: prose` keeps spec-reviewer and substitutes docs-reviewer for
code-quality-reviewer. It applies only when declared and actual changed files
are authored `.md` prose; any code, config, or generated artifact falls back to
the full reviewer pair. Docs-reviewer receives the same immutable packet and
reviews the contract-class subset. Its verdict occupies the quality column of
the normal verdict table.

Classify contract-class versus record-class with
`requesting-code-review` §Classification. All-record-class work dispatches only
spec-reviewer and records `code-quality slot: N/A — record-class prose`; mixed
work sends only the contract-class subset to docs-reviewer. The record-only
lane resolves from spec-reviewer's verdict alone.

## Orchestrator command hygiene

Read when the orchestrator edits after review, runs commands, or handles
version metadata:

- Before editing a file located through shell inspection, use the host's file
  read operation on that file; shell output does not satisfy a read-before-edit
  precondition. See `using-loom-code/references/environment-gotchas.md`.
- Apply `dispatch-hygiene-notes.md` §Environment hygiene to direct commands.
- For version parsing or manifest work, confirm a library is standard-library
  before importing it; do not add a third-party parser accidentally.

## Reviewer-retry research

Read `research-escalation.md` before the third re-dispatch when round two
repeats the same unresolved question, immediately when a finding includes
`evidence_needed:`, or before surfacing a semantics/convention `BLOCKED` state.
Do not use this escalation for missing dependencies or broken test
infrastructure.

## Role prompt catalog

Read only the prompt for the role being dispatched:

- `../../../agents/implementer.md`: worker; code, tests, and status.
- `../../../agents/spec-reviewer.md`: binary spec coverage verdict.
- `../../../agents/code-quality-reviewer.md`: three-valued quality verdict.
- `../../../agents/docs-reviewer.md`: prose quality verdict for its eligible lane.

Each role carries the managed baseline from `../../../scripts/_baseline.md`.
Spec-reviewer does not evaluate code quality; quality reviewers do not evaluate
spec coverage.

The skill-local `standards/`, `rubrics/`, and `checklists/` are generated
functional copies of the canonical code-team knowledge layer. Change the
canonical source, run `python3 loom-code/scripts/distribute.py`, and let
`verify-drift.py` enforce identity. See `../../../scripts/canonical/README.md`.
