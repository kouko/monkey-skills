# Voice Anchor Expansion — Implementation Plan

**Branch**: `research/copywriting-voice-anchor-expansion` (research) → branch from `main` for each implementation PR
**Target delivery**: 3 PRs (per user decision 2026-04-21)
**Plan locked**: 2026-04-21 after 4 research waves + architecture deliberation

## Executive summary

Expand `copywriting-toolkit` voice anchor library from ~19 entries (6 existing masters + 13 thin brand-era) to ~90 entries covering EN / JP / zh-TW across 4 quadrants × 3 landmark positions (center / extreme / toward-adjacent-Q). Goal: give Phase 6 Pass 3 register-signal access with deep LLM corpus trigger (via literary / screenwriter / brand-as-genre anchors) without losing craft-depth mitigation for canonical 6 masters.

Architecture: **Option B3** — existing Tier 1 byte-identical lineage files untouched; 14 new toolkit-originated per-quadrant + meta + axis-extreme files (flat, no subdirectory per Anthropic skill authoring).

## Context

- **6 research waves completed** on branch `research/copywriting-voice-anchor-expansion`:
  - Brand-era + copywriter (EN / JP / ZH / KR+EU+other) — 4 agents
  - Layer-0 literary + screen (JP/ZH + EN/KR) — 2 agents
  - Type 5 deferred candidate verification (國井美果 / SHIRO / KC Tsang / Dan Kennedy / Bill Jayme) — 1 agent
  - Gap filling (JP Q1/Q4 + zh-TW Q1/Q3 + EN Q2/Q3 extreme) — 3 agents
- **6 primary-source verified lineages** documented (李欣頻×4 / 糸井×1 / 葉明桂×1 / Ogilvy→Strunk&White / Orwell canon / 박웅현 for future).
- **Drift corrections identified** (to land in PR 2):
  - Z5: 多喝水 ≠ 吳念真（奧美 in-house）
  - Z6: 孫大偉 agency = 台灣奧美 / 偉太（非智威湯遜）
  - Z7: 長榮〈I SEE YOU〉旁白 = 金城武（非吳念真）
  - Z8: 全聯經濟美學 creative lead = 龔大中（非林敬凱；邱彥翔 為演員）
  - Z9 (new): HK CD 名字 = KC Tsang（非 Calvin Choy）; agency = BBDO（非 JWT）
  - Z10 (new): 全聯 TV-era 2006-2014 是 **Q3-center（格言）**，非 Q3-extreme
  - Z11 (new): 意識形態廣告 = 許舜英 **+ 鄭松茂** 共同創辦

## Architecture decisions (all locked)

1. **Option B3** — existing Tier 1 deep-dive files untouched; new per-quadrant + meta + axis-extreme = 14 new files
2. **Flat layout** — all new files directly under `standards/` (Anthropic one-level-deep)
3. **Cross-language fallback (JP → zh-TW STRONG)** — independent load of BOTH files (zh-qN + jp-qN) when applicable
4. **Axis extremes** — independent cross-language single file `axis-extreme-anchors.md`; MVP placeholder, V2 research populates
5. **Drift corrections bundled into PR 2** (per user decision)
6. **3 PRs** (per user decision)

## File manifest

### Existing files (Tier 1, **UNTOUCHED except for drift sync in PR 2**)

```
copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/
├── voice-and-tone.md                    # no change
├── jp-copy-craft-lineage.md             # no change (craft gate for 糸井/岩崎/眞木)
└── zh-copy-craft-lineage.md             # PR 2 syncs Z5-Z8 drift + Z9 + Z11 from upstream

copywriting-toolkit/skills/copywriting-voice-quadrant-stage/standards/
└── voice-quadrant-positioning.md        # PR 3 optional: add position field reference
```

### New files (14 toolkit-originated)

