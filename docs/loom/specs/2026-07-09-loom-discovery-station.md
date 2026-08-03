# Brief: loom-discovery — the problem-space station (business-value + user-insights)

Date: 2026-07-09
Stage: brainstorming output → writing-plans input
Design-side on-ramp: offered — user chose direct (repo precedent: monkey-skills deliberately has no `docs/loom/PRINCIPLES.md`; all prior loom stations were built via brainstorming → brief).

## Problem

The loom pipeline (principles → interface-design → spec → code) has no problem-space
stage. Job to be done: *when I bring a product-shaped idea to loom, I want the
pipeline to first establish — with recorded evidence — what problem exists, for whom,
and whether it is worth my time, so that downstream stations consume verified needs
instead of whatever happened to be in my head.*

Concrete failure modes today:

1. product-principles' adversarial intake assumes the user can already answer
   problem/users questions; when they can't, the flow dead-ends — no route to research
   (`loom-product-principles/skills/product-principles/SKILL.md:33-40`).
2. The only research machinery in the family sits at the most downstream station
   (loom-code brainstorming Axis 4) — backwards.
3. No audit trail of discovery reasoning → future drift-prevention and
   re-understanding impossible (user's explicit requirement).
4. The business/market turf was ceded to planning-team
   (`loom-product-principles/README.md:70`) but no on-ramp ever routes there —
   the cession is a dead end.

Six prior discussion rounds (this session) covered: stage-gap diagnosis, 3 research
rounds (classical frameworks ×9, AI-pipeline tools ×7, artifact formats ×10), the
two-layer split, station-vs-skill granularity, professional isolation, naming.

## Users

- kouko (solo dev, Traditional Chinese / Japanese / English) starting product-shaped
  work in any repo with loom installed.
- Weak-model sessions executing the family: trigger conditions and skill descriptions
  must be decidable without judgment (repo memory:
  `skill-triggering-diagnose-listing-before-text` — descriptions must survive listing
  eviction; per-skill description budget 1536).
- Future re-readers (6-months-later kouko, new sessions) consuming the audit trail.

## Smallest End State

One new plugin + connective-tissue sweep + one tripwire. Ships when:

1. **Plugin `loom-discovery`** (scaffold mirrors loom-spec: dual manifest
   `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json`, README, CHANGELOG,
   `scripts/test_marketplace_entry.py` + `test_plugin_manifest.py`, no hooks):
   - `skills/using-loom-discovery/` — family-entry router (+ `references/`
     claude-code-tools.md / codex-tools.md, per sibling pattern).
   - `skills/business-value/` — adversarial worth-it check. Optional (trigger
     conditions below), re-entrant after research. Artifact: `business-value.md`
     (why now / why me / opportunity cost / GO / NO-GO / NEEDS-MORE-RESEARCH).
     Register: Shape Up betting ("worth my time budget"), NOT Cagan business
     viability. Market sizing / GTM / revenue → delegate to
     `domain-teams:planning-team` (cross-plugin delegation contract), never inline.
   - `skills/user-insights/` — the core research verb. Artifact set under
     `docs/loom/discovery/<date>-<slug>/`:
     - `user-insights.md` — problem framing / opportunity space (evidence-linked
       needs as job stories, contexts, today's workarounds) / value commitment
       (which needs we serve + desired outcomes + appetite; states WHAT, never HOW)
       / risks & open questions. Problem-space-pure: no solution sections
       (Intercom rule "do not add the solution here").
       Two modes inside this skill, assigned per work nature: opportunity-space
       mapping is KNOWLEDGE work (research/explore mode — ground truth in the
       world); value commitment is a VALUE JUDGMENT (ground truth with the user).
       **Commitment interaction contract**: the agent presents the mapped
       opportunity space with evidence + an explicit recommendation
       (research-then-"my take", same protocol as loom-code brainstorming Axis 4);
       the commitment is written into `user-insights.md` only after the user
       ratifies it. Agents never self-commit on the user's behalf.
     - `research/` — one intermediate report per research question
       (goals → method → findings → insights skeleton).
     - `evidence.md` — claims-to-evidence registry (atomic-research model:
       evidence outlives any single report).
     Research engine: delegate heavyweight research to
     `research-toolkit:deep-deep-research` per cross-plugin contract; a light
     inline WebSearch mode for small scopes (boundary = design decision at
     writing-plans, see Open Questions).
   - Professional isolation is contract-level: the two skills share no artifact and
     no agent; business-value's agents may not map needs, user-insights' agents may
     not render investment verdicts.
2. **Connective tissue** (blast radius per repo memory
   `core-rule-removal-needs-plugin-wide-sweep` — sweep, expect residue):
   - `loom-pipeline/hooks/family-reception.md`: family map (:8-20), Three doors
     (:22-33, station enumeration :30), on-ramp table — **append** a discovery row,
     do NOT renumber (repo memory `retire-numbered-checks-dont-renumber`).
     Row condition (draft, finalize at writing-plans): "product-shaped work AND the
     problem/users cannot be articulated with evidence → suggest
     using-loom-discovery first"; note precedence over the principles row when both
     fire.
   - Four/five-station enumerations sweep: `loom-pipeline/README.md:33,40-41,76,118,129`;
     `loom-pipeline/skills/using-loom-pipeline/SKILL.md:7,11,26,51,58,64,174`;
     `loom-code/skills/using-loom-code/SKILL.md:96`; marketplace description for
     loom-pipeline (`.claude-plugin/marketplace.json:~124-126`); living design docs
     `docs/loom/specs/2026-07-04-loom-family-connective-tissue.md:14,70,124,147`.
   - `.claude-plugin/marketplace.json`: append loom-discovery entry (pattern:
     loom-spec entry :107-111). Description must equal plugin.json description
     (CI: `scripts/check-marketplace-description-sync.py` via
     `.github/workflows/skill-structure.yml:83-101`).
   - `docs/loom/README.md:9-17` table + `docs/loom/INDEX.md`: declare
     `docs/loom/discovery/` as the artifact home.
   - CI: extend `.github/workflows/loom-siblings-ci.yml` (or own workflow — Open
     Question) so the new plugin's manifest/marketplace tests run.
3. **product-principles tripwire**: at the intake boundary
   (`loom-product-principles/skills/product-principles/SKILL.md:33-40`) and the
   family entry redirect list
   (`loom-product-principles/skills/using-loom-product-principles/SKILL.md:16-31`):
   when the user cannot answer problem/users grilling with evidence, route to
   loom-discovery instead of dead-ending. Amend `README.md:70` boundary line
   (see What Becomes Obsolete).

### business-value trigger conditions (draft — finalize as decidable enumeration)

Fire when ANY: (a) the outcome is for others / will be published or maintained;
(b) multiple ideas compete for the same time budget; (c) meaningful resource spend.
Skip (silently, negative-guard style): personal tool, GO already decided by the user.

## Current State Evidence

- **Forward**: new station enters via family reception —
  `loom-pipeline/hooks/family-reception.md:8-20` (family map), :35-45 (on-ramp
  table), injected at session start by `loom-pipeline/hooks/session-start:3-6,53`.
- **Reverse (SSOT direction)**: on-ramp table is declared SSOT — its header says
  every entry's §Intake references it, never copies rows
  (`family-reception.md:35-39`). Station enumerations elsewhere are hand-synced
  prose (no distribute script) — that is exactly why the sweep is required.
  plugin.json description is SSOT mirrored into marketplace.json, enforced by
  `scripts/check-marketplace-description-sync.py`.
- **Error**: CI gates that fire on this change —
  `.github/workflows/skill-structure.yml:83-101` (description sync),
  `loom-siblings-ci.yml:25-35` (fires on marketplace.json edits),
  `.claude/hooks/validate-skill-folder-structure.sh` (blocks nested subfolders in
  skills/). New plugin needs its own `test_marketplace_entry.py` to pass.
- **Data**: `docs/loom/README.md:7-17` defines artifact homes (specs/, plans/,
  memory/, audits/, dogfood/, research/); `docs/loom/discovery/` does not exist and
  no convention yet declares new artifact families — extend that table.
- **Boundary**: planning-team owns market/business/strategy
  (`loom-product-principles/README.md:70`,
  `loom-product-principles/skills/product-principles/SKILL.md:33-40`);
  research-toolkit owns research engines (delegate, don't duplicate);
  loom-code brainstorming keeps its own Axis 4 research (feature-granularity,
  untouched by this change).

Evidence paths appendix: all citations gathered 2026-07-09 by Explore recon over
/Users/kouko/GitHub/monkey-skills (session agents; verified against files, not memory).

## Alternatives Considered (Axis 4 — 3 research rounds, EN+JA)

1. **No discovery station** (Kiro, GitHub Spec Kit ship without one — official docs
   verified). Rejected: the gap is the field's named "failure-deciding phase";
   JP practitioner writing concurs (調査/要件定義が失敗を決める).
2. **Artifact-free explore verb** (OpenSpec's `explore`,
   github.com/Fission-AI/OpenSpec). Rejected: user requires an audit trail for
   drift-prevention; artifact-free is the criticized end of the spectrum.
3. **Artifact-producing optional analysis phase** (BMAD-method Analyst → product
   brief, docs.bmad-method.org). **Adopted in spirit**: optional, artifact-producing,
   skippable by track.
4. **Single two-layer artifact** (one opportunity.md). Rejected in round 5:
   business analysis vs user research are different professions → two independent
   steps, two artifacts, hard agent-contract boundary.
5. **Two stations (two plugins)**. Deferred with named flip conditions: (a) assess
   grows portfolio/cross-project scope, (b) independent-install demand, (c) batch
   pipeline needs segment-level skip. Family precedent: professional separation
   lives at skill+agent level (loom-code implementer vs reviewers), plugin = packaging.
6. **Artifact formats**: Cagan Opportunity Assessment (svpg.com — business-leaning,
   trimmed), Intercom problem statement (problem-pure, adopted), Shape Up pitch
   (appetite concept borrowed, solution section rejected), Amazon PR/FAQ + Lean
   Canvas + Patton Opportunity Canvas (rejected: solution-flavored), Torres
   opportunity space (producttalk.org — adopted as the needs-mapping semantics),
   ResearchOps atomic research / NN/g report skeleton (adopted for the intermediate
   layer).

Naming trail (round 6): grill-me's own author demoted user-interrogation in favor of
domain grounding (aihero.dev/skills-grill-me) — supports research-over-grilling for
the needs verb; final names `business-value` × `user-insights` chosen for
plain-language legibility + tri-language currency (商業價值×使用者洞察 /
ビジネスバリュー×ユーザーインサイト) + "insight" anchoring the ResearchOps
evidence chain (facts → insights → recommendations).

## Decision

Build ONE new plugin `loom-discovery` with TWO professionally-isolated member skills
(`business-value`, `user-insights`) producing separate artifacts under
`docs/loom/discovery/<date>-<slug>/`, wire it into the family reception (append-only
on-ramp row), sweep all station enumerations, and add the product-principles
tripwire. Do NOT build: a second plugin, a discovery critic panel (v0.2 candidate),
pipeline-conductor batch segments for discovery (interactive-only in v0.1), or any
inline market/GTM analysis (delegate to planning-team).

## What Becomes Obsolete (Axis 5)

- `loom-product-principles/README.md:70` deferral line — amend, not delete:
  market/GTM/revenue stays planning-team turf; user/problem research is now
  loom-discovery turf. State "supersedes-in-part 2026-06-14 MVP brief's Out list"
  explicitly.
- product-principles' implicit dead-end on unanswerable grilling — replaced by the
  tripwire (SKILL.md:33-40 area).
- The on-ramp table's implicit "principles is the first stop for product-shaped
  work" — amended by the appended discovery row + precedence note.
- Living design doc `2026-07-04-loom-family-connective-tissue.md` four-station
  framing — update in the same change (it is declared living, :14).

## Out of Scope

- Discovery-critic panel (family GENERATE-station pattern) — BACKLOG, v0.2 candidate.
- loom-pipeline conductor driving discovery as a batch Workflow segment — v0.1 is
  interactive-only; enumeration text updated, orchestration deferred.
- Pre-grill / agent-answerer mechanism for loom-code brainstorming briefs (round-1
  discussion) — separate future brief.
- Two-station split — deferred with flip conditions (Alternatives #5).
- Any change to loom-code brainstorming's Axis 4, research-toolkit internals, or
  planning-team.
- Obsidian/Codex host parity beyond the standard sibling references/ pattern.

## Open Questions

1. business-value trigger conditions — final decidable wording (writing-plans).
2. Light-inline vs delegated research boundary for user-insights (draft: delegate
   when >3 research questions or external/user evidence needed; inline WebSearch
   otherwise) — finalize at writing-plans.
3. CI: fold into `loom-siblings-ci.yml` vs own `loom-discovery-ci.yml` — follow
   whichever pattern the sibling stations converged on at implementation time.
4. Does `user-insights.md` need a validator script (family pattern: stdlib
   structural validators per station) — assume yes, scope at writing-plans.
5. on-ramp row precedence wording when discovery row and principles row both fire —
   draft in Smallest End State, cold-reader test before ship.

## Memory recall honored (docs/loom/memory/)

`core-rule-removal-needs-plugin-wide-sweep` (station-enumeration sweep),
`retire-numbered-checks-dont-renumber` (on-ramp append-only),
`skill-triggering-diagnose-listing-before-text` (router description budget),
`stamp-changelog-test-counts-at-closeout`, `github-squash-merge-single-commit-drops-body`
(PR close-out).
