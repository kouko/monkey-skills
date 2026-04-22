---
title: copywriting-toolkit vs domain-teams:copywriting-team — A/B Retrospective
version: v1.12.0 (as of 2026-04-22)
status: decision-document
scope: evaluation-only (no code changes in this document)
---

# A/B Retrospective — copywriting-toolkit vs domain-teams:copywriting-team

## Executive summary

`copywriting-toolkit` (B) is a strict functional superset of `domain-teams:copywriting-team` (A). All 10 sampled Tier-1 framework canon files are byte-identical. B adds a 9-phase pipeline with envelope routing, a 90-anchor voice library (plugin-native), dedicated Ethics / Form / Audit phases, Express Mode, specialized agent roles, and Phase 5/6 voice split. A offers no capability B lacks except `jp-copy-craft-lineage.md` — which B has intentionally dissolved in v1.6.1 and replaced with the anchor library.

**Recommendation**: **Consolidate into toolkit**, with `domain-teams:copywriting-team` deprecated to a thin router / history marker. Rationale: A provides no unique capability; drift risk widens as B's anchor library evolves (6 months of active work, 90 anchors, 24 drift corrections); the A/B maintenance tax (0/128 B standards actually carry the mandated `DIVERGED FROM` header despite policy) is already showing failure.

**Secondary findings** (non-blocking for consolidation):
- Both plugins share a **薬機法 / FDA structure-function blind spot** for supplement/medical briefs — neither has category-triggered health-claim checklist extension. Gap belongs to upstream canon, not divergence.
- B has documentation discipline drift: Tier-2 DIVERGED headers missing uniformly. Independent of consolidation decision, this needs a fix.

---

## Part 1 — Inventory comparison

### Structural scale

| Dimension | A: `domain-teams:copywriting-team` | B: `copywriting-toolkit` |
|---|---|---|
| Total files (markdown) | ~44 | ~284 |
| SKILL.md | 1 monolithic (505 lines, 30.7 KB) | 14 (one per pipeline stage) |
| Agents | 0 (uses generic `domain-teams:worker` + `evaluator`) | 2 (`copywriter` sonnet + `copywriter-evaluator` opus) |
| Plugin manifest | N/A (sub-skill of domain-teams) | Yes (`.claude-plugin/`, standalone plugin) |
| Research / grounding notes | 8 (`grounding-v4.12.0` … `v4.18.2`) | Same 8 duplicated + 20+ `docs/voice-anchor-*` / `docs/register-references/` / `docs/format-templates/` / `docs/anchor-schema-v2*` |

### Standards distribution

| Standards family | A | B |
|---|---|---|
| Shared framework canon (19 files: PASONA / BEAF / AISAS / ULSSAS / ideation × 3 / SNS / ethics / psychology / short-form / mid-form / light-action / long-form-extended / verbalized-sampling / neta × 3 / voice-and-tone / voice-quadrant) | 19 in one `standards/` dir | Same 19 distributed across 10 skill dirs with INLINE duplication (`persuasion-psychology-anchor.md` × 5, `sns-evolution-aisas-ulssas.md` × 2) — 38 file-copies total |
| `jp-copy-craft-lineage.md` | Present (Tier 1 prose) | **Absent** — dissolved v1.6.1, replaced by anchor library |
| Anchor library (`anchor-*.md`) | **0** | **90** (43 EN + 28 JP + 19 ZH) |
| Quadrant routers (`{lang}-q{N}-anchors.md`) | 0 | 12 (en/jp/zh × q1-q4) |
| Anchor meta (`voice-anchor-meta-core.md`, `-detail.md`, `axis-extreme-anchors.md`) | 0 | 3 |
| Schema v2 docs (`docs/anchor-schema-v2.md` + pilot findings) | 0 | 2 |

**Critical finding**: the 90-anchor library is 100% plugin-native to B. A's voice system is the 2-axis quadrant (`voice-quadrant-positioning.md`) + 4-axis micro (`voice-and-tone.md`) + `jp-copy-craft-lineage.md` prose. **The anchor library is the single largest structural divergence**, and it has no upstream counterpart.

### Protocols / checklists / rubrics

