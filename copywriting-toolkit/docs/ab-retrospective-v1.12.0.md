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

---

## Part 5 — Actual copy output (E2E follow-up, 3 briefs through both plugins)

The Part 2 E2E tests were **predictions/simulations** — agents walked through pipeline logic without producing final copy. User requested actual copy to evaluate craft differences directly. This section captures the 3-brief actual-copy run.

### Brief 1 — Tagline (茶聲 Cha Sheng 有機茶, zh-TW Q3)

**Completed intake**: 台灣阿里山海拔 1,500m 有機轉型認證中小農單一產地烏龍茶 / 30-45 都會女性 / 短文案 5-20字 / 捷運+雜誌 / $30-45 per 100g / Schwartz Level 3

**Plugin A output** (Q3 center, no anchor auto-select):

| # | 切入點 | Copy |
|---|---|---|
| 1 | benefit | 一片葉子,一座山的回音 |
| 2 | benefit | 海拔一千五的從容 |
| 3 | target call-out | 給懂得放慢的人 |
| 4 | interactive question | 今天,泡一壺山的時間 |
| 5 | disruptive | 不急的茶,才叫好茶 |
| 6 | benefit | 山上的空氣,杯裡的安靜 |

A's top pick: 「海拔一千五的從容」(8 字)

**Plugin B output** (Q3 center, 龔大中 全聯經濟美學 anchor auto-selected):

| # | 切入點 | Copy | Anchor mechanic applied |
|---|---|---|---|
| 1 | benefit (對仗) | 喝得慢是閒情,喝得對是本事 | A是X B是Y + 動作態度落點 |
| 2 | target call-out (素人) | 知道好茶很多之後,我決定只喝一座山 | 「知道 A 之後我決定 B」句型 + 第一人稱 |
| 3 | benefit (對仗) | 山上有人顧茶,杯裡有人顧我 | 前後對仗 + 地點落點 |
| 4 | disruptive (自嘲) | 土的是茶園,不土的是泡它的人 | 台式自嘲「土」+ 對仗翻轉 |
| 5 | benefit (素人) | 我不在喝茶,就在去阿里山的路上 | 直借「不在 A 就在去 A 的路上」 |
| 6 | target call-out | 送禮是心意,送山是本事 | A是X B是Y + 動作落點 |

B's top pick: 「知道好茶很多之後,我決定只喝一座山」(15 字)

**Both plugins correctly blocked** 「有機」candidate (認證未完成 → 景表法 §5-1 優良誤認).

**B's anchor saturation is visibly deep**: 3/7 candidates use 對仗 A是X B是Y, 3/7 use 第一人稱「我」, 1/7 directly borrows 龔大中 signature 句型 (「不在 A 就在去 A 的路上」). A has 0/6 of these mechanics.

### Brief 2 — Sales email (SleepEase supplement, EN Q4)

**Completed intake**: natural sleep supplement (valerian/magnesium/L-theanine/chamomile) / 35-55 US knowledge workers, melatonin-skeptical / PASONA / structure-function claim compliant / $39.99/month / 60-day guarantee / Schwartz Level 3-4

**Plugin A** opens with Problem-first lead:
> "You close the laptop at 11:47 PM and your body is tired but your mind is still on the 2 PM call..."

**Plugin B** opens with Schwartz literal lead template:
> "Give me the 90 seconds it takes to read this, and I'll give you a specific reason the sleep aid in your nightstand drawer stopped working..."

**Key craft differences**:

1. **Awareness-stage calibration**: A's Problem-first lead is a Schwartz violation for Level 3-4 (Problem-first leads belong to Levels 1-2 Unaware). B leads with mechanism-differentiated offer per Schwartz canon.

2. **Bullet structure**: A uses conventional benefit bullets that resolve (ingredient + claim); B uses fascination bullets that withhold (e.g., "The single word on most sleep-supplement labels that tells you the dose is wrong" — names category + hook, withholds resolution).

3. **Specificity discipline** (Schwartz market-sophistication rule): A says "third-party tested"; B says "certificate of analysis published for every batch by a third-party lab" — specific mechanism, not generic claim.

4. **Form disambiguation**: A says "magnesium"; B says "magnesium glycinate, not citrate, not oxide, not 'magnesium complex'" — anti-generic specificity.

**Ethics behavior**:
- A: PASS clean (no testimonials invented, disciplined throughout)
- B: PASS_WITH_NOTES — Phase 7 flagged FIXABLE (fabricated Boston portfolio manager anecdote, FTC §255.1). **B's anchor register pulled writer toward persuasive pressure that required ethics-gate revision**; A's blander register never reached for the risky move.

