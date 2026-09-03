# loom-code artifact-chain inventory

Repo root: `/Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow`
Plugin: `loom-code` (14 skills under `loom-code/skills/*/SKILL.md`)
Method: direct read of every SKILL.md (full or targeted grep+read of dense
sections), skim of `hooks/*.md`, `agents/*.md` headers, and the marker CLI
`scripts/loom_gate_markers.py` docstring for the ground-truth marker schema.

---

## using-loom-code
- Purpose (plain words, 1 line): Router — decides which loom-code skill to invoke next; writes nothing itself.
- Entered via: user says "build/change/debug/review code"; family-reception.md's rule "要用 loom-X 就從 using-loom-X 開始" (`loom-code/hooks/family-reception.md:19-20`)
- INPUTS: chat context only (no file reads named in the router body) — `loom-code/skills/using-loom-code/SKILL.md:1-127` (whole file scanned, no path pattern read)
- OUTPUTS: none — `loom-code/skills/using-loom-code/SKILL.md:104` ("Does **not** write or review code itself — it routes")
- CONSUMERS: n/a (writes nothing)
- TERMS INTRODUCED: none new; table names the 8 pipeline stages — `loom-code/skills/using-loom-code/SKILL.md:47-57`
- MECHANISMS INVOKED: Skill tool dispatch only; no scripts of its own
- GATES: refuses "just push"/"just ask" rationalizations (5 load-bearing rules) — `loom-code/skills/using-loom-code/SKILL.md:15-23`

## brainstorming
- Purpose (plain words, 1 line): Forces exploration of intent/alternatives (5-axis framework) before any code is written; produces a written brief.
- Entered via: `using-loom-code` Stage 1 (Discovery) — `loom-code/skills/using-loom-code/SKILL.md:49`
- INPUTS:
  - `docs/loom/backlog/` (ready-check via `scripts/backlog_index.py --ready`) — `loom-code/skills/brainstorming/SKILL.md:63-65`
  - `docs/loom/KICKOFF-DEFAULTS.md` (`## On-ramp standing choices`) — `loom-code/skills/brainstorming/SKILL.md:67,76-77`
  - `docs/loom/maps/` (live-map check, delegates to `loom-workflow:decision-map`) — `loom-code/skills/brainstorming/SKILL.md:73`
  - `docs/loom/PURPOSE.md` (`**Why:**` line, for direction banner) — `loom-code/skills/brainstorming/SKILL.md:75`
  - distribution/sync script (e.g. `distribute.py`) to determine SSOT direction — `loom-code/skills/brainstorming/SKILL.md:155`
- OUTPUTS:
  - `docs/loom/specs/<date>-<topic>.md` — the **brief** — `loom-code/skills/brainstorming/SKILL.md:149`
  - (conditional) `docs/loom/loom_init.py`-scaffolded backlog/KICKOFF-DEFAULTS store, offered once — `loom-code/skills/brainstorming/SKILL.md:67-71`
- CONSUMERS:
  - `writing-plans` reads the brief at `docs/loom/specs/<date>-<topic>.md` — `loom-code/skills/writing-plans/SKILL.md:24,208`
- TERMS INTRODUCED:
  - `brief — the structured deliverable of brainstorming that writing-plans consumes` — `loom-code/skills/brainstorming/SKILL.md:117-119`
  - `Axis 0-5 — the 5-axis exploration framework (Upstream artifacts / Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete)` — `loom-code/skills/brainstorming/SKILL.md:41-43,57,79,87,93,99,109`
  - `on-ramp — family reception's criteria table for detour vs direct kickoff` — `loom-code/skills/brainstorming/SKILL.md:59,77`
  - `Direction banner — one printed line quoting PURPOSE.md's Why line at kickoff` — `loom-code/skills/brainstorming/SKILL.md:75`
- MECHANISMS INVOKED: `scripts/backlog_index.py`, `scripts/loom_init.py`, `scripts/check_field_microstructure.py --brief`
- GATES: HARD-GATE "do not start implementing until intent explored" (`SKILL.md:12-16`); brief self-check exit 0/1/2 (`SKILL.md:151`); Axis 0 ask-once gate when no standing choice (`SKILL.md:77`)

## writing-plans
- Purpose (plain words, 1 line): Splits a brief (or loom-design change-folder) into an atomic, dependency-graphed task plan for SDD.
- Entered via: `using-loom-code` Stage 2 (Planning), after brainstorming produces a brief — `loom-code/skills/writing-plans/SKILL.md:4,24`
- INPUTS:
  - `docs/loom/specs/<date>-<topic>.md` (the brief) — `loom-code/skills/writing-plans/SKILL.md:24,208`
  - `docs/loom/<change-id>/` (loom-design change-folder, validated via `validate_spec_output.py`) — `loom-code/skills/writing-plans/SKILL.md:288`
  - `docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md` (change-folder detection evidence) — `loom-code/skills/writing-plans/SKILL.md:290`
