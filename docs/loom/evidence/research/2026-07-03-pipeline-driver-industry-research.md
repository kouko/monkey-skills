# Pipeline-driver industry research — reliability of the loom-pipeline design (2026-07-03)

> Pre-brainstorm research for the `loom-pipeline` conductor plugin. Four
> parallel research agents (orchestration paradigm / multi-agent dev
> pipelines / LLM-judge reliability / JP-industry practice) were each given
> our design summary and instructed to find evidence FOR and AGAINST —
> negative results prioritized. This file is the synthesis; every claim
> carries its source.

**Design under test** (as validated by the 2026-07-03 pipeline dogfood +
F5 spike): a deterministic workflow script (conductor) orchestrates
stations (principles → design → spec → code); each station is a
fresh-context agent; artifacts hand off via the per-change folder;
gates emit machine-readable two-valued verdicts with mandatory
file:line evidence; writer≠judge via separate dispatches; panels at
GENERATE stations; retries/aggregation/loop-backs are plain code;
station agents cannot sub-dispatch (F5), so panels/triads live at the
script layer.

## Verdict up front

The architecture's pillars are **strongly corroborated** by independent
industry and research sources — in several cases near-verbatim
(12-Factor Agents' "Own Your Control Flow" / "Small, Focused Agents";
Microsoft Conductor targeting exactly "code review pipelines,
plan-then-implement loops"). No source argues the opposite direction
for structurally-known pipelines. However, the research surfaced
**seven concrete gaps** that must become spec requirements, and flags
**two of our choices as untested hypotheses** (two-valued verdict;
fresh-context-per-station at our granularity) that need our own
measurement rather than borrowed confidence.

## Corroborated pillars

| # | Our design choice | Strongest independent support |
|---|---|---|
| P1 | Control flow / retries / aggregation in code, not LLM | Anthropic "Building Effective Agents" (workflows = code-defined paths; agents only for unpredictable step counts) [1]; 12-Factor Agents F8/F10 — "goal+tools+loop" plateaus at 70–80% reliability [4]; Microsoft Conductor (2026) built explicitly against LLM-as-orchestrator for this problem class [10]; Anthropic's own multi-agent postmortem *added* deterministic safeguards after runaway spawning [2]; goal-drift study: constrain action spaces architecturally [6]; pharmax production pipeline under medical-grade requirements [J13] |
| P2 | File-artifact handoff with structured schemas | MetaGPT/ChatDev: structured intermediate artifacts > raw chat, explicitly to cut error propagation [B2][B3]; GitHub reliability patterns: typed schemas + bounded action sets + pre-execution validation [J2]; Spec Kit / Kiro converge on the same artifact chain [B10][B11] |
| P3 | Gate at every station, weighted upstream | MAST (1,600+ traces): terminal-only verification is insufficient; verification failures = 21.3% of all failures [B1]; error-cascade model: hub-node errors contaminate up to 100% downstream — concentrate verification budget on high-influence upstream nodes (= design/spec critics are the highest-leverage placement) [B12] |
| P4 | writer≠judge via fresh-context dispatch | Self-preference bias is causal, mechanism = familiarity/low perplexity of self-generated text — fresh context structurally avoids it [C1]; effect size: 52pp recall gap when judging own output [C2]; JP: self/family bias measurable, cross-family judges recommended [J6] |
| P5 | Mandatory file:line evidence, else malformed verdict | Evidence-grounding raises citation validity 0.62→0.96, evidence support 0.54→0.83 [C8]; adversarial refute-or-promote defect pipelines use the same rule [C9] |
| P6 | Panels of cheaper judges over one large judge | PoLL: 3 small heterogeneous judges beat one GPT-4-class judge on human-alignment AND cost (QA domain; code generalization open) [C3] |
| P7 | Run-level journal + resume | Durable-execution table stakes across Temporal/AWS/Cloudflare/Vercel [8]; our journal-cache resume matches the checkpoint half (see G6 for the gap) |

## The seven gaps (fold into loom-pipeline spec as requirements)

**G1 — Global run budget, not just per-station retries.**
Documented incidents: $4,200/63h retry loop [5]; $47k/11-day agent loop
[J14]; Temporal's warning that *nested* retries create self-inflicted
outages — a global retry/cost ceiling across the run is required, not
per-call caps [8]. IBM's loop-prevention triad: explicit termination
conditions, max retries/steps/wall-time in code [J14]. Our dogfood
driver had per-station retry ×2 only. → Spec: run-level token budget
(Workflow `budget` primitive), run-level wall-clock ceiling, and a
**rally cap on gate↔writer loop-backs** (JP production report needed a
hard "max 2 rounds" stop [J10]; a resident multi-agent setup ping-ponged
50 messages in 38 minutes without one [J4]).

**G2 — Critic trigger discipline (the self-critique paradox).**
On easy/already-good drafts, unconditional critique *hallucinates*
flaws — accuracy collapsed 98%→57% in controlled tests; the same loop
gains 20–60% on hard tasks [B13]. Our GENERATE critics are co-writers
(provenance-tagged additions, never verdict-flip churn), which blunts
the worst mode, but the risk transfers to NEEDS_REVISION churn and
noise rows. → Spec: critics keep the re-seed-don't-reject economy;
rally cap per G1; and the dogfood metric to watch is **critic
false-positive rate** (critic-found rows that a human later rejects),
not just recall.

**G3 — Rationale must travel with artifacts (the implicit-decision
loss).** Cognition's core argument against multi-agents is loss of
*implicit decisions* between contexts [B4] — their carve-out blesses
serial pipelines only when stages inherit full upstream context. Our
file handoff is not full-trace sharing; MAST's lost-history /
information-withholding modes are exactly this failure [B1]; JP open
question: how much "why" belongs in the artifact [J-OQ]. → Spec: every
station's output artifact carries a **Decisions section (what + why +
rejected alternatives)**; the change-folder already carries briefs and
the LOOM-SIMPLIFY ledger — make the rationale section a validator-checked
field, not a habit.