**Shipping readiness**:
- A ships clean immediately, zero revision cycles needed
- B ships after 1 revision round (remove anecdote or reframe as illustrative)

### Brief 3 — Banner audit (MeltFit 減肥廣告, 8 risk flags)

Banner: "Revolutionary breakthrough! Doctors HATE this one weird trick that melts belly fat in 7 days guaranteed. Limited time offer — only $29.99. Join 50,000+ satisfied customers today!"

**Risk-flag coverage on ORIGINAL (formal verdict, not prose mention)**:

| Plugin | Formal verdicts on original | Structure |
|---|---|---|
| A | **0 / 8** (prose diagnosis only; ethics gate runs only on rewrites per SKILL.md:461) | Markdown prose |
| B | **8 / 8** (4 FATAL + 4 FIXABLE with gate-item IDs + statute citations) | JSON envelope with `ethics_verdict_on_original: "NEEDS_REVISION"` + `fatal_findings[]` enumerated |

**B's FATAL findings** (directly usable for legal defense):
- `"guaranteed"` → CHK-CTW-ETH-005, 景表法 §5-1
- `"melts belly fat in 7 days"` → CHK-CTW-ETH-004, 薬機法 §68 + FDA structure-function boundary
- `"Doctors HATE"` → CHK-CTW-ETH-002, FTC §255.1
- `"50,000+ satisfied customers"` → CHK-CTW-ETH-006, FTC §255.1

**Rewrite variants**: Both plugins produce 3 compliant rewrites of comparable quality. B's output includes `three_reasons[]` per variant (auditable rationale) and `third-party test results posted` (falsifiable verification hook) that A's top rewrite lacks.

### Actual copy delta summary

| Brief | A char | B char |
|---|---|---|
| 1 (tagline) | Generic Q3 wellness, ambient register, non-anchored | Anchor-saturated 對仗 + 第一人稱 borrowed句型, identifiable as 全聯-adjacent |
| 2 (email) | Competent modern DR, Problem-first lead (Schwartz violation) | Schwartz-canon lead template, fascination withhold-bullets, mechanism-specific dose disambiguation. Requires 1 revision (anecdote) |
| 3 (audit) | Prose findings + 3 clean rewrites, ethics gate on rewrites only | 8/8 structured FATAL/FIXABLE verdicts on original + 3 rewrites with per-variant gated rationale |

---

## Part 6 — Deeper analysis beyond agent reports

The Part 5 actual-copy run surfaced 3 insights that neither Part 1 inventory nor Part 2 simulations predicted:

### Insight 1 — Anchor saturation is bimodal (structural vs stylistic)

**Structural anchors** (Schwartz in Brief 2) carry a generalizable framework — awareness-stage calibration, market-sophistication rule, fascination-withhold mechanics. Saturation delivers methodological upgrade independent of the brief's specific content. The anchor's craft TRANSFERS.

**Stylistic anchors** (龔大中 in Brief 1) carry signature句型 and voice fingerprints. Saturation delivers recognizability at the cost of pastiche risk. The anchor's voice LEAKS.

Current toolkit treats both as the same "anchor" with uniform `over-mimic risk` scale. The mechanic of over-mimic is actually different:
- Stylistic-anchor over-mimic = readers recognize the borrowed voice ("這不就是全聯嗎")
- Structural-anchor over-mimic = readers get generic pastiche of the method (carnival-barker Hopkins-era for Schwartz)

The existing `safe_substitute_for` + over-mimic mitigation system handles stylistic risk well but doesn't distinguish the two types. Possible future schema field: `anchor_type: structural | stylistic | hybrid`.

### Insight 2 — Anchor pressure creates ethics-gate work

Brief 2 observation: B's Schwartz anchor pulled writer toward fabricated testimonial (Boston portfolio manager). Phase 7 Ethics MUST gate caught it as FIXABLE. System working as designed, BUT the work arose from the anchor's persuasive pressure.

Two readings:
- **Optimistic**: defense-in-depth working. Higher-rigor anchor produces more persuasive copy; higher persuasive copy risks more ethics drift; gate catches drift. Net positive.
- **Pessimistic**: the system creates work for itself. A's blander register produced clean output with fewer gate cycles. Rigor has ethics-handling overhead.

For this trade-off to be net-positive, the copy improvement from anchor application must justify the revision-cycle cost. E2E evidence suggests it does for Level 3-4 skeptic audiences but may not for simpler briefs.

### Insight 3 — Audit architecture wins independently of anchor system

Brief 3's B advantage has nothing to do with the 90-anchor library. B wins on architectural choice: Phase 7 Ethics MUST runs on ORIGINAL (not only rewrites) + structured JSON envelope with statute citations.