- OUTPUTS:
  - `docs/loom/plans/<date>-<topic>.md` — the **plan** — `loom-code/skills/writing-plans/SKILL.md:203,324`
  - plan-document-reviewer verdict embedded in the plan header (`Plan-document-reviewer verdict: PENDING → PASS`) — `loom-code/skills/writing-plans/SKILL.md:212`
- CONSUMERS:
  - `subagent-driven-development` reads the plan for task dispatch — `loom-code/skills/writing-plans/SKILL.md:21,30-37` (pipeline diagram)
  - `finishing-a-development-branch` reads/flips plan `Stage:` field — `loom-code/skills/finishing-a-development-branch/SKILL.md:178`
  - `dispatching-parallel-agents` reads `Independent:`/`Files touched` fields — `loom-code/skills/writing-plans/SKILL.md:283`
- TERMS INTRODUCED:
  - `plan — the reviewed task DAG at docs/loom/plans/<date>-<topic>.md` — `loom-code/skills/writing-plans/SKILL.md:201-203`
  - `Task — one unit with one RED/GREEN test + one module boundary` — `loom-code/skills/writing-plans/SKILL.md:14-18,239-263`
  - `Review Batch — a group of Tasks sharing one aggregate reviewer fan-out` — `loom-code/skills/writing-plans/SKILL.md:266-279`
  - `plan-document-reviewer — the self-review prompt-file role for a plan` — `loom-code/skills/writing-plans/SKILL.md:99-101`
  - `Stage — plan lifecycle enum: planning | sdd:wave-N | review:round-N | blocked:user-decision | finishing` — `loom-code/skills/writing-plans/SKILL.md:212`
  - `Seam — the field naming what a dependent task consumes from its predecessor` — `loom-code/skills/writing-plans/SKILL.md:254`
  - `Status — per-task progress ledger field (pending/implemented(<sha>)/done(<sha>)/etc.)` — `loom-code/skills/writing-plans/SKILL.md:262`
  - `kickoff briefing — the pre-SDD batch of one-way-door decisions` — `loom-code/skills/writing-plans/SKILL.md:181-183`
- MECHANISMS INVOKED: `scripts/check_field_microstructure.py`, `scripts/check_scenario_coverage.py`, `scripts/plan_card.py`, `references/plan-document-reviewer-prompt.md` dispatched as evaluator
- GATES: 2-round NEEDS_REVISION cap with structural-split escape hatch (`SKILL.md:83`); field-microstructure gate blocks drafting/review (`SKILL.md:156`); scenario-coverage gate blocks PASS (`SKILL.md:326`); mandatory kickoff briefing before SDD (`SKILL.md:183`)

## subagent-driven-development
- Purpose (plain words, 1 line): Orchestrates per-task implementer + reviewer triads (and optional aggregate Batch review) against a plan, executing continuously until all tasks are done.
- Entered via: `using-loom-code` Stage 3 (Execution) — `loom-code/skills/using-loom-code/SKILL.md:51`; fires when task >1hr or >1 module — `loom-code/skills/subagent-driven-development/SKILL.md:4`
- INPUTS:
  - `docs/loom/plans/<date>-<topic>.md` (the plan, incl. `## Review Batches`) — `loom-code/skills/subagent-driven-development/SKILL.md:115-133`
  - `loom-code/agents/implementer.md` (dispatched-agent input contract) — `loom-code/skills/subagent-driven-development/SKILL.md:143`
  - handed-down live-gate packet env vars (`LOOM_LIVE_GATE_PACKET` etc.) — `loom-code/skills/subagent-driven-development/SKILL.md:10-18`
- OUTPUTS:
  - plan `Status` field flips (`implemented(<sha>)`, `done(<sha>)`) written via `plan_card.py` — `loom-code/skills/subagent-driven-development/SKILL.md:270`
  - plan `## Decision Log` entries — `loom-code/skills/subagent-driven-development/SKILL.md:272`
  - reviewer dispatch receipt (`record-dispatch` subcommand output JSON) — `loom-code/skills/subagent-driven-development/SKILL.md:218-227`
  - implementation commits (via implementer subagents, one per task)