```
copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/
├── voice-anchor-meta.md                 # NEW ~400 lines (PR 1)
├── jp-q1-anchors.md                     # NEW ~200 lines (PR 2)
├── jp-q2-anchors.md                     # NEW ~250 lines (PR 2)
├── jp-q3-anchors.md                     # NEW ~300 lines (PR 2)
├── jp-q4-anchors.md                     # NEW ~200 lines (PR 2)
├── zh-q1-anchors.md                     # NEW ~150 lines (PR 2)
├── zh-q2-anchors.md                     # NEW ~300 lines (PR 2)
├── zh-q3-anchors.md                     # NEW ~300 lines (PR 2)
├── zh-q4-anchors.md                     # NEW ~150 lines (PR 2)
├── en-q1-anchors.md                     # NEW ~300 lines (PR 3)
├── en-q2-anchors.md                     # NEW ~300 lines (PR 3)
├── en-q3-anchors.md                     # NEW ~350 lines (PR 3)
├── en-q4-anchors.md                     # NEW ~200 lines (PR 3)
└── axis-extreme-anchors.md              # NEW ~150 lines placeholder (PR 1)
```

### SKILL.md / rubric updates (PR 3)

```
copywriting-voice-tone-stage/SKILL.md            # Pass 3 load logic update
copywriting-voice-quadrant-stage/SKILL.md        # optional: position field
copywriting-voice-tone-stage/rubrics/voice-consistency-gate.md  # over-mimic adherence check
```

### Upstream domain-teams (drift corrections)

```
domain-teams/skills/copywriting-team/skills/copywriting-voice-tone-stage/standards/
└── zh-copy-craft-lineage.md             # PR 2 prerequisite — Z5-Z11 drift corrections
```

## PR 1 — Foundation (scaffold + meta + axis-extreme placeholder)

**Purpose**: establish schema / rubric / registry in meta; create 13 file skeletons for PR 2/3 to populate; stub axis-extreme. Zero upstream blocker.

**Branch**: `feat/copywriting-toolkit-voice-anchor-foundation-v1.4.0`

### Commits

1. **`feat(copywriting-toolkit): scaffold voice-anchor-meta.md`**
   - Schema definition (anchor entry structure)
   - 4-condition selection rubric
   - Cross-cultural unified label rubric (19 labels × 4 cultures)
   - Over-mimic mitigation registry (15+ entries from research)
   - Verified lineage map (6 primary-source citations)
   - Cross-reference-valid-for registry (JP→zh-TW STRONG)
   - Corrections catalog (Z5-Z11 pointer — actual corrections land in PR 2)

2. **`feat(copywriting-toolkit): scaffold 13 per-quadrant + axis-extreme anchor skeletons`**
   - Create 12 `{lang}-q{N}-anchors.md` files with header + empty sections
   - Each header: `## Quadrant mapping / ## Canonical landmarks / ## Anchor entries / ## Cross-references`
   - Create `axis-extreme-anchors.md` with 4 axis stubs + "research pending" note

3. **`chore(copywriting-toolkit): version bump v1.3.0 → v1.4.0 + CHANGELOG`**
   - `plugin.json` version bump
   - CHANGELOG entry noting foundation-only landing; content lands in v1.4.1 / v1.4.2

### Verification

```bash
# Structure check
ls copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/ | wc -l
# Expected: 3 existing + 14 new = 17 files

# Meta file completeness
grep -E "^## (Schema|Rubric|Mitigation|Lineage|Cross-reference|Corrections)" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/voice-anchor-meta.md
# Expected: 6 section headers

# No broken cross-refs yet (empty skeletons are expected)
```

### Rollback

Revert single PR — no downstream consumer yet.

## PR 2 — JP + zh-TW content + drift corrections

**Purpose**: populate 8 files (JP Q1-Q4 + zh-TW Q1-Q4); land Z5-Z11 drift corrections via domain-teams upstream + toolkit sync.

**Branch**: `feat/copywriting-toolkit-voice-anchor-jp-zh-v1.4.1`

**Prerequisite**: **upstream domain-teams PR must merge FIRST** (drift Z5-Z11 in `domain-teams/skills/copywriting-team/skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md`)

### Upstream PR (domain-teams, prerequisite)

**Branch**: `fix/copywriting-team-zh-lineage-drift-v4.17.0`

Commit: `fix(copywriting-team): zh-copy-craft-lineage drift corrections Z5-Z11`
- Z5: 多喝水 attribution (奧美 in-house, not 吳念真)
- Z6: 孫大偉 agency 台灣奧美 / 偉太
- Z7: 〈I SEE YOU〉旁白 = 金城武
- Z8: 全聯 creative lead = 龔大中
- Z9: HK CD = KC Tsang / BBDO (not Calvin Choy / JWT)
- Z10: 全聯 TV-era 2006-2014 = Q3-center (not Q3-extreme)
- Z11: 意識形態廣告 = 許舜英 + 鄭松茂 co-founder