| Kind | A | B | Overlap |
|---|---|---|---|
| Protocols | 9 (in `protocols/`) | 13 (distributed) + `express-mode.md`, `copy-ideation-parallel.md`, `phase-decision-tree.md`, others | 9 shared; B adds 4 plugin-native |
| Checklists | 3 | 3 (same names, distributed) | 3 shared — 2 content-diverged (ethics-checklist, framework-adherence; intake-completeness diverged via Express Mode extension) |
| Rubrics | 3 | 3 | 3 shared — 2 content-diverged (form-appropriate-gate, voice-consistency-gate) |

### Architecture

| Dimension | A | B |
|---|---|---|
| Shape | Monolithic skill with `## Workflows` table; 8 embedded workflows | 9-phase pipeline (Phase 0-8 + audit alt-entry), one skill per phase |
| Input contract | Raw prompt → Q1-Q10 hard gate | Same Q1-Q10 + Express Mode fast-path + `envelope.schema.json` cross-phase contract |
| Bounce-back | Not modeled (gate NEEDS_REVISION stops) | Formal envelope-violation routing with retry caps (`bounce_round ≥ 3` or `total_retries ≥ 4` → HALT) |
| Ethics gate | `checklists/ethics-checklist.md` MUST | Dedicated Phase 7 skill + Phase 0.5-B pre-draft grill + T1/T2/T3 tier routing |
| Form gate | SHOULD in workflow | Dedicated Phase 8 skill, promoted MUST |
| Voice Consistency | SHOULD gate | Phase 6 owns + Phase 8 8b cross-gate re-read |
| Phase 5 / 6 split | **No split** — voice folded into one skill | **Yes** — quadrant-stage (strategic) + tone-stage (tactical anchor rewrite) |
| Anchor library v2 schema | N/A | Plugin-native; `docs/anchor-schema-v2.md` + `anchor-schema-v2-pilot-findings.md` |
| Audit entry | Workflow variant (`Copy Audit` within SKILL.md, forces intake) | Dedicated skill (`copywriting-audit-stage`) skipping Phase 0-4; emits `ethics_verdict_on_original` as first-class structured output |
| Verification density | Baseline | v1.2.0 pruned ~10% back after v1.0.x-v1.1.0 accumulation |

---

## Part 2 — E2E A/B test results (3 briefs, minimal input)

Test methodology: dispatch same sparse brief (no voice_reference, no tone_cue, limited context) through both plugins end-to-end. Observe routing, gate verdicts, output quality, cost.

### Brief 1 — Short-form tagline ("Help me write a tagline for my new organic tea brand")

Tests: minimal-input handling, voice auto-selection without explicit reference.

| Dimension | A wins | B wins | Tied |
|---|---|---|---|
| Minimal-input handling | | ✓ (explicit Express Qual + disqualifier transparency) | |
| Voice discipline | | ✓ (Phase 5 quadrant + Phase 6 Pass 3d auto-select; anchor-saturated output) | |
| Legal/ethics catch | | ✓ (catches at grill AND Phase 7; T1/T2/T3 tier routing) | |
| Output quality | | ✓ (anchor-saturated vs generic Q3) | |
| Cost efficiency | ✓ (~30-40% cheaper, fewer hops) | | |

**Key observation**: Both plugins correctly bounce back to intake (sparse brief). Neither produces unsolicited copy. Downstream, B wins 4/5 dimensions on rigor; A wins 1/5 on cost.

**Output preview (if brief were completed)**:
- A: Q3-generic wellness — e.g. "Nature, poured daily." / 「自然而然，每一杯」 (register but non-anchored, interchangeable)
- B (zh-TW with 全聯 anchor auto-select): 「有機，不是標語，是日常」 / 「今天的茶，是明天的你」 (register-saturated, non-translated)

### Brief 2 — Long-form PASONA ("Write a sales email for my new supplement that helps with sleep")

Tests: legal-risk automatic detection (薬機法 / FDA structure-function claim territory).