- CONSUMERS:
  - `finishing-a-development-branch` invoked automatically once all tasks DONE — `loom-code/skills/subagent-driven-development/SKILL.md:29`
  - `requesting-code-review` reads the same plan's `Review Batches` disposition indirectly through the reviewer contract described here
- TERMS INTRODUCED:
  - `Packet / ReviewPacket — the sealed, immutable evidence bundle for one reviewer fan-out` — `loom-code/skills/subagent-driven-development/SKILL.md:205-215`
  - `ExecutionAuthorityProjection — sealed current-plan projection issued before Packet construction` — `loom-code/skills/subagent-driven-development/SKILL.md:203`
  - `SafeResolutionReceipt — the resolved-verification evidence required to materialize a Packet` — `loom-code/skills/subagent-driven-development/SKILL.md:208-211`
  - `wave — a set of Independent:true tasks dispatched in one fan-out step` — `loom-code/skills/subagent-driven-development/SKILL.md:150` ("When the wave completes...")
  - `Batch review checkpoint — the review gate over an eligible set of atomic Tasks post-implementation` — `loom-code/skills/subagent-driven-development/SKILL.md:189-201`
  - `finalize / reopen / individual_fallback / wait_refuse — the four Batch result outcomes from resolve_aggregate_review` — `loom-code/skills/subagent-driven-development/SKILL.md:253-261`
  - `Progress ledger — the plan's per-task Status field, sole SSOT` — `loom-code/skills/subagent-driven-development/SKILL.md:270`
  - `Live-gate receipt — the SDD-only proof-of-packet-consumption written under a live-gate station` — `loom-code/skills/subagent-driven-development/SKILL.md:8-18`
- MECHANISMS INVOKED: `scripts/live_gate_station_receipt.py`, `scripts/check_review_batches.py`, `scripts/review_context.py` (+ `--validate`), `scripts/batch_review_cli.py` (ready/packet/record-dispatch/apply-result), `scripts/plan_card.py`, `verification-before-completion`'s test-command resolver
- GATES: mandatory-new-plan-intake checker before any Task claim (`SKILL.md:117-122`); Packet construction fail-closed sequence checker→projection→Packet→dispatch (`SKILL.md:203-205`); `MALFORMED_PACKET` re-dispatch-once rule (`SKILL.md:295`); `Review-weight: mechanical` marker must come from the plan, never improvised (`SKILL.md:307`)

## tdd-iron-law
- Purpose (plain words, 1 line): No production code without a failing test first — the RED-GREEN-REFACTOR discipline enforced on every implementer.
- Entered via: `using-loom-code` Stage 4 (Discipline, during execution) — `loom-code/skills/using-loom-code/SKILL.md:52`; also invoked directly before any implementation
- INPUTS: chat/task context only — no file path pattern read (whole `SKILL.md` scanned, `loom-code/skills/tdd-iron-law/SKILL.md:1-111`)
- OUTPUTS: none (no artifact path written by this skill itself; it disciplines code the implementer writes) — `loom-code/skills/tdd-iron-law/SKILL.md:1-111`
- CONSUMERS: n/a
- TERMS INTRODUCED:
  - `Iron Law — no production code without a failing test first` — `loom-code/skills/tdd-iron-law/SKILL.md:8-14`
  - `Red-Green-Refactor — the only TDD cycle` — `loom-code/skills/tdd-iron-law/SKILL.md:26-40`
  - `Characterization Tests — Feathers' legacy-code backfill technique, not an Iron Law violation` — `loom-code/skills/tdd-iron-law/SKILL.md:71`
  - `False-green diagnostic — 4-step check that a passing-on-first-run test is real` — `loom-code/skills/tdd-iron-law/SKILL.md:88-97`
- MECHANISMS INVOKED: none of its own; `standards/tdd-standard.md` functional copy referenced
- GATES: "Delete the code. Write the test. Start over." consequence for violation — `loom-code/skills/tdd-iron-law/SKILL.md:14`

## systematic-debugging
- Purpose (plain words, 1 line): 4-phase gate (REPRODUCE→ISOLATE→HYPOTHESIZE→VERIFY) for investigating bugs; no fixing without reproducing.
- Entered via: `using-loom-code` Stage 5 (Repair, when stuck) — `loom-code/skills/using-loom-code/SKILL.md:53`; also invoked from tdd-iron-law's False-green diagnostic and SDD implementer BLOCKED — `loom-code/skills/systematic-debugging/SKILL.md:106-107`
- INPUTS: chat/task context only — whole file scanned, `loom-code/skills/systematic-debugging/SKILL.md:1-143`
- OUTPUTS: none (produces a regression test via handoff to tdd-iron-law, not written by this skill itself) — `loom-code/skills/systematic-debugging/SKILL.md:83` ("Write a regression test")
- CONSUMERS: n/a
- TERMS INTRODUCED:
  - `Repro quality — 🟢 Reliable / 🟡 Intermittent / 🔴 Cannot reproduce` — `loom-code/skills/systematic-debugging/SKILL.md:43-47`
  - `Anchored-thinking guard — mandatory WebSearch after 2 falsifications` — `loom-code/skills/systematic-debugging/SKILL.md:90-100`