Merge upstream first. Wait 30-60s (per `feedback_stacked_pr_race`). Then proceed to toolkit PR.

### Toolkit PR commits

1. **`chore(copywriting-toolkit): sync zh-copy-craft-lineage from domain-teams upstream`**
   - `cp domain-teams/.../zh-copy-craft-lineage.md copywriting-toolkit/.../zh-copy-craft-lineage.md`
   - Verify `diff -q` empty

2. **`feat(copywriting-toolkit): populate jp-q1/q2 anchor inventory`**
   - jp-q1-anchors.md: 朝日天声人語 / 日経ビジネス / 東洋経済 / 夏目漱石 / Reuters JP / Bloomberg JP (with Reuters/Bloomberg caveat)
   - jp-q2-anchors.md: 仲畑貴志 / 秋山晶 / 寺山修司 / 谷崎潤一郎《陰翳礼讃》/ 川端康成 / MUJI 田中一光 + 原研哉 / JR東海 そうだ京都 / 糸井 Q2-edge pointer / 岩崎 pointer / 眞木 pointer

3. **`feat(copywriting-toolkit): populate jp-q3/q4 anchor inventory`**
   - jp-q3-anchors.md: 向田邦子 / 谷川俊太郎 / 宮沢賢治 / 吉本ばなな / 坂元裕二 / 梅田悟司 + ジョージア / ほぼ日 / 佐々木宏 白戸家 / 澤本嘉光 / 糸井重里 pointer / 岩崎 pointer
   - jp-q4-anchors.md: クックパッド / Kurashicom (Q4 subset only) / ジャパネットたかた 高田明 (1990-2015 founder only) / 通販生活 / UNIQLO 2006- / ワークマン SNS era

4. **`feat(copywriting-toolkit): populate zh-q1/q2 anchor inventory`**
   - zh-q1-anchors.md: 天下雜誌 / 報導者 center register / 研之有物
   - zh-q2-anchors.md: 朱家鼎 KC Tsang Q2-extreme HK + 鐵達時 / 王家衛 monologue + mitigation / 張愛玲 / 白先勇 / 朱天文 / 錢鍾書 / 誠品 / 中興百貨 / 左岸咖啡館 / 許舜英 pointer / 李欣頻 pointer / 葉明桂 pointer

5. **`feat(copywriting-toolkit): populate zh-q3/q4 anchor inventory (includes 全聯 Q3-center re-classification)`**
   - zh-q3-anchors.md: 全聯 TV-era 2006-2014 **(Q3-center, 格言)** / 吳念真 保力達B / 朱天文 / 黃春明 / 三毛 / 故宮「朕知道了」/ 台灣吧 / 胡湘雲 大眾銀行 / 龔大中 / 杜蕾斯 環時 (CN) / 金鵬遠 / 向田邦子 JP-ref / 糸井 JP-ref
   - zh-q4-anchors.md: PChome 商品文 / MOMO 購物 / Kurashicom JP-ref (Q4 subset)

6. **`chore(copywriting-toolkit): voice-anchor-meta updates — Z5-Z11 corrections + cross-ref registry`**
   - Update meta.md §Corrections with actual correction details (not just pointer)
   - Populate cross-reference-valid-for entries for JP→zh-TW anchors

7. **`chore(copywriting-toolkit): version bump v1.4.0 → v1.4.1 + CHANGELOG`**

### Verification

```bash
# zh-lineage sync verified byte-identical
diff -q domain-teams/skills/copywriting-team/skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md \
        copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md
# Expected: empty output

# All 8 JP + zh anchor files populated (no empty sections)
for f in jp-q{1,2,3,4}-anchors.md zh-q{1,2,3,4}-anchors.md; do
  grep -L "TBD\|TODO\|placeholder" "copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/$f"
done
# Expected: all 8 files listed (none have TBD markers)

# 全聯 re-classification
grep -A 3 "全聯.*Q3-center\|Q3-center.*全聯" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/zh-q3-anchors.md
# Expected: 全聯 TV-era 2006-2014 entry under Q3-center section (NOT extreme)

# Meta corrections populated
grep -c "^### Z[5-9]\|^### Z1[01]" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/voice-anchor-meta.md
# Expected: ≥7 (Z5 through Z11)
```

### Rollback