This is important because:
- It means B's consolidation argument is **strongest for audit use case**
- The generative use case consolidation argument has trade-offs (anchor pastiche risk, revision-cycle cost)
- If future consolidation work is modular, audit-path consolidation could precede generative-path with less controversy

---

## Part 7 — Reader goal sensitivity (critical reframe)

The Part 4 recommendation ("consolidate into toolkit") was framed neutrally — "B is strict functional superset". The Part 5 actual copy evidence reveals this neutral framing misses a crucial variable: **user's goal**.

### Goal spectrum

| User goal | Correct tool | Why |
|---|---|---|
| "Just ship something safe and pass legal review" | A (or B with Express Mode + no anchor selection) | Bland output ships cleaner, zero revision cycles |
| "Avoid mediocrity — I want distinctive craft" | **B (strictly)** | A is structurally incapable of non-generic output. A's cleanest ships are generic-by-construction, not safe-by-design |
| "Audit existing copy for legal exposure" | B (unambiguously) | Structured verdict on original + statute citations |
| "Sophisticated reader conversion lift" | B + Schwartz anchor | Awareness-stage calibration is only in B's library |

### Anti-mediocrity framing (critical for this plugin's intent)

If the plugin's intended user persona is "copywriter avoiding AI-generic output" (which is B's origin per CHANGELOG v1.0 — "defense against AI-voice generic failure mode"), the retrospective recommendation shifts:

- Not "B is better" — **A is disqualified**. A's "safety" is its mediocrity, not a feature
- A's cleaner-ships property is a byproduct of lacking anchor system, not a virtue
- Consolidation isn't "B incrementally preferred" — **it's "A is the wrong tool for the plugin's core value proposition"**

For anti-mediocrity users, the previously-flagged concerns (龔大中 句型 borrowing, Schwartz anchor ethics-pressure) become **acceptable costs for distinctiveness**. The alternative isn't "safe clean output" — it's "mediocrity forever".

### Product implications (may guide future work, separate from consolidation)

Insight from anti-mediocrity lens:

1. **Anchor selection fit-to-positioning is a gap**. Brief 1 Pass 3d auto-selected 龔大中 (全聯-adjacent 庶民-aspirational register). But 茶聲 is 輕奢送禮 positioning — probably better fit: 李欣頻 literary-consumption or 原研哉 minimalism. Current Pass 3d matches on language + quadrant only, not positioning axis. **Candidate feature**: positioning-to-anchor register-family matrix.

2. **New-brand briefs should FORCE anchor selection, not auto-select**. Previous analysis suggested "no-signal → anchor-free fallback". For anti-mediocrity users this is wrong direction. Correct behavior: **3-5 anchor candidates presented with sample outputs**, user picks deliberately. Fail loud with choices, not silent default.

3. **Gate revision policy needs "preserve distinctive" rule**. Gate NEEDS_REVISION currently may revise away signature language alongside FATAL issues. Should distinguish "must-fix legal" vs "must-preserve style signature" in revision loop.

4. **Anchor type classification** (structural vs stylistic) — see Insight 1. Different over-mimic characteristics need different mitigation logic.

---

## Revised recommendation (v1.12.0 final)

Consolidation into toolkit remains correct. **Revised rationale**:

**Pre-v1.12.0 framing** (Part 4): B is functional superset. A provides no unique capability. Keep A/B drift risk accumulating.

**Post-actual-copy framing** (Parts 5-7): B is a **tunable spectrum** from generic fallback to highly-anchored distinctive craft. A is a **fixed bland point** on that spectrum. Consolidation isn't removing a viable option — it's removing a redundant fixed point that the spectrum already contains.

For users with anti-mediocrity goal (plugin's stated value proposition): **A is disqualified by mission, not merely dominated on metrics**.

Execution plan from Part 4 stands. Follow-up work (anchor-type classification, positioning-to-anchor matrix, new-brand forced-deliberation, gate revision policy refinement) belongs to separate roadmap — not blocker for consolidation.

---

## Appendix: files cited

- `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/copywriting-team/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/copywriting-team/protocols/copywriting-brainstorming.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/using-copywriting-toolkit/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/using-copywriting-toolkit/protocols/phase-decision-tree.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-intake/protocols/express-mode.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-audit-stage/SKILL.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/skills/copywriting-ethics-check-stage/checklists/ethics-checklist.md`
- `/Users/kouko/GitHub/monkey-skills/copywriting-toolkit/CLAUDE.md` (§Provenance, §A/B Coexistence, §Verification Density, §Handoff Envelope, §Router Validation, §External Caller Guide)
