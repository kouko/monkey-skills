# Plan: AFK research lane — kickoff fork-harvest parallel research subagents

**Source brief**: docs/loom/specs/2026-07-14-afk-research-lane.md
**Total tasks**: 5
**Critical-path depth**: 4 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-07-14 22:33, 14/14 checks, 0 gaps)

## Task 1 — §(b) fan-out/join execution rule + worker packet contract

- **Description**: In `kickoff-briefing.md` §(b), extend the Axis-4-lite paragraph (currently :51-58, ending at the arm-fold sentence :63-66) with the parallel execution rule: after triage marks M forks researchable, dispatch M research subagents in ONE fan-out step (point at `dispatching-parallel-agents/SKILL.md` §3 "Dispatch all N subagents in one fan-out step" — do not duplicate its mechanics); each worker carries a compact research packet = the fork statement + a pointer to `brainstorming/references/axis4-research-protocol.md` (EN+JA bilingual rule :18-20, shipped-options + recommendation contract :4) + report contract (approaches w/ citations + recommendation + conditional reversal, ≤30 lines, no file dumps); kickoff blocks until all M return (single join point — pins written once, ordering deterministic); orchestrator distills each return into the existing pinned format `Kickoff decision: <fork> → <resolution>` plus a one-line citation tail; findings exceeding pin size land under `docs/loom/research/` per existing convention, pin points at the file; the pay-per-hit sentence (zero forks = zero research) stays intact. Do NOT edit `axis4-research-protocol.md` (method SSOT untouched) and do NOT change the pin format (SDD grep key).
- **Module**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Files touched**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-14-afk-research-lane.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/kickoff-briefing.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/dispatching-parallel-agents/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/brainstorming/references/axis4-research-protocol.md
- **Acceptance**:
  - **RED**: `grep -c "one fan-out step" loom-code/skills/writing-plans/references/kickoff-briefing.md` returns 0
  - **GREEN**: §(b) contains the fan-out/join rule (grep hits for "one fan-out step" AND "join"), the worker packet contract with the ≤30-line report bound, and the `Kickoff decision:` pin block is byte-unchanged (`grep -c 'Kickoff decision: <fork> → <resolution>'` still 1)
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: Smallest End State item 1 "Fan-out: after triage marks M forks researchable, dispatch M research subagents in ONE fan-out step" + item 2 "Join: kickoff blocks until all M return… distills each return into the existing pinned format" + item 3 "Pay-per-hit unchanged"

## Task 2 — §(b) degradation notes (WebSearch-unavailable + Codex sequential floor)

- **Description**: Append the degradation rules to the §(b) block Task 1 produced: (a) a worker that finds WebSearch unavailable reports it per `axis4-research-protocol.md` `## If WebSearch is unavailable` (:55-66) — report, never imagine — and that fork falls back to triage arm 2 (direct ask with vintage caveat); (b) Codex host: when parallel fan-out is unavailable, sequential dispatch is the floor — the lane's research-then-pin semantics hold (one sentence; host tool mappings stay owned by `using-loom-code/references/{claude-code-tools,codex-tools}.md`, pointer only).
- **Module**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Files touched**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-14-afk-research-lane.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/kickoff-briefing.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/brainstorming/references/axis4-research-protocol.md
- **Acceptance**:
  - **RED**: `grep -c "WebSearch" loom-code/skills/writing-plans/references/kickoff-briefing.md` returns 0
  - **GREEN**: §(b) names both degradation paths (grep hits for "WebSearch" and a Codex sequential-floor sentence); `axis4-research-protocol.md` is byte-unchanged (`git diff --stat` shows no change to it)
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 4 "Degradation: WebSearch-unavailable inside a worker → … falls back to arm-2 (ask with vintage caveat). Codex host: sequential dispatch is the floor"

## Task 3 — §(f) mid-implementation single-worker pointer sentence

- **Description**: Add one pointer sentence to `kickoff-briefing.md` §(f) (:126-139): the mid-implementation firing point's single-fork case fires ONE background research subagent instead of inline research — same worker packet as §(b), no join complexity; SDD's ask-gate mechanics unchanged (pointer stays at `subagent-driven-development/SKILL.md` §Asking the user gate ①).
- **Module**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Files touched**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-14-afk-research-lane.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/kickoff-briefing.md
- **Acceptance**:
  - **RED**: `awk '/^## \(f\)/,0' loom-code/skills/writing-plans/references/kickoff-briefing.md | grep -c "background research subagent"` returns 0
  - **GREEN**: same command returns ≥1; the sentence points at §(b)'s packet rather than restating it
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 5 "§(f) mid-implementation firing point: single-fork case fires ONE background research subagent instead of inline research — same packet, no join complexity (pointer sentence, mechanics unchanged)"

