# loom-workflow artifact-chain inventory

Repo root: /Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow
All paths below are relative to repo root unless noted otherwise.

---

## brief-before-asking
- Purpose (plain words, 1 line): Deliver a 6-block Mental-Model-first briefing before asking the user a non-trivial engineering fork; no artifact, pure conversational protocol.
- Entered via: called by name from `loom-code:brainstorming` — `loom-code/skills/brainstorming/SKILL.md:55`; from `loom-code:writing-plans` kickoff — `loom-code/skills/writing-plans/references/kickoff-briefing.md:110` and `:207`; from `loom-code:requesting-code-review` — `loom-code/skills/requesting-code-review/SKILL.md:33` and `loom-code/skills/requesting-code-review/references/relay-phrasing.md:20`; named in the loom-code family reception hook — `loom-code/hooks/family-reception.md:42`; and in loom-design's on-ramp/entry routers — `loom-design/skills/using-loom-design/SKILL.md:51`, `loom-design/skills/using-loom-pipeline/SKILL.md:101`, `loom-design/skills/using-loom-design/references/family-reception.md:42`.
- INPUTS: chat context only (the fork/question already being asked) — `loom-workflow/skills/brief-before-asking/SKILL.md:17-22`
- OUTPUTS: none (turn-final chat text only; the 6-block briefing itself is never persisted to a file) — `loom-workflow/skills/brief-before-asking/SKILL.md:84-93`
- CONSUMERS: none (ephemeral chat output; no artifact to consume)
- TERMS INTRODUCED:
  - `6-block briefing — Mental Model / Situation / Why-this-fork / Options / My take / Open ends` — `loom-workflow/skills/brief-before-asking/SKILL.md:84-93`
  - `Mode A/B/C/D — proactive vs. reactive-on-question/explanation/stakes trigger modes` — `loom-workflow/skills/brief-before-asking/SKILL.md:15-82`
  - `repeated-confusion guard — 2nd consecutive confusion signal forces a hard stop back to Mental Model` — `loom-workflow/skills/brief-before-asking/SKILL.md:67`
- MECHANISMS INVOKED: none (no scripts/hooks own to this skill; it is pure prose protocol)
- GATES: turn-ordering rule — briefing must land as its own turn before `AskUserQuestion` fires, never stacked in the same turn — `loom-workflow/skills/brief-before-asking/SKILL.md:22`; repeated-confusion guard forces reframing rather than proceeding — `loom-workflow/skills/brief-before-asking/SKILL.md:67`.

---

