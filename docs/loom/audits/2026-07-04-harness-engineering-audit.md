# loom-* vs Harness Engineering Standards — Audit

- **Date**: 2026-07-04
- **Scope**: all five loom plugins (loom-product-principles, loom-interface-design, loom-spec, loom-code, loom-pipeline) + family tissue (#488) + firing harness + git-memory delegation
- **Yardstick**: "harness engineering" as defined by the 2026-02 canon (term coined by Mitchell Hashimoto; formalized by OpenAI / Ryan Lopopolo): *"the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."*
- **Status**: findings accepted; implementation decisions PENDING discussion (see §Recommendations)

## Verdict (one line)

loom-* meets or exceeds the standard on process-discipline dimensions (7/11 ✅) — the gaps concentrate in **deterministic enforcement**: several core disciplines that the canon (and Anthropic's own steering framework) classify as hook-grade are still carried by prose.

Reference datum: swapping the harness moves SWE-bench by ~22 points; swapping the model moves it ~1 point (Morph analysis, cited in the canon).

## Scorecard

| # | Standard dimension | loom-* state | Verdict |
|---|---|---|---|
| 1 | Mechanisms over requests | Core disciplines (TDD iron law, review-before-push, verification-before-completion, git-memory gate, brainstorm-first) are **prose-enforced**; only 2 repo hooks exist (skill folder structure, codex-manifest drift — both PostToolUse) | ⚠️ |
| 2 | Evals as harness components | Firing harness + 3 corpora (28 records) + F3 live acceptance = leading practice; but **manually triggered, not in CI**; trap #6 transcript check not automated | ⚠️ |
| 3 | Feedback-speed hierarchy (ms→s→min→h) | ms-tier exists for skill authoring (2 hooks); code-side feedback relies on subagent review (min–h tier) + CI | ⚠️ |
| 4 | Context economy | SKILL.md ~6k-token cap; §Intake points at SSOT, never copies (test-pinned); conditional reference loading; MEMORY.md index style | ✅ |
| 5 | Planning/execution separation + human gates | brainstorm → plans → SDD; 4 human gates; never-auto-merge; PR-open terminal stop; continuous-mode STOP contract | ✅ |
| 6 | Cross-session state | git-memory (trailers + PR Memory + `--verify` executable gate); handoff [T1]/[T2] verification commands = standardized startup routine; TOML-intent/JSON-state separation | ✅ |
| 7 | Typed handoff boundaries | Workflow `schema` forces structured subagent output; but **verdicts are text conventions**, not schema-validated (conductor v0.1's 8 🔴 were all cross-module field-contract bugs) | ⚠️ |
| 8 | Docs designed for rot | Dated frozen briefs/specs + status ≈ ADR practice; Decision trailers; README sweep option C explicitly scoped by drift risk | ✅ |
| 9 | E2E — give agents eyes | ui-verification (host browser/device automation, N/A first-class, half-measure labeling) — exactly the canon's countermeasure to premature "done" | ✅ |
| 10 | Observability | Run ledger; discard/unparsed counts never swallowed (hardened in #489); no hook-event telemetry pipeline | ⚠️ |
| 11 | Sunset clause (model improves → harness shrinks) | LOOM-SIMPLIFY ledger + deliberate-simplification review dimension — rare explicit alignment | ✅ |

**Noted tension (not a defect)**: SessionStart standing injection ≈ 10KB (two hooks + router body) vs the canon's <50-line pointer ideal (IFScale: 150–200 instructions triggers primacy bias). This is a conscious trade backed by F3 behavioral testing (less injection → lower firing rate). Next harness touch: measure injection-halved vs firing-rate delta.

## The core finding: enforcement carrier inventory

Two kinds of constraint:

- **Prompt constraint**: rule lives in SKILL.md prose; the model *chooses* to comply. On violation, nothing happens.
- **Mechanism constraint**: rule encoded in hook/CI/script exit codes. On violation, the operation **physically fails**.

| Discipline | Rule text strength | Actual carrier | On violation |
|---|---|---|---|
| TDD iron law | "No production code without a failing test first" | prose | nothing fires |
| No push without review | "git push without review-PASS = violation" | prose | push succeeds |
| verification-before-completion | package-level tests required before "done" | prose | "done" is claimable |
| git-memory commit gate | "invoke before every commit" | prose (+ `--verify` script that someone must remember to run) | commit lands |
| brainstorm before implementing | "skip = violation" | prose | no friction |
| Skill folder flatness | — | **PostToolUse hook** | Write/Edit blocked ✅ |
| Codex manifest sync | — | **PostToolUse hook + CI** | blocked ✅ |
| Commit convention | — | **CI (14 checks)** | PR red ✅ |
| Workflow handoff fields | — | **schema-forced** | output rejected, agent retries ✅ |

Pattern: **mechanisms protect peripheral engineering quality; prose carries the soul of the system. Protection strength is inversely correlated with importance.**

Why this is a real risk (all three from this repo's own history):

1. loom's "Red flags" tables are an admission that prompts get rationalized around — and they fight rationalization with more prose (recursive dependence on the same unreliable substrate). Hooks don't listen to excuses.
2. Weak model tiers fabricate check outputs (obsidian dogfood memory: disk-level cross-check is mandatory). Prompt compliance on weak tiers is not discounted — it is zero. SDD implementers often run on cheap tiers.
3. The 22-vs-1 datum above.

Calibration — loom is NOT bare prose; it sits mid-spectrum:

```
bare prose ── test-pinned prose ── behavior-verified prose ── mechanism
(typical repo)  (loom today)          (loom today)             (the gap)
```

Test-pinned: anti-copy assertions on §Intake, cap tests on router lines. Behavior-verified: firing harness + F3 drive real `claude -p`. Social mechanism: SDD triads, whole-branch review, fresh-context panels — effective, but min–h latency, and the reviewers are themselves prompt-constrained.

## Industry research (2026-07-04, EN+JP sweep)

### Consensus 1 — official position: only hooks are deterministic

Anthropic's steering framework classifies CLAUDE.md / Rules / Skills / Subagents all as **Suggestive**; only Hooks (and managed settings) as **Deterministic**. Official phrasing: *"When there's something that absolutely must not happen, an instruction is the wrong tool… under pressure, in a long session or an ambiguous situation the model can fail to follow a prompted rule."* Decision test (MindStudio distillation): would violation cause financial loss / data leak / compliance breach → hook; otherwise prompt suffices.

### Consensus 2 — three-layer division, not replacement

Nobody argues prose frameworks are wrong. The JP-community formulation: **CLAUDE.md = rule definition, Skills = workflow guidance, Hooks = mechanical enforcement** — layered, not substitutive. Anthropic's anti-pattern table matches: "every time X do Y" in CLAUDE.md is wrong (hook), but a 30-line procedural workflow as a hook is also wrong (skill). loom's architecture is correctly chosen; its third layer is thin.

### Consensus 3 — "hard to mechanize" has a known resolution: hook guarantees the gate FIRES; judgment can stay LLM

**TDD Guard** (nizos/tdd-guard, actively maintained) is the mechanized TDD iron law: PreToolUse intercepts Write/Edit/MultiEdit on every file write; validator is another LLM (configurable fast/capable model) judging "failing test exists" / "no over-implementation"; violation → exit 2 + corrective feedback. Supports pytest (loom's stack), Vitest/Jest/Go/Rust/RSpec; mid-session toggle; custom rules. Known costs: per-edit LLM call (latency + spend); bypass drift (agents route around — author's successor project **Probity** uses session-activity analysis instead).

Key insight: **the hook's determinism is that the check always runs, not that the verdict is deterministic.** Interception is mechanical; judgment can be model-based — loom already owns the worker≠judge machinery; TDD Guard just mounts the judge at write-time (seconds) instead of review-time (minutes–hours).

Superpowers (loom-code's prototype) moved the same direction: hook-assisted skill activation (loom's SessionStart hook + F3 already does this ✅); more aggressive kin (VSDD plugin) hook-block implementation code during spec phases.

### Counter-caution — approval fatigue and bypass behavior

Repeated community lesson ("500 lines of rules" genre): over-hooking produces approval fatigue and **workaround behavior** (heredoc file writes, matcher evasion) that is harder to detect than honest violation. Industry pacing: start with rules whose violation cost is highest AND whose interception condition is most mechanical; pilot per-edit LLM gates later with false-block measurement. This matches loom's sunset-clause ethos: every hook also needs an existence justification.

## Recommendations (implementation PENDING discussion)

| Priority | Item | Interception condition | Cost |
|---|---|---|---|
| 1 | PreToolUse: block `git push` / `gh pr create` without review-PASS artifact | pure file/state check, zero LLM | ~day |
| 2 | PreToolUse: block `git commit --no-verify` | string match | trivial |
| 3 | Stop hook: package-level tests as completion condition (`stop_hook_active` loop guard) | deterministic pytest run | ~day |
| 4 | TDD Guard pilot on one real SDD venue: measure latency / spend / false-block rate, then adopt-vs-build decision | hook mechanical + LLM judge | pilot first |
| 5 | Firing-harness offline half into CI (`validate_corpus` + `grade`; `run` mode stays manual/nightly) | pure offline | small |
| 6 | Verdict schema-validation script (locks reviewer output fields; echoes conductor v0.1's 8 🔴 lesson) | script | small |
| — | Brainstorm quality / review depth: **keep prose + evaluator** (industry consensus: Suggestive tier is correct for non-catastrophic quality judgments; loom's test-pinned + behavior-verified prose is the ceiling of that tier) | — | — |

## Sources

- Steering Claude Code: skills, hooks, rules, subagents — Anthropic official: https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- awesome-harness-engineering (taxonomy, 12 categories): https://github.com/ai-boost/awesome-harness-engineering
- Harness Engineering Best Practices for Claude Code / Codex Users: https://nyosegawa.com/en/posts/harness-engineering-best-practices-2026/
- nizos/tdd-guard: https://github.com/nizos/tdd-guard (author blog: https://nizar.se/tdd-guard-for-claude-code/; successor: https://github.com/nizos/probity)
- Claude Code Skills vs Hooks (MindStudio): https://www.mindstudio.ai/blog/claude-code-skills-vs-hooks-difference
- Prompts Don't Enforce Rules. Hooks Do.: https://claudecodefornoncoders.substack.com/p/prompts-dont-enforce-rules-hooks
- Superpowers TDD 強制フレームワーク解説 (JP): https://ai-revolution.co.jp/media/superpowers-claude-code-guide/
- TDD Guard 検証 (Zenn, JP): https://zenn.dev/serada/articles/20260213-claude-code-commands
- Harness Engineering: Making AI Coding Agents Work in 2026 (Faros): https://www.faros.ai/blog/harness-engineering