1. Revert toolkit PR (13 commits)
2. Revert domain-teams upstream PR (if needed — drift corrections are always safe to keep; revert only on catastrophic)

### Risks

- **Stacked PR race**: upstream merge → toolkit PR retarget. Follow `feedback_stacked_pr_race`: wait 30-60s or explicit retarget
- **Byte-identical drift during sync**: `cp` must be atomic; verify `diff -q` is empty before commit
- **Z10 re-classification impact**: 全聯 is already referenced in `voice-quadrant-positioning.md` as Q3. No change there needed (Q3 is correct; only center/extreme layer is new)

## PR 3 — EN content + SKILL.md pipeline integration

**Purpose**: populate 4 EN quadrant files; update Phase 6 Pass 3 load logic to consume new per-quadrant architecture; update voice-consistency gate rubric.

**Branch**: `feat/copywriting-toolkit-voice-anchor-en-pipeline-v1.4.2`

### Commits

1. **`feat(copywriting-toolkit): populate en-q1/q2 anchor inventory`**
   - en-q1-anchors.md: Ogilvy Rolls-Royce / Hathaway Man / Economist (Abbott AMV BBDO) / Hopkins Pepsodent / Bernbach VW+Avis / BMW Ultimate / Stratechery / Basecamp / Hemingway iceberg / Carver / Didion / Amy Hempel / E.B. White / Orwell / McPhee
   - en-q2-anchors.md: Apple Think Different / Nike "Just Do It" (center) + "Dream Crazy/Crazier" (extreme) / Patek Philippe Generations / Absolut print campaign / Oatly activist mode / Extinction Rebellion Declaration (civic-only mitigation) / Patagonia "Don't Buy This Jacket" / Toni Morrison / James Baldwin / Kazuo Ishiguro

2. **`feat(copywriting-toolkit): populate en-q3/q4 anchor inventory`**
   - en-q3-anchors.md: MailChimp / Innocent Drinks / Oatly center / Liquid Death / Steak-umm Allebach / Duolingo Parvez 2021-22 window / Phoebe Waller-Bridge Fleabag / Nora Ephron / George Saunders / Taika Waititi / Greta Gerwig / Chekhov / Raymond Carver Q3 edge / Gary Halbert peer-edge
   - en-q4-anchors.md: Amazon product copy / REI expert advice / Basecamp Rework / Gary Halbert DR / Bill Jayme direct-mail / Raymond Chandler / Dashiell Hammett / IKEA assembly voice / Morning Brew / Dollar Shave Club launch video

3. **`refactor(copywriting-toolkit): Phase 6 Pass 3 load logic — craft-gate vs register-signal vs axis-extreme`**
   - Update `copywriting-voice-tone-stage/SKILL.md` §When lineage craft applies + §Pass 3 activation guard
   - New branching:
     ```
     # Tier 1 — craft gate
     if voice_reference ∈ {糸井,岩崎,眞木,谷山} → load jp-copy-craft-lineage.md
     if voice_reference ∈ {許舜英,李欣頻,葉明桂} → load zh-copy-craft-lineage.md
     
     # Tier 2 — register signal (new)
     elif voice_reference ∉ craft-gate masters:
       load voice-anchor-meta.md
       load {output_language}-q{voice_quadrant.primary}-anchors.md
       if cross-reference-valid-for[output_language] STRONG:
         load jp-q{...}-anchors.md (JP→zh-TW case)
     
     # Tier 3 — axis extreme
     if voice_quadrant.position matches "axis-*":
       load axis-extreme-anchors.md (V2: expand when research populates)
     ```

4. **`refactor(copywriting-toolkit): voice-quadrant-positioning — add optional position field to envelope`**
   - Extend `voice_quadrant` object schema with optional `position: "center" | "extreme" | "toward-Qn" | "axis-{authority,affinity,reason,emotion}"` field
   - Update Preconditions + I/O Contract sections
   - Document fallback behavior when position missing (default to "center")

5. **`refactor(copywriting-toolkit): voice-consistency-gate — over-mimic adherence dimension`**
   - Update `rubrics/voice-consistency-gate.md` to check:
     - Primer register's grammar features preserved
     - Over-mimic tropes NOT leaked (per mitigation clauses in meta.md)
   - Add new gate dimension with SHOULD-level priority

6. **`chore(copywriting-toolkit): version bump v1.4.1 → v1.4.2 + CHANGELOG`**