## complexity-critique
- Purpose (plain words, 1 line): One-shot deletion-first gate that judges a single proposed change by smallest end state / LOC delta / what it deletes, ending in a PROCEED/RESHAPE/REJECT verdict.
- Entered via: called by name from `loom-code:brainstorming` Axis 3 — `loom-code/skills/brainstorming/SKILL.md:95`, `:173`, `:192`, `:202`; from `loom-code:systematic-debugging` as an optional lateral delegate — `loom-code/skills/systematic-debugging/SKILL.md:109`.
- INPUTS:
  - `domain-teams:code-team/standards/mindset-*.md` (canonical mindset docs; bundled copies tracked in this skill's own `references/`) — `loom-workflow/skills/complexity-critique/SKILL.md:29`
  - one specific proposed change described in chat — `loom-workflow/skills/complexity-critique/SKILL.md:9-11`
  - repository evidence (LOC/file/function counts from affected paths) — `loom-workflow/skills/complexity-critique/SKILL.md:59`
- OUTPUTS: none — a chat-delivered verdict (PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT) with rationale, not written to a file — `loom-workflow/skills/complexity-critique/SKILL.md:79-90`
- CONSUMERS: none found (verdict is consumed in-conversation by the caller skill/user, not read back by any script)
- TERMS INTRODUCED:
  - `Verdict — one of PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT` — `loom-workflow/skills/complexity-critique/SKILL.md:81-90`
  - `smallest end state — the Q1 test: what the codebase should look like after the change, not how little work alters today's code` — `loom-workflow/skills/complexity-critique/SKILL.md:33-35`
- MECHANISMS INVOKED: none (no scripts; four bundled `references/mindset-*.md` files read as prose, mirrored from `domain-teams:code-team/standards/`)
- GATES: "no change ships without a named mindset and all three questions, in order" — `loom-workflow/skills/complexity-critique/SKILL.md:31`; "Never silently approve a Q2 increase" — `loom-workflow/skills/complexity-critique/SKILL.md:88`.

---

## cot-explain
- Purpose (plain words, 1 line): One-shot generator that turns existing reasoning (a file, folder, or this conversation) into a self-contained HTML page built around a chain-of-thought Mermaid diagram.
- Entered via: no caller found in `loom-code/` or `loom-design/` (`grep -rln "loom-workflow:cot-explain" loom-code/ loom-design/` returns nothing) — user-phrase-only entry, e.g. "a CoT diagram" / "explain how we reasoned this" — `loom-workflow/skills/cot-explain/SKILL.md:9`.
- INPUTS:
  - a user-named file/folder/glob ("File mode") — `loom-workflow/skills/cot-explain/SKILL.md:47-52`
  - the current conversation ("Conversation mode") — `loom-workflow/skills/cot-explain/SKILL.md:54-68`
  - `references/mermaid-cot-spec.md` (diagram house convention) — `loom-workflow/skills/cot-explain/SKILL.md:138`
  - `assets/cot-report-template.md` (markdown template copied to start the page) — `loom-workflow/skills/cot-explain/SKILL.md:209`
- OUTPUTS:
  - `${TMPDIR:-/tmp}/cot-explain/<YYYY-MM-DD>-<slug>.md` (the markdown artifact, "the artifact"; overwritten per slug, temporary) — `loom-workflow/skills/cot-explain/SKILL.md:260-264`
  - `<same-dir>/<slug>.html` (rendered via `scripts/render_cot_html.py`, derived from the markdown, temporary) — `loom-workflow/skills/cot-explain/SKILL.md:260-264`, `:276-278`
  - `<name>.fidelity.md` beside the page (Step 6 fidelity-check verdict, `verdict: PASS/FAIL` + `reviewed_md_sha256:`) — `loom-workflow/skills/cot-explain/SKILL.md:322-324`, `:349-351`
  - optional published Artifact (only after Step 6 PASS, on explicit user ask) — `loom-workflow/skills/cot-explain/SKILL.md:330-332`, `:361-364`
- CONSUMERS:
  - the `.md` is read by `scripts/render_cot_html.py` and `scripts/verify_cot_html.py` in the same skill run — `loom-workflow/skills/cot-explain/SKILL.md:275-279`
  - the `.fidelity.md` is read by `--stamp` to fill the markdown's `verified:`/`fidelity_checked` frontmatter fields — `loom-workflow/skills/cot-explain/SKILL.md:311-324`
  - none found outside this skill (both files are declared temporary; no other skill or script reads them)
- TERMS INTRODUCED:
  - `岔路 (rejected-options table) — anything considered and ruled out, with the reason` — `loom-workflow/skills/cot-explain/SKILL.md:79-80`, `:128-134`
  - `mechanism node — a node that says something will be built, changed, or done: code, policy, contract, protocol, or standard` — `loom-workflow/skills/cot-explain/SKILL.md:89-91`
  - `fidelity check — a 3-round simulatability round-trip (reconstruct / compare-without-page / reverse-check-for-invention) gating publication` — `loom-workflow/skills/cot-explain/SKILL.md:334-347`
- MECHANISMS INVOKED: `scripts/render_cot_html.py`, `scripts/verify_cot_html.py` (both under `loom-workflow/skills/cot-explain/`)
- GATES: `verify_cot_html.py` FAIL breaks the contract and exits 1, blocking HTML delivery — `loom-workflow/skills/cot-explain/SKILL.md:292-293`; Step 6 fidelity check must PASS before conversion-for-sharing or Artifact publication — `loom-workflow/skills/cot-explain/SKILL.md:330-333`, `:361-364`; early-exit gate if fewer than 5 reasoning states are found — `loom-workflow/skills/cot-explain/SKILL.md:112-117`.

---

## dbt-model-style
- Purpose (plain words, 1 line): Enforces a dbt+Redshift model style/structure contract (CTE roles, zero-logic final CTE, naming, YAML header, comments, syntax) when authoring/editing/reviewing a `.sql` dbt model.
- Entered via: no caller found in `loom-code/` or `loom-design/` — user-phrase-only entry, e.g. authoring/editing a `.sql` dbt model or "符合規範嗎" — `loom-workflow/skills/dbt-model-style/SKILL.md:4`.
- INPUTS:
  - the `.sql` dbt model file being authored/edited/reviewed — `loom-workflow/skills/dbt-model-style/SKILL.md:13`
  - `references/example-model.sql` (worked full example) — `loom-workflow/skills/dbt-model-style/SKILL.md:38`
  - `references/dotstar-passthrough.md` (conditional load for multi-source `.*` passthrough) — `loom-workflow/skills/dbt-model-style/SKILL.md:78`
  - `checklists/dbt-model-self-check.md` (post-write checklist) — `loom-workflow/skills/dbt-model-style/SKILL.md:246`
  - optionally `target/manifest.json` (dbt manifest, for `--manifest` validation mode) — `loom-workflow/skills/dbt-model-style/SKILL.md:251`
- OUTPUTS: the edited `.sql` model file itself (style-conformant CTEs, two-block header comment, config block) — `loom-workflow/skills/dbt-model-style/SKILL.md:36-45`; no separate artifact file is produced by this skill
- CONSUMERS: the warehouse table comment, IF `persist_docs` is enabled — the first `/* */` header block is written into the Redshift table/column comment via `dbt run` — `loom-workflow/skills/dbt-model-style/SKILL.md:112-118`; the redshift-comment MCP server later reads that comment as its source of truth (per its own tool instructions) — `loom-workflow/skills/dbt-model-style/SKILL.md:122-124`
- TERMS INTRODUCED:
  - `final CTE iron law — the final CTE has zero logic, only column selection + aliases + comments` — `loom-workflow/skills/dbt-model-style/SKILL.md:21`, `:59-61`
  - `two-block header — first /* */ = frontmatter+narrative (reaches table comment); second /* */ = business rules (human-facing only)` — `loom-workflow/skills/dbt-model-style/SKILL.md:110-176`
  - `name matches content — a column name's qualifier (e.g. __paid) must not smuggle in semantics it doesn't have` — `loom-workflow/skills/dbt-model-style/SKILL.md:85`
- MECHANISMS INVOKED: `scripts/validate_header.py` (mechanical header/shape validator, optional `--manifest` mode)
- GATES: `scripts/validate_header.py` non-zero exit = violations, must pass before shipping/opening the PR — `loom-workflow/skills/dbt-model-style/SKILL.md:245-253`.

---

## decision-map
- Purpose (plain words, 1 line): Chart and work through a persistent, multi-session Outcome Map — a long-term decision/delivery tracker whose open questions ("fog") become typed tickets closing independently over time.
- Entered via: called by name from `loom-code:brainstorming`'s Axis 0 Live-map check — `loom-code/skills/brainstorming/SKILL.md:73`, `:75`, `:178`; referenced/enforced from `loom-code/hooks/git-guard.py:191` and named in `loom-code/hooks/family-reception.md:95`; ticket-file shape is read by `loom-code:tdd-iron-law`'s prototype-branch exemption — `loom-code/skills/tdd-iron-law/SKILL.md:48`.
- INPUTS:
  - `docs/loom/maps/<map-id>/MAP.md` (the Outcome Map itself, re-read on resume) — `loom-workflow/skills/decision-map/references/map-format.md:27-28`
  - `docs/loom/maps/<map-id>/tickets/<slug>.md` (individual ticket files) — `loom-workflow/skills/decision-map/references/map-format.md:29-30`
  - `references/map-format.md`, `references/prototype-contract.md`, and its `## Backlog boundary contract` section — `loom-workflow/skills/decision-map/SKILL.md:24-30`
  - a Ticket, Plan, or repository root passed to `map_progress.py` — `loom-workflow/skills/decision-map/SKILL.md:71-73`
  - Brief/Plan/Git/PR/CI state (read-only, never copied into the Map) — `loom-workflow/skills/decision-map/SKILL.md:21-22`
- OUTPUTS:
  - `docs/loom/maps/<map-id>/MAP.md` (created by `map_init.py`, mutated by `map_transaction.*` operations) — `loom-workflow/skills/decision-map/SKILL.md:53-54`
  - `docs/loom/maps/<map-id>/tickets/` directory + `<slug>.md` ticket files (created by `map_init.py`, closed/updated via `map_transaction.close_and_rechart` etc.) — `loom-workflow/skills/decision-map/SKILL.md:53-54`, `:123-131`
- CONSUMERS:
  - `loom-code:brainstorming`'s Live-map check reads `MAP.md`/ticket liveness before opening a new brief — `loom-code/skills/brainstorming/SKILL.md:73`
  - `loom-code:tdd-iron-law` reads a ticket file (`type: prototype`) to grant the prototype-branch TDD exemption — `loom-code/skills/tdd-iron-law/SKILL.md:48`
  - `loom-code/hooks/git-guard.py` cites the map contract at push-time — `loom-code/hooks/git-guard.py:191`
- TERMS INTRODUCED:
  - `Outcome Map — one persistent outcome-control loop that advances through multiple independently closed delivery arcs` — `loom-workflow/skills/decision-map/SKILL.md:10-13`
  - `fog (F-<n>) — monotonic record of open questions recorded while charting` — `loom-workflow/skills/decision-map/SKILL.md:39`
  - `Destination acceptance (DA-<n>) — Destination acceptance criteria recorded at charting` — `loom-workflow/skills/decision-map/SKILL.md:38`
  - `closure types — grilling / research / prototype / delivery (exactly four)` — `loom-workflow/skills/decision-map/SKILL.md:15-18`, `:160-173`
  - `Decisions-so-far gist — one durable summary preserved on ticket close` — `loom-workflow/skills/decision-map/SKILL.md:127`
  - `UnknownRoute — typed routing of an exposed unknown to fog / a typed ticket / Out-of-scope` — `loom-workflow/skills/decision-map/SKILL.md:139-141`
  - `re-entry states — absent / broken / ambiguous-live / live / blocked / claimed / da-gap (top-level); unbriefed / briefed / planning / implementing / reviewing / finishing / repair-required / delivered (delivery phase)` — `loom-workflow/skills/decision-map/SKILL.md:73-76`
- MECHANISMS INVOKED: `scripts/map_init.py`, `scripts/map_store.py` (validate), `scripts/map_progress.py`, `scripts/check_map_links.py`, `scripts/check_map_fog.py`, plus library modules `map_transaction.py` (claim/close/archive/retire) and `migrate_map_v3.py` (all under `loom-workflow/skills/decision-map/scripts/`)
- GATES: `charting`→`active` transition requires a risk pass + `user-ratified:` record + `map_store.py validate` — `loom-workflow/skills/decision-map/SKILL.md:62-65`; Map clear requires fog empty + all tickets closed/withdrawn + every DA satisfied with valid evidence — `loom-workflow/skills/decision-map/SKILL.md:41-43`; close-time gate runs `map_store.py validate` + `check_map_links.py` + `check_map_fog.py`, exit 2 = contract violation — `loom-workflow/skills/decision-map/SKILL.md:185-194`; never claim blocked work — `loom-workflow/skills/decision-map/SKILL.md:81`.

---

## distill-sessions
- Purpose (plain words, 1 line): Mines past Claude Code / Codex session transcripts + `/insights` facets for friction patterns and produces a reviewable, human-approved SKILL.md improvement-proposals document.
- Entered via: no caller found in `loom-code/` or `loom-design/` skills (only referenced inside a firing-behavior test asserting it fires on user phrasing, `loom-code/scripts/test_loom_firing_harness.py:755` — not a skill-to-skill call) — user-phrase-only entry, e.g. "mine my skill logs for loom-code" — `loom-workflow/skills/distill-sessions/SKILL.md:21`.
- INPUTS:
  - `~/.claude/projects/**/*.jsonl` (Claude Code session transcripts) — `loom-workflow/skills/distill-sessions/SKILL.md:60`
  - `~/.codex/sessions/**/*.jsonl` (Codex session transcripts) — `loom-workflow/skills/distill-sessions/SKILL.md:60-61`
  - `~/.claude/usage-data/facets/*.json` (`/insights` facets, when present) — `loom-workflow/skills/distill-sessions/SKILL.md:61`
  - the target SKILL.md body being scoped (e.g. `loom-code:*`) — `loom-workflow/skills/distill-sessions/SKILL.md:12`, `:79-84`
- OUTPUTS:
  - `top.json` (Stage 1 ranked friction + per-trajectory dispatch payloads) — `loom-workflow/skills/distill-sessions/SKILL.md:79-90`
  - `merged.json` (Stage 3 collected Memory Items) — `loom-workflow/skills/distill-sessions/SKILL.md:111-117`
  - `docs/skill-mining/<date>-<target>-proposals.md` (Stage 4 rendered proposal doc; the "required per-target artifact") — `loom-workflow/skills/distill-sessions/SKILL.md:127-138`
  - the target SKILL.md itself, mutated ONLY after explicit human approval via `scripts/apply.py --approved` — `loom-workflow/skills/distill-sessions/SKILL.md:148-160`
  - optional `docs/skill-mining/<date>-advisory-report.md` (cross-target advisory report) — `loom-workflow/skills/distill-sessions/SKILL.md:172-177`
- CONSUMERS:
  - `top.json` is read by Stage 2's per-trajectory subagent dispatch — `loom-workflow/skills/distill-sessions/SKILL.md:99-101`
  - `merged.json` is read by `scripts/propose.py` (Stage 4) and `scripts/report.py` (advisory) — `loom-workflow/skills/distill-sessions/SKILL.md:127-130`, `:172-175`
  - the proposals `.md` is read by the human reviewer, then by `scripts/apply.py` — `loom-workflow/skills/distill-sessions/SKILL.md:145-151`
  - none found for the final mutated target SKILL.md beyond the human/agent that edited it — no downstream loom-workflow script re-consumes it
- TERMS INTRODUCED:
  - `Memory Item — the strict-markdown shape a per-trajectory subagent returns (title/description/content/kind/section_anchor)` — `loom-workflow/skills/distill-sessions/SKILL.md:106-117`
  - `trajectory — one dispatched (skill, session, kind) unit, deterministic UUID5` — `loom-workflow/skills/distill-sessions/SKILL.md:90-95`
- MECHANISMS INVOKED: `scripts/main.py`, `scripts/propose.py`, `scripts/apply.py`, `scripts/report.py` (all under `loom-workflow/skills/distill-sessions/`)
- GATES: `apply.py` refuses without `--approved`, refuses writes under `references/`, requires exact section-anchor + contiguous old-text match — `loom-workflow/skills/distill-sessions/SKILL.md:149-153`; Stage 2 requires explicit user confirmation before any subagent dispatch (paid, sends session text out) — `loom-workflow/skills/distill-sessions/SKILL.md:44-46`; oversized-trajectory (>1M token) items are skipped with a warning, never silently sent — `loom-workflow/skills/distill-sessions/SKILL.md:48-52`.

---

## git-memory
- Purpose (plain words, 1 line): Mandatory gate before every `git commit` / `gh pr create` / `gh pr merge` that decides whether Decision/Learning/Gotcha memory trailers apply, and recalls past decisions on request.
- Entered via: mandatory delegation target from `loom-code:finishing-a-development-branch` Step 3 (P3-D) — `loom-code/README.zh-TW.md:159`, `loom-code/tests/integration/test-git-memory-delegation.sh:32-54`, `loom-code/ROADMAP.md:222,231,258,320`; noted as unaffected by worktree switching in `loom-code:using-git-worktrees` — `loom-code/skills/using-git-worktrees/SKILL.md:93`; distinguished from `loom-code:loom-memory` (repo-native lesson store, NOT this skill) — `loom-code/skills/loom-memory/SKILL.md:10`, `:53`.
- INPUTS:
  - the composed commit message / PR body text (before finalizing) — `loom-workflow/skills/git-memory/SKILL.md:85-113`
  - `git log`, `git rev-parse`, PR history (for recall) — `loom-workflow/skills/git-memory/SKILL.md:40`
  - `standards/memory-conventions.md`, `protocols/compose-commit.md`, `protocols/compose-pr.md`, `protocols/recall.md`, `protocols/privacy-judge-spec.md` (own references) — `loom-workflow/skills/git-memory/SKILL.md:226-236`
- OUTPUTS:
  - git commit trailers `Decision:` / `Learning:` / `Gotcha:` / `Related:` / `Supersedes:` on the commit message — `loom-workflow/skills/git-memory/SKILL.md:55-61`
  - a rendered `## Memory` section in the PR body + a raw unbolded trailer footer as the PR's last authored block — `loom-workflow/skills/git-memory/SKILL.md:99-103`
- CONSUMERS:
  - `scripts/memory-grep.sh --verify` / `--verify-merged` / `--verify-strict` read the commit/PR trailers back at merge time — `loom-workflow/skills/git-memory/SKILL.md:120-127`
  - `loom-code:finishing-a-development-branch` enforces the verification as an executable gate — `loom-workflow/skills/git-memory/SKILL.md:128-134`
  - `protocols/recall.md` reads `git log`/PR history to answer "why did we…" queries later — `loom-workflow/skills/git-memory/SKILL.md:202-224`
- TERMS INTRODUCED:
  - `Decision: / Learning: / Gotcha: trailers — structured commit/PR memory keys` — `loom-workflow/skills/git-memory/SKILL.md:55-59`
  - `Related: / Supersedes: — linking and replacement relations between trailers` — `loom-workflow/skills/git-memory/SKILL.md:60-61`
  - `invocation gate vs. trailer gate — always invoke the skill; the skill alone decides whether trailers are added` — `loom-workflow/skills/git-memory/SKILL.md:14-28`
- MECHANISMS INVOKED: `scripts/memory-grep.sh`, `scripts/privacy-scan.py`
- GATES: privacy gate fail-closed — deterministic scan + fresh-context judge must both pass before any commit/PR text is published, any finding/BLOCK/error makes the carrier BLOCKED — `loom-workflow/skills/git-memory/SKILL.md:170-200`; capture-verification gate at merge (`memory-grep.sh --verify-merged`) enforced by `finishing-a-development-branch` — `loom-workflow/skills/git-memory/SKILL.md:128-134`.

---

## goal-create
- Purpose (plain words, 1 line): Drafts a four-field goal condition for a session run (SESSION mode) or a repository purpose statement (ARC mode) — never fires on its own, must be invoked by name.
- Entered via: never auto-fires — `loom-workflow/skills/goal-create/SKILL.md:57-58`; named as an available option by `loom-workflow:handoff` Prepare mode — `loom-workflow/skills/handoff/SKILL.md:88-91` (same plugin, sibling); named by `loom-code`'s `check_north_star_link.py` unanswered-purpose message — `loom-code/scripts/check_north_star_link.py` (per `loom-workflow/skills/goal-create/SKILL.md:62-63`); named by `loom-code:finishing-a-development-branch` when `docs/loom/PURPOSE.md` is absent — `loom-code/skills/finishing-a-development-branch/SKILL.md` (per `loom-workflow/skills/goal-create/SKILL.md:64-65`).
- INPUTS:
  - `references/goal-shape.md` (SESSION mode's SSOT for the four-field shape) — `loom-workflow/skills/goal-create/SKILL.md:16-19`
  - `references/input-floor.md` (the two input slots, refusal rule, provenance tags) — `loom-workflow/skills/goal-create/SKILL.md:21-24`
  - `docs/loom/PURPOSE.md` (ARC mode reads/checks for existing store) — `loom-workflow/skills/goal-create/SKILL.md:45-53`
- OUTPUTS:
  - a four-field goal condition (Outcome / Constraints / Verification / Stop-when) delivered in chat, checked by Claude Code's own goal evaluator against conversation text — never written to a file by this skill — `loom-workflow/skills/goal-create/SKILL.md:16-19`, `loom-workflow/skills/goal-create/references/goal-shape.md:47-50`
  - a drafted `Why` / `Done when` pair for `docs/loom/PURPOSE.md`, presented for the user's own confirmation — the skill itself never writes the file — `loom-workflow/skills/goal-create/SKILL.md:45-48`
- CONSUMERS:
  - the SESSION-mode goal text is consumed by "Claude Code's goal evaluator," a harness feature that reads only conversation text — `loom-workflow/skills/goal-create/references/goal-shape.md:47-50`
  - `docs/loom/PURPOSE.md` (once user-landed) is later read by `loom-code/scripts/check_north_star_link.py` and quoted by `loom-code:brainstorming`'s direction banner — `loom-code/skills/brainstorming/SKILL.md:75` (`**Why:**` line)
- TERMS INTRODUCED:
  - `four-field goal — Outcome / Constraints / Verification / Stop-when` — `loom-workflow/skills/goal-create/references/goal-shape.md:7-14`
  - `Standing decision rule — choices the goal does not pre-decide are the run's to make, searched-decided-recorded, never a stop-and-ask` — `loom-workflow/skills/goal-create/references/goal-shape.md:36-38`
  - `SESSION mode / ARC mode — the two named modes of this one skill` — `loom-workflow/skills/goal-create/SKILL.md:10-12`
- MECHANISMS INVOKED: `scripts/goal_lint.py`
- GATES: `goal_lint.py` must exit 0 before a SESSION-mode draft is shown to the user (structure-only check, re-run after each fix) — `loom-workflow/skills/goal-create/SKILL.md:26-41`; ARC mode reports N/A and scaffolds nothing when no `docs/loom/` store exists — `loom-workflow/skills/goal-create/SKILL.md:50-53`.

---

## handoff
- Purpose (plain words, 1 line): Saves session state to a structured HANDOFF file (Prepare mode) so a future cold-context agent can resume cleanly, or loads/verifies a prior HANDOFF (Resume mode).
- Entered via: no caller found in `loom-code/` or `loom-design/` — user-phrase-only entry, e.g. "wrap up" / "save state" / "pick up where we left off" — `loom-workflow/skills/handoff/SKILL.md:5`.
- INPUTS:
  - `references/handoff-schema.md` (10-block template SSOT, read fully before every author/interpret) — `loom-workflow/skills/handoff/SKILL.md:24`, `:95`
  - `git rev-parse HEAD`, `git rev-parse --abbrev-ref HEAD`, `git status --short`, `git log --oneline -5`, `claude --version`/`codex --version` (state-gathering commands) — `loom-workflow/skills/handoff/SKILL.md:29-35`
  - `.claude/handoffs/` directory listing (Resume mode, `ls -t`) — `loom-workflow/skills/handoff/SKILL.md:105-108`
- OUTPUTS:
  - `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md` (the 10-block structured handoff file) — `loom-workflow/skills/handoff/SKILL.md:10-11`, `:37-38`
  - a `## Resume Launcher` block appended to that same file + an identical copy-paste init prompt printed in chat — `loom-workflow/skills/handoff/SKILL.md:78-86`
- CONSUMERS: a future session's own invocation of `handoff` Resume mode reads the latest file via `ls -t .claude/handoffs/ | head -1` — `loom-workflow/skills/handoff/SKILL.md:105-108`; no consumer found outside this same skill (no loom-code/loom-design skill reads `.claude/handoffs/*`).
- TERMS INTRODUCED:
  - `HANDOFF — 10-block structured operational restart record (Frontmatter/Situation/Background/All user messages/Recent decisions/Pending/Critical files/Do Not Touch/Verification commands/Confidence flags)` — `loom-workflow/skills/handoff/SKILL.md:39-49`
  - `[T1] load-bearing / [T2] advisory — verification-command mismatch severity tiers` — `loom-workflow/skills/handoff/SKILL.md:70-76`, `:123-136`
  - `Resume Launcher — a thin pointer block naming the exact HANDOFF path` — `loom-workflow/skills/handoff/SKILL.md:78-86`
- MECHANISMS INVOKED: none (no scripts; pure git-command + file-write protocol)
- GATES: Resume mode refuses to interpret/act on a HANDOFF if `references/handoff-schema.md` is unavailable (fail closed) — `loom-workflow/skills/handoff/SKILL.md:99-103`; a [T1] verification mismatch forces REFUSE TO CONTINUE and asks the user — `loom-workflow/skills/handoff/SKILL.md:124-129`; Resume mode ends at a Synthesis-check and waits for user confirmation before acting — `loom-workflow/skills/handoff/SKILL.md:138-140`.

---

## independent-advisor
- Purpose (plain words, 1 line): Gets a second opinion on the current plan/decision from a different executor (stronger model / higher effort / different vendor) — same lens, different who-answers.
- Entered via: no caller found in `loom-code/` or `loom-design/` — user-phrase-only entry, e.g. "second opinion" / "ask a stronger model" — `loom-workflow/skills/independent-advisor/SKILL.md:4`.
- INPUTS:
  - `references/executor-detection.md` (static + live-probe candidate-executor checks) — `loom-workflow/skills/independent-advisor/SKILL.md:88-89`, `:218-219`
  - `references/dispatch-protocol.md` (three-roles / blind-judging dispatch procedure) — `loom-workflow/skills/independent-advisor/SKILL.md:274`
  - `references/report-contract.md` (report field order, rejection keys, worked wording) — `loom-workflow/skills/independent-advisor/SKILL.md:368-369`
  - the user's current plan/decision + incumbent proposal material (in `audit` mode) — `loom-workflow/skills/independent-advisor/SKILL.md:23-25`
  - a commit id / PR number / brief approval line / user wording (`mode_basis` evidence) — `loom-workflow/skills/independent-advisor/SKILL.md:31-38`
- OUTPUTS: a chat-delivered report with divergence points, confidence, and proposed changes — no file path is specified; delivered wherever the report is written per `references/report-contract.md` — `loom-workflow/skills/independent-advisor/SKILL.md:366-369`; the report is explicitly "a read-only record" (its own delivered fields don't get rewritten in place) — `loom-workflow/skills/independent-advisor/SKILL.md:383-385`
- CONSUMERS: none found (chat-delivered, no file artifact to consume)
- TERMS INTRODUCED:
  - `tier pair — model tier economy/standard/frontier crossed with effort low/medium/high` — `loom-workflow/skills/independent-advisor/SKILL.md:15-18`
  - `explore mode / audit mode — three-role open-solution-space run vs. single-leg full-context check of an incumbent proposal` — `loom-workflow/skills/independent-advisor/SKILL.md:22-25`
  - `mode_basis — the verbatim quoted fact (commit/PR/brief/user wording) supporting the mode decision` — `loom-workflow/skills/independent-advisor/SKILL.md:36-38`
- MECHANISMS INVOKED: none named directly in SKILL.md (executor static/live-probe commands live in `references/executor-detection.md`)
- GATES: single checkpoint before any dispatch (material leaves the machine only after this) — `loom-workflow/skills/independent-advisor/SKILL.md:137`; egress disclosure before spend — `loom-workflow/skills/independent-advisor/SKILL.md:171`; "no citable fact" forces asking the user rather than guessing the mode — `loom-workflow/skills/independent-advisor/SKILL.md:57-59`; each leg output passes a mechanical shape check (6 distinguishable rejection reasons) before entering the report — `loom-workflow/skills/independent-advisor/SKILL.md:389-398`.

---

## proposal-critique
- Purpose (plain words, 1 line): Triages a multi-item proposal (list/plan/prose) into KEEP / DEFER / DROP using evidence-grounding × necessity, so no item ships un-triaged.
- Entered via: called by name from `loom-code:brainstorming` Axis 4 — `loom-code/skills/brainstorming/SKILL.md:174`, `:203`; also referenced (not necessarily invoked) in `loom-code/TECH-SPEC.md:317` and `loom-code/ROADMAP.md`.
- INPUTS: a user-supplied multi-item proposal (list, plan, or prose recommendation) in chat — `loom-workflow/skills/proposal-critique/SKILL.md:9`
- OUTPUTS: a chat-delivered KEEP/DEFER/DROP triage in the fixed markdown Output Contract shape — no file path specified, delivered in-conversation — `loom-workflow/skills/proposal-critique/SKILL.md:67-81`
- CONSUMERS: none found (chat-delivered decision surface, consumed by the caller/user directly)
- TERMS INTRODUCED:
  - `GROUNDED / HEURISTIC-OK / SPECULATIVE — evidence-grounding values` — `loom-workflow/skills/proposal-critique/SKILL.md:27-30`
  - `ESSENTIAL / SPECULATIVE — necessity values` — `loom-workflow/skills/proposal-critique/SKILL.md:32-34`
  - `KEEP / KEEP-WITH-CAVEAT / DEFER / DROP — the four triage verdicts` — `loom-workflow/skills/proposal-critique/SKILL.md:40-51`
  - `DEFER fall-through — DEFER without an articulable re-trigger condition falls through to DROP` — `loom-workflow/skills/proposal-critique/SKILL.md:53-55`
- MECHANISMS INVOKED: none (pure prose gate, no scripts)
- GATES: "NO MULTI-ITEM PROPOSAL SHIPS WITHOUT TRIAGE" iron law — `loom-workflow/skills/proposal-critique/SKILL.md:13-15`; DEFER without a re-trigger condition must fall through to DROP — `loom-workflow/skills/proposal-critique/SKILL.md:53-55`.

---

## recap-state
- Purpose (plain words, 1 line): In-session re-orientation — produces a structured 6-block recap ending with a Synthesis-check when the user loses the thread; never writes to a file.
- Entered via: no caller found in `loom-code/` or `loom-design/` — user-phrase-only entry, e.g. "where were we" / "我跟丟了" — `loom-workflow/skills/recap-state/SKILL.md:5`.
- INPUTS:
  - `references/seven-block-schema.md` (full V1 template, block rules, five principles; read fully before every recap) — `loom-workflow/skills/recap-state/SKILL.md:17-19`
  - the current conversation only (in-session) — `loom-workflow/skills/recap-state/SKILL.md:10-13`
- OUTPUTS: none — explicitly "Chat only: do not write the recap to a file" — `loom-workflow/skills/recap-state/SKILL.md:138`
- CONSUMERS: none (chat-only, ephemeral)
- TERMS INTRODUCED:
  - `Synthesis-check — a soft gate ending block that states expected next direction and waits for user confirm/redirect` — `loom-workflow/skills/recap-state/SKILL.md:75-76`, `:106-114`
  - `L3 six-block schema — Situation/Background/Assessment/Why-this-question/Pending/Synthesis-check (Block 4 skipped at L3)` — `loom-workflow/skills/recap-state/SKILL.md:34-44`, `:78-82`
- MECHANISMS INVOKED: none (pure prose protocol)
- GATES: does not continue past the recap until the user responds to the Synthesis-check (soft gate) — `loom-workflow/skills/recap-state/SKILL.md:106-114`, `:143`.

---

## Totals

**Distinct artifact types written by this plugin (12 skills), with canonical path pattern:**
1. `docs/loom/maps/<map-id>/MAP.md` — decision-map
2. `docs/loom/maps/<map-id>/tickets/<slug>.md` — decision-map
3. `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md` — handoff
4. `${TMPDIR:-/tmp}/cot-explain/<YYYY-MM-DD>-<slug>.md` — cot-explain
5. `${TMPDIR:-/tmp}/cot-explain/<slug>.html` — cot-explain
6. `${TMPDIR:-/tmp}/cot-explain/<slug>.fidelity.md` — cot-explain
7. `docs/skill-mining/<date>-<target>-proposals.md` — distill-sessions
8. `docs/skill-mining/<date>-advisory-report.md` — distill-sessions (optional)
9. `top.json` / `merged.json` (working-directory intermediate files) — distill-sessions
10. target `SKILL.md` (mutated in place, human-approved) — distill-sessions
11. git commit trailers `Decision:`/`Learning:`/`Gotcha:`/`Related:`/`Supersedes:` — git-memory
12. PR body `## Memory` section + raw trailer footer — git-memory
13. `docs/loom/PURPOSE.md` `Why`/`Done when` draft (user-landed, not skill-written) — goal-create
14. the edited `.sql` dbt model file itself (style applied in place) — dbt-model-style

(brief-before-asking, complexity-critique, independent-advisor, proposal-critique, and recap-state write no persistent artifact — all five are chat-delivered only.)

**Distinct terms introduced (deduplicated, 12 skills → 25 terms):**
6-block briefing; Mode A/B/C/D; repeated-confusion guard; Verdict (complexity-critique's 4-value); smallest end state; 岔路 (rejected-options table); mechanism node; fidelity check; final CTE iron law; two-block header; name matches content; Outcome Map; fog (F-<n>); Destination acceptance (DA-<n>); closure types (grilling/research/prototype/delivery); Decisions-so-far gist; UnknownRoute; re-entry states; Memory Item; trajectory; Decision:/Learning:/Gotcha: trailers; Related:/Supersedes:; invocation gate vs. trailer gate; four-field goal (Outcome/Constraints/Verification/Stop-when); Standing decision rule; SESSION/ARC mode; HANDOFF (10-block schema); [T1]/[T2] tiers; Resume Launcher; tier pair (economy/standard/frontier × low/medium/high); explore/audit mode; mode_basis; GROUNDED/HEURISTIC-OK/SPECULATIVE; ESSENTIAL/SPECULATIVE; KEEP/KEEP-WITH-CAVEAT/DEFER/DROP; DEFER fall-through; Synthesis-check; L3 six-block schema.

**Skills with NO caller in loom-code or loom-design (user-phrase-only entry):**
- cot-explain
- dbt-model-style
- distill-sessions (a test file asserts it fires on user phrasing; no skill-to-skill call)
- handoff
- independent-advisor
- recap-state

(6 of 12 skills. The other 6 — brief-before-asking, complexity-critique, decision-map, git-memory, goal-create, proposal-critique — are each named/called from at least one loom-code or loom-design skill.)

**Skills whose output has no consumer found:**
- brief-before-asking (no output at all — chat only)
- complexity-critique (verdict is chat-only)
- independent-advisor (report is chat-only, no file)
- proposal-critique (triage is chat-only)
- recap-state (chat only, explicitly forbidden to write a file)
- dbt-model-style's edited `.sql` file has one *conditional* consumer (the redshift-comment MCP, only when `persist_docs` is enabled) — otherwise none
- handoff's HANDOFF file has exactly one consumer: this same skill's own Resume mode in a future session — no other skill reads `.claude/handoffs/*`
- cot-explain's `.md`/`.html`/`.fidelity.md` are consumed only internally by its own scripts in the same run; nothing outside the skill reads them afterward (both declared temporary)
