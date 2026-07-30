# Brief: requesting-docs-review — standalone docs-review skill for loom-code

Date: 2026-07-30 · Stage: brainstorming output → writing-plans input
Branch: `feat-requesting-docs-review-skill` · loom-code 0.41.0 → 0.42.0

## Design-side on-ramp

Offered: N/A — tool-shaped increment inside an existing plugin (loom-code), not
product-shaped/user-facing work; no on-ramp row fired (negative guard).

## Problem

When a docs-heavy branch closes out, review must catch the defects that matter
in prose (wrong instructions, dead citations, cross-artifact contradictions)
and converge in bounded rounds. Today's docs review is a per-dispatch prose
override grafted onto the code-review harness: it fixed rubric scope
(0.40.0) and blocking class (0.41.0), but the structure that produced a
9-round non-converging loop is still standing where the fixes do not reach —
mixed branches keep pure code rubrics, no round cap exists anywhere on the
whole-branch loop, the override lives in ~900 words of dispatch prose on a
code-shaped agent contract, and doc-only SDD tasks still get the code triad.

Root-cause evidence (2026-07-30 four-stream investigation):
- Aggregation-rule mismatch is the confirmed primary cause: the shared
  "any 🔴 or ≥2 🟡 → NEEDS_REVISION" rule mechanically retrodicts every
  verdict of the 9-round loop; 6 of 8 blocking rounds were pure-🟡
  (`docs/loom/specs/2026-07-30-docs-review-blocking-class.md:24-50`).