### Verification

```bash
# All EN files populated
for f in en-q{1,2,3,4}-anchors.md; do
  grep -L "TBD\|TODO\|placeholder" "copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/$f"
done
# Expected: 4 files listed

# Pass 3 load logic updated
grep -E "register signal|register-signal|Tier 2" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/SKILL.md
# Expected: match

# Position field documented
grep "position.*center\|position.*extreme\|position.*axis" \
  copywriting-toolkit/skills/copywriting-voice-quadrant-stage/SKILL.md
# Expected: match

# Gate rubric over-mimic check added
grep -E "over-mimic|mitigation" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/rubrics/voice-consistency-gate.md
# Expected: match

# End-to-end smoke test (manual):
#   brief with voice_reference = "Didion" + output_language = "en" → should resolve to Q2 + load en-q2-anchors.md
#   brief with voice_reference = "糸井" + output_language = "zh-TW" → should resolve to Q3 + load zh-q3-anchors.md + jp-q3-anchors.md (cross-ref)
#   brief with voice_reference = "糸井" + output_language = "ja" → should load jp-copy-craft-lineage.md (existing craft gate)
```

### Rollback

Revert toolkit PR. Pipeline falls back to pre-PR-3 load logic (will not find new anchor files, but craft-gate still works for 6 canonical masters).

## Content sources per file

Each per-quadrant file draws from specific research docs on branch `research/copywriting-voice-anchor-expansion`:

| Target file | Source docs |
|---|---|
| jp-q1-anchors | voice-anchor-gap-research.md §JP Q1 |
| jp-q2-anchors | voice-anchor-research.md §JP + voice-anchor-layer-0-research.md §JP literary |
| jp-q3-anchors | voice-anchor-research.md §JP + voice-anchor-layer-0-research.md §JP literary + voice-anchor-gap-research.md |
| jp-q4-anchors | voice-anchor-gap-research.md §JP Q4 |
| zh-q1-anchors | voice-anchor-gap-research.md §zh-TW Q1 |
| zh-q2-anchors | voice-anchor-research.md §ZH + voice-anchor-layer-0-research.md §ZH literary |
| zh-q3-anchors | voice-anchor-research.md §ZH + voice-anchor-gap-research.md §zh-TW Q3 + Z10 re-class |
| zh-q4-anchors | voice-anchor-research.md §ZH (thin; mostly JP cross-ref) |
| en-q1-anchors | voice-anchor-research.md §EN + voice-anchor-layer-0-research.md §EN literary |
| en-q2-anchors | voice-anchor-research.md §EN + voice-anchor-gap-research.md §EN Q2 extreme |
| en-q3-anchors | voice-anchor-research.md §EN + voice-anchor-layer-0-research.md §EN literary + voice-anchor-gap-research.md §EN Q3 extreme |
| en-q4-anchors | voice-anchor-research.md §EN + voice-anchor-archived-references.md §Type 5 PROMOTE (Bill Jayme) |
| voice-anchor-meta | voice-anchor-layer-0-research.md (lineage map + mitigation registry + rubric) + voice-anchor-gap-research.md (corrections) |
| axis-extreme-anchors | placeholder (V2 research) |

**Archived anchors** (NOT in inventory): all entries in `voice-anchor-archived-references.md` stay archived.

## Entry template (for populating quadrant files)

Each anchor entry in a per-quadrant file follows:

```markdown
### {anchor name} ({language/culture} | {quadrant} {position})

- **Era**: {years}
- **Agency / creator**: {specific attribution}
- **Primary sources**: {2-3 verified refs with URL/ISBN}
- **Representative lines** (verbatim, not paraphrase):
  - {line 1}
  - {line 2}
  - {line 3}
- **Voice signature**:
  - Dimension 1: {characteristic}
  - Dimension 2: {characteristic}
  - Dimension 3: {characteristic}
  - Dimension 4: {characteristic}
- **LLM corpus depth**: DEEP/MEDIUM-DEEP/MEDIUM/THIN — {rationale}
- **Over-mimic risk**: LOW/MEDIUM/HIGH
  - Mitigation (if HIGH): "{≤15-word clause}"
- **Cross-reference-valid-for**:
  - {lang}: STRONG/MEDIUM/WEAK
- **Cross-cultural equivalents**: {parallel anchors in other cultures}
- **Trigger slug**: `{culture}-{name-kebab-case}-{style-label}`
```

