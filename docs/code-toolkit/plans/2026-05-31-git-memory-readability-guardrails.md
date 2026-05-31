# Plan: git-memory readability guardrails

Source brief: docs/code-toolkit/specs/2026-05-31-git-memory-readability-guardrails.md
Total tasks: 2   ← uncapped; width is fine
Critical-path depth: 2 (≤5)   ← T1 → T2
Execution order: sequential (Task 2 after Task 1)
Plan-document-reviewer verdict: PASS (2026-05-31, round 1, 11/14 applicable)
  — Note: guardrail 3 (diagram venue) was briefly added then DROPPED after round-2 recon
  found it already fully present in memory-conventions.md §Diagram venue; the plan is
  reverted to the exact round-1-reviewed 2-guardrail content (RED grep restored to its
  valid form), so the round-1 PASS stands — re-review skipped per writing-plans
  "amending a PASS plan" (b) (additive-safe revert to the reviewed state).

## Task 1 — memory-conventions.md: two readability guardrails + dual-consumer invariant + worked example
- Description: Edit `dev-workflow/skills/git-memory/standards/memory-conventions.md` to add,
  in the §Format rules / §Commit-trailers area, **two audience-calibrated readability
  guardrails** for trailer values (calibrated for the future-developer/agent reader):
  (1) **Scannability** — lead with the point in the first clause; push elaboration to an
  RFC-822-folded continuation line (folding already documented); generalize the existing
  `Decision:`-only "1-3 sentences" into a scannability rule across all trailer types; add
  a caveat that the hard-250 line-length is a **ceiling, not a target** (prefer folding/
  splitting over a 250-char run-on). (2) **Expand session-ephemeral jargon** — a trailer
  must be legible to a reader who was NOT in the session; expand or avoid one-off coinages
  (e.g. "P2", cluster names, session-local labels); shared codebase/domain terms (e.g.
  `gws`) are fine.
  (A proposed third "diagram venue" guardrail was DROPPED — `memory-conventions.md`
  already has a complete `## Diagram venue` section, so there is nothing to add.)
  Add the **dual-consumer invariant** note (from brief §Dual-consumer
  invariant): restructure-not-truncate; keep trailer KEYS line-anchored + standard RFC-822
  folding so `git log --grep='^Decision:'` / `%(trailers)` / Phase-3 digest still parse;
  net-positive-for-the-retrieving-agent. Add ONE before/after worked example (a real dense+
  jargon trailer → scannable, self-contained form). Do NOT change trailer key vocabulary,
  the folding mechanism, or import code-toolkit's asking-the-user rules.
- Module: dev-workflow/skills/git-memory/standards/memory-conventions.md
- Files touched: dev-workflow/skills/git-memory/standards/memory-conventions.md
- Context paths:
  - docs/code-toolkit/specs/2026-05-31-git-memory-readability-guardrails.md
  - dev-workflow/skills/git-memory/standards/memory-conventions.md
- Acceptance:
  - RED: `grep -ciE "scannab|lead with|session-ephemeral|not in the (session|room)|restructure" memory-conventions.md` returns 0.
  - GREEN: both guardrails present (scannability: lead-with-point + folding + 250-is-ceiling;
    expand-ephemeral-jargon: legible-to-reader-not-in-session + shared-domain-terms-OK) +
    dual-consumer invariant (restructure-not-truncate + keys-line-anchored + folding/grep
    preserved + agent-net-positive) + one before/after example; trailer KEY vocabulary
    (`Decision:`/`Learning:`/`Gotcha:`/`Related:`) and the RFC-822 folding rule are
    UNCHANGED (`grep -c` for the existing keys + folding example still present); no
    asking-the-user-style rule imported (`grep -ci "outcome, not mechanism\|state anchor"`
    returns 0); SKILL.md body / conventions within token budget; validate-skill-folder hook clean.
- Dependencies: none
- Independent: false  # only one content task in this wave
- Brief item covered: Smallest End State items 1+2 (scannability + expand-ephemeral-jargon
  guardrails) + §Dual-consumer invariant.

## Task 2 — dev-workflow version bump + CHANGELOG
- Description: Bump the **dev-workflow** plugin version (minor — additive guidance; confirm
  current version from `dev-workflow/.claude-plugin/plugin.json` and increment the minor)
  and add a CHANGELOG entry describing the git-memory readability guardrails (scannability +
  expand-session-ephemeral-jargon), the dual-consumer invariant (human archaeologist + agent
  `git log --grep` retrieval; restructure-not-truncate, machine-parse contract preserved),
  grounded in readable-commit canon (Chris Beams 50/72 — what & why, self-contained), with a
  provenance pointer to the brief. Sync marketplace.json only if it carries the dev-workflow
  version. No prior-version backfill.
- Module: release metadata (dev-workflow plugin manifest + changelog)
- Files touched: dev-workflow/.claude-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - dev-workflow/CHANGELOG.md
  - docs/code-toolkit/specs/2026-05-31-git-memory-readability-guardrails.md
- Acceptance:
  - RED: plugin.json version unchanged from current; no new CHANGELOG entry for the bump.
  - GREEN: dev-workflow plugin.json version bumped one minor (valid JSON via `python3 -m
    json.tool`); CHANGELOG entry naming the readability guardrails + dual-consumer invariant
    + Chris-Beams grounding + brief pointer.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Open Question 1 (dev-workflow minor version bump).

## Notes
- **Target is dev-workflow, not code-toolkit** — git-memory is a dev-workflow skill; the
  version bump is on the dev-workflow plugin manifest.
- Only 2 tasks, sequential (T2 names what T1 changed). No parallel wave. Critical-path
  depth = 2.
- **SKILL.md pointer dropped** (brief Open Question 2): the guardrails live in
  `standards/memory-conventions.md`, which `git-memory/SKILL.md` already cites as "the
  source of truth that protocols and scripts follow" — a separate SKILL.md pointer would be
  redundant (deletion-first). The guardrails fire via the existing reference.
- Doc-only skill: no pytest; acceptance is grep-diagnostic + validate-skill-folder hook +
  token budget. The dual-consumer invariant (machine-parse contract preserved) is a
  REVIEW-stage check the spec-/quality-reviewers must verify on T1.
- Brief lives under `docs/code-toolkit/specs/` (brainstorming's hardcoded path) though the
  target is dev-workflow — a known cross-plugin path quirk, not load-bearing.
