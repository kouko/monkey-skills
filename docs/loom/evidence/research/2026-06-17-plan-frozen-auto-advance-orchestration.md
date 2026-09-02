# Plan-frozen → unattended → PR: is an auto-advance orchestrator sound?

> Deep-research report (research-toolkit:deep-research). 2026-06-17.
> Scope decided with kouko: **freeze point = the plan** (atomic tasks + RED/GREEN);
> **stop point = PR-open** (human merges). Question: does running plan→PR unattended
> reintroduce the "crutch-class orchestration" the prior `auto-build-harness` eval rejected?
> Deliverable: a recommendation, not code.

## Pipeline stats

| | |
|---|---|
| Angles | 6 (gate-trust / agentic-SWE / spec-frameworks / HITL / Bitter-Lesson / JP-native) |
| Sources fetched + extracted | 15 (primary-heavy: Anthropic, OpenAI, ICLR, GitHub, arXiv, Cognition) |
| Load-bearing claims adversarially verified | 5 (3 refutation voters each; 9 re-run after a session-limit abstention) |
| Claims surviving quorum | 5 / 5 |
| Agent calls | ~45 (6 search + 15 fetch + 24 verify) |

## Bottom line

The prior conclusion — **don't build crutch-class orchestration** — still holds, and it does
**not** block what kouko wants. "Plan-frozen → auto-advance → stop at PR" is both (a) the
**industry-standard autonomy envelope** and (b) achievable as a **thin, verification-class**
layer over the existing gates. What the evidence forbids is the *other* thing: a smart
router/brain that thinks or re-routes for the model, and auto-merge to main.

Three hard constraints fall out of the evidence, and they line up exactly with the scope
kouko already chose:

1. **Stop at the PR — every real system does.** None auto-merge to main.
2. **The review gate isn't trustworthy enough to *remove* the human — only to *reduce* their load.** Automated review catches roughly half of real defects. So a PASS means "ready to show a human," not "safe to merge."
3. **The thing actually worth building is the STOP/ESCALATE trigger, not the auto-advance.** The dominant failure mode of unattended agents is not knowing when to stop.

## Verified findings (all survived 3-voter adversarial quorum)

### A. Automated code review misses a large fraction of real defects — SURVIVED (1 voter refuted the *number*, not the thesis)
Best **independent** benchmarks put top-tool recall at ~50–60% (Martian/CodeRabbit ~53.5%
F1; Qodo best-in-class ~60% default / 71% extended), and academic agent benchmarks are far
lower (c-CRAB arXiv 2603.23448: frontier tools detect 20–32% of human-flagged issues; all
tools combined ~40%). Vendor self-claims of ~82% recall (Greptile) do **not** replicate
independently. The cited "51%" was a #3-ranked tool's F1, mislabeled as best-tool recall —
corrected here. **Implication:** a whole-branch-review PASS cannot be the thing that
auto-merges; it can only decide "ready for a human." This is *why* the stop point is PR-open.
Sources: codeant.ai (Martian 200k+ PR bench); qodo.ai; arXiv 2603.23448.

### B. Unattended autonomous agents fail on underspecified/blocked tasks and don't self-escalate — SURVIVED (high)
answer.ai's hands-on month with Devin: **3 successes / 14 failures / 3 inconclusive out of
20** real tasks; documented tunnel-vision (pursued an impossible Railway deploy unattended
for >1 day, hallucinating features). Corroborated across failure-mode papers (arXiv
2511.19933 "stubborn loops / overconfidence / no built-in failure signals"; arXiv 2509.13941).
**Implication:** the single most valuable thing to build is a reliable **halt-and-escalate**
trigger, not the auto-advance plumbing. Autonomy only worked on tasks "so small and
well-defined that doing them manually would be faster."
Sources: answer.ai 2025-01-08; arXiv 2511.19933, 2509.13941.