## Branch strategy

```
main
├── research/copywriting-voice-anchor-expansion    # research docs (stays unmerged until needed)
├── fix/copywriting-team-zh-lineage-drift-v4.17.0  # upstream domain-teams (PR 2 prereq)
├── feat/copywriting-toolkit-voice-anchor-foundation-v1.4.0    # PR 1
├── feat/copywriting-toolkit-voice-anchor-jp-zh-v1.4.1         # PR 2
└── feat/copywriting-toolkit-voice-anchor-en-pipeline-v1.4.2   # PR 3
```

**Merge order**: upstream fix → PR 1 → PR 2 → PR 3. PR 1 has zero dependency; PR 2 depends on upstream fix + PR 1; PR 3 depends on PR 2.

## Cross-cutting concerns

### Tier 1 byte-identical discipline

Per `copywriting-toolkit/CLAUDE.md §Provenance & Divergence`:

- **Existing jp-copy-craft-lineage.md**: NO changes in any PR (stays byte-identical with upstream)
- **Existing zh-copy-craft-lineage.md**: PR 2 only changes = upstream drift sync (Z5-Z11); byte-identical after sync
- **New toolkit-originated files (14 total)**: follow zh-copy-craft-lineage.md v1.0.1 precedent — "immutable canon without upstream diff target"; no DIVERGED header required (they are NOT derived from upstream)

### CC CI type whitelist

Per `feedback_cc_type_whitelist`: only {refactor, feat, fix, chore, docs} allowed. All commits above verified compliant. No `test:` / `ci:` prefixes — any test/eval work bundles under relevant `feat`/`chore`.

### Schema governance

`voice_quadrant` object gains optional `position` field in PR 3. Breaking change risk: downstream skills already treat `voice_quadrant.primary` as required (Q1-Q4 enum). Adding optional `position` is additive — no break. Callers without position field fall back to "center" default.

### Version bumps

- v1.3.0 (current) → v1.4.0 (PR 1 foundation) → v1.4.1 (PR 2 JP/zh) → v1.4.2 (PR 3 EN/pipeline)
- plugin.json version bump in each PR's final `chore:` commit

## Token cost analysis

Token estimates based on ~12 tokens/line for markdown with entry metadata. All figures are per-pipeline-run unless stated.

### Baseline (current pipeline, pre-implementation)

| Phase | Always-loaded | Conditional (Pass 3) | Total |
|---|---|---|---|
| Phase 5 | voice-quadrant-positioning.md (~8K) + SKILL.md (~3K) | — | ~11K |
| Phase 6 | voice-and-tone.md (~4K) + SKILL.md (~5K) | jp or zh lineage (0-5.3K, 20% trigger) | ~9-14K |
| **Total** | — | — | **~20-25K** |

### New architecture (PR 1+2+3 merged)

**File size estimates**:
- `voice-anchor-meta.md`: ~400 lines / ~5K tokens
- `{lang}-q{N}-anchors.md` (12 files): avg ~250 lines / ~3K tokens each
- `axis-extreme-anchors.md` (MVP stub): ~150 lines / ~2K tokens
- Existing `jp-copy-craft-lineage.md` / `zh-copy-craft-lineage.md`: unchanged

**Pass 3 path weighted cost** (with estimated brief-type distribution):

| Path | Trigger rate | Baseline + meta | Pass 3 conditional | Per-run total | vs baseline |
|---|---|---|---|---|---|
| No Pass 3 (short-form, no voice_reference) | ~10% | 20K + 5K meta = 25K | 0 | ~25K | +5K (meta) |
| Craft gate (existing 6 masters) | ~20% | 25K | +3.3-5.3K lineage | ~28-30K | +5-8K |
| Register signal (new, no cross-lang) | ~40% | 25K | +3K quadrant | ~28K | +3-8K (new capability) |
| Register signal (JP→zh-TW STRONG) | ~20% | 25K | +6K (zh-qN + jp-qN) | ~31K | +6-11K |
| Axis extreme (MVP placeholder) | ~5% | 25K | +2K | ~27K | +2-7K |
| Axis extreme (V2 populated) | future ~5% | 25K | +5K | ~30K | +5-10K |

**Weighted per-run average**: `0.1×25 + 0.2×29 + 0.4×28 + 0.2×31 + 0.1×27 = ~28.7K tokens`

