# Weak-model dual dogfood — Cluster B behaviors + instrument v0.1 flow

> **Type**: dogfood run report (two targets, weak-model operators)
> **Date**: 2026-07-10
> **Target A**: Cluster B's four shipped behaviors (branch
> feat-loom-code-upstream-hardening / PR #526), exercised by 7 haiku
> cold-operators in synthetic sandboxes, disk-verified.
> **Target B**: instrument v0.1 construction flow run end-to-end by a
> haiku operator with a sonnet simulated user (designer persona, quote
> tool product idea); orchestrator relayed messages. MECHANICAL-face
> validation only — taste-level probing quality requires the real-user
> T6 gate, which this run does NOT replace.
> **Honest caveats**: (1) simulated user, not the real persona; its
> persona card scripted one deliberate stall; (2) the orchestrator
> nudged the operator twice (post-design-stance transition; final
> confirmation resend) and reminded the sim-user once with a generic
> "point out anything you never said" line before the read-back —
> generic, but a mild prompt toward fabrication-catching; (3) operator
> = haiku, deliberately below the authoring tier.

## Target A — verdict: 7/7 after one fix loop (5/7 as shipped)

| Probe | Behavior | Result |
|---|---|---|
| A1 count=1 auto-bind | detection cascade | ❌ round 1 (wrong repo) → ✅ re-probe after fix |
| A2 count=0 N/A-loud | detection cascade | ✅ (correct statement, proceeds on brief) |
| A3 count=2 ask+recency | detection cascade | ❌ round 1 (wrong repo) → ✅ re-probe (asked, recommended most-recent, archived excluded) |
| A4 branch-slug match | detection cascade | ✅ (bound via layer i, surfaced binding, explained loser) |
| A5 archive-on-close | finishing + script | ✅ disk-verified: bound-ness recovered from plan join keys, folder moved, move staged |
| A6 coverage gate | script + wiring | ✅ exit 1, PASS blocked, both legal paths cited, dropped scenario named |
| A7 principles derivation | code-reviewer D8 | ✅ both repos: rev-parse anchor, correct activation + honest N/A |

**FINDING-A1 (fixed on the branch, commit c3b2ee49)**: the cascade text
never said WHERE to run detection — 2/4 haiku operators ran `git branch`
/ `docs/loom/` globs in the ambient cwd (a different repo). The natural
experiment: the SAME tier followed D8 correctly because D8 names a
concrete anchor (`git rev-parse --show-toplevel`). One anchoring
paragraph added (mirrors D8) + windowed regression test; re-probes 2/2
correct; delta-reviewed PASS. Lesson (also in the close-out commit's
Learning trailer): for weak-tier executors, WHERE to run a check is as
load-bearing as WHAT to check.

## Target B — verdict: mechanical face WORKS on haiku; 6 findings for Cluster A's T5

Flow completed end-to-end: opening statement → 4 Product probe rounds →
Design expert lane (2 lenses, 3+3 candidates, mixed decision) →
Engineering 5 stance briefings + delegated stack → artifact (304 lines:
3 principle sections, Deviation Ledger, FP1-5 falsifiable gates,
read-back summary) → per-section + total read-back → 2 user corrections
applied and disk-verified.

Success criteria (instrument v0.1 table, mechanical reading):

| # | Criterion | Grade | Evidence |
|---|---|---|---|
| 1 | Question-set adequacy | **PARTIAL** | Q1-Q4, Q6-Q8 asked (incl. v0.1's Q8 lifecycle/scale — fired explicitly). **Q5 "why not existing alternatives" never asked** (FINDING-B1) |
| 2 | Candidate breadth | PASS | 3 visual + 3 interaction candidates, ≥2 traditions, non-head entries (Vignelli, Emotional Design); audit produced considered-but-rejected (Bauhaus, Nielsen, ISO) — but kept internal, not surfaced (FINDING-B2, instrument wording ambiguity) |
| 3 | Propose-then-react | PASS | kill-signal stall → two concrete scenarios → user reacted productively ("幫我省心變幫我埋雷") |
| 4 | Falsifiability + read-back | PASS | FP1-5 concrete and losable; read-back caught BOTH planted-class distortions: a priority flattening (Norman+JTBD written co-equal vs decided hierarchy) and a fabricated requirement (GDPR — user: 「我沒印象自己講過」), same class as the paper run's D5 |
| 5 | Output shape | **PARTIAL** | Deviation ledger ✓, unique principles ✓, read-backs ✓; version pins PARTIAL (design canons pinned 1961/2010/1992, Norman + engineering canons unpinned); two artifact-surface defects below |

### Findings (feed Cluster A's T5 SKILL.md rewrite)

- **FINDING-B1 (question-set execution)**: Q5 (why not existing
  alternatives) dropped by the weak operator. The instrument lists it
  but nothing forces coverage. T5 should give the skill a
  question-coverage self-check before leaving the Product section
  (mirror: coverage gate philosophy — enumerate, don't trust recall).
- **FINDING-B2 (instrument ambiguity)**: "name 1-2 considered-but-
  rejected, with reasons" doesn't say TO WHOM. Paper run surfaced them
  to the user; this operator kept them in the internal audit. Decide and
  write it down (recommendation: surface to user — it's the honesty
  device).
- **FINDING-B3 (artifact language)**: conversation was zh-TW; artifact
  came out English. Instrument/skill must state the artifact-language
  convention (repo convention wins; user-facing constitution arguably
  belongs in the user's language — a designer/PM must be able to READ
  their own constitution).
- **FINDING-B4 (terminology drift)**: user's product is a 報價單
  (quote) tool; the English artifact says "Invoice" throughout — a
  domain-meaning shift (pre-agreement quote vs post-work bill) the user
  couldn't catch because the read-back was delivered in Chinese. T5:
  read-back must surface the artifact's actual key terms, and artifact
  language (B3) compounds this.
- **FINDING-B5 (canon citation hygiene)**: E4 cites "Local-First" as
  canon for a cloud+encryption decision — the rejected direction cited
  as the anchor. Anchors table needs the same read-back scrutiny as
  content (or validator-level check in T4: anchor named ⇒ consistent
  with the stance it anchors).
- **FINDING-B6 (weak-operator transition stall)**: the operator went
  idle after collecting the design stance and needed an external nudge
  to run the canon audit + propose step — the highest-cognitive-load
  transition. T5 should make the transition imperative and mechanical
  ("after the stance is collected, IMMEDIATELY run the audit; do not
  wait"). Also observed: the operator self-dispatched a subagent for
  the canon audit — worked well, worth sanctioning explicitly.

### What held up (evidence the design carries to weak tiers)

Batch-size self-correction after one user complaint; cross-section
propagation fired exactly as codified (Q1 presented as derived-stance
confirmation, crediting the Product-section kill signal); Q8
lifecycle/scale fired (v0.1 fix live); propose-then-react recovered the
scripted stall; the read-back gate caught both real distortions at
haiku tier — the two guards that earned their place in the paper run
earned it again one tier down.

## Disposition

- Target A: fix already shipped to PR #526 (c3b2ee49); this report is
  the run record.
- Target B: findings B1-B6 are input to Cluster A's T5 (SKILL.md
  construction-flow rewrite) and T4 (validator) — carry them into the
  task dispatch packets. The formal T6 cold-operator gate (real user +
  shipped skill) REMAINS pending; this run de-risks mechanics only.