- MECHANISMS INVOKED: none of its own; delegates to WebSearch, references `condition-based-waiting.md`, `root-cause-tracing.md`, `defense-in-depth.md`, `character-encoding-debug.md`
- GATES: Phase-to-phase gates (`SKILL.md:49,65,75,88`); HARD-GATE "no fixing without reproducing" (`SKILL.md:12-14`)

## dispatching-parallel-agents
- Purpose (plain words, 1 line): Fan out N independent subagents (across-task/domain) in one message when domains are proven disjoint; not a within-task mechanism.
- Entered via: `using-loom-code` §Auxiliary, or the SDD auto-suggest hook when ≥2 plan tasks are `Independent: true` — `loom-code/skills/using-loom-code/SKILL.md:62,64`
- INPUTS:
  - plan's `Independent: true` / `Files touched` fields — `loom-code/skills/dispatching-parallel-agents/SKILL.md:85,95`
  - `loom-code/agents/implementer.md` (per-branch TDD contract) — `loom-code/skills/dispatching-parallel-agents/SKILL.md:75`
- OUTPUTS:
  - plan `Status` field entries `claimed(@<branch>)`, `done(<sha>)`, `blocked` (mode-b shared ledger) — `loom-code/skills/dispatching-parallel-agents/SKILL.md:95`
- CONSUMERS:
  - `writing-plans/references/plan-format.md` owns the Status grammar these writes conform to — `loom-code/skills/dispatching-parallel-agents/SKILL.md:95`
- TERMS INTRODUCED:
  - `mode (a) / mode (b) — one-orchestrator-fan-out vs separate-sessions-in-one-repo dispatch` — `loom-code/skills/dispatching-parallel-agents/SKILL.md:91`
  - `Shared ledger — plan Status entries coordinating mode-b sessions` — `loom-code/skills/dispatching-parallel-agents/SKILL.md:95`
- MECHANISMS INVOKED: none of its own; uses host Agent-call fan-out; delegates integration check to `verification-before-completion`
- GATES: "Prove independent domains" 3-condition checklist before dispatch — `loom-code/skills/dispatching-parallel-agents/SKILL.md:30-38`; mandatory refusals list — `loom-code/skills/dispatching-parallel-agents/SKILL.md:102-110`

## requesting-code-review
- Purpose (plain words, 1 line): Whole-branch two-arm code-reviewer panel that must PASS before any push/merge/PR; mints the push-gate marker.
- Entered via: `using-loom-code` Stage 6 (Review) — `loom-code/skills/using-loom-code/SKILL.md:54`; also fires as Push-as-trigger when `git push`/`gh pr create`/`gh pr merge` is attempted without a prior PASS — `loom-code/skills/requesting-code-review/SKILL.md:48`
- INPUTS:
  - branch diff via `scripts/review_context.py --repo <path>` (produces `target_repo`,`reviewed_sha`,`plugin_version`,`resources`) — `loom-code/skills/requesting-code-review/SKILL.md:100`
  - `docs/loom/PRINCIPLES.md` (principles-conformance, self-derived) — `loom-code/skills/requesting-code-review/SKILL.md:114`
  - `LOOM-SIMPLIFY:` markers in changed source files (deliberate-simplification ledger harvest) — `loom-code/skills/requesting-code-review/SKILL.md:116`
- OUTPUTS:
  - `<git-dir>/loom/review-pass.json` (via `loom_gate_markers.py review-pass` or `mint --review-na-record-only`) — `loom-code/scripts/loom_gate_markers.py:11-25`; skill call sites `loom-code/skills/requesting-code-review/SKILL.md:105,124`
- CONSUMERS:
  - `hooks/git-guard.py` PreToolUse gate reads `review-pass.json` before allowing `git push`/`gh pr create` — `loom-code/hooks/git-guard.py:22,695`
  - `finishing-a-development-branch` Step 1/Phase 1 invokes this skill and reads its verdict — `loom-code/skills/requesting-code-review/SKILL.md:223`
