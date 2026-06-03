# Brief — `dogfood-skill-testing` (dev-workflow)

Date: 2026-06-03 · Stage: brainstorming → (pending) writing-plans
Source pattern: `vercel-labs/agent-browser` `skill-data/dogfood/` (6-phase exploratory QA + issue-taxonomy + report-template)

## Problem

When building a skill, the author can statically score its design (`skill-judge`),
optimize its description against *known* trigger prompts (`skill-creator-advance`
eval loop), or mine *past* session logs for friction (`distill-sessions`). None
of these does **adversarial, exploratory, black-box behavioral probing of a
skill-in-development** — a fresh agent that *doesn't know the author's intent*
actively trying to make the skill misbehave, surfacing the **unanticipated**
defects (mis-trigger, over-trigger, cold-start collapse, jargon leak, gate
bypass, workflow drift, convention violation) that no author-written test prompt
covers.

JTBD: *When I've drafted or edited a skill and want to know how it actually
behaves before I trust it, I want to unleash a fresh blind agent that probes its
triggers and workflow and reports what breaks with reproducible evidence, so I
ship a skill that fires when it should and does what it claims — not one that
passed my own conformance checks but fails on inputs I never imagined.*

This formalizes the **"BLIND round-trip dogfood"** repeatedly deferred across
prior skill work (memory: `feedback_real_dogfood_catches_semantic_bugs`,
`project_handoff_v0_1_shipped` v0.2 deferred item).

## Users

- **Primary**: kouko, authoring/editing skills in the `monkey-skills` monorepo,
  mid-development — the skill is a **raw `SKILL.md` in the working tree, NOT yet
  installed** into `~/.claude/plugins/cache/`. Wants a behavioral gut-check
  before committing.
- **Conditions**: skill-under-test is un-registered; testing must work pre-install
  by reading working-tree files directly. Runs inside a `code-toolkit:*` /
  `dev-workflow:*` SDD session.
- **Existing tools they reach for**: `skill-judge` (static), `skill-creator-advance`
  (author conformance loop), `distill-sessions` (telemetry). This fills the
  black-box-exploratory gap between them.

## Smallest End State