**Delta vs baseline**: **+3-4K tokens per run (+15-20% per pipeline average)**

### Architecture comparison (why Option B3 is the most token-efficient path given scope)

| Architecture | Pass 3 peak load | Per-run weighted avg | Notes |
|---|---|---|---|
| Current (6 masters only, no expansion) | 5.3K | ~22K | No register-signal capability |
| **Option B3 (this plan)** | **6K** | **~28.7K** | Per-quadrant ~3K each |
| Option B (per-language monolithic) | 13K | ~35K | Per-lang file ~10-13K |
| Option A (single voice-anchor-taxonomy.md) | 50K+ | OOM risk | Not viable |

**Key win**: Option B3 saves **~7-10K tokens per Pass 3 trigger** vs Option B because per-quadrant files are 3-4× smaller than per-language monolithic. This saving compounds across `copywriter` + `copywriter-evaluator` agent invocations per pipeline.

### Per-agent multiplier (pipeline with multiple voice-touching agents)

Each subagent invocation independently loads the standards it needs — context is not shared across agents. Worst-case short-form pipeline run with voice-touching phases:

| Phase | Agent | Voice-standards delta |
|---|---|---|
| Phase 4 draft | copywriter | +3K (voice hint for drafting) |
| Phase 5 quadrant | copywriter | +11K (existing, unchanged) |
| Phase 6 Pass 1-3 | copywriter + evaluator | +10K avg (meta + quadrant anchor + gate rubric) |
| Phase 8 form check | evaluator | +3K (if over-mimic check subset loaded) |
| **Voice-related total per pipeline** | — | **~27K per full run** |

Baseline equivalent: ~15K (Phase 5 q-positioning 11K + Phase 6 lineage conditional 4K if triggered).

**Delta per voice-intensive pipeline**: **+12K (~+80%)** in worst-case. Typical briefs cluster around +3-6K per run.

### Cost breakdown by category

1. **Always-load overhead (`voice-anchor-meta.md` ~5K)**: every run pays, regardless of Pass 3
2. **Per-trigger conditional load (3-6K)**: varies by Pass 3 branch (craft-gate / register-signal / axis-extreme)
3. **Per-agent multiplier**: each standards-consuming agent loads its own copy of relevant standards

### Optimization options (for v1.5 if usage shows pain)

| Optimization | Savings | Cost | When to trigger |
|---|---|---|---|
| **Meta split**: core (~2K always) + rich (~3K conditional) | -3K on no-Pass-3 runs (~10% of briefs) | Load logic complexity | If real-usage avg exceeds 40K voice-stack tokens |
| **Progressive disclosure within quadrant file**: landmark sections lazy-loaded by `voice_quadrant.position` | -1-2K per load | Requires precise position field | v2 pipeline upgrade |
| **Lazy cross-ref registry**: only load when applicable | -500 tokens/run | Moderate | v1.5 |
| **Meta.md only on Pass 3 trigger**: remove always-load | -5K on no-Pass-3 runs | Phase 7/8 may need meta subset | v1.5 after usage audit |
| **YAML frontmatter tighter template** | -20-30% per file | Readability loss | Not recommended |
| **Split quadrant into center/extreme files** | -1-2K per load | 12 → 24 files; too fragmented | Not recommended |

### Trigger criteria for v1.5 optimization

Activate optimization work if any of:

- Real-usage pipeline average exceeds **40K voice-stack tokens** across representative briefs
- User feedback cites voice-stack loading as bottleneck (perceived latency > 15s for Pass 3 skills)
- Cost tracking shows voice-stack token cost > 60% of full pipeline token cost

Below these thresholds, Option B3 baseline is acceptable.

### Honest trade-off summary

**Cost**: +3-4K tokens per run weighted average (+15-20%)

**In exchange**:
- 60% of briefs gain register-signal capability that didn't exist
- Pass 3 load per trigger ~7-10K smaller than Option B alternative
- Tier 1 byte-identical policy preserved (zero drift risk)
- Backward compatible for existing 6-master craft-gate flow (~20% of briefs unchanged)

No architecture achieves lower token cost while delivering the register-signal capability. Cheaper architectures (skip expansion / skip Layer-0) lose voice precision; more expensive architectures (Option B monolithic / single taxonomy file) burn 2-3× more per trigger.