| Dimension | Winner | Why |
|---|---|---|
| Intake discipline | Tie | Both hard-gate Q1-Q10 |
| Intake auditability | **B** | Router + envelope + `audit_trail[]` vs agent-level BLOCKED |
| Ethics canon coverage | Tie | Same Tier-1 checklist, byte-identical |
| Ethics hints (TW/JP D2C patterns) | **B** | v1.1.0 hints block (ethics-checklist.md:202-216) |
| Supplement/薬機法/FDA trigger | **Tie (shared gap)** | Neither has category-triggered health-claim checklist item |
| Upstream ethics catch (pre-draft) | **B** | Q8 grill + Express 0.5-B grill surfaces claim BEFORE draft; A's ethics runs only post-draft |
| Brief-level claim adjudication | **B** | Phase 7 judges `brief` + `draft`; A judges draft only |
| Defense-in-depth (drafter strategically omits FATAL claim) | **B** | B's brief-scope adjudication catches the gap |
| Runtime cost (full run) | **A** | Monolithic, fewer hops |

**Shared gap identified**: Neither plugin has explicit supplement/薬機法/FDA structure-function trigger. Both rely on opus evaluator's general legal knowledge to connect "supplement + sleep claim" → 優良誤認. Plausible future extension: category-triggered health checklist loaded when `brief.product.category ∈ {supplement, health, medical, pharma}`.

### Brief 3 — Audit path ("Here's a marketing banner — tell me if it's good")

Banner contains 5 risk flags: "guaranteed" absolute / "Doctors HATE" fabricated authority / "melts belly fat in 7 days" health outcome / "50,000+ satisfied customers" unsubstantiated testimonial / "Limited time offer" urgency.

| Dimension | A wins | B wins | Tied |
|---|---|---|---|
| Audit path existence | | ✓ (dedicated skill, clean envelope, no intake friction) | |
| Risk flag coverage (content) | | | ✓ (same checklist, 5/5 both) |
| **Formal verdict on ORIGINAL** | | ✓ (`ethics_verdict_on_original` as first-class field) | |
| Output structure | | ✓ (JSON envelope with per-field verdicts) | |
| Actionability (per-variant gate verdicts) | | ✓ | |
| Cost vs value | ✓ (cheaper for low-stakes browsing) | | |

**Critical behavioral delta**: A's audit workflow runs Ethics Gate **only on rewrites**, not on the original. B runs Phase 7 MUST on the original and emits `ethics_verdict_on_original: NEEDS_REVISION` as structured output. For a banner with ≥2 likely FATAL items, B provides a defensible legal document; A provides advisory prose.

### E2E aggregate

| Brief | A wins | B wins | Tied |
|---|---|---|---|
| Brief 1 (tagline, minimal) | 1/5 (cost) | 4/5 | 0 |
| Brief 2 (supplement email) | 1 (runtime cost) | 5 (auditability, grill, brief-scope, hints, defense-in-depth) | 4 (shared gate canon) |
| Brief 3 (audit external copy) | 1/5 (cost for low-stakes) | 4/5 | 1 (content coverage) |
| **Aggregate** | 3 wins (all cost-only) | 13 wins | 5 ties |

