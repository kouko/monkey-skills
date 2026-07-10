# Plan: ascii-graph trigger-rate fix + loom visual-contract preload

Source brief: docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md
Total tasks: 4
Critical-path depth: 2 (≤5)
Execution order: parallel-where-possible (Task 1 ∥ Task 3; then Task 2, Task 4)
Plan-document-reviewer verdict: PASS (2026-07-10, 14/14 checks)

## Task 1 — ascii-graph-toolkit SessionStart trigger card

- Description: Create the plugin's SessionStart hook that injects a ≤5-line
  trigger card into every session. New `hooks/hooks.json` wires
  `SessionStart (matcher: startup|clear|compact)` to a new
  `hooks/session-start` bash script that reads `hooks/trigger-card.md` and
  emits it as `hookSpecificOutput.additionalContext` (3-key defensive shape
  AND `hookEventName` present — mirror `loom-pipeline/hooks/session-start`;
  fail open with empty context if the card file is missing). Card draft
  (implementer may tighten wording, must keep the three pinned elements —
  the invoke-first rule, the CJK/≥3-box condition, the trivial-ASCII
  exemption):

  ```
  # Diagram trigger card (ascii-graph-toolkit)
  Before typing any box-drawing / ASCII diagram (┌─┐, +--+) in chat or a
  text artifact: if the diagram has CJK (中/日) labels anywhere OR ≥3
  boxes, invoke the `ascii-graph` skill FIRST — its width-aware generators
  and verify-loop keep full-width characters aligned; eyeballed CJK padding
  silently breaks. Trivial all-ASCII sketches (≤2 boxes, no CJK) may be
  hand-drawn. Option comparisons stay markdown tables, not ASCII boxes.
  ```

- Module: ascii-graph-toolkit/hooks
- Files touched: ascii-graph-toolkit/hooks/hooks.json,
  ascii-graph-toolkit/hooks/session-start,
  ascii-graph-toolkit/hooks/trigger-card.md,
  ascii-graph-toolkit/scripts/test_trigger_card.py
- Context paths:
  - loom-pipeline/hooks/session-start
  - loom-pipeline/hooks/hooks.json
  - loom-pipeline/scripts/test_family_relay.py
  - docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md
- Acceptance:
  - RED: ascii-graph-toolkit/scripts/test_trigger_card.py::test_session_start_emits_trigger_card
    fails (hooks/session-start does not exist yet)
  - GREEN: executing `ascii-graph-toolkit/hooks/session-start` exits 0 and
    prints JSON where `hookSpecificOutput.hookEventName == "SessionStart"`
    and `hookSpecificOutput.additionalContext` contains "ascii-graph",
    "CJK", and the exemption line; `hooks.json` parses and wires the
    matcher `startup|clear|compact` to the script; test file runs under
    `PYTHONDONTWRITEBYTECODE=1 python -m pytest ascii-graph-toolkit/scripts/`
- External surfaces: Claude Code SessionStart hook contract
  (`hookSpecificOutput.additionalContext`; `hookEventName` REQUIRED —
  omitting it silently disables the hook and spams validation errors, see
  machine memory feedback_hook_specific_output_requires_hookeventname).
- Dependencies: none
- Independent: true
- Brief item covered: "New `hooks/hooks.json` + `hooks/session-start`
  emitting a ≤5-line trigger card via
  `hookSpecificOutput.additionalContext`" (Smallest End State PR1.1, PR1.4)

## Task 2 — action-moment description + version/marketplace sync

- Description: Rewrite `skills/ascii-graph/SKILL.md` frontmatter description
  as an action-moment sentence and sync the two version/description copies.
  Description draft (implementer may tighten; must start with "Use BEFORE",
  must keep at most ONE CJK trigger phrase per the A/B-refuted-stuffing
  memory):

  ```
  Use BEFORE typing the first `┌` of any ASCII/box-drawing diagram, table,
  or flowchart destined for chat, Slack, PR text, or code comments —
  REQUIRED when labels contain CJK (中/日文字) or the diagram has ≥3 boxes.
  Deterministic width-aware generators (table / flow / tree / bar / arch /
  seq) plus a wcwidth verify-loop keep full-width characters aligned where
  eyeballed padding silently breaks. Pure Python; no Mermaid renderer needed.
  ```

  Bump `ascii-graph-toolkit/.claude-plugin/plugin.json` version 0.4.0 →
  0.5.0; update `.claude-plugin/marketplace.json` (root) ascii-graph-toolkit
  entry description to stay consistent with the new SKILL.md description
  intent (marketplace copy stays one-line).
- Module: ascii-graph-toolkit/skills/ascii-graph
- Files touched: ascii-graph-toolkit/skills/ascii-graph/SKILL.md,
  ascii-graph-toolkit/.claude-plugin/plugin.json,
  ascii-graph-toolkit/.codex-plugin/plugin.json,
  .claude-plugin/marketplace.json,
  ascii-graph-toolkit/scripts/test_trigger_card.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/SKILL.md
  - docs/loom/memory/skill-triggering-diagnose-listing-before-text.md
  - docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md
- Acceptance:
  - RED: ascii-graph-toolkit/scripts/test_trigger_card.py::test_description_is_action_moment
    fails (description still the noun phrase)
  - GREEN: SKILL.md description starts with "Use BEFORE", contains exactly
    one CJK phrase segment, ≤1024 chars; plugin.json version == "0.5.0";
    marketplace.json ascii-graph-toolkit description mentions the
    before-you-draw trigger; full test file passes