**G4 — Two-valued verdict is OUR hypothesis, not literature.** No
study tests whether banning bare PASS reduces verdict inflation [C-OQ].
Adjacent warning: biased judges can look *consistent* while being
systematically wrong — stable verdicts ≠ calibrated verdicts [C5][C7].
→ Keep the design (its rationale is coverage-relativity, which stands),
but treat as a hypothesis: the Sonnet-vs-Fable A/B should also compare
verdict distributions against human review on the same branch.

**G5 — Panel aggregation is as load-bearing as panel diversity.**
Panels can *amplify* bias depending on composition + aggregation
method [C4]; same-family judges (all-Claude tiers — our realistic
config) plausibly share correlated blind spots; cross-vendor judging is
the literature's mitigation [C3][J6] but is outside our harness today.
→ Spec: aggregation rules live in script code (already our direction);
record per-judge verdicts in the ledger (not just the aggregate) so
correlated-blind-spot analysis is possible later; note cross-model
judging as a parked re-trigger (if the harness gains non-Claude models).

**G6 — Checkpointing is not durable execution.** The Diagrid critique:
checkpoint/resume without failure *detection*, automatic recovery, and
idempotent replay is the documented gap in LangGraph-class systems [9]
— we inherit it. → Spec: per-station wall-time watchdog (a hung station
must fail loud, not hang the run); stations idempotent on re-run
(adopt-if-exists, already proven in the dogfood driver); resume is
manual-but-one-command (journal + resumeFromRunId, already exists);
do NOT market the driver as "durable" — it is checkpointed.

**G7 — Gate gaming has channels our reviewers don't see.** Beyond
test-weakening (mitigated by TDD iron law + reviewers): weak-assertion
tests that pass on mutated code [C13], and answer-lookup-style
shortcuts that look clean in a diff [C11 — 63% of one frontier model's
SWE-bench "successes" retrieved the upstream fix]. Verifier-writer
separation gives "moderate" gains; no silver bullet [C12]. → Spec:
mutation-testing spot-check as a SHOULD-tier gate (post-v1 backlog);
the whole-branch reviewer's cross-task-coherence dimension stays; honest
scope note that greenfield work lowers (not eliminates) lookup-gaming
relevance.

## Untested-at-our-granularity (measure, don't assume)

- **Fresh-context per station**: no surveyed production system isolates
  at our granularity (MetaGPT/ChatDev keep persistent role-agents;
  Devin/OpenHands/Jules/Codex are continuous-context loops) [B7][B8][B9].
  There is no field validation for or against — our dogfoods are the
  evidence base. G3's rationale-in-artifact requirement is the hedge.