### C. Verification is the binding constraint as generation cheapens — SURVIVED (high)
Faros AI telemetry (10k+ devs, 1,255 teams): high-AI-adoption teams merged **+98% PRs** but
PR **review time rose +91%**; a 238-dev field study found AI review additive and PR closure
time up 5h52m→8h20m; senior engineers spend ~3.6× longer reviewing AI vs human code
(CodeRabbit). AWS CTO Werner Vogels frames it as "verification debt"; formal-methods advocate
de Moura agrees verification is the bottleneck (automated proof = "future hope, not current
achievement"); METR's RCT (devs 19% *slower* with AI) points to downstream review/QA, not
generation, as the limiter. No credible source argues the opposite. **Caveat:** the exact
percentages are vendor/industry telemetry, not peer-reviewed — but the direction is robust
and multi-source. **Implication (Bitter-Lesson):** keep/strengthen verification-class
structure; that is where the constraint lives.
Sources: faros.ai; logrocket.com; leodemoura.github.io; METR.

### D. Industry converges on RISK-BASED human checkpoints, not per-action approval — SURVIVED (high)
Anthropic (Measuring Agent Autonomy): mandating per-action approval "will create friction
without necessarily producing safety benefits"; focus on whether humans can "effectively
monitor and intervene"; Claude Code asks for clarification **>2× more often than humans
interrupt it**. Auto Mode telemetry: users approve **93%** of permission prompts (Anthropic's
own "approval fatigue"). OpenAI guardrails: pause "before side effects like cancellations,
edits, shell commands" — gate state-changing/irreversible actions, not every step. Anthropic
safe-agents: checkpoints "before irreversible actions." **Implication:** put the human gate at
the *irreversible boundary* (the merge) + on gate-failure/uncertainty — exactly PR-open. Don't
sprinkle per-step approvals.
Sources: anthropic.com/research/measuring-agent-autonomy; anthropic.com/engineering/claude-code-auto-mode; developers.openai.com guardrails-approvals.

### E. No universal "trust threshold" for an LLM-judge gate — calibrate + escalate — SURVIVED (high)
The rigorous way to let a judge gate a decision automatically is **selective prediction**:
trust the verdict only above a confidence threshold calibrated on human labels, and
**escalate/abstain below it** (ICLR 2025 "Trust or Escalate", Jung/Brahman/Choi, arXiv
2407.18370 — provable human-agreement lower bound; cascade cheap→strong judge). Judge-quality
work uses high bars (Pearson r ≥ 0.80 "strong alignment") but treats them as context-dependent,
not universal; naive confidence thresholds are brittle because judges are systematically
overconfident. **Implication:** any gate the auto-advance acts on must be able to emit "not
sure → stop and ask," not just PASS/FAIL. A binary gate with no abstention is the unsafe design.
Sources: ICLR 2025 Trust or Escalate (arXiv 2407.18370); OpenReview "Judge's Verdict"; arXiv 2508.06225.

## Cross-corroborated framework facts (not separately vote-verified — agree across ≥3 primary docs)

Every shipped spec-driven / agentic system places the human gate at the same two points:
**(i) before implementation** (agree on the plan/spec) and **(ii) at the PR / irreversible
step** (review + merge) — and lets execution *between* run autonomously:

- **GitHub Spec Kit** — `/speckit.implement` runs the whole task list autonomously
  (validates prereqs, parses tasks.md, executes in dependency order, no per-task gate), but
  human review/clarify sits *between* phases and a post-impl human verification is still
  required; issue #1323 proposes `/speckit.review` as a constitution-aware *final* gate.
- **OpenSpec** — "Agree before you build — human and AI align on specs before code"; propose→apply→archive.
- **GitHub Copilot coding agent / OpenHands / SWE-agent / Devin** — agent works in an
  isolated env and opens a PR; the human reviews the diff and merges. None auto-merge.
- **Anthropic "Building Effective Agents"** — workflows (predefined paths) beat autonomous
  agents for well-defined tasks; "add complexity *only* when it demonstrably improves outcomes."
- **Cognition "Don't Build Multi-Agents"** — parallel sub-agents make conflicting decisions
  without shared context; prefer a single-threaded linear agent with continuous context.

## Answering the three sub-questions

1. **Gate trustworthiness** — No fixed number licenses blind trust. Automated review recall
   ~50% means the gate can't replace the human merge decision; the safe pattern is
   calibrate-confidence + escalate-below-threshold (Trust or Escalate). So the gate's job in
   an auto-advance loop is to decide *ready-for-human* and to *stop when unsure* — not to merge.

2. **Existing practice** — Freeze the contract (plan/spec) → auto-execute → **stop at the PR,
   human merges** is the universal envelope. The escalate point is the irreversible boundary
   (merge) plus mid-run blockers. Observed failure mode: agents over-run blockers unattended
   (Devin 3/20), which is the argument *for* an explicit stop trigger, not against autonomy.

3. **Harness shape** — A **thin runbook over existing skills** is the durable choice. The
   auto-advance layer should add only verification-class connective tissue (run stage→stage,
   halt+escalate on NEEDS_REVISION/BLOCKED/low-confidence, stop at PR). A new "orchestrator
   brain" that decides/re-routes is crutch-class — exactly what Cognition, Anthropic, and the
   Bitter-Lesson all warn decays as models improve. Build the stop rule; don't build the brain.

## Recommendation

- **Toolkit merge: NO — B/D=D holds.** Auto-advance needs the *gates to chain*, which is
  orthogonal to packaging. Merging the 4 plugins is crutch-class consolidation with zero
  verification benefit and real coupling cost. Keep them modular.
- **Orchestrator: build the THIN version only** — a `plan → PR` auto-advance layer that
  (a) runs the existing pipeline stage-to-stage with no human "go" between waves,
  (b) **halts and escalates to the human on any NEEDS_REVISION / BLOCKED / uncertain gate**,
  (c) **stops at PR-open** for the human merge. This is a *refinement* of, not a contradiction
  to, the prior "don't build orchestration" verdict: the prior eval rejected a thinking
  router; a stop-and-escalate envelope is the opposite — it is verification-class.
- **The load-bearing piece is the STOP trigger, not the plumbing.** Design it first: explicit
  halt conditions (gate verdict ≠ PASS, implementer BLOCKED, repeated retry, low confidence)
  → surface to the human. Anthropic's data says Claude already over-asks, which is the *safe*
  direction here.

## Open question for the build decision (→ complexity-critique)

Is the auto-advance layer a **documented runbook** (prose the model follows, zero new code) or
a **thin skill** (a SKILL.md that sequences the stages)? Both avoid the crutch trap; the
runbook is the smaller, more Bitter-Lesson-aligned default. Pressure-test with
`dev-workflow:complexity-critique` before writing anything.

## Caveats / confidence

- Findings A–E survived adversarial quorum; A's precise recall number was corrected, C's exact
  percentages are vendor telemetry (direction robust, magnitudes soft), E's "the SOTA way"
  overstates single-method consensus.
- Framework facts are cross-corroborated across primary docs but not separately vote-verified.
- This is an *evaluation*; no orchestrator skill exists yet (verified: 0 on main).
