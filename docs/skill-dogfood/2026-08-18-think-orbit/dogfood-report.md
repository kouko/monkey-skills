# Dogfood report — `think-orbit` (using-think-orbit / thinking-session / break-assumption)

> Behavioral dogfood per `skill-dev-toolkit:dogfood-skill-testing`. Findings are advisory and fix-actionable; the human is the final calibrator. No pass verdict is stamped (floor, not ceiling).

## Metadata

| Field | Value |
|---|---|
| Skill path | `think-orbit/skills/{using-think-orbit,thinking-session,break-assumption}` (installed copy `~/.claude/plugins/cache/monkey-skills/think-orbit/0.1.1` == main 34c6232c) |
| Skill version | 0.1.1 |
| Date | 2026-08-18 |
| Passes run | activation (real harness, 27 queries × 2 runs) · executor + 2 blind auditors · cold-reader |
| Model pinned | orchestrator claude-fable-5; Probe A via `claude -p` 2.1.234 default model; executor/auditors/cold-reader = session default (Fable) except Probe A runner + cold-reader on sonnet |
| Activation fidelity | real-harness sandbox (installed skill menu of this machine = distractor set); **caveat**: `--max-turns 2`, and this machine's global settings let `Bash` run despite `--allowedTools Skill` — recall numbers are a lower bound |
| Real material | Probe B used a real open question of the user's (backlog entry `2026-08-18-loom-decision-trail-as-dag-view-via-think-orbit-render`) with five real repo documents as sources; user turns were simulated from the user's documented stance (`[USER-SIM]`) — this is NOT the T12 real-material checkpoint (the user's own reading of the output is what T12 measures) |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 2 |
| Medium | 5 |
| Low | 5 |
| **Total** | 12 |

## Findings

### FINDING-001: Folder-mentioning requests never reach the skill — the agent inspects the path first, then asks (High · Trigger-miss · blind)
- **Probe**: A. Queries #0, #2, #5, #6, #10, #11, #13 (all mention a folder: 「資料夾在 ./decision」「I have notes in a folder」「資料は ./hiring にある」) — 0/14 runs fired any think-orbit skill.
- **Expected**: `using-think-orbit` fires; the router's own intake ladder resolves `<root>`.
- **Actual**: turn 1 = `Bash ls/find` on the path; turn 2 = ask the user to confirm the path — no `Skill()` call (`probe-a/summary.md`; raw JSONL in the runner's `/tmp/to-probe-nvgw-logs/`).
- **Root cause**: the descriptions describe *what* the plugin is, not that it *owns intake*; a router facing "think about X, sources in ./folder" reads the folder as the task and never considers the skill. Partly a harness artifact (`--max-turns 2`), but the first-move preference is real.
- **Why static review missed it**: description coherence checks and the SKILL tests only pin phrase presence, not the router's first move under a folder cue.
- **Location**: `using-think-orbit/SKILL.md` frontmatter `description`; `thinking-session/SKILL.md` description.
- **Suggested fix**: add to the router description an explicit ownership cue — e.g. "Invoke BEFORE inspecting any folder the user names: this skill owns intake (project directory, sources)"; mention "given a folder of notes / sources" as a trigger shape. Re-run Probe A queries #0/2/5/6/10/11/13.

### FINDING-002: `break-assumption` never fires standalone (High · Trigger-miss · blind)
- **Probe**: A. Queries #14–#17（「假設破了」「情況變了」「前提不成立了」/ "one of my assumptions just broke"）— 0/8 runs.
- **Actual**: the model answers "I have no prior context to trace" instead of loading the skill (`probe-a/summary.md`).
- **Root cause**: the description promises a break flow over an existing project, so without visible project state the router judges it inapplicable; the router `using-think-orbit` also does not list assumption-broke phrases strongly enough to fire and hand off.
- **Why static review missed it**: `test_break_assumption_skill_names_break_verb_and_two_followups` pins body literals, not routing.
- **Location**: `break-assumption/SKILL.md` description; `using-think-orbit/SKILL.md` description.
- **Suggested fix**: (a) put the assumption-broke phrases into `using-think-orbit`'s description as a first-class trigger (router fires, resolves `<root>`, hands off); (b) make `break-assumption`'s description say it applies whenever the user reports a premise changed — if no project is known, it starts by asking for `<root>` (or hands to the router). Re-run #14–#17.

### FINDING-003: `check` runs per batch, not per node boundary (Medium · Gate-bypass · informed)
- **Probe**: B. Executor wrote 6 FACT nodes in one second then ran `check` once; 13 nodes / 6 checks (`executor-transcript.md` :85-88, :104; both auditors flagged).
- **Expected**: SKILL says "after writing or editing any node/assumption file run `dag.py check`".
- **Root cause**: "boundary" is read as "after this batch of writes"; the SKILL never says one file = one check.
- **Location**: `thinking-session/SKILL.md` §gate.
- **Suggested fix**: state "one `check` per written file (or per user-visible turn), never per batch" — or accept batches explicitly and say so; add a transcript-checkable rule.

### FINDING-004: GOAL interrupt fires even when the opening message already states the goal (Medium · Workflow-drift · informed)
- **Probe**: B (`executor-transcript.md` :45 vs :14; both auditors and the executor flagged).
- **Root cause**: SKILL mandates "ask what the user wants to think through" unconditionally.
- **Location**: `thinking-session/SKILL.md` §first sitting, interrupt (a).
- **Suggested fix**: when the opening already names the goal, write the GOAL node and ask only for confirmation of the wording (one line), not the question again.

### FINDING-005: Cross-branch assumption forced into one branch by the ≤3-per-branch cap (Medium · Output-quality · informed)
- **Probe**: B. `part1_checkpoint_go` (user-supplied, pivotal for both branches and a non-branch CLAIM) filed under branch A only; a future `break` will not mark the nodes it actually affects (auditor #1 valid-but-wrong; auditor #2 C4).
- **Location**: `thinking-session/SKILL.md` §branches/assumptions; `node-schema.md` assumptions.
- **Suggested fix**: allow an assumption with `branch: null` (project-wide) or a list of branches; the ≤3 cap applies per branch, project-wide assumptions counted separately; nodes cite it via `inputs` explicitly.

### FINDING-006: FACT bodies leak inference ("so what" tails) (Medium · Output-quality · informed)
- **Probe**: B (`executor-project/nodes/gap_is_data_not_renderer.md:11`, `decision_log_shape.md:11`; both auditors).
- **Root cause**: SKILL defines FACT by frontmatter (source+quote) but says nothing about keeping the FACT body inference-free.
- **Location**: `thinking-session/SKILL.md` §node types; `node-schema.md`.
- **Suggested fix**: "a FACT body restates and contextualizes the quote; any 'this means…' sentence belongs in a CLAIM node that inputs the FACT."

### FINDING-007: `render`/`impact` are silent on success — the agent cannot tell the view was written without listing the folder (Medium · Convention-violation · informed)
- **Probe**: B (executor note 1: tempted to `cat views/dag.md`).
- **Location**: `dag.py render` (prints nothing); SKILL documents silence only for `check`.
- **Suggested fix**: `render` prints one line `dag view: views/dag.md` (as `break`/`impact` already print `impact view: …`); SKILL relays that path to the user.

### FINDING-008: `status` enum and `load_bearing` semantics are not in the SKILL body a cold reader sees (Low · Cold-start · blind)
- **Probe**: C. First-time reader stopped at writing the GOAL file's `status` field ("what other values exist? never enumerated") and met `load_bearing` at :71 before its explanation.
- **Location**: `thinking-session/SKILL.md` §minimal examples / §nodes.
- **Suggested fix**: one inline line: `status: current | stale (stale is written only by break)`; define `load_bearing` at first use.

### FINDING-009: `stale`/`weakened` defined only in break-assumption; router lists `break` without them (Low · Progressive-disclosure · blind)
- **Probe**: C.
- **Location**: `using-think-orbit/SKILL.md` verb table.
- **Suggested fix**: one clause in the router's `break` row.

### FINDING-010: Trivial "think" requests may over-fire in practice (Low · Over-trigger risk · blind, not observed)
- **Probe**: C named 「想一下晚餐吃什麼」「幫我想個標語」 as likely wrong fires; Probe A's distractors did not include such cases (0 over-triggers observed on the 7 should-NOT queries).
- **Suggested fix**: add a negative cue to the router description ("not for one-off casual choices or generative brainstorming of names/taglines") and add those two queries to the corpus.

### FINDING-011: 3/40 runs routed straight to `thinking-session`, skipping the router's intake ladder (Low · Workflow-drift · blind)
- **Probe**: A (#1, #9, #18 run 1).
- **Location**: `thinking-session/SKILL.md` description ("normally reached via using-think-orbit" still fires).
- **Suggested fix**: either make thinking-session's description non-triggering (router only), or make thinking-session run the root ladder itself when entered directly.

### FINDING-012: Query "structured thinking, later look back at premises" missed (Low · Trigger-miss · blind)
- **Probe**: A #19 (0/2), no folder cue.
- **Suggested fix**: add 「有結構的思考」「回頭看前提」/ "structured thinking" / "trace what it rested on" to the router description.

## Raw outputs appendix

### A. Activation runs — `probe-a/summary.md` (per-query table, 2 runs), `probe-a/results.json`, `probe-a/corpus.json`. Totals: TP exact 12/40 · TP other think-orbit skill 3/40 · FN 25/40 · TN 14/14 · over-trigger 0/14.
### B. Cold-reader audit — sonnet, zero context, three SKILL.md files: verbatim answers recorded in the orchestrator transcript (session 3bc12f9a); key lines quoted in FINDING-008/009/010.
### C. Executor artifacts — `executor-project/` (13 nodes, 5 assumptions, `views/dag.md`); sources were five real repo documents (backlog entry, two memory files, umbrella brief excerpt, Part 1 Decision Log).
### D. Executor trajectory — `executor-transcript.md` (191 lines; §Executor notes lists ambiguities: render silent; GOAL write-then-confirm vs assumptions confirm-then-write; open-ended ending not in the render milestone list; git-repo root left untracked).
### E. Auditor judgments — two blind auditors, both **ACCEPTABLE** (mechanics clean: schema, verbatim quotes, 18 edges = 18 inputs, prose 2–4 sentences; analysis depth: crux assumption "render accepts type-less loom nodes" unnamed; branch A framed narrower than the source allows; deadline vs checkpoint slip unnamed).

## Re-run after 0.1.2 fixes (branch build via `--plugin-dir`)
Corpus = the 13 previously-missed queries + 2 new should-NOT (晚餐吃什麼／想標語), 2 runs each — `probe-a2/summary.md`. Result: **22/26 fired think-orbit (was 1/26)**; TP-exact 14, router-instead-of-leaf 8 (all four assumption-broke queries now enter via `using-think-orbit`, by design), FN 4 (#1 「規劃明年上半年的產品路線圖，我手上有三份會議記錄」 ×2, #6 "continue the decision we started last week in ./decisions/pricing" ×2), TN 4, over-trigger 0. FINDING-001/002/010/012 → resolved for the measured shapes; residual: bare "plan X with N documents" and English "continue the decision in <path>" still miss under `--max-turns 2`. FINDING-003–009/011 → applied in 0.1.2 (see CHANGELOG), verified by 13 SKILL-pin tests + a 4-arm review.

## Not a T12 substitute
The executor's user turns were simulated. T12 (real-material checkpoint) still requires the user to run a sitting on their own material and judge readability of `views/dag.md` + the node files. Suggested order: fix FINDING-001/002 (entry) first, then run T12 with the wider entry.