- TERMS INTRODUCED:
  - `contract-class vs record-class — the .md routing classification` — `loom-code/skills/requesting-code-review/SKILL.md:62-64`
  - `simplification_ledger — the harvested LOOM-SIMPLIFY: shortcut records attached to a verdict` — `loom-code/skills/requesting-code-review/SKILL.md:116-124,175`
  - `review-pass marker — the .git/loom/review-pass.json gate artifact` — `loom-code/scripts/loom_gate_markers.py:11`
  - `dead-arm rule — single-arm degraded-evidence fallback after one re-dispatch` — `loom-code/skills/requesting-code-review/SKILL.md:115`
  - `deliberate-simplification ledger — scope-bounded branch-shortcut records with ceiling/upgrade/ref` — `loom-code/skills/requesting-code-review/SKILL.md:116-124`
- MECHANISMS INVOKED: `scripts/live_gate_station_receipt.py`, `scripts/review_context.py` (+`--validate`), `scripts/review_scope.py`, `scripts/plan_card.py --set-stage`, `scripts/loom_gate_markers.py`, dispatched agent `loom-code/agents/code-reviewer.md`
- GATES: Push-as-trigger block (no prior PASS this session → block push) — `loom-code/skills/requesting-code-review/SKILL.md:48`; aggregation rule (any 🔴 or ≥2 🟡 → NEEDS_REVISION) — `loom-code/skills/requesting-code-review/SKILL.md:186-193`; review-loop convergence cap (round 1 + ≤2 delta-confirmation cycles) — `loom-code/skills/requesting-code-review/SKILL.md:126`

## requesting-docs-review
- Purpose (plain words, 1 line): Whole-artifact two-arm docs-reviewer panel for changed `.md` files (5 prose dimensions), single-round-plus-one-confirmation contract; docs arm of requesting-code-review's routing.
- Entered via: `requesting-code-review` Step 1 routing when the branch diff is docs-only or mixed — `loom-code/skills/requesting-docs-review/SKILL.md:39-40`; also direct "review my docs" — `loom-code/skills/requesting-docs-review/SKILL.md:41`
- INPUTS:
  - immutable context packet from `review_context.py` (adopted or self-resolved) — `loom-code/skills/requesting-docs-review/SKILL.md:66`
  - citation pre-pass via `scripts/check_doc_citations.py` — `loom-code/skills/requesting-docs-review/SKILL.md:71`
  - `resolved-scope` handed down from `requesting-code-review` (contract-class `.md` subset) — `loom-code/skills/requesting-docs-review/SKILL.md:70`
- OUTPUTS:
  - `<git-dir>/loom/review-pass.json` (shared marker, only when this skill owns the whole review) — `loom-code/skills/requesting-docs-review/SKILL.md:77,81`
- CONSUMERS:
  - `hooks/git-guard.py` reads the same `review-pass.json` — `loom-code/hooks/git-guard.py:22`
  - `requesting-code-review` receives the returned verdict (mixed-branch, non-mint path) — `loom-code/skills/requesting-docs-review/SKILL.md:77`
- TERMS INTRODUCED:
  - `CONVERGENCE CONTRACT (Directives 1-4) — round 1 whole-artifact only + one confirmation cycle` — `loom-code/skills/requesting-docs-review/SKILL.md:55-60`
  - `read-context — non-.md material a docs-reviewer opens to verify claims, never scored` — `loom-code/skills/requesting-docs-review/SKILL.md:73,89`
  - `read_context_findings / out_of_scope — non-gating verdict blocks` — `loom-code/skills/requesting-docs-review/SKILL.md:122-137`
  - `class: instruction | evidence — per-finding blocking classification` — `loom-code/skills/requesting-docs-review/SKILL.md:73,87`
- MECHANISMS INVOKED: `scripts/review_context.py`, `scripts/check_doc_citations.py`, `scripts/review_scope.py`, `scripts/loom_gate_markers.py`, dispatched agent `loom-code/agents/docs-reviewer.md`
- GATES: aggregation rule computed over instruction-class findings only — `loom-code/skills/requesting-docs-review/SKILL.md:83-92`; STILL_BLOCKING after one confirmation cycle → STOP — `loom-code/skills/requesting-docs-review/SKILL.md:58`

## ui-verification
- Purpose (plain words, 1 line): Drives the real rendered app through every state ui-flows.md enumerates before branch close; conditional gate, GUI-only.
- Entered via: `using-loom-code` Stage 7b (conditional) — `loom-code/skills/using-loom-code/SKILL.md:56`; fires only if branch touched UI AND `ui-flows.md` exists — `loom-code/skills/ui-verification/SKILL.md:20-29`
- INPUTS:
  - `docs/loom/<change-id>/ui-flows.md` (§1 inventory checklist) — `loom-code/skills/ui-verification/SKILL.md:24`