## Task 4 — Bump loom-code 0.30.2 → 0.31.0 + CHANGELOG entry

- **Description**: In `loom-code/.claude-plugin/plugin.json:3` replace the exact literal `"version": "0.30.2"` with `"version": "0.31.0"`. In `loom-code/CHANGELOG.md`, insert above the `## [0.30.2]` entry (:8) a Keep-a-Changelog entry: heading `## [0.31.0] — 2026-07-14 — AFK research lane (kickoff fork-harvest parallel research subagents)`, `### Added` bullet describing §(b) fan-out/join execution rule + worker packet + degradation notes and §(f) single-worker pointer (kickoff-briefing.md), citing the brief path. No other changes.
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/loom-code/CHANGELOG.md
- **Acceptance**:
  - **RED**: `python3 scripts/check_version_bump.py` fails (skills/** changed by Tasks 1-3 while plugin.json still reads 0.30.2), or equivalently `grep -c '"version": "0.31.0"' loom-code/.claude-plugin/plugin.json` returns 0
  - **GREEN**: `check_version_bump.py` passes for loom-code; CHANGELOG has the `## [0.31.0] — 2026-07-14` entry above `## [0.30.2]`
- **Dependencies**: Tasks 2, 3 complete first
- **Independent**: false
- **Brief item covered**: Decision section "bump loom-code 0.31.0" + Smallest End State "Version: loom-code 0.30.2 → 0.31.0 (new behavior, minor). CHANGELOG."

## Task 5 — Mirror version bump into the Codex manifest (sync script)

- **Description**: SSOT is `loom-code/.claude-plugin/plugin.json`. Run `python3 scripts/sync_codex_manifests.py` (which mirrors shared fields into `loom-code/.codex-plugin/plugin.json`, preserving Codex-only `interface`) and commit the result unmodified. No hand-written edits to the output.
- **Module**: `loom-code/.codex-plugin/plugin.json`
- **Files touched**: `loom-code/.codex-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/scripts/sync_codex_manifests.py
  - /Users/kouko/GitHub/monkey-skills/loom-code/.claude-plugin/plugin.json
- **Acceptance**:
  - **RED**: `python3 scripts/sync_codex_manifests.py --check --all` exits nonzero (loom-code Codex manifest still at 0.30.2, drift detected)
  - **GREEN**: same command exits 0
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Review-weight**: mechanical
- **Brief item covered**: Smallest End State "Codex manifest sync."

## Notes

- Change-folder binding: input is a brainstorming brief via explicit handoff (Layer 0 — detection not run). For the record, the repo's single non-archived change-folder `docs/loom/2026-07-12-us-sec-primary-source-layer/` belongs to the investing arc and is unrelated; not bound.
- Brief correction (recon fact): the brief's packet wording「Axis-4 protocol pointer (EN+JA, shipped options, "My take" format)」— the literal string "My take" does not exist in `axis4-research-protocol.md`; the recommendation contract lives at its :4 protocol line and the EN+JA rule at :18-20. Task 1's packet text points at those real anchors instead of the "My take" label.
- Blast radius (recon): no committed test asserts `kickoff-briefing.md` content — prose RED checks are the grep diagnostics above. Consumers `subagent-driven-development/SKILL.md:34,:128` and `writing-plans/SKILL.md:119` reference the file by pointer only; the `Kickoff decision:` pin format is unchanged, so zero downstream schema impact.
- Tasks 1-3 all edit the same file — no parallel eligibility anywhere in this plan; SDD sequential dispatch throughout. Tasks 2 and 3 sit at the same dependency level (both need only Task 1) but share `Files touched`, so they stay sequential in listed order — Task 3's pointer sentence needs §(b)'s packet (Task 1), not Task 2's degradation notes.
- marketplace.json needs no edit: it carries per-plugin description (unchanged), not version (recon fact 7).

## Decision Log

1. chose host-agnostic conditional wording for the CHANGELOG's Codex note ("falls back to a sequential research floor when parallel fan-out is unavailable") because live verification shows Codex 0.139 can spawn subagents, so an absolute "no background-agent primitive" claim was false — cost-of-change: none; the conditional stays true whichever way host capabilities move
