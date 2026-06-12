# SDD tooling, coding harnesses, and the "stronger models need less scaffolding" debate (2025–2026)

> **Type**: research synthesis (web-sourced, multi-angle, both-sides). Date: 2026-06-12.
> **Method**: ~11 EN + JP WebSearches across the SDD-tool landscape, OpenSpec-vs-composition, and the scaffolding/Bitter-Lesson debate, plus the OpenSpec CLI hands-on test (`docs/spec-toolkit/design/…L2-ab-validation-results` sibling). Confidence tags + thin-evidence flags inline. Primary sources preferred over listicles.
> **Why this exists**: to ground the decision *not* to integrate the OpenSpec CLI into the skill (see `project_spec_toolkit_mvp` memory + the complexity-critique verdict), and to stress-test whether spec-toolkit/code-toolkit's scaffolding survives the "bet on the model" critique.

## 中文 TL;DR

業界分兩派但其實在講不同層:**鷹架有兩種 —— 「拐杖型」(替模型補能力,如複雜路由、多 agent 硬切)該隨模型變強而砍(Bitter Lesson);「驗證型」(測試/spec 驗收/writer≠judge review)反而是 2026 公認的新瓶頸,跟模型多強無關、甚至更需要。** 「模型越強越不需要鷹架」這論點真實且有重量級提倡者(Sutton、Anthropic、Cognition),但它打生成側,打不到驗證側。對我們:**code-toolkit 的 TDD+review = 驗證型 = Bitter-Lesson-proof,留;spec-expansion 的 L2/L3 = 偏拐杖型 = regime-bound + model-bound,要定期用裸模型 baseline 重測、且設計成「容易刪」。**

---

## Part 1 — The SDD tooling landscape + OpenSpec-loop vs composition