A **pure-prompt** skill `dev-workflow/skills/dogfood-skill-testing/` (no scripts;
mirrors the original dogfood's SKILL.md + references + templates shape) that, given
a **path to a skill-in-development directory in the working tree**, runs a
**dual-pass** behavioral dogfood and emits a structured findings report.

**Substrate (the load-bearing port decision):** the target is not installed in the
user's real environment, but trigger fidelity is highest when measured through the
real harness. Two mechanisms, by component:

- **Trigger activation → real-harness sandbox (primary)** — copy the working-tree
  skill (+ a small fixed set of distractor sibling skills) into a **temp
  `.claude/skills/`**, run `claude -p "$QUERY" --max-turns 1 --allowedTools Skill
  --output-format stream-json`, and parse the JSONL stream for `Skill()` tool_use
  events to decide fired / didn't-fire. Ephemeral sandbox ≠ the user's real
  install, so this still satisfies "test a skill that isn't installed." **Fallback**
  (no `claude` CLI / no API key): inject the `description` into a fresh subagent's
  synthetic skill-menu and ask which it routes to — mark findings
  `fidelity:approximate`. (Method: Scott Spence sandboxed-activation eval.)
- **Behavioral / read probes → content injection** — read the raw working-tree
  `SKILL.md` (+ bundle) and inject into fresh `Agent` subagents (cold-reader,
  executor, auditor). No live registry needed.

This makes the skill **agent-driven-CLI**, like the original dogfood drives the
`agent-browser` CLI — the SKILL.md instructs the agent to run `claude -p` + Bash;
no bundled Python harness (still "pure-prompt" in the no-compiled-scripts sense).

**Dual-pass (user-selected scope) — structured per the user's OWN mined dogfood
practice (see §Dogfood method):**

1. **Blind pass — activation harness + cold-reader** — two parts:
   - **Activation measurement** (real-harness sandbox, primary; injection fallback,
     per Substrate): run a corpus of **should-trigger** + **should-NOT-trigger**
     queries through `claude -p` and compute true-positive (miss) + true-negative
     (over-trigger) rates against a distractor set. Corpus shape per Scott Spence:
     ~20 should-trigger + ≥5 should-NOT-trigger, ≥2 runs each (non-determinism →
     average, don't conclude from one run). Catches: `trigger-miss`, `over-trigger`.
   - **Cold-reader audit** (fresh zero-context subagent reads the SKILL.md as a
     first-time user): fixed question set (self-contained? trigger hit/miss + 2
     unsure cases? per-mode procedure executable? undefined terms?). Catches:
     `cold-start`, `jargon-leak`, `description↔behavior mismatch`. Defeats **bias
     accumulation** — the in-session dev agent treats its own jargon as baseline;
     the cold-reader cannot.
2. **Informed pass — executor + blind auditor (context-firewalled)** — TWO fresh
   subagents:
   - **executor** (informed): given the **full SKILL.md body + bundle**, manually
     runs the skill end-to-end on **real/realistic input**, explicitly told *"the
     user has NOT installed this plugin — execute as if invoked"*, forced through
     the **cold-start / fallback path** (no config folder present).
   - **auditor** (blind): given **only the executor's produced output** and a
     domain-expert persona, told *"you have NO context about how this was produced"*
     — judges quality independently. **Quality rubric = the skill's own declared
     contract + a domain standard** (user decision 2026-06-03): first extract the
     skill-under-test's self-declared success criteria / gates / output contract
     (what it says it delivers, what it says it blocks), then add the domain
     persona's professional bar (factual correctness, no fabrication, no leakage).
     This catches BOTH *"failed its own declared bar"* AND *"met its bar but is
     domain-wrong"* (the §11-1 / NDA-leak class). Output-quality is a **first-class
     peer of triggering** in v0.1 — specified as concretely (representative-task
     selection + this rubric), not an afterthought. The firewall is load-bearing: it catches what
     self-grading structurally cannot (e.g. fabricated citation passing a
     format-only check). **Industry LLM-as-judge guardrails baked in**: (a) the
     auditor judges against an **independent rubric / the description's promise**,
     NOT against intent re-inferred from the artifact — defends the *oracle problem*
     (Konstantinou, ICST 2025: LLM-written assertions echo the buggy impl, not the
     intent); (b) judge **non-determinism** → run ≥2×, pin the model version, treat
     a single run as variance not verdict; (c) judge the **trajectory** (executor's
     steps), not only the final output — correct output can mask broken reasoning;
     (d) **coarse score buckets** (fine scales hurt consistency).
   Catches: `workflow-drift`, `gate-bypass`, `convention-violation`,
   `integration-crash` (modules green alone, broken joined on real data),
   `valid-but-wrong output`.

**Phase structure** (port of dogfood's 6 phases, substrate-swapped):

| dogfood (original) | dogfood-skill-testing |
|---|---|
| Initialize (dirs, template, browser session) | Locate target skill dir; read+split frontmatter(description)/body; enumerate bundle; create `docs/skill-dogfood/<date>-<skill>/`; copy report template |
| Authenticate | Build probe contexts (blind-context = description[+distractors]; informed-context = full body+bundle) |
| Orient (screenshot/snapshot map) | Read skill → derive probe matrix: intended triggers, near-miss should-NOT-triggers, workflow steps, gates, conventions to assert |
| Explore (visit pages, edge cases) | **Run dual-pass probes** via fresh `Agent` subagents |
| Document (append issue + repro evidence) | Append each finding immediately; **evidence = probe prompt + subagent transcript excerpt** showing the defect |
| Wrap up (counts, close) | Finalize severity counts; close report |

**Bundled files** (all single-level subfolders — conforms to flat-folder hook):
- `references/defect-taxonomy.md` — severity (Critical/High/Medium/Low) ×
  categories (Trigger-miss / Over-trigger / Cold-start / Workflow-drift /
  Gate-bypass / Jargon-leak / Convention-violation / Progressive-disclosure /
  Output-quality). Port+adapt of `issue-taxonomy.md`. Each category annotated with
  the measured community frequency where known (Trigger-miss 68% / desc-too-short
  41% / missing-version 62% / over-trigger-conflicts — from the 214-skill audit) so
  the dogfood agent prioritizes the high-base-rate defects first.
- ~~`references/dogfood-method.md`~~ **FOLDED INLINE** (complexity-critique
  2026-06-03, RESHAPE): the operative method rules (cold-reader question set,
  executor+auditor firewall, axis-sweep predict-then-execute, force-the-fallback-
  path, floor-not-ceiling, environment guards) live **inline in the SKILL.md
  workflow steps**, not a standalone shallow-module file. Per the user's own
  `extract-to-reference` lesson: one-sentence behavior rules stay inline.
- `templates/dogfood-report-template.md` — metadata (skill path/version/date/passes/
  model-pinned) → severity summary table → per-finding blocks → **Raw outputs
  appendix** (every executor artifact + probe transcript + activation query→result,
  so the user can review what the auditor judged, then drive fixes by talking to the
  main agent — no embedded feedback form). **The report's consumer is the
  main agent that will FIX the skill**, so every finding must be fix-actionable,
  not just a symptom report. Per-finding fields:
  `FINDING-###` · severity · category · pass[blind|informed] · **probe prompt** ·
  **expected** · **actual** · **transcript evidence** (excerpt proving it) ·
  **root cause** (why it happened) · **why static review missed it** (what a
  structural/self-grade check sees as PASS while this is broken — the
  floor-not-ceiling signal) · **location** (`SKILL.md:§section` or
  `references/<file>` the defect traces to — frontmatter description / a body
  workflow step / a gate clause / a bundled file) · **suggested fix direction**
  (advisory edit class — e.g. "add trigger token 'X' to description first line",
  "§Workflow step 3 says 'verify' but not how → spell out the check", "gate clause
  is a SHOULD, defect needs MUST") · repro (how to re-run the probe).
  Findings are **advisory** — dogfood points the main agent at the exact location +
  change class; the main agent decides and applies the edit (auto-fix stays out
  of scope).
  **Human-in-the-loop (user decision 2026-06-03, refined)**: the report must SURFACE
  THE RAW TEST OUTPUTS to the user, not just the auditor's distilled verdict — every
  finding links to (and an appendix collects) the **actual executor-produced
  artifact + the probe transcript excerpt** that the auditor judged, plus each
  activation run's query → fired/didn't. The user is the final calibrator
  (LLM-as-judge research: *human calibration catches what judges miss*; user's own
  lesson: tool-result-only outputs were un-reviewable). **No embedded feedback
  form** — the report is simply the conversational handoff artifact: the user reads
  the surfaced outputs, then **talks to the main agent directly** to drive the fix.
  The report's job is to make that conversation possible (outputs visible) and
  productive (findings already localized + fix-pointed); the user steers from there.
- `trigger-eval.json` — **self-dogfood** trigger corpus (this skill eating its own
  food), matching sibling convention (`distill-sessions/trigger-eval.json:1`).
  (`test-prompts.json` **deferred to v0.1.1** per complexity-critique — the skill
  can dogfood its own workflow dynamically; the static workflow corpus is a
  nice-to-have, not v0.1-blocking.)

**Complexity verdict (2026-06-03): RESHAPE applied.** No god-object (trigger /
output-quality / readability compose cleanly at the report boundary). Cuts: folded
`dogfood-method.md` inline; deferred `test-prompts.json`. **Kept by user decision**:
the injection fallback for activation (robustness / headless-portability over the
minor control-flow saving — trade-off named & accepted). Bundle: 1 reference +
1 template + 1 corpus.

**Evidence standard** (port of dogfood's "repro is everything"): every finding
must cite the **actual probe prompt + the subagent's actual response** (transcript
excerpt) that demonstrates the defect — no findings asserted from reading SKILL.md
alone (that is `skill-judge`'s job). Target ~5–10 well-evidenced findings over
volume.

## Dogfood method (codified from user's own practice)

Mined from ~10 prior dogfood episodes across monkey-skills main + worktrees (two
parallel transcript-mining agents, cross-validated). This skill **codifies the
user's existing method**, it does not invent one. Load-bearing principles:

1. **Cold-reader defeats bias accumulation.** The single highest-yield technique:
   a fresh zero-context subagent reading the SKILL.md as a first-time user. The
   in-session dev agent unconsciously treats its own jargon/structure as baseline
   and self-rationalizes — only a firewalled fresh agent reacts like a real first
   user. (User self-caught a real jargon-leak this way: *"我用了 jargon 沒定義,
   這正是 dogfood fail"*.)
2. **Executor / auditor context firewall.** The agent that *runs* the skill is
   informed; the agent that *judges the output* must be blind to how it was
   produced. Self-grading is blind to its own blind spots (the §11-1 fabricated
   citation passed `self_grade.py` SRC 5/5; only the blind GC auditor caught it).
3. **Structural pass is the floor, not the ceiling.** A green grader / passing
   smoke test is necessary, never sufficient. **Forbid stamping "dogfood-pass"
   when the behavioral test was deferred** (the wiki-ingest anti-pattern: structural
   pillars green + "dogfood-pass" while the LLM-behavior core was never run).
4. **Real data, then EXECUTE the output.** Synthetic + static-pass gives false
   confidence; the dangerous bugs are valid-but-wrong (AOV 3× divergence) and
   integration crashes (modules green alone, crash joined on a real document).
   These only appear when the skill's actual workflow runs on real/realistic input
   and the produced artifact is judged.
5. **Axis-sweep: predict-then-execute.** Each round names the highest-risk untested
   axis (input shape / language / grain / semantics / cold-start), **predicts the
   failure before running**, then executes to confirm. Rotate to a new axis when
   one is exhausted (user: *"再跑別的 dogfood axis... 測試徹底一點"*).
6. **Force the cold-start / fallback path.** Highest bug density, least exercised —
   run with no config folder present.
7. **Environment guards.** Pin to `origin/main` (worktree inherits stale branch
   state — a subagent once recommended a deleted skill); post-run `grep` any
   recommended slug against the current skill folder; flag meta-dogfood familiarity
   bias and triangulate against an external skill.
8. **Persist findings to disk.** Dogfood outputs that lived only in tool-result
   memory were later un-reviewable. Always write the severity-tagged audit report.
9. **Human is the final calibrator.** Show the user the RAW test outputs +
   transcripts (not just the auditor's verdict) so they can judge for themselves,
   then hand off to a normal conversation with the main agent to drive the fix — no
   embedded feedback form. The auditor's judgment is a draft, not gospel; LLM judges
   share the agent's blind spots and the human closes that gap by reading the
   outputs and steering.

## Current State Evidence

- **Forward (entry/registration)**: sibling skill-* tools live in
  `dev-workflow/skills/{skill-judge,skill-creator-advance,distill-sessions,skill-refactor,skill-tuning}`;
  new skill slots beside them. Plugin manifest
  `dev-workflow/.claude-plugin/plugin.json:1` (v2.14.1) keywords array enumerates
  the family — `dogfood-skill-testing` + a `version` bump (→ 2.15.0, minor: new
  skill) land here.
- **Reverse (SSOT/sync)**: dev-workflow skills are **self-contained** (no internal
  `distribute.py` — unlike code-toolkit↔code-team). The taxonomy + report-template
  SSOT to **port/adapt** is external: `vercel-labs/agent-browser`
  `skill-data/dogfood/{references/issue-taxonomy.md,templates/dogfood-report-template.md}`.
  No drift-sync obligation.
- **Error/boundary (fidelity gap)**: injected-context trigger simulation
  **approximates** but does not equal the live Claude Code harness trigger
  mechanism (which uses the registered-skill description set). Precedent for this
  approximation: `dev-workflow/skills/distill-sessions/trigger-eval.json:1`
  (`{query, should_trigger}` pairs evaluated without live firing). → goes in Open
  Questions as a named limitation.
- **Data (probe corpus shape)**: reuse existing precedents —
  `trigger-eval.json` = `[{query, should_trigger:bool}]` for blind-trigger probes;
  `test-prompts.json` = `{id, category(happy-path|edge-case|stress), prompt,
  expected_behavior, edge_case_dimensions}`
  (`skill-judge/test-prompts.json:1`) for informed-workflow probes.
- **Boundary (negative space, from each sibling's frontmatter)**:
  `skill-judge` = static design score, explicitly "Do NOT use for behavioral/
  runtime testing"; `skill-creator-advance` = create/redesign + **conformance**
  eval loop (author's known prompts); `distill-sessions` = retrospective telemetry
  mining; `skill-refactor` = token/structure, behavior-preserving; `skill-team` =
  domain-team authoring. dogfood-skill-testing = **prospective black-box
  exploratory behavioral discovery** — disjoint from all five.
- Evidence paths appendix: `dev-workflow/.claude-plugin/plugin.json`,
  `dev-workflow/skills/skill-judge/SKILL.md` (frontmatter lines 1–18),
  `dev-workflow/skills/distill-sessions/trigger-eval.json`,
  `dev-workflow/skills/skill-judge/test-prompts.json`,
  `dev-workflow/CHANGELOG.md` (Keep-a-Changelog + SemVer format).

## Decision

**Build** `dev-workflow:dogfood-skill-testing` v0.1 as a pure-prompt skill that
runs **dual-pass (blind + informed)** black-box behavioral dogfood on an
**un-installed, working-tree** skill by **injecting its raw files into fresh
subagents**, and emits a transcript-evidenced findings report to
`docs/skill-dogfood/`.

The report is an **agent-actionable fix dossier**: each finding localizes the
defect to a SKILL.md section / bundled file, states root cause, and names a
suggested edit class — enough for the main agent to apply an effective fix
(advisory; dogfood discovers + points, main agent edits).

**Will NOT build**: live-harness trigger hooking; auto-fixing found defects;
scoring/grading (that's skill-judge); scripts/automation harness (pure prompt,
like original dogfood); a CI integration. Findings **feed** `skill-creator-advance`
(author fixes) / `distill-sessions` (corpus) — dogfood-skill-testing only
discovers + reports.

## Alternatives Considered (Axis 4 — researched)

Industry approaches to testing/evaluating agent skills (via WebSearch, EN+JA):

1. **White-box conformance eval (train/test split on trigger prompts)** —
   Anthropic skill-creator 2.0 / MLflow skill eval
   ([claude.com blog](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills),
   [MLflow](https://mlflow.org/blog/evaluating-skills-mlflow/)).
   • Pro: quantitative, regression-trackable. • Con: only measures conformance to
   *author-written* prompts — misses unknown-unknowns. → already covered by
   `skill-creator-advance`; NOT this skill.
2. **Behavior-Quality (BQ) three-layer testing (assertions/labels/judges)** —
   ([Kent Chen, Medium](https://kentchendev.medium.com/working-with-claude-code-testing-ai-agent-behavior-a-practical-guide-to-bq-testing-601dbbdd53cd)).
   • Pro: tests action-patterns not exact output (right for non-determinism).
   • Con: still presumes known expected behavior. → borrow the "judge catches
   nuanced decision errors" idea as the informed-pass evidence judge.
3. **Exploratory adversarial dogfood (black-box, blind agent finds bugs)** —
   `vercel-labs/agent-browser` dogfood skill. • Pro: surfaces unanticipated
   defects, discovery not conformance. • Con: non-deterministic, needs human
   triage of findings. → **the model we port.**
4. **JA signal**: 自動発火率 20–50% 実測 (Scott Spence) /「description冒頭50文字に
   トリガーワード集中」/「100%発火しない→Slash Commandsへ」
   ([zenn](https://zenn.dev/yoshi333/articles/e0c778062332f3),
   [sios tech-lab](https://tech-lab.sios.jp/archives/51010)). → confirms
   **trigger-firing is THE highest-value defect class** → blind pass leads.

**Empirical agent-skill-specific data (round 2, deep-fetched)** — grounds the
defect taxonomy + the trigger method in measured numbers, not traditional SWE:

- **Sandboxed activation eval** (Scott Spence,
  [measuring-skill-activation](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)
  / [make-skills-activate-reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)):
  no-hook baseline **50–55%**; forced-eval hook **100% TP + 100% TN**; llm-eval
  **100% TP but 20% TN (4 false positives)**. Corpus 22 standard (19 should-fire) +
  24 hard (5 should-NOT-fire), 2 runs, ~$5.59/250 invocations. → the sandbox-harness
  method this skill adopts; over-trigger is only measurable with should-NOT-fire +
  distractors.
- **214-skill audit, 73% silently broken**
  ([DEV/thestack_ai](https://dev.to/thestack_ai/i-audited-214-claude-code-skills-73-were-silently-broken-2m9a)):
  missing trigger phrases **68%**, desc <20 words **41%**, no body code examples
  **55%**, missing version **62%**, score <60/100 **73%**, 12 overlapping-desc
  conflict pairs. *"A bad SKILL.md doesn't throw an error — it just never gets
  invoked."* → defect-taxonomy frequencies + the skill's reason-for-being.
- **LLM-as-judge pitfalls** (Braintrust / Patronus / Monte Carlo / 電通デジタル /
  issoh / pharmax): judges share the agent's blind spots; oracle problem
  (Konstantinou, ICST 2025); correct output masks broken reasoning; judge
  non-determinism (multi-run + pin version); layered deterministic-vs-LLM;
  coarse score buckets; position/verbosity bias. → baked into the auditor role.
- **Agentic red-team** ([OWASP Top 10 for Agentic Apps, Dec 2025](https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications);
  promptfoo / DeepTeam / ARTKIT): per-step labeled-trajectory grading. Mostly
  security-framed — borrow the trajectory-grading idea, not the threat model.

**EN/JA agreement**: both treat trigger-precision as the dominant failure mode
and accept non-determinism (test patterns, not exact output). No disagreement.

**My take**: port #3's black-box exploratory spirit, instrument the blind pass
with #1's trigger-corpus shape (`should_trigger` pairs) and the informed pass
with #2's judge idea. Recommend dual-pass (matches user selection).

## What Becomes Obsolete (Axis 5)

Nothing is removed (additive new skill). Forward-looking: once shipped, the
**manual ad-hoc "let me spin up a subagent and see if my skill triggers"** dance
(done by-hand repeatedly in prior sessions, never codified) becomes obsolete —
this skill is its formalization. The repeatedly-deferred "BLIND round-trip
dogfood" backlog item is realized and should be struck from the deferred list.

## Out of Scope

- Auto-fixing / auto-editing the skill-under-test (discovery + report only).
- Numeric grading / letter scores (skill-judge owns that).
- Live-harness trigger registration or installing the skill to test it.
- Scripts / Python harness (pure-prompt skill).
- Testing installed/published skills via the real registry (v0.1 = working-tree
  injection only).
- CI / automation integration.
- Rolling the dogfood pass across many skills in one run (single target per run).

## Open Questions

1. ~~Trigger-sim fidelity~~ **RESOLVED** — v0.1 uses the real-harness sandbox
   (`claude -p` + temp `.claude/skills/`) as primary, injection as fallback marked
   `fidelity:approximate`. (User decision 2026-06-03.) Remaining sub-question: pin
   which `claude` model for the activation runs (lean: the session default;
   document it in the report header for reproducibility).
2. **Distractor skills for the blind menu** — over-trigger is only detectable with
   distractors present, so v0.1 SHOULD include a small fixed distractor set. Open:
   hand-pick from dev-workflow siblings, or let the agent pick N nearby
   descriptions? (Lean: small fixed sibling set.)
3. **Report home** — `docs/skill-dogfood/<date>-<skill>.md` (mirrors
   `docs/skill-mining/`)? Confirm naming.
4. **Subagent count / depth budget** — (Lean: port "5–10 well-evidenced findings
   over volume"; v0.1 ≈ 1 cold-reader + 1 executor + 1 auditor per axis, ~2–3 axes.)
5. **Persona matrix in v0.1?** — mining shows parallel personas (self / domain-expert
   / cold-start) separate router-discoverability from procedure-correctness. Fold
   into v0.1 or defer? (Lean: cold-start persona is mandatory; extra personas
   optional/deferred.)
6. **Graded-skill calibration (out of scope v0.1?)** — for skills that ship a
   grader, the user's practice adds an LLM-vs-hand Pearson calibration
   (misfire→deterministic-tier, never lower the target). Powerful but specialized;
   propose **out of scope for v0.1**, candidate for v0.2.
7. **Re-dogfood-to-confirm loop** — the user re-runs the SAME cases after patching
   to confirm no regression (verdict arc across versions). v0.1 supports this by
   re-invocation; a built-in regression-diff is a v0.2 candidate.
