# Brief: Port Pocock's compression philosophy into skill-dev-toolkit

Date: 2026-07-13
Source: brainstorming (5-axis walk). Upstream study: mattpocock/skills research +
writing-plans equivalence-gated refactor pilot (PR #559,
docs/skill-dogfood/2026-07-13-writing-plans-token-refactor/gate-evidence.md).

## Design-side on-ramp

Axis 0 negative guard applied — increment to existing dev-tooling skills, not
product-shaped/user-facing work; skipped silently.

## Problem

(Axis 1) Skills in this repo accumulate token bloat through additive edits.
The existing skill-refactor gate PROVES a cut preserved behavior, but carries
no knowledge of WHAT to cut (candidate generation is unguided) and nothing
teaches writing lean at authoring time. Matt Pocock's empirically-refined
techniques — leading words that recruit model priors, a bloat taxonomy
(no-op sentences / sediment / negative instructions / premature completion
claims), thin-orchestrator-over-thick-reference design — currently exist only
in this session's conversation and will evaporate. Job to be done: "when
creating or refactoring a skill, apply proven compression techniques without
breaking weak-model contracts."

## Users

(Axis 2) kouko + future Claude sessions of ANY tier doing skill development in
this repo via skill-dev-toolkit (skill-refactor rounds, skill-creator-advance
authoring, sweep workflows' analyst agents). Job story: when I run a
skill-refactor round, I want ranked, named cut-candidates and tier-safe move
recipes, so the gate spends its verification budget on cuts that are likely
both safe and large.

## Smallest End State

(Axis 3) Three small deliverables, all content (no new tooling):

1. **skill-refactor/references/refactor-moves-catalog.md** — add one
   Medium-risk move: **Leading-word substitution** (replace an explanation
   with the pre-trained concept's name, e.g. Fowler smell names, "Child
   Test"), carrying a mandatory guard line: equivalence runs MUST use the
   weakest tier that will execute the target skill (priors vary by tier —
   Anthropic's own Haiku-vs-Opus guidance + this repo's
   explicit-contract-load-bearing evidence). Plus summary-table row.
2. **skill-refactor/references/ablation-mode.md** — add a **taxonomy-guided
   candidate pre-pass**: scan sections against Pocock's bloat taxonomy
   (no-op sentences, sediment, negative instructions, premature completion,
   duplication) to RANK ablation targets before the leave-one-out runs —
   cheaper ordering, same gate. Candidate-finder discipline unchanged.
3. **skill-creator-advance/references/writing-lean.md** (NEW file) — authoring-
   time guidance: model-already-smart doctrine (Anthropic), leading words,
   bloat taxonomy as self-review checklist, **"thin orchestrator over thick
   reference"** as the named design dimension (recon found the concept exists
   as Progressive Disclosure but the steps-vs-reference framing is unnamed),
   weak-tier floor rule. Body of SKILL.md gets AT MOST a one-line pointer —
   the body is already 6,085 words vs the 4,500 cap (see Boundary evidence);
   net body growth must be ≤0 (fold the pointer into §Writing Style by
   tightening existing lines).

Version: skill-dev-toolkit 0.1.0 → 0.2.0 (content addition) + CHANGELOG entry.
Attribution: mattpocock/skills is MIT (verified in clone LICENSE, © 2026 Matt
Pocock) — cite repo + aihero.dev in the new reference file.

## Current State Evidence

- **Forward**: new moves plug into refactor-moves-catalog.md's risk-tier
  sections (`### Name` + prose + Example + Equivalence risk, summary table at
  refactor-moves-catalog.md:186-201; classification table :8-14). SKILL.md
  references the catalog at skill-refactor/SKILL.md:170-173 and :336.
  ablation-mode.md exists (72 lines) with the candidate-finder discipline
  pinned at skill-refactor/SKILL.md:161.
- **Reverse**: catalog + ablation-mode consumed ONLY by skill-refactor's own
  SKILL.md/READMEs (grep: no other runtime consumers;
  dev-workflow/docs/skill-governance.md:28 lists catalog as "skill-refactor
  specific | none needed") — no cross-plugin sync obligations.
- **Error**: no error paths — pure reference-content change; the gate scripts
  (equivalence_check.py etc.) are untouched.
- **Data**: word counts — refactor-moves-catalog.md 1,088w (reference files
  not capped); skill-refactor/SKILL.md 2,365w (headroom +2,135);
  **skill-creator-advance/SKILL.md 6,085w — ALREADY −1,585 over the 4,500
  hard cap** (scripts/check-skill-structure.py:298 WORD_HARD_CAP), silently,
  because skill-dev-toolkit is not in the skill-structure CI scan list
  (.github/workflows/skill-structure.yml:40-59 scans only domain-teams + 4
  loom plugins).
- **Boundary**: plugin version 0.1.0 (.claude-plugin/plugin.json); CHANGELOG.md
  exists; .codex-plugin mirror exists (plugin.json only — sync via
  scripts/sync_codex_manifests.py). Overlap check: skill-judge D1 already
  scores "every paragraph earns its tokens" (skill-judge/SKILL.md:88) — no new
  judge dimension needed.

## Alternatives Considered

(Axis 4 — EN+JA WebSearch, 5 shipped approaches found)

1. **Authoring style guide / "model is already smart" doctrine** — Anthropic
   best-practices (EN: platform.claude.com skills best-practices); JA
   independent agreement (mynameisfeng.com Claude-Code reverse-engineering
   guide; local-llm.memo.wiki). Pros: zero infra. Cons: unenforced, drifts.
   → PARTIALLY ADOPTED: we fold the doctrine into deliverable 3.
2. **Progressive disclosure / thin-orchestrator architecture** — Anthropic +
   MindStudio (EN). Already present in skill-creator-advance as Progressive
   Disclosure; only the naming is missing. → ADOPTED as naming, not new build.
3. **Leading words + bloat taxonomy (Pocock)** — aihero.dev
   writing-great-skills; claims 63% reduction across his set. Pros: only
   approach naming WHY short works. Cons: **no verification step — pruning
   judged by eye**. → CORE ADOPTION, with his weakness fixed by our gate.
4. **Eval-gated refactoring / CI regression** — promptfoo, PromptEval, Kinde,
   Traceloop (EN). We already ship this (skill-refactor Q1/Q2/Q3). → ALREADY
   HAVE; it becomes the safety net under approach 3. Honest no-hit from
   research: no shipped deterministic token-budget linter for skill files
   exists anywhere — unoccupied niche, deliberately NOT built here (BACKLOG
   candidate, see Out of Scope).
5. **Automatic compression (LLMLingua family)** — Microsoft (EN); JA sources
   add that LLMLingua-1 degrades on Japanese text (zenn.dev/knowledgesense).
   REJECTED: targets runtime RAG/context stuffing; output is non-human-
   readable token soup, unusable as maintained source.

**EN-JA disagreement (finding)**: EN discourse centers authoring discipline +
CI gates; JA discourse centers mechanical/automatic compression and API cost.
On the core doctrine (short prompts, model already reasons) they agree fully.
JA-only caveat: token-level auto-compression is language-fragile; authoring-
level compression is not — reinforcing the rejection of approach 5.

**My take**: adopt 3 (candidate generation) + naming from 2, grounded doctrine
from 1, all gated by our existing 4. Pocock generates, our gate verifies —
each supplies what the other lacks.

**Weak-model sensitivity (research)**: Anthropic explicitly warns "what works
perfectly for Opus might need more detail for Haiku" — compression has a
model-tier floor; no published benchmark quantifies it (practice-derived).
This grounds deliverable 1's mandatory weakest-tier verification guard.

## Decision

Build: the three content deliverables above (one new move, one pre-pass
section, one new authoring reference), version bump + CHANGELOG + codex
manifest sync. NOT build: any new script/linter/CI gate; any skill-judge
rubric change; any refactor OF skill-creator-advance's over-cap body beyond
the ≤0-net-growth pointer constraint. Why: the gap analysis shows the repo
already owns the verification half (unique among all researched approaches);
the missing half is exactly the candidate-generation knowledge, which is pure
content.

## Out of Scope

- Deterministic token-budget CI linter for skill files (unoccupied industry
  niche; would pair with adding skill-dev-toolkit to the skill-structure scan
  — BACKLOG candidate, references existing memory
  ci-skill-structure-scan-gap-obsidian).
- skill-creator-advance body refactor to get back under the 4,500 cap (its own
  future skill-refactor round — now easier WITH these moves shipped).
- Applying the new moves to any other skill (that's future sweep work, e.g.
  re-running code-toolkit-skill-refactor-sweep with the enriched catalog).
- skill-judge rubric changes (D1 already covers token economy).
- Porting/quoting Pocock's writing-great-skills text wholesale (MIT allows it,
  but we distill principles with attribution instead — our contexts differ:
  he has no verification gate to lean on).

## What Becomes Obsolete

(Axis 5) Mostly additive — flagged and justified: the taxonomy pre-pass
SUBSTITUTES cost (ranks targets before expensive leave-one-out ablation runs,
so fewer blind runs), and deliverable 3's naming retires the unnamed,
re-derived-each-time framing of steps-vs-reference. No file/process is
deleted. The additive-YAGNI flag is answered by PR #559's demonstrated demand:
round 1 wasted budget cutting the wrong candidates first.

## Open Questions

(none — scope fork [include deliverable 3 or defer] resolved by the user's
original plural framing「skill 開發相關的 skill 裡面」and the ≤0-net-growth
constraint making it safe.)