- OUTPUTS: none (verdict-only; no file written) — `loom-code/skills/ui-verification/SKILL.md:105-106`
- CONSUMERS: n/a
- TERMS INTRODUCED:
  - `verified / mismatch / unreachable / untestable — the four per-state classification outcomes` — `loom-code/skills/ui-verification/SKILL.md:60-70`
  - `half-measure — a weaker static check substituted for a real state drive, never counts as verified` — `loom-code/skills/ui-verification/SKILL.md:67-70`
- MECHANISMS INVOKED: `chrome-devtools` MCP or `agent-device` MCP (host-dependent); none of its own scripts
- GATES: two-valued verdict, no bare PASS — `loom-code/skills/ui-verification/SKILL.md:75-89`

## using-git-worktrees
- Purpose (plain words, 1 line): Convention + guardrails for running parallel branches via native `git worktree`, one branch per checkout under `.worktrees/`.
- Entered via: user request for parallel branches, or a brainstorming brief flagging a long design phase — `loom-code/skills/using-git-worktrees/SKILL.md:91`
- INPUTS: `.gitignore` (checked via `git check-ignore .worktrees/`) — `loom-code/skills/using-git-worktrees/SKILL.md:43`
- OUTPUTS:
  - `.worktrees/<branch-slug>/` checkout directories — `loom-code/skills/using-git-worktrees/SKILL.md:41-43,56-68`
  - `.gitignore` entry `.worktrees/` (one-time setup commit) — `loom-code/skills/using-git-worktrees/SKILL.md:49-54`
- CONSUMERS:
  - `finishing-a-development-branch` cleanup phase invokes `git worktree remove` on close — `loom-code/skills/using-git-worktrees/SKILL.md:92`
- TERMS INTRODUCED: none new (uses native `git worktree` vocabulary) — `loom-code/skills/using-git-worktrees/SKILL.md:12-17`
- MECHANISMS INVOKED: native `git worktree add|remove|prune|list`
- GATES: refuses existing path / branch already attached to a worktree — `loom-code/skills/using-git-worktrees/SKILL.md:43`; `git worktree remove` refuses on uncommitted changes — `loom-code/skills/using-git-worktrees/SKILL.md:81`

## loom-memory
- Purpose (plain words, 1 line): Record/recall/prune the repo-native practice-memory store; conditional — N/A if the repo has no store charter.
- Entered via: user says "有沒有相關經驗"/"記住這個做法" etc., or `finishing-a-development-branch`'s memory-timing check — `loom-code/skills/loom-memory/SKILL.md:11-12`; `loom-code/skills/finishing-a-development-branch/SKILL.md:173`
- INPUTS:
  - `docs/loom/memory/README.md` (charter; fires only if present) — `loom-code/skills/loom-memory/SKILL.md:22-23`
  - `docs/loom/memory/` index + bodies (grep before write; recall) — `loom-code/skills/loom-memory/SKILL.md:49-50,70-72`
- OUTPUTS:
  - `docs/loom/memory/<slug>.md` — `loom-code/skills/loom-memory/SKILL.md:55-56`
  - `docs/loom/memory/README.md` `## Index` (regenerated) — `loom-code/skills/loom-memory/SKILL.md:57-58`
  - `docs/loom/backlog/` entry (when classified as backlog-shaped) — `loom-code/skills/loom-memory/SKILL.md:43`
- CONSUMERS:
  - `finishing-a-development-branch`'s "Memory-store integrity" row runs the same integrity checker before close-out commit — `loom-code/skills/finishing-a-development-branch/SKILL.md:174`
  - future `loom-memory` recall invocations read this store — `loom-code/skills/loom-memory/SKILL.md:68-72`
- TERMS INTRODUCED:
  - `record / recall / prune — the three verbs over the practice-memory store` — `loom-code/skills/loom-memory/SKILL.md:18,39,68,82`
  - `keep / merge / retire — the three prune verdicts` — `loom-code/skills/loom-memory/SKILL.md:93-101`
- MECHANISMS INVOKED: `scripts/check_loom_memory_integrity.py` (`--write`, `--check`)
- GATES: N/A-loud gate when charter absent — `loom-code/skills/loom-memory/SKILL.md:20-26`; never delete without explicit user approval — `loom-code/skills/loom-memory/SKILL.md:103`