**Recommendation**: ship as planned; measure actual pipeline token usage for 2 weeks post-merge; revisit optimization only if v1.5 trigger criteria met.

## Risks

1. **Upstream sync conflict**: if domain-teams zh-copy-craft-lineage.md receives concurrent edits between upstream merge and toolkit sync, diff may not match. Mitigation: keep upstream PR small (drift-only), merge, immediately sync.
2. **Anchor content drift during population**: when translating research findings into per-quadrant entries, factual slippage possible. Mitigation: entry template enforces verbatim quotes + primary source URL; evaluator agent review before commit.
3. **Pass 3 load logic regression**: new branching may break existing JP/ZH 6-master flow. Mitigation: Tier-1 craft-gate branch preserves existing behavior exactly; register-signal branch only activates for non-craft-gate voice_reference values.
4. **File discovery inflation**: 14 new files in flat `standards/` directory may overwhelm. Mitigation: naming convention (`{lang}-q{N}-anchors.md`) makes purpose obvious at ls time.
5. **Axis-extreme V2 deferral risk**: placeholder file may stay empty forever. Mitigation: file has `last-reviewed` date; planning-team can schedule V2 research when actual brief triggers axis-extreme need.
6. **zh-HK coverage thin**: only 朱家鼎 鐵達時 + 王家衛 as HK anchors. Acceptable per scope decision (zh-HK is reference pool for zh-TW, not output target).

## Out of scope

- Korean (KR) anchor inventory — archived per decision 2026-04-21
- Visual-dominant skip-list promotion to anchor — archived permanently
- Schema migration to continuous coordinates `(x, y)` — out of scope (discrete quadrants + landmarks sufficient)
- Tier 1 discipline exception requests — any edit to existing jp/zh-copy-craft-lineage.md beyond Z5-Z11 drift requires separate proposal
- Cross-culture bidirectional registry — only JP→zh-TW STRONG is implemented; zh-TW→JP, en→zh-TW etc. deferred to V2

## Open dependencies

1. Upstream domain-teams PR `fix/copywriting-team-zh-lineage-drift-v4.17.0` must merge before PR 2
2. `copywriting-team` must have v4.17.0 or equivalent version to support Z5-Z11 corrections in toolkit cp
3. Review bandwidth for 3 sequential PRs (~200-400 LOC each in PR 2/3)

## Verification — post-merge smoke tests

After PR 3 merges:

1. **Craft-gate integrity** (existing 6 masters):
   ```
   brief: {voice_reference: "糸井重里", output_language: "ja", voice_quadrant: {primary: "Q3"}}
   expected: Pass 3 loads jp-copy-craft-lineage.md ONLY (no per-quadrant load)
   ```

2. **Register-signal new path**:
   ```
   brief: {voice_reference: "Didion", output_language: "en", voice_quadrant: {primary: "Q2"}}
   expected: Pass 3 loads voice-anchor-meta.md + en-q2-anchors.md
   ```

3. **Cross-language STRONG fallback (JP → zh-TW)**:
   ```
   brief: {voice_reference: "谷崎陰翳礼讃", output_language: "zh-TW", voice_quadrant: {primary: "Q2"}}
   expected: Pass 3 loads voice-anchor-meta.md + zh-q2-anchors.md + jp-q2-anchors.md
   ```

4. **Corrections propagated**:
   ```
   query: zh-q3 anchors.md
   expected: 全聯 TV-era 2006-2014 classified under Q3-center (格言), NOT extreme
   ```

5. **Over-mimic gate triggered**:
   ```
   draft using {voice_reference: "Hemingway"} with he-said/she-said robotic chains
   expected: voice-consistency-gate FAIL with "over-mimic: dialogue-tag chains > 2 per 50 words"
   ```

## Checklist before starting implementation

- [ ] Research docs reviewed (4 files on `research/copywriting-voice-anchor-expansion`)
- [ ] Architecture 4 decisions confirmed (Option B3 / flat / independent load / axis-extreme single file)
- [ ] Upstream domain-teams branch permission confirmed
- [ ] Review bandwidth secured for 3 sequential PRs
- [ ] plugin.json current version confirmed (v1.3.0 assumed in this plan)
- [ ] Entry template reviewed by reviewer
- [ ] Smoke test scenarios reviewed

## Next action

Begin PR 1 scaffold. Start with `voice-anchor-meta.md` content pass (schema + rubric + registries), then create 13 file skeletons.