### Landscape (2026)
Every major AI-coding vendor shipped an SDD flavor; they converge on one four-phase loop **Specification → Plan → Tasks → Implementation** ([Augment Code](https://www.augmentcode.com/tools/best-spec-driven-development-tools), [arXiv 2602.00180](https://arxiv.org/html/2602.00180v1)).

| Tool | Positioning | Best for |
|---|---|---|
| GitHub Spec Kit (90k★) | governance layer; fixed pipeline; per-feature disposable spec | greenfield / teams / SDD on-ramp |
| OpenSpec (52k★, most-active OSS SDD) | continuity layer; change-centric delta (ADDED/MODIFIED/REMOVED) syncing to a central `specs/` baseline; no MCP/API-key | brownfield / existing projects |
| AWS Kiro | IDE-native; requirement → schema/API auto-expansion | IDE workflows |
| cc-sdd / BMAD / Tessl / Antigravity | variants | situational |

Sources: [specnative](https://www.specnative.dev/blog/openspec-vs-speckit), [Martin Fowler SDD](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html), JP: [mayogames](https://mayogames.hatenablog.com/entry/openspec-vs-speckit), [zenn/gmomedia (OpenSpec/spec-kit/cc-sdd)](https://zenn.dev/gmomedia/articles/8ccf71e50858de), [iret](https://iret.media/182499).

### Key fact: OpenSpec is used WITH a coding agent, not standalone
OpenSpec installs `agents.md` / skills / commands into Claude Code (and 25+ tools); it is "designed to be integrated … rather than used standalone" ([supported-tools](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md), [dev.to integration](https://dev.to/bezael/como-integrar-openspec-con-claude-code-paso-a-paso-5ej3), [Claude Plugin Hub](https://www.claudepluginhub.com/plugins/chenxizhang-openspec-plugins-openspec)). Its workflow is `/opsx:propose → /opsx:apply → /opsx:archive`, where **the host agent does the actual coding** — OpenSpec itself is a spec-storage + slash-prompt convention layer, not a codegen engine.

### OpenSpec full loop vs spec-expansion + code-toolkit

| Dimension | OpenSpec loop (+ base agent) | spec-expansion + code-toolkit |
|---|---|---|
| GENERATE | one `/opsx:propose` prompt → agent default | USM×OOUX×matrix + **L2/L3 systematic coverage** + honesty rails (deep) |
| VERIFY | `/opsx:apply` → agent default coding, **no enforced TDD/review** | **TDD iron law + SDD writer≠judge triad + whole-branch review** (deep) |
| DECLARE (persistent baseline) | ✅ **mature**: delta tracking + archive + central `specs/` truth | ❌ **absent** (the real gap) |
| Maturity / ecosystem | 52k★, 25+ tools, battle-tested, low setup | bespoke, primary-source-grounded, solo ecosystem |
| Shape | **wide coverage, shallow per station** | **narrow coverage, deep per station** |

**Verdict (from complexity-critique, deletion-first):** don't integrate the CLI into the skill (REJECT) — our output is already CLI-validate-clean with zero dependency (verified, see below). OpenSpec's genuine value is its **DECLARE/baseline layer**, which is itself a "do we need a persistent spec baseline at all" question → DEFER until a concrete need. Compose, don't absorb: `spec-expansion (GENERATE) → OpenSpec (DECLARE, optional) → code-toolkit (VERIFY)`.

### Empirical: our output passes the real OpenSpec CLI
`npx @fission-ai/openspec@latest validate <change> --strict` (v1.4.1) on the PiP-app dogfood output → **"is valid", issues:[]**. Negative control (a requirement stripped of its scenario) → CLI correctly errors → proves it substantively parses our spec delta. Our `proposal.md` carries spec-toolkit's own 7 sections and lacks OpenSpec's `## Why/What Changes/Impact`, yet validate passes → **validate is strict on the spec delta, lenient on proposal.md** (the exact hybrid bet). Zero-migration claim now CLI-backed.

---

## Part 2 — The scaffolding debate

### The "bet on the model / thinnest viable harness" thesis (real, named proponents)

- **Sutton's Bitter Lesson, applied to harnesses**: general methods + compute beat hand-crafted structure; "the architectural assumptions baked in today will be obsolete in six months when a more capable model ships" ([hugobowne](https://hugobowne.substack.com/p/ai-agent-harness-3-principles-for), [Daniel Miessler "Bitter Lesson Engineering"](https://danielmiessler.com/blog/bitter-lesson-engineering)). **Confidence: HIGH as a design philosophy.**
- **Design harness components to be easy to delete**; as models improve you *actively strip* structure, routing, special-casing ([Medium "Models Are Almost Obsolete…"](https://medium.com/@nomannayeem/models-are-almost-obsolete-harnesses-are-what-matter-now-a5230a7995c6), [arXiv 2603.05344 terminal coding agents](https://arxiv.org/abs/2603.05344)). HIGH (multi-source).
- **Anthropic, *Building Effective Agents*** (primary, vendor): "find the simplest solution possible … this might mean not building agentic systems at all"; "avoid complex frameworks"; "reduce abstraction layers" ([anthropic.com](https://www.anthropic.com/research/building-effective-agents)). HIGH (first-party).
- **Cognition / Walden Yan, *Don't Build Multi-Agents*** (primary): a single linear agent + maximal shared context "gets you surprisingly far"; splitting decisions across agents causes conflicting actions ([cognition.ai](https://cognition.ai/blog/dont-build-multi-agents)). HIGH (first-party).
- **Karpathy / Willison**: prompt → context → harness engineering; "context engineering" names the real work ([Willison](https://simonwillison.net/2025/jun/27/context-engineering/)). HIGH.

### The counter: structure/verification stays regardless of model strength (also strong)

- **The bottleneck moved from generation to verification.** "Producing code is now free; knowing it's correct is not" ([Opslane](https://www.opslane.com/blog/verification-bottleneck), [SRLabs](https://srlabs.de/blog/ai-verification-bottleneck), [metalbear](https://metalbear.com/blog/testing-bottleneck-ai/)). **Confidence: HIGH (multiple 2026 sources).**
- **Boris Cherny (Claude Code creator)**: the single most important thing is to "give Claude a way to **verify its work**" (via [Wix Eng manifesto](https://medium.com/wix-engineering/the-ai-coding-agent-manifesto-c8f61629d677)). HIGH.
- **AI coding didn't speed delivery because coding was never the bottleneck** — Agoda, practitioner-empirical ([InfoQ 2026-03](https://www.infoq.com/news/2026/03/agoda-ai-code-bottleneck/)). HIGH.
- **writer ≠ judge**: an agent testing its own output is "grading your own exam"; fix = different model writes vs reviews, or fresh-context agent ([Wix manifesto](https://medium.com/wix-engineering/the-ai-coding-agent-manifesto-c8f61629d677)). HIGH — and this *is* code-toolkit's SDD triad + `feedback_failure_learning_automation_safety`.
- **Harness engineering is a *growing* 2026 discipline**: "every time the agent makes a mistake, change the system so it structurally cannot recur" (rules/tools/constraints) ([bits-bytes-nn EN/JP](https://bits-bytes-nn.github.io/insights/agentic-ai/2026/04/05/evolution-of-ai-agentic-patterns-en.html), [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)). HIGH.
- **The two giants publicly disagree**: Cognition "don't build multi-agents" vs Anthropic's multi-agent research system "outperforms single agent by 90%" — but both converge on "context engineering is everything" ([CTOL](https://www.ctol.digital/news/ai-leaders-clash-agent-architecture-cognition-anthropic-strategies/)). HIGH (Anthropic's 90% is a first-party benchmark — caveat).

### Empirical backbone: METR
Frontier autonomous task time-horizon **doubles ~every 7 months** (every ~4 months in 2024–25); Claude Opus 4.6 = **14.5h** at the 50% mark, Feb 2026 ([METR Time Horizon 1.1](https://metr.org/blog/2026-1-29-time-horizon-1-1/), [AI Digest](https://theaidigest.org/time-horizons)). HIGH (first-party, reliable). **Cuts both ways**: it's measured at 50% reliability — high-reliability horizons are far shorter, so the same data feeds "models are getting strong fast" *and* "the reliability gap (→ verification) persists" ([arXiv 2603.29231 "Beyond pass@1"](https://arxiv.org/pdf/2603.29231)).

---

## Part 3 — The reconciling synthesis (two kinds of scaffolding)

**Confidence: MEDIUM (interpretive synthesis, but grounded in the above).**

The two camps mostly aren't in conflict — they target different layers:

- **"Crutch" scaffolding** = hand-crafted structure that *substitutes for model capability* (complex routing, special-casing, prompt hacks, forcibly splitting a task across multiple agents). → **Bitter Lesson applies: strip it as models improve.** This is what Anthropic / Cognition / Sutton attack.
- **"Verification" scaffolding** = external *ground truth that checks the model's output* (tests, spec acceptance criteria, writer≠judge review gates, execution-as-truth). → **Bitter Lesson does NOT reach it** — it doesn't substitute for capability, it independently audits output. As models generate faster, verification is needed *more*, not less. This is the 2026 "verification is the bottleneck" consensus, and even the bet-on-the-model camp's own Boris Cherny says give the model a way to verify.

**One line: strip the structure that thinks *for* the model; keep the structure that checks *on* the model.**

---

## Part 4 — When scaffolding is worth it (regime-dependent)

| Condition | Scaffolding pays | Bare model wins |
|---|---|---|
| Horizon | long, multi-step, cross-session | short, single-step |
| Risk | high (data-loss, money, correctness-critical) | low / throwaway |
| Greenfield vs brownfield | greenfield / thin-context (no existing code to lean on) | brownfield (code is the context) |
| Correctness bar | must be reliably-complete + verifiable | demo / exploration |
| Model tier | strong model → thinner *crutch* scaffolding (verification stays) | — |

Matches our own measured regime finding (`feedback_spec_coverage_value_greenfield_regime`): the spec-coverage scaffold wins systematically only in greenfield/high-risk.

## Part 5 — Implications for spec-toolkit / code-toolkit

- **code-toolkit (TDD iron law + writer≠judge triad + whole-branch review) = verification scaffolding → Bitter-Lesson-proof.** The 2026 consensus (verification is the bottleneck; don't grade your own exam) directly endorses it. Keep it regardless of model strength; it matters *more* as generation gets cheaper.
- **spec-expansion's L2/L3 = closer to crutch scaffolding → regime-bound AND model-bound.** Our blind A/B showed it lifts recall for the *current* model in greenfield/interaction-dense regimes — but a stronger model may reach those combinations/paths unaided (`feedback_ab_baseline_reveals_marginal_behavioral_delta`). Its justification is not permanent. **Action: re-run the bare-model baseline A/B periodically; design each lens/gate to be easy to delete (Bitter-Lesson engineering) so a capability the model later subsumes can be removed without a redesign.**
- **Don't integrate OpenSpec CLI into the skill** (confirmed by both the deletion-first critique and this research): it's a wide-shallow workflow layer; we already pass its validate with zero dependency; its only deep layer (DECLARE) is a deferred need.

## Caveats / thin evidence
- The "bet on the model / thin harness" side is mostly **design-philosophy opinion essays** — there is **no controlled study** showing "strip the harness and quality holds". METR proves models improve, not that verification scaffolding is dispensable.
- The "verification is the bottleneck" side has more **practitioner-empirical** weight (Agoda/InfoQ, surveys).
- Anthropic's "multi-agent 90% better" is a first-party benchmark.
- This round was EN-primary on the harness debate; JP sources were richer on the SDD-tool landscape (Part 1). The two-kinds-of-scaffolding reconciliation is this author's synthesis, not a cited consensus.
