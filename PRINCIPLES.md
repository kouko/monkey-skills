# Product principles — loom (monkey-skills)
ratified-by: kouko 2026-09-04

## Who
People who describe what they want in plain words and have only basic software-engineering knowledge, working alone or in a small team, on Claude Code or Codex CLI. They cannot judge the quality of a spec, a plan, or a diff.

## Non-negotiables (ordered)
1. The user answers only three kinds of questions — what do you want, does it react the way you expect, is it done — plus consequence-form choices for one-way doors; never a question that requires reading code.
2. Quality comes from machines, not from the user's sign-off: at least two fresh-context reviewers in the full lane and one in the small lane (a change whose diff falls entirely within the pre-authorised classes — tests only, docs only, CI/config, version sync, clean revert — touching one plugin and no gate, skill, contract, standing document or interface surface), a blind run by someone who did not write it (omitted only when every Acceptance line is mechanical), and an adversarial pass; every incident becomes a permanent eval.
3. Every gate recomputes facts from the repository; no gate trusts a claim written by the agent it checks.
4. Any new mechanism must arrive with a regression eval and must not raise the net mechanism count without a declared budget exception.
5. The user's existing data is never rewritten, deleted, or sent off the machine without being asked first, even when there is only one way to do the job.

## Won't do
- Ask the user to review specs, plans, or diffs for quality.
- Require a second model vendor; it is the user's standing choice, suggested at most once per change.
- Add prose-only gates; a rule that must block lives in the checker.

## Failure we must avoid
Work that passes every gate while its quality is insufficient and the user cannot see that it is — the user says "OK" to a blind-run report that hides the problem.

## Fixed choices
- Three plugins with one-way dependency on loom-code's versioned contract package.
- Host hooks (Claude Code plugin hooks, Codex `.codex/hooks.json`), never git hooks.
- Hard cutover: pre-1.0 artifacts are archived in place, never converted.
