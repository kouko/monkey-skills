# Brief — review-cost reduction, Option B (contract-class-scoped docs review + single-round-with-confirmation + host-native model tiering + plan-reviewer misroute fix)

- Date: 2026-08-11 (v2 — Option B rescope, supersedes the same-day v1 "recalibrate-only" draft after user chose B; v1's aggregation change is CONTAINED in B)
- Arc authorization: user, verbatim — 「可以幫我把整套機制都實作在 loom 裡面嗎？ 另外模型選擇機制是否可以相容 codex ?」; rescope to B chosen by user in-conversation (「B 吧」) after the demolition evaluation.
- Branch: `feat/review-cost-reduction` off main@18bc7922
- Standing constraint: LAST review-mechanism arc for now (user budget stop-loss). New discoveries get FILED, not built.

## Problem

Documentation review under loom costs an order of magnitude more than the value it demonstrably delivers, and the cost does not respond to model tier. Grounded diagnosis (three first-party audits + industry research + n=1,357 dispatch audit):

1. **The review pool is bottomless by arithmetic, not by reviewer failure.** Blind 4-arm experiment (2026-08-04): 7 accurate, zero-overlap 🟡 findings on an already-passed corpus — "reviewer found nothing" is not a reachable terminal state for prose; a tested "harm gate" filter was refuted. The 2+🟡→NEEDS_REVISION rule converts this inexhaustible sampling into mandatory revision loops.
2. **Revision rounds manufacture their own defects.** 9-round audit (2026-07-28): 6/9 rounds found defects the previous round's remediation introduced.
3. **The demonstrated value is narrow**: exactly ONE load-bearing intercept in the mechanism's history — an instruction-class defect in implementer-facing contract text, caught only by whole-artifact scope (n=1). The costliest defect class is structurally invisible to docs review (2026-07-31 backtest); cheap mechanical checks retired two defect classes permanently at a fraction of a round's cost.
4. **Record-class prose dominates the reviewed volume**: 4-week git data — 668 of 1,179 changed `.md` file-instances (57%) are `docs/loom/` records (audits, backlog, reports); 26% of md-touching commits touch ONLY records. Industry reviews none of this: the only coding-agent project with dedicated docs review (github/spec-kit `/speckit.analyze`) reviews ONLY the three consumed planning artifacts, advisory-only; every AI PR reviewer surveyed treats `.md` as incidental advisory; docs-as-code guidance (Vale/markdownlint at Grafana/Datadog) reserves blocking for mechanically-checkable defects. EN and JP research arms agree (JP: coding-agent-context dedicated docs review NOT FOUND; textlint CI practice is gradual, no blocking-policy precedent).
5. **Reviewer arms inherit the most expensive model by default and it buys no fewer loops** (n=1,357: docs arm 93% expensive tiers; 464 sonnet spec-reviews zero incidents; round counts track artifact type + contract rules, not tier).
6. **plan-document-reviewer misroutes as an agent type** — a cold operator substituted docs-reviewer with the wrong checklist for 3 rounds ending in a fiat PASS (field incident, external consumer repo).

Job to be done: **review only the text that machines execute, block only on what must not ship, confirm fixes without re-sampling, on the cheapest empirically-safe tier, with routing a cold operator cannot get wrong.**

## Users

- kouko orchestrating loom arcs in this repo (Fable-tier sessions where "inherit" = most expensive model).
- Cold operators / weak-model orchestrators in external consumer repos — every new rule must be mechanical (path rules, count rules, explicit routing sentences), never judgment prose.
- Codex CLI hosts — model hints must live in Codex-native artifacts with the known silent-fallback gotcha documented.

## Smallest End State

Four coupled changes, one loom-code version bump:

### 1. Scope narrowing — docs review covers contract-class `.md` only

- **Contract-class** (reviewed): plugin-shipped text a weak model executes — `*/skills/**/*.md` (SKILL.md + references/protocols/checklists/rubrics/standards), `*/agents/*.md`, plugin hook `.md`. **Record-class** (exempt from the docs arm): `docs/loom/**` (audits, backlog, reports, close-outs, memory store), README/CHANGELOG tri-language mirrors. Classification is PATH-BASED (mechanical, weak-model-safe); exact glob list fixed at plan time.
- Artifacts with their own dedicated gates keep them and stay out of the docs arm: plans (plan-document-reviewer), briefs (brainstorming checkpoint). No double review.
- Record-only branches: zero docs-review dispatches. **Push-guard continuity requirement**: such branches must still satisfy the arm-agnostic push guard — mechanism (mechanically-validated record-only exemption marker vs guard-side path check) decided at plan time; the requirement (no docs-only push may dead-end at the guard) is fixed here.

### 2. Review loop — single round with delta confirmation (aggregation thresholds UNCHANGED — 2026-08-11 user decision)

- **Aggregation thresholds stay exactly as today** (any 🔴 → NEEDS_REVISION; 2+🟡 → NEEDS_REVISION; exactly-1-🟡 → PASS_WITH_NOTES; docs-side instruction/evidence eligibility unchanged). The originally-planned "🟡 at any count → debt" relaxation was DROPPED by user decision (option 1) after the mandated history-check tripped its own STOP condition: `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md` — 14/14 classifiable 🟡s in sampled 2+🟡 verdicts were load-bearing (selection-bias caveats recorded in the audit's Limits; the decisive signal: top-tier reviewers had rated all 14 load-bearing findings 🟡 not 🔴, empirically falsifying the planned reviewer-escalation valve). This is the brief's conditional reversal exercised as designed.
- **Loop shape replaces round-counting**: Round 1 = whole-artifact (the mode that produced the n=1 load-bearing catch), the ONLY full review. No gating findings → done (non-gating findings → debt, as today). Gating verdict → fix → **delta confirmation by the SAME reviewer via SendMessage** (proven pattern, #684/#685; exercised live 5× in this arc's own plan gate and task reviews) — not a fresh dispatch, not a re-sample. Still-blocking after one fix cycle → STOP, surface to user. Terminal state is "no gating findings", never "clean" (unreachable by arithmetic). Session death before confirmation → one fresh single round (no cross-session delta resume machinery).
- Writer-side revision-delta self-screen (live, 0.74.0) stays — belt and braces against fix-introduced defects.
- Consequences absorbed: the auto-delta third-round mechanism and most of `convergence-contract.md` become obsolete; the directive-1 open gap ("what follows a failed authorized round") is answered by the STOP rule. The cost pathology this item kills is the fix→full-re-sample spiral (6/9 rounds self-introduced, 7/28 audit) — killed by confirmation scope, independent of thresholds.

### 3. Host-native reviewer model defaults — M3

- Claude Code: `model:` frontmatter in `loom-code/agents/*.md` — spec-reviewer / code-quality-reviewer / docs-reviewer → `sonnet`; implementer + code-reviewer (whole-branch judgment) → unset (inherit). Dispatch-time `model` param remains the upward-override path.
- **Mechanical upgrade rule** (named, path-based): branch touches `agents/*.md` (the reviewers' own contracts) or exceeds a contract-file-count threshold → dispatch that docs review at `opus`; a contested 🔴 → second opinion one tier up. Honesty note carried into the shipped text: catch-quality-by-tier is UNMEASURED — the upgrade rule is the hedge, priced at pennies because it triggers rarely.
- Codex: `.codex/agents/<name>.toml` `model=` / `model_reasoning_effort=` (native, file takes precedence). MUST document the JP-sourced gotcha: under Multi Agent V2, `hide_spawn_agent_metadata=true` silently ignores per-agent model config — workaround `hide_spawn_agent_metadata = false` under `[features.multi_agent_v2]`. Emission-vs-documentation decided at plan time (`sync_codex_manifests.py` currently syncs manifests only — emission = new tested surface).
- Relative-effort prose is the shared explaining layer; host-native alias values live only in each host's own artifact.

### 4. Misroute fix (unchanged from v1)

`writing-plans/SKILL.md` §Self-review states: plan-document-reviewer is a PROMPT FILE for a general-purpose subagent, NEVER an agent-registry lookup; no other reviewer agent may substitute. Disambiguate SKILL.md:9's SUBAGENT-STOP role listing. Dispatch guidance gains "model: sonnet default". Cold-reader (haiku) probe verifies routing.

Rider (stale fact): `claude-code-tools.md` "4 plugin-level agents" → 5.

## Current State Evidence

- **Forward**: aggregation SSOT `requesting-code-review/SKILL.md:167-176` (:171 any-🔴 rule, :174 2+🟡 rule, :176 exactly-1-🟡 rule). Routing sites now ALSO in scope for B: rcr `:38,44` (triviality carve-out routes authored prose to docs arm), `:92` (docs-only branch delegates whole review), `:93` (mixed-branch per-file split + worse-of-two-arms join), `:141` (instruction|evidence schema). Cascades: `requesting-docs-review/SKILL.md:65-69`; `finishing-a-development-branch/SKILL.md:21,83,117-136` (flow diagram + dispatch table + cap-STOP); `subagent-driven-development/SKILL.md:121,127` (Review-weight: prose triad substitution) + `:139-144` (verdict table; row :144 already ships 🟡/🟢 as debt — the wording model); `agents/docs-reviewer.md:465-477`; shared carve-out sentence in `agents/{code-reviewer:54,spec-reviewer:62,code-quality-reviewer:66}` + `scripts/_reviewer-discipline.md:8`; `writing-plans/references/plan-format.md:111` (prose-weight marker semantics) + `plan-document-reviewer-prompt.md:48` (rule 16 file-type eligibility).
- **Reverse** (SSOT/sync, `sync_codex_manifests.py` read in full): `.claude-plugin/plugin.json` SSOT → `.codex-plugin/plugin.json` mirror, manifests only; `docs-reviewer.md` reaches Codex only via `distribute.py` generic target lists — no docs-review-specific Codex wiring to unpick. loom-pipeline: ZERO references (grep-verified) — B does not touch the pipeline.
- **Error** (failure paths): misroute path `writing-plans/SKILL.md:9` + `:97-109` (:109 revision-delta sentence — pins in `test_wp_extraction_pointers.py`, do not disturb). Push-guard path: `hooks/git-guard.py` is arm-agnostic but REQUIRES a review-pass marker; `loom_gate_markers.py:170-198,803-823,1083-1093` embeds docs-arm dimension sets + origin-exemption logic — record-only exemption must integrate here without breaking marker validation.
- **Data**: n=1,357 dispatch audit (Problem §5; auto-memory `feedback_docs_review_arms_default_sonnet.md`). 4-week git classification: 115 md-touching commits; 325 contract / 668 record / 186 other file-instances; 83 commits ≥1 contract file; 30 record-only. Audits: `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` (9-round trajectory; the n=1 whole-artifact catch; both self-flagged as n=1), `2026-07-31-a-class-interceptability-backtest.md` (5/9 interceptable, 1/9 certain; costliest defect invisible; carries unresolved parent-audit inconsistencies — re-verify before citing numbers), `2026-08-04-docs-review-convergence-experiment.md` (pool arithmetic; harm gate refuted; delta-scope validated; has errata — cite the corrected values only). History-check duty (seed entry): sample past 2+🟡 NEEDS_REVISION verdicts for load-bearing 🟡s BEFORE the relaxation lands — plan MUST include this task; falsified-neighbor carriers were 🟡-tagged.
- **Boundary**: word walls — rcr **3934/3935 (1 word)**, SDD **4175/4175 (0)**, writing-plans 4081/4099, rdr 3326/4430 (room — B's routing/loop rewrite lands mostly here), finishing 4485 (CI ~4500). B's rcr routing edits (:38,44,92,93) must be word-neutral or take a sanctioned ratchet raise (+ reason in test message; precedents 4023→4047→4099). Pin tests (~100 assertions, 12 files): `test_requesting_docs_review_skill.py` (29), `test_docs_reviewer_agent.py` (14), `test_review_scope_stations.py` (13, shared with code arm), `test_docs_review_mode.py` (9), `test_docs_review_blocking_class.py` (5, incl. relocation pin), `test_rdr_extraction_pointers.py` + `test_review_scope_docs_station.py` (6 each), `test_reviewer_r3_conditional.py` (5), `test_plan_format_prose_weight.py` (4), `test_review_weight_prose.py` (3), `test_check16_prose_row.py` + `test_finishing_docs_arm.py` (3 each). Agent frontmatter today: `name:` + `description:` only.

Evidence paths appendix: files named above, plus `docs/loom/backlog/2026-08-10-yellow-findings-should-default-to-debt-not-revision-loops.md`, `docs/loom/backlog/2026-08-10-plan-document-reviewer-misrouted-as-agent-type.md`, `loom-code/skills/requesting-docs-review/references/convergence-contract.md` (39 ln, mostly obsoleted), `loom-code/skills/using-loom-code/references/{claude-code-tools,codex-tools}.md`, `scripts/sync_codex_manifests.py`.

## Decision

We will narrow the docs arm to contract-class `.md` (path-ruled; record-class ships unreviewed), replace round-counting with single-whole-artifact-round + same-reviewer delta confirmation (terminal state "no gating findings"; aggregation thresholds themselves unchanged per the 2026-08-11 user decision recorded in §2), ship reviewer model defaults host-natively under the M3 rule (sonnet defaults + mechanical path-triggered upgrades + Codex toml with the silent-fallback gotcha documented), and make plan-document-reviewer's prompt-file routing substitution-proof. We will NOT demolish the mechanism entirely (Option C rejected: the n=1 whole-artifact instruction catch is real and loom's contract text is machine-executed — an above-industry justification for one hard gate), will NOT keep record-class review in any advisory form (pure sampling noise per the convergence experiment), will NOT add any new review mechanism, and will NOT touch loom-pipeline (zero coupling, verified). Why B over A: A left the dispatch volume and the record-class noise pool untouched; the audits localize ALL demonstrated value in contract-class whole-artifact review, and industry practice (spec-kit's consumed-artifacts-only scope; Vale's mechanical-blocking-only guidance) independently converges on the same boundary.

## Alternatives Considered (Axis 4)

**Industry survey (EN arm, 2026-08-11)**: dedicated docs review is the outlier — obra/superpowers (loom's ancestor): none; spec-kit: the sole dedicated agent, advisory-only, consumed-artifacts-only; OpenHands/Aider/Cursor-BugBot/claude-code-action/Codex-cloud-review/CodeRabbit/Greptile: incidental advisory; Vale/markdownlint: blocking reserved for mechanically-checkable defects, with the named failure mode "if writers cannot merge documentation fixes because of passive voice warnings, they will bypass the linter entirely". Sources: github.com/obra/superpowers/tree/main/skills · github.github.com/spec-kit/reference/agentic-sdd.html · grafana.com/docs/writers-toolkit/review/lint-prose/ · datadoghq.com blog (Vale) · vendor docs per survey.

**spec-kit deep-dive (`/speckit.analyze`)**: on-demand (not a gate); 6-dimension checklist; 4 severity tiers with only CRITICAL soft-blocking (constitution conflicts auto-CRITICAL by rule); read-only report, remediation offered never applied; "re-run until clean" with NO round cap — safe only because its 3 artifacts are anchored (consistent with our pool-arithmetic finding); scope excludes all record/README prose. Sources: github.github.com/spec-kit/reference/agentic-sdd.html · raw.githubusercontent.com/github/spec-kit/main/templates/commands/analyze.md.

**JP arm**: coding-agent-context dedicated docs review NOT FOUND; CyberAgent's 仕様書レビュー agents are adjacent (non-coding-agent, human-final, de-facto advisory); textlint/RedPen CI = gradual green-ification, no blocking-policy precedent found; transferable LLM-review findings: sycophancy bias, multi-turn accuracy decay, binary verdicts more stable than scores. Sources: developers.cyberagent.co.jp/blog/archives/62064/ · qiita.com/kane_ryu/items/c463c0cfb2e0f598f800 · zenn.dev/tyabu12/articles/0007-llm-two-stage-review · speakerdeck.com (SmartHR textlint).

**Codex mechanism (EN + JP corroboration)**: per-subagent `.codex/agents/<name>.toml` CORROBORATED bilingually (project overrides personal; omitted fields inherit); `agents.default_subagent_*` EN-only; subagent GA v0.115.0 (2026-03, JP source); Multi Agent V2 silent-fallback gotcha (JP-only find) as in §3 above. EN↔JP disagreement: none; JP added the gotcha EN missed.

**Rejected paths**: (a) Option A recalibrate-only — leaves record-class noise + dispatch volume untouched (superseded by B, whose item 2 contains A's aggregation change); (b) Option C full demolition — loses the one demonstrated net; 530-line agent + ~100 pin assertions rebuild cost makes it low-reversibility; conditional reversal recorded: if the user later judges cold-reader probes + pin tests + CI validators sufficient for contract text, C is honest — then fix a whole-artifact cold-read probe as the cheap replacement duty; (c) advisory-only for contract class (full spec-kit alignment) — rejected: loom contract text is machine-executed, an instruction defect becomes an execution incident (the n=1 catch was exactly this class); (d) "harm gate" severity filter — experimentally refuted (2026-08-04); (e) absolute model names in shared prose; (f) instruction-class-loops-at-any-severity; (g) prose-only effort classes; (h) personal-rules-only fix; (i) M2 (docs arm keeps expensive tier) — pays a proven-unnecessary premium (loop counts tier-independent) to hedge an unmeasured risk that M3's targeted upgrade rule hedges for pennies.

## Projected cost delta (rough multiplicative model, stated honestly as an estimate)

Record-only branches (26% of md commits): dispatches → 0. Remaining branches: file payload ≈ ×1/3 (668/993 loom-md instances exempt), rounds ≈ ×0.5-0.6 (single round + at most one cheap delta confirmation replaces multi-round full re-sampling; gating thresholds unchanged per §2), price ≈ ×0.2 (sonnet default). Net docs-review cost ≈ 8-12% of today (was 5-10% before the 🟡-relaxation was dropped). Factors individually evidenced; their interaction unmeasured.

## What Becomes Obsolete (Axis 5)

- ~~2+🟡 rule and cascade restatements~~ — NO LONGER obsolete: aggregation thresholds survive intact per the 2026-08-11 user decision (§2); their wording and pin tests stay untouched.
- Auto-delta third-round mechanism + the bulk of `convergence-contract.md` (39 ln) — replaced by single-round + confirmation.
- Docs-arm review of record-class files, including the mixed-branch per-file split's record share (rcr :93 semantics simplify).
- Pin tests on the loop/round mechanism (cap wording, auto-delta round) → migrated to pin the confirmation contract; threshold pins untouched.
- De-facto "inherit = most expensive" on checklist reviewer arms.
- Backlog entries retired or shrunk at close-out: directive-1 gap (answered by STOP rule), delta-round-cross-session-resume (no round 2 dispatch exists), out-of-scope-deferrals durable record (docs side: moot for record files; remaining scope re-filed narrower).
- NOT obsolete: whole-artifact scope (round 1 keeps it — it produced the only real catch); blocking-class eligibility; writer-side revision-delta self-screen; plan gate + brief checkpoint (their own mechanisms, untouched); push guard (arm-agnostic, stays — gains a record-only continuity path).

## Out of Scope

- Any new review mechanism; any further review-mechanism arc (stop-loss).
- Option C demolition; six-plugin merge / family packaging (separate evaluation arc).
- loom-pipeline changes (zero coupling verified).
- Changing implementer / whole-branch code-reviewer model defaults.
- `~/.claude/rules/model-dispatch.md` addendum (parallel item, user-diff-gated).
- Codex-side hook/guard porting.
- Mechanical prose linters (Vale-style) for record class — industry-plausible but NOT this arc; file as backlog if wanted.
- The 🟡-as-debt-at-any-count relaxation — DROPPED 2026-08-11 (user option 1) on the history-check STOP evidence; revisit only with new evidence that separates conventional from load-bearing 🟡s mechanically (the tested "harm gate" was already refuted 2026-08-04).

## Open Questions

1. Record-only push-guard continuity mechanism: exemption marker (mechanically validated) vs guard-side path check — plan time, inside `loom_gate_markers.py`'s existing docs-arm logic (:170-198, 803-823, 1083-1093).
2. `.codex/agents/*.toml`: emitted by `sync_codex_manifests.py` vs documentation-only — plan time.
3. Contract-file-count threshold for the M3 upgrade rule (exact N) — plan time; must be a literal number in shipped text.
4. History-check sampling frame (which past 2+🟡 verdicts are reachable: dev-repo PR bodies + memory; consumer transcripts private) — plan defines the sample before the relaxation task runs.

## Design-side on-ramp

Axis 0 walk skipped per negative guard (mechanism increment). Ready check RAN (queue empty; seeds surfaced). Ignited-start-condition entries surfaced at checkpoint: anti-copy greps (writing-plans touch), rule-skill-vs-agent-contract (reviewer rule edits — honored in-arc by editing both surfaces, mechanism deferred), out-of-scope-deferrals (partially retired by B, remainder re-filed), change-binding-chain (generic next-touch). loom-init: N/A.