- Prose has no termination oracle: 6 of 9 rounds shipped a defect injected by
  the previous round's own remediation
  (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md:46-49`).
- The second pathological loop ran on a MIXED branch, outside 0.41.0's
  docs-only trigger (`docs/loom/specs/2026-07-30-docs-review-blocking-class.md:196-201`).
- Whole-branch review is the only loop in the family with no cap
  (`docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md:20-33`).
- 35-day session mining: ~10 doc-artifact loops (2–6 rounds) vs ~3 code loops
  (all converged in 2 rounds with mechanically verifiable fixes).

Docs shipping is not an edge case: the entire loom pipeline front half
(discovery / principles / design / spec) ships prose-only branches — this is a
peer lane, not an accommodation.

## Users

- The solo operator (kouko) closing out branches via
  `finishing-a-development-branch` in any repo with loom-code.
- Orchestrator + reviewer agents across model tiers. Weak-tier executors are a
  design constraint: contracts must be validator-enforced, not prose-only
  (`docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md`), and
  agent prose must survive haiku cold-reads
  (`docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`).

## Smallest End State

1. **New skill** `loom-code/skills/requesting-docs-review/` (SKILL.md ≤6k
   tokens, flat folder per `.claude/hooks/validate-skill-folder-structure.sh:51-75`)
   owning the docs arm of branch review:
   - the five prose dimensions (omission / ambiguity / inconsistency /
     incorrect-fact / missing-population), whole-artifact scope,
     `class: instruction | evidence` fail-closed, instruction-only gating —
     relocated from `requesting-code-review/SKILL.md:97,100,147,173-186`;
   - `check_doc_citations.py` pre-pass riding the dispatch packet (unchanged
     script, `loom-code/scripts/check_doc_citations.py:399-466`);
   - **convergence contract** (the new part):
     (a) hard cap: 2 review rounds, then STOP and surface to the user with
         the surviving findings — never a silent third round (precedent:
         critics' 2-round cap + user-authorized breach; industry: 2–3-round
         caps shipped in EN+JA sources, see Alternatives);
     (b) round 2 reviewers receive round 1's findings verbatim and must
         verify fixes against quoted evidence before raising anything new;
         re-litigating a closed finding in new words is forbidden
         (JA "概ね対応済み" ban precedent);
     (c) oscillation stop: a finding that resurfaces after being
         fix-verified ends the loop immediately → user;
     (d) evidence-class fixes for unchanged prose stay appended corrections,
         never in-place rewrites (0.41.0 rule, relocated).
2. **New agent** `loom-code/agents/docs-reviewer.md` — prose-native contract
   mirroring `code-reviewer.md` structure (frontmatter, verdict-only
   role-contract, verdict template with prose `dimension_scores:` +
   `class:` per finding), carrying the three injection-marker blocks and
   registered in `distribute.py` target lists (`distribute.py:186-217,260-263`).
   Verdicts mint through the existing `loom_gate_markers.py` schema
   (prose dimension names are already schema-valid, `loom_gate_markers.py:201-218`).
3. **Routing** stays where callers already are — `requesting-code-review`
   Step 1 becomes a three-way dispatch:
   - all files `.md` → delegate whole review to `requesting-docs-review`;
   - mixed → per-file split: code files → code-reviewer panel, `.md` files →
     docs-reviewer, orchestrator unions verdicts (both arms must pass);
   - code-only → unchanged path.
   `finishing-a-development-branch:19-20,81,100-117` keeps invoking
   requesting-code-review as today (no caller-facing change); its flow text
   updates to name the docs arm.
4. **Trivial-skip boundary defined**: `requesting-code-review/SKILL.md:48,54`
   "doc change" exemption narrows to mechanical doc edits (typo, version
   bump, generated/sync output); authored prose routes to docs review.
5. **SDD per-task prose review** (user checkpoint 2026-07-30: include in this
   arc): plan tasks may declare `Review-weight: prose` alongside the existing
   `mechanical` (`subagent-driven-development/SKILL.md:110-117`); the
   orchestrator then replaces the code-quality-reviewer arm with the
   docs-reviewer agent — implementer and spec-reviewer stay (spec conformance
   is artifact-type-agnostic). Plan-side gate: extend Check 16
   (`writing-plans/references/plan-document-reviewer-prompt.md:48,67`) with
   the prose row (allowed only when the task's Files touched are all `.md`
   authored prose; fail-closed to full triad, mirroring mechanical's
   fail-closed rule).
6. **Test migration + release**: re-point
   `test_docs_review_mode.py` / `test_docs_review_blocking_class.py` pins to
   the new skill's files; bump plugin.json to 0.42.0 (+ CHANGELOG, marketplace
   description sync, codex manifest sync — all CI-enforced,
   `.github/workflows/loom-code-ci.yml:94-120`, `skill-structure.yml:305`).

## Current State Evidence

- **Forward**: `finishing-a-development-branch/SKILL.md:19-20` (flow names
  requesting-code-review), `:81` (delegation row), `:100-117` (verdict
  routing + B2 fallback + silent fix→re-review loop — the uncapped loop);
  `requesting-code-review/SKILL.md:43` (invoked as Step 1), `:94-97` (docs
  mode = one paragraph at line 97), `:100`, `:147`, `:173-186`, `:48,54`
  (trivial-skip lines that exempt exactly what the new skill reviews).
- **Reverse (SSOT)**: `domain-teams/skills/code-team/{standards,rubrics,checklists}`
  is canonical; loom-code holds functional copies via hand-maintained ROUTE
  (`loom-code/scripts/distribute.py:5-16,43,54-99,109-115`). Agent files are
  hand-authored with three regenerated injection blocks
  (`distribute.py:186-217,323-348`); a new agent must carry all three marker
  pairs or distribute.py raises (`:260-263`). A new prose rubric MAY be
  loom-code-local (ROUTE is opt-in per file) — decision below.
- **Error/guards**: `loom_gate_markers.py:201-218` (schema), `:224-247`
  (findings need path-like `where:`), `:257-273` (exit 4 schema-fail / exit 3
  NEEDS_REVISION refuses to mint); `loom-code/hooks/git-guard.py:12-49`
  (push gate wants fresh review-pass.json + verified.json pinned to HEAD);
  `.claude/hooks/validate-skill-folder-structure.sh:51-75` (flat folders).
- **Data/tests**: `test_docs_review_mode.py:36-43,166-185` (pins SKILL.md
  path, trigger phrasing, polarity mutation test, 5 dimension names);
  `test_docs_review_blocking_class.py` (pins class taxonomy, aggregation
  sentences, and `0.41.0` in plugin.json + CHANGELOG at `:319-336`);
  `check_doc_citations.py:1-42,399-466` (CLI, exit codes);
  CI runs whole test dirs (`loom-code-ci.yml:94`).
- **Boundary**: `subagent-driven-development/SKILL.md:110-117`
  (Review-weight: mechanical — the only per-task relief valve; fail-closed);
  `writing-plans/references/plan-document-reviewer-prompt.md:48,67`
  (Check 16); `agents/code-reviewer.md:1-30,332,346,386-389` (template a
  docs-reviewer mirrors); repo CLAUDE.md §Skill Structure (6k-token cap).
- Evidence paths appendix: see the files cited above; recon 2026-07-30.

## Decision

Build the standalone skill + prose-native agent + three-way routing +
convergence contract as one arc (shape B, ratified by user 2026-07-30 over
shape C — jurisdiction cleanliness; recorded in `docs/loom/BACKLOG.md`
§"Standalone docs-review skill"). The prose rubric ships **loom-code-local**
(not routed from code-team): docs review is loom-code jurisdiction, no other
plugin consumes it today, and adding a ROUTE entry is a later one-liner if
domain-teams ever needs it. Convergence rules are enforced by the skill's
orchestrator contract + minted verdict flow (validator-checked where cheap),
not by prose alone. We do NOT build: a findings-ledger instrument (P1+P2
stays parked), a Vale/textlint lint layer (see Alternatives — reversal
condition recorded), citation content-drift checking, or any change to
critics / design-side stations.

## Alternatives Considered (Axis 4 — researched 2026-07-30, EN+JA)

| Alternative | Who ships it | Why rejected here |
|---|---|---|
| Keep docs mode inside requesting-code-review (status quo) | this repo 0.40–0.41 | dispatch-prose override on a code agent is the recorded weak-executor failure shape; mixed branches uncovered; no cap. Kept as fallback if this arc is abandoned. |
| Prose agent on shared skeleton (shape C) | — | rejected by user 2026-07-30 (jurisdiction cleanliness); C's one dividend (agent reuse in SDD) survives in B via the standalone agent. |
| Advisory-only LLM doc review, human decides | NTT Docomo "AI部長" (Claude/Bedrock, 50+ users) [JA] | our gate must block pushes; BUT this is the recorded demotion path: if instruction-class FP stays high after tuning, demote the LLM panel to advisory and let only mechanical checks block. |
| Deterministic prose lint gate (Vale / textlint) | Datadog, Netlify, GitLab [EN]; Cybozu, Sansan [JA] | cannot check instruction correctness / factual claims — the classes that loop. Deferred, not rejected: reversal condition = if wording/style-class findings dominate post-ship rounds, add a lint pre-gate for long-lived instruction surfaces (SKILL.md), skip short-lived plans. |
| Per-round finding caps + convergence rules for LLM reviewers | caphtech, IIWNL convergence template [JA]; multi-model convergence loops, 1–2 loop CI caps [EN] | adopted, not rejected — source of the 2-round cap, re-litigation ban, oscillation stop. EN/JA agree on caps+tiering; they diverge on block-vs-advise (finding recorded above). |

Sources (labeled): vale.sh / datadoghq.com Vale post / netlify.com docs-linting [EN];
blog.cybozu.io 2020-09-11, buildersbox.corp-sansan.com 2022-04-18 [JA];
graphite.com conventional-comments guide [EN]; zenn.dev/caphtech ai-review-first-design,
qiita.com/IIWNL 6feb36d5 [JA]; nttdocomo-developers.jp 2025-12-05 [JA];
zylos.ai multi-model-ai-code-review-convergence [EN].

## What Becomes Obsolete (Axis 5)

- `requesting-code-review/SKILL.md` Step 1 docs paragraph (line 97), the
  Step 3 docs sentence (line 100), §Aggregation docs paragraph (line 184),
  and the schema `class:` comment scope (line 147) — relocated, deleted at
  source in the same change.
- The `:48,54` blanket "doc change" trivial-skip — replaced by the narrowed
  mechanical-only boundary.
- `test_docs_review_mode.py` / `test_docs_review_blocking_class.py` pins on
  the old SKILL.md paths + 0.41.0 version pins — re-pointed, not duplicated.
- `docs/loom/BACKLOG.md` §"Standalone docs-review skill" PARKED entry —
  flips to in-progress/SHIPPED as part of this arc.

## Out of Scope

- Findings-ledger instrumentation (P1+P2) — stays PARKED with its own
  re-trigger (`docs/loom/BACKLOG.md`).
- Vale/textlint mechanical lint layer — deferred with reversal condition
  (Alternatives table).
- Citation content-drift, unbackticked citations, `--sections` promotion —
  explicitly out of scope since 0.40.0; unchanged here.
- Critics (completeness-critic / design-critic) and their outer-loop caps —
  zero recorded pathology; untouched.
- Any change to `dev-workflow:git-memory` or the push-guard hook contract.

## Open Questions

1. Panel shape for the docs arm on mixed branches: mirror the two-arm union
   or single docs-reviewer? Default: mirror current panel conventions;
   plan stage decides with token cost in view.
2. Cap-breach protocol wording: adopt critics' "user-authorized breach"
   verbatim (default yes).

(Resolved 2026-07-30: SDD `Review-weight: prose` is IN scope — user
checkpoint; see Smallest End State item 5.)