- **Judge model tier (Sonnet-class vs frontier)**: literature is mixed
  and none of it tests code-review gates in a staged pipeline;
  reasoning capability appears to matter more than parameter count
  [C6][C14]. The planned A/B remains necessary — now with G4's
  verdict-distribution comparison folded in.

## Expectation calibration

Honest industry baseline for full-autonomy pipelines is low-double-digit
task success (Devin: 13.86% SWE-bench Lite at launch; one independent
test 3/20; merge rate 34%→67% over 18 months of iteration) [B6].
JP field reports echo: spec-driven *form* without a qualified review
subject degrades into vibe-coding [J7]; AI-covered logic review breeds
complacency at ~60% coverage [J11]; gate-pass ≠ shared intent — the
human merge gate is a review of meaning, not a formality [J12]. Our
human gates (change-id minting, product decisions, cost policy, final
merge) are load-bearing and stay.

## Source index

Orchestration paradigm: [1] anthropic.com/research/building-effective-agents ·
[2] anthropic.com/engineering/multi-agent-research-system ·
[4] github.com/humanlayer/12-factor-agents ·
[5] medium.com/@sattyamjain96 ($4,200 postmortem) ·
[6] arxiv.org/abs/2505.02709 (goal drift) ·
[8] temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal ·
[9] diagrid.io/blog/checkpoints-are-not-durable-execution ·
[10] opensource.microsoft.com/blog/2026/05/14/conductor ·
[11] rlancemartin.github.io/2025/07/30/bitter_lesson (steel-man against rigidity) ·
[13] deepset.ai/blog/ai-agents-and-deterministic-workflows-a-spectrum

Dev pipelines: [B1] arxiv.org/abs/2503.13657 (MAST) ·
[B2] arxiv.org/abs/2308.00352 (MetaGPT) · [B3] arxiv.org/abs/2307.07924 (ChatDev) ·
[B4] cognition.com/blog/dont-build-multi-agents ·
[B6] cognition.ai/blog/devin-annual-performance-review-2025 ·
[B7] OpenHands/SWE-agent architecture (dev.to/truongpx396) ·
[B8] Google Jules (digitalapplied.com) · [B9] Codex Cloud (intuitionlabs.ai) ·
[B10] github.com/github/spec-kit · [B11] kiro.dev/docs/specs ·
[B12] arxiv.org/abs/2603.04474 (error cascades) ·
[B13] snorkel.ai/blog/the-self-critique-paradox

Judge reliability: [C1] arxiv.org/abs/2404.13076 · [C2] arxiv.org/abs/2410.21819 ·
[C3] arxiv.org/abs/2404.18796 (PoLL) · [C4] arxiv.org/abs/2505.19477 ·
[C5] arxiv.org/abs/2606.19544 · [C6] arxiv.org/abs/2507.10535 (CodeJudgeBench) ·
[C7] arxiv.org/abs/2604.16790 · [C8] arxiv.org/abs/2601.08654 (Rulers) ·
[C9] arxiv.org/abs/2604.19049 · [C11] cursor.com/blog/reward-hacking-coding-benchmarks +
anthropic.com/research/reward-tampering + metr.org/research ·
[C12] arxiv.org/abs/2606.26300 · [C13] atlassian.com/blog (Rovo mutation testing) ·
[C14] iternal.ai/llm-selection-guide

JP industry: [J2] jobirun.com + atmarkit.itmedia.co.jp (GitHub patterns) ·
[J4] zenn.dev/daichi_hirahara (38-min/50-msg loop) ·
[J5] techblog.jmdc.co.jp/entry/20251208 (judge instability ±10%) ·
[J6] tech.revcomm.co.jp (self/family bias) ·
[J7] dev.classmethod.jp (Kiro → vibe-coding regression) ·
[J9] iret.media/186388 (Spec Kit monorepo split problem) ·
[J10] zenn.dev/dotdtech_blog (max-2-rounds stop) ·
[J11] zenn.dev/kenimo49 (6-stage AI coverage) ·
[J12] developersblog.dmm.com (review = intent sharing) ·
[J13] zenn.dev/pharmax (deterministic pipeline in healthcare) ·
[J14] blog.serverworks.co.jp + techtarget.itmedia.co.jp (cost blowups, IBM triad)