## verification-before-completion
- Purpose (plain words, 1 line): Requires a real package-level test-suite run (with evidence) before anything can be declared "done"; mints the verified marker.
- Entered via: `using-loom-code` Stage 7 (Verification) — `loom-code/skills/using-loom-code/SKILL.md:55`; fires on "I'm done"/"ready to ship" without shown invocation — `loom-code/skills/verification-before-completion/SKILL.md:4`
- INPUTS:
  - project's declared test command (`AGENTS.md`, `make`/`just`, `package.json` scripts) — `loom-code/skills/verification-before-completion/SKILL.md:57`
- OUTPUTS:
  - `<git-dir>/loom/verified.json` (via `loom_gate_markers.py verified --run "<cmd>"`) — `loom-code/skills/verification-before-completion/SKILL.md:61`; schema `loom-code/scripts/loom_gate_markers.py:28-38`
- CONSUMERS:
  - `hooks/git-guard.py` PreToolUse gate requires it fresh (bound to current HEAD sha) before push — `loom-code/skills/verification-before-completion/SKILL.md:61`; `loom-code/hooks/git-guard.py:25,707`
  - `finishing-a-development-branch` Phase 2 invokes this skill, then Step 9c re-mints at final HEAD — `loom-code/skills/finishing-a-development-branch/SKILL.md:27,216-220`
- TERMS INTRODUCED:
  - `verified marker — the .git/loom/verified.json test-suite-green artifact bound to HEAD sha` — `loom-code/scripts/loom_gate_markers.py:28-38`
- MECHANISMS INVOKED: `scripts/loom_gate_markers.py verified`
- GATES: HARD-GATE "no DONE without package-level test invocation" — `loom-code/skills/verification-before-completion/SKILL.md:12-16`; exit-0-with-0-tests treated as configuration bug, not pass — `loom-code/skills/verification-before-completion/SKILL.md:59`

## finishing-a-development-branch
- Purpose (plain words, 1 line): The branch-close orchestrator — review → verification → git-memory commit → push → optional PR/CI-repair → optional worktree cleanup; never auto-merges.
- Entered via: `using-loom-code` Stage 8 (Branch close) — `loom-code/skills/using-loom-code/SKILL.md:57`; fires on "finish this branch"/"ship it" — `loom-code/skills/finishing-a-development-branch/SKILL.md:4`
- INPUTS:
  - the branch's plan `docs/loom/plans/<date>-<topic>.md` (for Stage-flip and change-folder binding detection) — `loom-code/skills/finishing-a-development-branch/SKILL.md:172,178`
  - `docs/loom/PURPOSE.md` (purpose-linked betting check) — `loom-code/skills/finishing-a-development-branch/SKILL.md:184`
  - `docs/loom/backlog/` (backlog-close check, review-due reminder) — `loom-code/skills/finishing-a-development-branch/SKILL.md:175-176`
- OUTPUTS:
  - `docs/loom/INDEX.md` (regenerated living-spec index) — `loom-code/skills/finishing-a-development-branch/SKILL.md:171`
  - `docs/loom/archive/<date>-<change-id>/` (archive-on-close move) — `loom-code/skills/finishing-a-development-branch/SKILL.md:172`
  - `docs/loom/memory/*.md` (staged into close-out commit, delegates to `loom-memory`) — `loom-code/skills/finishing-a-development-branch/SKILL.md:173`
  - `docs/loom/plans/<plan>.md` Stage flip to `finishing` — `loom-code/skills/finishing-a-development-branch/SKILL.md:178`
  - `<git-dir>/loom/{verified.json,review-pass.json,waiver.json}` minted at final HEAD — `loom-code/skills/finishing-a-development-branch/SKILL.md:215-225`
  - a close-out git commit + `git push` + optional `gh pr create` PR — `loom-code/skills/finishing-a-development-branch/SKILL.md:227-251`
- CONSUMERS:
  - `hooks/git-guard.py` reads the minted markers before allowing the push it triggers — `loom-code/hooks/git-guard.py:22,25`
  - GitHub / `gh pr view`/`gh pr merge` read the opened PR — `loom-code/skills/finishing-a-development-branch/SKILL.md:252,276`
- TERMS INTRODUCED:
  - `waiver — one-shot .git/loom/waiver.json bypass of both push markers` — `loom-code/scripts/loom_gate_markers.py:46-49`; skill call site `loom-code/skills/finishing-a-development-branch/SKILL.md:225`
  - `archive-on-close — moving a consumed loom-design change-folder to docs/loom/archive/` — `loom-code/skills/finishing-a-development-branch/SKILL.md:172`
  - `Stage-flip duty — flipping the plan's Stage header to finishing before close-out commit` — `loom-code/skills/finishing-a-development-branch/SKILL.md:178`
  - `stale-scan — plan_card.py's advisory scan across docs/loom/plans/` — `loom-code/skills/finishing-a-development-branch/SKILL.md:180`