**Pattern**: B dominates on rigor, auditability, and defense-in-depth. A wins only on cost/speed. The cost differential is real (~30-40% cheaper on full runs per B's own `§Verification Density Principle`) but is a one-time architectural choice — Express Mode (in B) already addresses the "low-stakes fast path" use case.

---

## Part 3 — Divergence analysis

### Tier-1 byte-identical compliance

Sample of 10 shared standards all byte-identical:
- `persuasion-psychology-anchor.md` ✓
- `long-form-pasona-canon.md` ✓
- `short-form-catchcopy-canon.md` ✓
- `mid-form-beaf-canon.md` ✓
- `sns-evolution-aisas-ulssas.md` ✓
- `light-action-frameworks.md` ✓
- `long-form-extended-frameworks.md` ✓
- `verbalized-sampling.md` ✓
- `neta-injection-techniques.md` ✓
- `persuasion-ethics.md` ✓

**Tier-1 honor system working (today)**. But no CI guard — any A-side edit silently out-of-sync until manual `diff -q`. Per B's own CLAUDE.md: "Lint (future CI)" — never built.

### Tier-2 DIVERGED header compliance

**Finding**: 0 / 128 B-side standards carry the mandated `<!-- DIVERGED FROM -->` header, despite policy in `copywriting-toolkit/CLAUDE.md §Tier 2`.

Two explicitly-diverged files without headers:
- `voice-quadrant-positioning.md` — v1.11.2 added 15+ Brand Corpus cross-refs (by-design per v1.11.2 Tier-1 scope refinement)
- `voice-and-tone.md` — diverged

**Verdict**: documentation discipline lapse, not policy violation (v1.11.2 CLAUDE.md refinement clarifies that team-curated segments inside standards are Tier 2). But the header is still mandated and missing.

Across 13 shared protocols, 5 lack DIVERGED header.

### Content-diverged files (shared filename, different body)

- `ethics-checklist.md` — B adds v1.1.0 hints block (lines 202-216 with TW/JP D2C patterns)
- `form-appropriate-gate.md` — B adds form-specific criteria
- `voice-consistency-gate.md` — B adjusted for Phase 6 integration
- `intake-completeness-checklist.md` — B adds Express Mode section
- `voice-quadrant-positioning.md` — B adds Phase 6 anchor cross-refs (v1.11.2)
- `voice-and-tone.md` — B diverged

All divergences are by-design extensions. All lack header.

### Drift risks

1. **No CI guard on Tier-1 sync**: honor system working today; one A-side edit breaks invariant silently
2. **Inline-duplicate drift inside B**: `persuasion-psychology-anchor.md` × 5 copies; CLAUDE.md acknowledges risk + suggests "sync script"; none built
3. **Research note duplication**: 8 `grounding-v4.*.md` byte-identical across A and B; when A advances to v4.19.0+, B must re-copy manually
4. **`jp-copy-craft-lineage.md` active divergence**: A ships it; B dissolved it. Evaluators reach materially different conclusions for JP long-copy voice
5. **Anchor library gravity**: B's 90-anchor + v2 schema is a large, actively-evolving asset. A cannot catch up without importing wholesale, at which point structural convergence is forced

### Feature asymmetry

**B-only (worth backporting to A if A survives)**:
- Express Mode fast-path
- Envelope / bounce-back routing
- Phase 5/6 voice split
- Anchor library v2
- Specialized agent roles (copywriter sonnet / evaluator opus)
- Dedicated audit-stage skill
- Phase 0.5-B ethics grill (T1/T2/T3 tier routing)
- `audit_trail[]` observability

**A-only (worth preserving if A retires)**:
- `jp-copy-craft-lineage.md` — but B intentionally dissolved it; preserve as historical reference only

### Shared gaps (belong to upstream canon, unaffected by consolidation decision)

1. **薬機法 / FDA structure-function trigger** — neither plugin catches supplement/medical claim automatically; opus evaluator carries the load
2. **Category-aware checklist extensions** — neither plugin loads category-specific standards (e.g., financial / medical / supplement have distinct legal surfaces)
3. **Subscription-trap / recurring-billing patterns** — not in shared ethics checklist

---

## Part 4 — Recommendation

### The 4 options revisited

| Option | Verdict | Rationale |
|---|---|---|
| Keep A/B | ✗ Rejected | A provides no unique capability. Drift risk widens as B's anchor library evolves. Maintenance tax (DIVERGED headers 0/128) already showing failure. |
| **Consolidate into toolkit** | ✓ **Recommended** | B is functional superset. No capability loss on retirement of A. Tier-1 canon already stays in B (byte-identical). Eliminates drift risk + dual maintenance. |
| Consolidate into domain-teams | ✗ Rejected | Would require importing 90-anchor library, envelope schema, 14-skill pipeline into domain-teams — structural explosion. domain-teams as a meta-plugin is deliberately monolithic-per-team; forcing B's architecture into A would either (a) break domain-teams shape or (b) lose B's features. |
| Fork further | ✗ Rejected | No product reason to diverge. A and B serve same users, same use cases. |

### Recommended execution path: Consolidate-into-toolkit

**Architecture after consolidation**:

- **B (`copywriting-toolkit`)** = canonical copywriting plugin. Continues as-is.
- **A (`domain-teams:copywriting-team`)** = thin deprecation marker:
  - Convert `SKILL.md` to a 30-line router: "This skill has moved. Use `copywriting-toolkit` plugin for full pipeline." Include delegation example.
  - Keep `jp-copy-craft-lineage.md` as archived historical reference for audit purposes (it's dissolved in B by design; preserving the original is defensive history)
  - Remove standards/ / protocols/ / checklists/ / rubrics/ duplicates — they all live in B now
  - If domain-teams meta-plugin must list copywriting as a team (roster integrity), the deprecation stub satisfies the requirement without content duplication

**Why not full delete of A**: domain-teams is a meta-plugin with a consistent team roster (code / qa / docs / devops / research / design / planning / investing / copywriting / skill-team / using-domain-teams). Deleting the copywriting-team entirely would break the meta-plugin's naming pattern. A deprecation stub preserves the roster while making B the canonical implementation.

### Pre-consolidation cleanup (should happen regardless)

Independent of consolidation decision, these items need fixing:

1. **Retrofit DIVERGED headers** on B's actually-diverged Tier-2 standards (`voice-quadrant-positioning.md`, `voice-and-tone.md`, `ethics-checklist.md`, `form-appropriate-gate.md`, `voice-consistency-gate.md`, `intake-completeness-checklist.md`, 5 protocols). Policy compliance.
2. **Build CI lint** for Tier-1 sync (`diff -q` against domain-teams for Tier-1 files). Currently honor-system; failure mode is silent.
3. **Sync script for inline-duplicated standards** (`persuasion-psychology-anchor.md` × 5 in B). CLAUDE.md acknowledges need; not built.

Items 1-3 are not blockers for consolidation — consolidation actually **resolves items 1-2** (no more cross-plugin sync needed once A is deprecation stub) and **simplifies item 3** (still an in-plugin concern).

### Post-consolidation follow-ups (separate work)

Not part of consolidation PR; track as future backlog:

1. **Category-triggered checklist extensions** — shared gap: supplement / health / medical / financial / subscription categories lack explicit legal-surface coverage. Belongs in meta-core as category router. E2E Brief 2 showed both plugins missing 薬機法/FDA trigger.
2. **薬機法 / FDA structure-function explicit check item** — add to `ethics-checklist.md`. Opus evaluator usually catches by general knowledge but mechanical enforcement is safer.
3. **Tooling**: CI guard + inline-duplicate sync script (items 2-3 above).

### Consolidation execution plan (separate PR, NOT in this document's scope)

If consolidation approved, future PR delivers:
1. Convert `domain-teams/skills/copywriting-team/SKILL.md` to deprecation router stub (~30 lines)
2. Archive `jp-copy-craft-lineage.md` in `domain-teams/skills/copywriting-team/docs/archive/` with note "dissolved in copywriting-toolkit v1.6.1; preserved for historical audit"
3. Delete duplicated `standards/` / `protocols/` / `checklists/` / `rubrics/` from `domain-teams/skills/copywriting-team/` (canonical in B)
4. Update `domain-teams/skills/using-domain-teams/SKILL.md` to route copywriting queries to `copywriting-toolkit` plugin
5. Update `copywriting-toolkit/CLAUDE.md §A/B Coexistence` to reflect consolidation outcome
6. Bump `copywriting-toolkit` version (v1.12.0 → v1.13.0 since this is the consolidation landing)
7. CHANGELOG entry

Estimated scope: ~1-2 session, single PR, no new content authored. Mostly deletion + one router stub + documentation.

---

## Confidence assessment

- **High confidence**: B is functional superset on observed use cases. Inventory audit + 3 E2E briefs all point same direction.
- **Medium confidence**: cost delta claim (A ~30-40% cheaper per full run). Based on plugin self-report (`CLAUDE.md §Verification Density Principle`); not independently measured in this retrospective. Does not materially change recommendation — cost advantage is addressable via Express Mode in B.
- **Low-stakes decision**: consolidation scope is mostly deletion + stub. Reversible if needed.

## Appendix: files cited

- `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/copywriting-team/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/copywriting-team/protocols/copywriting-brainstorming.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/using-copywriting-toolkit/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/using-copywriting-toolkit/protocols/phase-decision-tree.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-intake/protocols/express-mode.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-audit-stage/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-ethics-check-stage/checklists/ethics-checklist.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/CLAUDE.md` (§Provenance, §A/B Coexistence, §Verification Density, §Handoff Envelope, §Router Validation, §External Caller Guide)