- External surfaces: Claude Code skill-listing description budget
  (per-skill cap 1536 chars; keep ≤1024 for margin).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "description rewritten as an action-moment sentence
  … at most one representative CJK trigger phrase" + "marketplace.json
  description synced; plugin.json version bump" (Smallest End State PR1.2,
  PR1.3)

## Task 3 — loom-pipeline reception preloads §Visual defaults

- Description: Extend `loom-pipeline/hooks/session-start` so the injected
  reception context additionally contains the `### (b) Visual defaults`
  section of `hooks/family-relay.md`, extracted AT RUNTIME (sed/awk range
  over the heading boundaries) — no duplicated rule text committed anywhere
  (pointer-not-copy stays intact; family-relay.md remains SSOT). Preserve
  the existing fail-open behavior. Bump loom-pipeline plugin.json version
  (0.6.1 → 0.7.0).
- Module: loom-pipeline/hooks
- Files touched: loom-pipeline/hooks/session-start,
  loom-pipeline/scripts/test_family_relay.py,
  loom-pipeline/.claude-plugin/plugin.json,
  loom-pipeline/.codex-plugin/plugin.json
- Context paths:
  - loom-pipeline/hooks/session-start
  - loom-pipeline/hooks/family-relay.md
  - loom-pipeline/scripts/test_family_relay.py
  - docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md
- Acceptance:
  - RED: loom-pipeline/scripts/test_family_relay.py::test_reception_includes_visual_defaults
    fails (session-start output lacks the Visual-defaults lines)
  - GREEN: running `loom-pipeline/hooks/session-start` emits
    additionalContext containing both "ascii-graph-toolkit" and "markdown
    comparison table" sourced from family-relay.md §(b) (assert extraction,
    e.g. by mutating a temp copy — content change in family-relay.md must
    be reflected in output without editing session-start); existing 6
    test functions in test_family_relay.py still pass; plugin.json
    version == "0.7.0"
- External surfaces: Claude Code SessionStart hook contract (same as
  Task 1 — `hookEventName` stays present in the emitted JSON).
- Dependencies: none
- Independent: true
- Brief item covered: "session-start additionally extracts family-relay.md
  §(b) Visual defaults at runtime and appends it to the injected reception
  card" (Smallest End State PR2.1, PR2.3)

## Task 4 — brainstorming SKILL.md operative visual line

- Description: Add the operative one-liner to
  `loom-code/skills/brainstorming/SKILL.md` §Visual companion: flow/state
  diagrams in briefs and user-facing summaries are GENERATED via
  `ascii-graph-toolkit` (or Mermaid where the channel renders it), never
  hand-drawn box art — pointing at family-relay.md §(b) as the SSOT for
  the channel rule. Keep total word count ≤4,500 (CHK-SKL-010; current
  3,562). Bump loom-code plugin.json version (0.28.0 → 0.28.1).
- Module: loom-code/skills/brainstorming
- Files touched: loom-code/skills/brainstorming/SKILL.md,
  loom-pipeline/scripts/test_family_relay.py,
  loom-code/.claude-plugin/plugin.json,
  loom-code/.codex-plugin/plugin.json
- Context paths:
  - loom-code/skills/brainstorming/SKILL.md
  - loom-pipeline/scripts/test_family_relay.py
  - scripts/check-skill-structure.py
  - docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md
- Acceptance:
  - RED: loom-pipeline/scripts/test_family_relay.py::test_brainstorming_visual_operative_line
    fails (SKILL.md §Visual companion lacks the generated-not-hand-drawn
    rule)
  - GREEN: SKILL.md §Visual companion contains "ascii-graph-toolkit" and a
    not-hand-drawn operative phrase; `python3 scripts/check-skill-structure.py`
    passes CHK-SKL-010 for the file; loom-code plugin.json version ==
    "0.28.1"; full test_family_relay.py passes
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "brainstorming SKILL.md §Visual companion gains the
  operative one-liner … word headroom OK" (Smallest End State PR2.2, PR2.3)

## Notes

- **Two shipping waves**: Tasks 1-2 ship as PR1 from branch
  `more-visualization` (ascii-graph-toolkit 0.5.0); Tasks 3-4 ship as PR2
  from a separate branch (loom-pipeline 0.7.0 + loom-code 0.28.1). The
  `Dependencies` field is within-plan; PR grouping does not add dependency
  edges (Task 3 does not depend on Tasks 1-2).
- Task 2 and Task 4 share no files across waves; they stay
  `Independent: false` only because each depends on its wave's predecessor
  (shared test file within the wave).
- Review weight: all four tasks are hook / trigger-surface work — full
  review triad per task, no `Review-weight: mechanical` claims
  (docs/loom/memory/gate-review-weight-on-task-kind-not-loc.md).
- CI reminder: conventional-commit type whitelist + mandatory single scope
  (machine memory feedback_cc_type_whitelist); never `git add -A`.
- Version bumps MUST sync the Codex manifest: run
  `python3 scripts/sync_codex_manifests.py <plugin>` after editing
  `.claude-plugin/plugin.json` (CI drift gate `--check`; AGENTS.md
  §Commands). Amended post-PASS: additive Files-touched extension on
  Tasks 2/3/4 (`.codex-plugin/plugin.json`), schema/DAG unchanged —
  re-review skipped per writing-plans §Amending a PASS plan (b).