- MECHANISMS INVOKED: `scripts/check-living-spec-index.py`, `scripts/archive_change_folder.py`, `scripts/check_loom_memory_integrity.py`, `scripts/backlog_index.py`, `scripts/plan_card.py`, `scripts/check_north_star_link.py`, `scripts/post_pr_ci.py`, `scripts/loom_gate_markers.py`, `hooks/git-guard.py` (as the gate it must satisfy)
- GATES: `hooks/git-guard.py` PreToolUse gate blocks `git push`/`gh pr create` without both fresh markers — `loom-code/skills/finishing-a-development-branch/SKILL.md:215-217`; STOP-and-ask on unresolved `PURPOSE.md` — `loom-code/skills/finishing-a-development-branch/SKILL.md:184`; never auto-merge — `loom-code/skills/finishing-a-development-branch/SKILL.md:332`

---

## Totals

**Distinct artifact types written by this plugin** (canonical path pattern):

1. Brief — `docs/loom/specs/<date>-<topic>.md` (brainstorming)
2. Plan — `docs/loom/plans/<date>-<topic>.md` (writing-plans; mutated by SDD/requesting-code-review/finishing)
3. Memory entry — `docs/loom/memory/<slug>.md` (loom-memory)
4. Backlog entry — `docs/loom/backlog/<entry>.md` (loom-memory, brainstorming's loom_init.py, finishing's backlog-close row)
5. Living-spec index — `docs/loom/INDEX.md` (finishing-a-development-branch)
6. Archived change-folder — `docs/loom/archive/<date>-<change-id>/` (finishing-a-development-branch)
7. `verified` gate marker — `<git-dir>/loom/verified.json` (verification-before-completion, re-minted by finishing)
8. `review-pass` gate marker — `<git-dir>/loom/review-pass.json` (requesting-code-review, requesting-docs-review)
9. `waiver` gate marker — `<git-dir>/loom/waiver.json` (finishing-a-development-branch, one-shot)
10. `.worktrees/<branch-slug>/` checkout + `.gitignore` entry (using-git-worktrees)
11. Reviewer dispatch receipt / ReviewPacket / apply-result JSON (subagent-driven-development's `batch_review_cli.py`)
12. Git commit(s) + `git push` + opened PR (finishing-a-development-branch)
13. `docs/loom/KICKOFF-DEFAULTS.md` scaffold (brainstorming's loom_init.py, one-time offer)

**Distinct terms introduced (deduplicated):**
brief, on-ramp, Direction banner, Axis 0-5, plan, Task, Review Batch, plan-document-reviewer, Stage, Seam, Status (progress ledger), kickoff briefing, Packet/ReviewPacket, ExecutionAuthorityProjection, SafeResolutionReceipt, wave, Batch review checkpoint, finalize/reopen/individual_fallback/wait_refuse, Progress ledger, Live-gate receipt, Iron Law, Red-Green-Refactor, Characterization Tests, False-green diagnostic, Repro quality (🟢/🟡/🔴), Anchored-thinking guard, mode (a)/mode (b), Shared ledger, contract-class/record-class, simplification_ledger, review-pass marker, dead-arm rule, deliberate-simplification ledger, CONVERGENCE CONTRACT (Directives 1-4), read-context, read_context_findings/out_of_scope, class: instruction|evidence, verified/mismatch/unreachable/untestable, half-measure, record/recall/prune, keep/merge/retire, verified marker, waiver, archive-on-close, Stage-flip duty, stale-scan.

That is **44 distinct named terms** across 14 skills.

**Skills whose output has no consumer found:**
- `using-loom-code` — writes nothing (router only), n/a by construction.
- `tdd-iron-law` — writes nothing itself (disciplines code the implementer writes elsewhere).
- `systematic-debugging` — writes nothing itself (hands the regression test to tdd-iron-law's cycle, but does not itself produce a citable path).
- `dispatching-parallel-agents` — writes only the plan's `Status` field (mode-b), which is the same artifact `writing-plans`/`plan-format.md` already owns — not a distinct output type with its own consumer chain beyond that shared ledger.
- `ui-verification` — verdict-only, writes nothing (reads `ui-flows.md`, produces no file).
- `using-git-worktrees` — the `.worktrees/` checkout itself has no downstream *reader*; only `finishing-a-development-branch` *removes* it (cleanup, not consumption of content).

All other skills' outputs have at least one confirmed consumer (mostly `hooks/git-guard.py` for the three gate markers, and the next pipeline stage for brief/plan/memory/index/archive).
