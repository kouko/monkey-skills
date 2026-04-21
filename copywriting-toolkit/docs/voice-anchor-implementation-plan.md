# Voice Anchor Expansion — Implementation Plan

**Branch**: `research/copywriting-voice-anchor-expansion` (research) → branches from `main` for each implementation PR
**Target delivery**: 3 PRs (per user decision 2026-04-21)
**Plan locked**: 2026-04-21 after 4 research waves + architecture deliberation + token-cost optimization

## Executive summary

Expand `copywriting-toolkit` voice anchor library from ~19 entries (6 existing masters + 13 thin brand-era) to ~90 entries covering EN / JP / zh-TW across 4 quadrants × 3 landmark positions (center / extreme / toward-adjacent-Q). Phase 6 Pass 3 gains register-signal access with deep LLM corpus trigger (literary / screenwriter / brand-as-genre anchors) without losing craft-depth mitigation for 6 canonical masters.

**Architecture**: Option B3 + 4 token optimizations — existing Tier 1 untouched; **15** new toolkit-originated files (flat, no subdirectory per Anthropic skill authoring); lazy-load everywhere via meta split + landmark-targeted quadrant sections + cross-ref lazy + Pass-3-gated meta load.

**Token outcome**: weighted per-run cost ≈ baseline (+4% worst case, often cheaper than baseline on no-voice runs).

## Context

- **6 research waves completed** on branch `research/copywriting-voice-anchor-expansion`:
  - Brand-era + copywriter (EN / JP / ZH / KR+EU+other) — 4 agents
  - Layer-0 literary + screen (JP/ZH + EN/KR) — 2 agents
  - Type 5 deferred verification (國井美果 / SHIRO / KC Tsang / Dan Kennedy / Bill Jayme) — 1 agent
  - Gap filling (JP Q1/Q4 + zh-TW Q1/Q3 + EN Q2/Q3 extreme) — 3 agents
- **6 primary-source verified lineages** documented
- **Drift corrections** (to land in PR 2 via upstream):
  - Z5: 多喝水 ≠ 吳念真（奧美 in-house）
  - Z6: 孫大偉 agency = 台灣奧美 / 偉太
  - Z7: 長榮〈I SEE YOU〉旁白 = 金城武
  - Z8: 全聯經濟美學 creative lead = 龔大中
  - Z9: HK CD 名字 = KC Tsang（非 Calvin Choy）; agency = BBDO（非 JWT）
  - Z10: 全聯 TV-era 2006-2014 = **Q3-center（格言）**，非 Q3-extreme
  - Z11: 意識形態廣告 = 許舜英 **+ 鄭松茂** 共同創辦

## Architecture decisions (all 8 locked)

1. **Option B3** — existing Tier 1 deep-dive untouched; new per-quadrant + meta + axis-extreme = 15 new files
2. **Flat layout** — all new files directly under `standards/` (Anthropic one-level-deep)
3. **Cross-language fallback (JP→zh-TW STRONG)** — independent load of both files
4. **Axis extremes** — single cross-language `axis-extreme-anchors.md`; MVP placeholder, V2 populates
5. **Meta split** (new) — `meta-core.md` (~2K, essential) + `meta-detail.md` (~3K, rich) for lazy-load
6. **Landmark sections within quadrant files** (new) — structural: explicit `## Landmark: {position}` markers; load-logic: Pass 3 reads only target section
7. **Lazy cross-ref registry** (new) — cross-reference-valid-for lives in meta-detail, loaded only on cross-lang trigger
8. **Meta load is Pass-3-conditional** (new, pending Phase 7/8 audit in PR 3) — no always-load overhead
9. **Drift corrections bundled into PR 2**
10. **3 PRs** per user decision

## File manifest

### Existing files (Tier 1, UNTOUCHED except drift sync in PR 2)

```
copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/
├── voice-and-tone.md                    # no change (always-load)
├── jp-copy-craft-lineage.md             # no change — craft gate for 糸井/岩崎/眞木/谷山
└── zh-copy-craft-lineage.md             # PR 2 syncs Z5-Z11 from upstream

copywriting-toolkit/skills/copywriting-voice-quadrant-stage/standards/
└── voice-quadrant-positioning.md        # PR 3 optional: position field reference
```

### New files (15 toolkit-originated)

```
copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/
├── voice-anchor-meta-core.md            # NEW ~200 lines (PR 1) — schema + rubric + over-mimic registry
├── voice-anchor-meta-detail.md          # NEW ~200 lines (PR 1) — lineage map + cross-ref registry + corrections detail
├── jp-q1-anchors.md                     # NEW ~200 lines (PR 2) — with landmark sections
├── jp-q2-anchors.md                     # NEW ~250 lines (PR 2)
├── jp-q3-anchors.md                     # NEW ~300 lines (PR 2)
├── jp-q4-anchors.md                     # NEW ~200 lines (PR 2)
├── zh-q1-anchors.md                     # NEW ~150 lines (PR 2)
├── zh-q2-anchors.md                     # NEW ~300 lines (PR 2)
├── zh-q3-anchors.md                     # NEW ~300 lines (PR 2) — includes 全聯 Q3-center re-classification
├── zh-q4-anchors.md                     # NEW ~150 lines (PR 2) — thin, JP cross-ref heavy
├── en-q1-anchors.md                     # NEW ~300 lines (PR 3)
├── en-q2-anchors.md                     # NEW ~300 lines (PR 3)
├── en-q3-anchors.md                     # NEW ~350 lines (PR 3)
├── en-q4-anchors.md                     # NEW ~200 lines (PR 3)
└── axis-extreme-anchors.md              # NEW ~150 lines placeholder (PR 1)
```

### SKILL.md + rubric updates (PR 3)

```
copywriting-voice-tone-stage/SKILL.md            # Pass 3 load logic + Phase 7/8 audit outcome
copywriting-voice-quadrant-stage/SKILL.md        # optional position field
copywriting-voice-tone-stage/rubrics/voice-consistency-gate.md  # over-mimic adherence check
```

### Upstream domain-teams (PR 2 prerequisite)

```
domain-teams/skills/copywriting-team/skills/copywriting-voice-tone-stage/standards/
└── zh-copy-craft-lineage.md             # Z5-Z11 drift corrections
```

## Entry template (quadrant files with landmark sections)

```markdown
# {lang}-{quadrant} Voice Anchors

Quadrant: {Q1 / Q2 / Q3 / Q4}
Register: {authority-reason / authority-emotion / affinity-emotion / affinity-reason}

## Overview
{1-paragraph quadrant character summary}

## Landmark: center
Canonical prototype voice for this quadrant. Use when brief asks for standard register.

### {anchor name}
- **Era**: {years}
- **Agency / creator**: {attribution}
- **Primary sources**: {2-3 URLs/ISBNs}
- **Representative lines** (verbatim):
  - {line 1}
  - {line 2}
- **Voice signature**: {3-4 dimensions}
- **LLM corpus depth**: DEEP/MEDIUM-DEEP/MEDIUM
- **Over-mimic risk**: LOW/MEDIUM/HIGH + mitigation (if HIGH, ≤15 words)
- **Cross-reference-valid-for**: {other langs with strength}
- **Trigger slug**: `{culture}-{name-kebab}-{style-label}`

### {another center anchor}
...

## Landmark: extreme
Maximum-intensity expression of the quadrant. Use when brief asks for peak register; apply mitigation clauses.

### {anchor}
...

## Landmark: toward-Q{adjacent-1}
Anchors that edge toward adjacent quadrant while remaining in primary. Use for hybrid briefs.

### {anchor}
...

## Landmark: toward-Q{adjacent-2}
...

## Cross-references
- External cross-lang anchors usable (per meta-detail cross-ref registry)
```

**Progressive disclosure rationale**: Pass 3 agent with `voice_quadrant.position = "center"` reads only `## Landmark: center` section (~1-1.5K tokens) rather than whole file (~3K). When position missing, falls back to reading full file.

## PR 1 — Foundation (scaffold + 2-file meta + landmark skeletons + axis-extreme placeholder)

**Purpose**: establish meta split + 13 file skeletons (with landmark sections) + axis-extreme stub. Zero upstream blocker.

**Branch**: `feat/copywriting-toolkit-voice-anchor-foundation-v1.4.0`

### Commits

1. **`feat(copywriting-toolkit): scaffold voice-anchor-meta-core + meta-detail (split for lazy-load)`**
   - `voice-anchor-meta-core.md` (~200 lines):
     - Schema definition (anchor entry structure)
     - 4-condition selection rubric (essential rules only)
     - Over-mimic mitigation registry (15+ entries as index table — full mitigations in detail file)
     - Pointers to detail file sections
   - `voice-anchor-meta-detail.md` (~200 lines):
     - Verified lineage map (6 primary-source citations, full detail)
     - Cross-reference-valid-for registry (JP→zh-TW STRONG + other combinations)
     - Cross-cultural unified label rubric (19 labels × 4 cultures matrix)
     - Z5-Z11 corrections catalog (detailed)

2. **`feat(copywriting-toolkit): scaffold 13 anchor inventory files with landmark sections`**
   - 12 `{lang}-q{N}-anchors.md` files with header + 4 landmark sub-sections (center / extreme / toward-Q{adj1} / toward-Q{adj2}) + cross-references section
   - Each section empty with `<!-- TBD populated in PR 2/3 -->` marker
   - `axis-extreme-anchors.md` with 4 axis stubs (authority-extreme / affinity-extreme / reason-extreme / emotion-extreme) + "research pending V2" note

3. **`chore(copywriting-toolkit): version bump v1.3.0 → v1.4.0 + CHANGELOG`**
   - `plugin.json` bump
   - CHANGELOG: "Voice anchor expansion foundation — meta split + 13 skeletons; content lands in v1.4.1 / v1.4.2"

### Verification

```bash
# File count
ls copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/ | wc -l
# Expected: 3 existing + 15 new = 18 files

# Meta files distinct
test -f copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/voice-anchor-meta-core.md
test -f copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/voice-anchor-meta-detail.md

# Landmark section structure in every quadrant file
for f in copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/{jp,zh,en}-q[1-4]-anchors.md; do
  grep -c "^## Landmark:" "$f"
done
# Expected: each file reports 4 (center / extreme / toward-Q{adj1} / toward-Q{adj2})
```

### Rollback

Revert single PR — no downstream consumer yet (load logic update lives in PR 3).

## PR 2 — JP + zh-TW content + drift corrections

**Purpose**: populate 8 files (JP Q1-Q4 + zh-TW Q1-Q4); land Z5-Z11 via domain-teams upstream + toolkit sync.

**Branch**: `feat/copywriting-toolkit-voice-anchor-jp-zh-v1.4.1`

### Upstream PR (prerequisite)

**Branch**: `fix/copywriting-team-zh-lineage-drift-v4.17.0`

Commit: `fix(copywriting-team): zh-copy-craft-lineage drift corrections Z5-Z11`
- All 7 Z5-Z11 corrections detailed in Context §

**Merge upstream first. Wait 30-60s per `feedback_stacked_pr_race`. Then proceed to toolkit PR.**

### Toolkit PR commits

1. **`chore(copywriting-toolkit): sync zh-copy-craft-lineage from domain-teams upstream`**
   - `cp` from upstream; verify `diff -q` empty

2. **`feat(copywriting-toolkit): populate jp-q1/q2 anchor inventory (landmark-organized)`**
   - jp-q1-anchors.md:
     - center: 朝日天声人語 / 日経ビジネス / 東洋経済
     - extreme: Reuters JP / Bloomberg JP (with intl-wire caveat)
     - toward-Q2: 夏目漱石 ironic-observer
     - toward-Q4: Stratechery JP equivalent gap (note: no strong native anchor)
   - jp-q2-anchors.md:
     - center: MUJI 原研哉 / Apple TD (global ref) / ほぼ日 Q2-edge
     - extreme: 寺山修司 / 眞木準 pointer to existing lineage
     - toward-Q1: 谷崎潤一郎《陰翳礼讃》
     - toward-Q3: 川端康成 / JR東海「そうだ京都」 / 糸井重里 Q2-edge pointer / 岩崎俊一 pointer

3. **`feat(copywriting-toolkit): populate jp-q3/q4 anchor inventory (landmark-organized)`**
   - jp-q3-anchors.md:
     - center: 向田邦子 / 糸井重里 pointer / 坂元裕二 / 岩崎俊一 pointer
     - extreme: 糸井「生きろ」/ 谷川俊太郎 / 宮沢賢治 / 吉本ばなな
     - toward-Q2: 梅田悟司 ジョージア / 佐々木宏 白戸家 / 澤本嘉光
     - toward-Q4: 伊丹十三 urbane-detail-wit
   - jp-q4-anchors.md:
     - center: クックパッド / Kurashicom Q4 subset (with Q3/Q4 boundary warning)
     - extreme: ジャパネットたかた 高田明 (1990-2015 founder only) / 通販生活 / ワークマン SNS
     - toward-Q1: UNIQLO LifeWear 2013-
     - toward-Q3: (thin native; note 北欧 Q3 overlap)

4. **`feat(copywriting-toolkit): populate zh-q1/q2 anchor inventory (landmark-organized)`**
   - zh-q1-anchors.md:
     - center: 天下雜誌 / 報導者 center register / 研之有物
     - extreme: 報導者 extreme register (with Q1-Q2 edge flag)
     - toward-Q2: (gap; flag for future)
     - toward-Q4: 商業周刊 strategy-imperative
   - zh-q2-anchors.md:
     - center: 誠品 李欣頻 pointer / 中興百貨 許舜英 pointer / 左岸咖啡館 葉明桂 pointer
     - extreme: 朱家鼎 KC Tsang 鐵達時 HK / 王家衛 monologue + mitigation
     - toward-Q1: 錢鍾書 / 白先勇 elegiac
     - toward-Q3: 張愛玲 aphoristic-observation / 朱天文 temporal-slowness

5. **`feat(copywriting-toolkit): populate zh-q3/q4 anchor inventory (includes 全聯 Q3-center re-classification)`**
   - zh-q3-anchors.md:
     - center: **全聯 TV-era 2006-2014 (格言-aphorism, Q10 re-class)** / 吳念真 保力達B / 胡湘雲 大眾銀行 / 龔大中
     - extreme: 故宮「朕知道了」/ 台灣吧
     - toward-Q2: 黃春明 / 朱天心 / 三毛 lyrical-travel
     - toward-Q4: (thin)
     - Cross-ref: 向田邦子 JP STRONG / 糸井 JP STRONG
   - zh-q4-anchors.md:
     - center: PChome / MOMO 購物專家
     - extreme: (gap; note TW DR tradition thin)
     - toward-Q3: (brief)
     - toward-Q1: (brief)
     - Cross-ref: Kurashicom Q4 JP MEDIUM / Cookpad JP STRONG

6. **`chore(copywriting-toolkit): voice-anchor-meta updates — Z5-Z11 correction details + cross-ref populate`**
   - Update meta-detail.md §Corrections with actual correction text (not pointer)
   - Populate cross-reference-valid-for entries for populated JP→zh-TW anchors

7. **`chore(copywriting-toolkit): version bump v1.4.0 → v1.4.1 + CHANGELOG`**

### Verification

```bash
# zh-lineage sync verified byte-identical
diff -q domain-teams/skills/copywriting-team/skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md \
        copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md
# Expected: empty

# All 8 JP + zh files populated (no TBD markers)
for f in jp-q{1,2,3,4}-anchors.md zh-q{1,2,3,4}-anchors.md; do
  grep -L "TBD\|TODO\|<!-- populated" "copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/$f" && echo "$f: populated"
done

# 全聯 Q3-center re-classification verified
grep -A 3 "^## Landmark: center" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/zh-q3-anchors.md | grep "全聯"
# Expected: match (全聯 under center, NOT extreme)

# Corrections detail populated
grep -c "^### Z[5-9]\|^### Z1[01]" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/voice-anchor-meta-detail.md
# Expected: ≥7
```

### Rollback

1. Revert toolkit PR (7 commits)
2. Upstream drift corrections are safe — keep unless catastrophic

## PR 3 — EN content + Phase 7/8 audit + pipeline integration

**Purpose**: populate 4 EN quadrant files; audit Phase 7/8 for meta dependencies; wire Pass 3 load logic (craft-gate / register-signal / axis-extreme + landmark-targeted + cross-lang independent load); update rubric.

**Branch**: `feat/copywriting-toolkit-voice-anchor-en-pipeline-v1.4.2`

### Commits

1. **`feat(copywriting-toolkit): populate en-q1/q2 anchor inventory (landmark-organized)`**
   - en-q1-anchors.md:
     - center: Ogilvy Rolls-Royce / Hathaway Man / BMW Ultimate / Abbott Economist
     - extreme: The Economist brand / WebMD / Reuters EN / Bloomberg EN / Hopkins Pepsodent
     - toward-Q2: Bernbach DDB (Q1↔Q3 hybrid note) / Basecamp manifesto-mode
     - toward-Q4: McPhee / Stratechery / Basecamp Getting Real / Hemingway iceberg / Carver / Hempel / Orwell / E.B. White
   - en-q2-anchors.md:
     - center: Apple Think Different / Nike Just Do It / Patagonia Don't Buy This Jacket
     - extreme: Nike Dream Crazy/Crazier anaphoric / Extinction Rebellion Declaration (civic-only mitigation)
     - toward-Q1: Patek Philippe Generations / Absolut Vodka / BMW Ultimate edge
     - toward-Q3: Oatly activist mode / Toni Morrison / James Baldwin / Kazuo Ishiguro / Didion

2. **`feat(copywriting-toolkit): populate en-q3/q4 anchor inventory (landmark-organized)`**
   - en-q3-anchors.md:
     - center: MailChimp / Innocent Drinks / Oatly center / Nora Ephron / Raymond Carver Q3 edge
     - extreme: Steak-umm Allebach / Duolingo Parvez 2021-22 formative window / Phoebe Waller-Bridge Fleabag / Liquid Death
     - toward-Q2: George Saunders / Taika Waititi / Greta Gerwig
     - toward-Q4: Dollar Shave Club launch / Gary Halbert peer-edge / Chekhov
   - en-q4-anchors.md:
     - center: Amazon product / REI expert / IKEA assembly / Basecamp Rework
     - extreme: Gary Halbert DR / Bill Jayme direct-mail
     - toward-Q1: Morning Brew / Hopkins reason-why edge
     - toward-Q3: Raymond Chandler / Dashiell Hammett

3. **`refactor(copywriting-toolkit): Phase 7/8 meta dependency audit (determines Option 4 scope)`**
   - Audit Phase 7 ethics check: does it need `voice-anchor-meta-core.md` for over-mimic? Likely NO (ethics ≠ voice)
   - Audit Phase 8 8b form check: does it need over-mimic mitigation registry for voice-overlap check? Possibly YES
   - Audit deliverable: embedded in commit message + PR description
   - If Phase 8 8b needs meta-core → Option 4 scope limits to Pass-3-only (meta-detail stays Pass-3, meta-core loads at Phase 8 too)
   - If neither needs meta → Option 4 full: meta-core + meta-detail both Pass-3-conditional

4. **`refactor(copywriting-toolkit): Phase 6 Pass 3 load logic — craft-gate / register-signal / axis-extreme + landmark-targeted + meta lazy`**
   - Update `copywriting-voice-tone-stage/SKILL.md` §When lineage craft applies + §Pass 3 activation guard
   - New branching structure:
     ```
     # Pass 3 activation predicate (existing v1.2.0 lazy gate preserved)
     if Pass 3 trigger == TRUE:
         # Tier 1 — craft gate (existing behavior preserved)
         if voice_reference ∈ {糸井, 岩崎, 眞木, 谷山}:
             load jp-copy-craft-lineage.md
             load meta-core (for over-mimic rules)
         elif voice_reference ∈ {許舜英, 李欣頻, 葉明桂}:
             load zh-copy-craft-lineage.md
             load meta-core
         
         # Tier 2 — register signal (new)
         elif voice_quadrant.position matches "axis-*":
             load meta-core
             load axis-extreme-anchors.md
         else:
             load meta-core
             load meta-detail
             if voice_quadrant.position present:
                 read only ## Landmark: {position} section of {output_lang}-q{primary}-anchors.md
             else:
                 load full {output_lang}-q{primary}-anchors.md
             # cross-language fallback
             if cross-reference-valid-for[output_lang] == STRONG for relevant anchor:
                 load jp-q{primary}-anchors.md (section-targeted if possible)
     
     else (no Pass 3 trigger):
         # Per Option 4: no meta load at all
         (or per audit outcome: meta-core only if Phase 8 8b needs it later)
     ```

5. **`refactor(copywriting-toolkit): voice-quadrant-positioning — optional position field`**
   - Add optional `voice_quadrant.position` to envelope schema
   - Values: `center | extreme | toward-Q{n} | axis-{authority,affinity,reason,emotion}`
   - Default when missing: `center`
   - Document in Preconditions + I/O Contract sections

6. **`refactor(copywriting-toolkit): voice-consistency-gate — over-mimic adherence dimension`**
   - Update `rubrics/voice-consistency-gate.md` to check:
     - Primer register's grammar features preserved
     - Over-mimic tropes NOT leaked (against mitigation clauses in meta-core)
   - Add dimension with SHOULD-level priority

7. **`chore(copywriting-toolkit): version bump v1.4.1 → v1.4.2 + CHANGELOG`**

### Verification

```bash
# All EN files populated with landmark sections
for f in en-q{1,2,3,4}-anchors.md; do
  grep -c "^## Landmark:" "copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/$f"
done
# Expected: each file reports 4

# Phase 7/8 audit outcome documented
grep -E "Phase 7.*audit|Phase 8.*8b.*audit|meta-core.*Phase" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/SKILL.md

# Pass 3 load logic implements tier structure
grep -E "Tier 1.*craft|Tier 2.*register|register-signal|landmark-targeted" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/SKILL.md

# Position field added
grep "position.*center\|position.*extreme\|position.*axis" \
  copywriting-toolkit/skills/copywriting-voice-quadrant-stage/SKILL.md

# Gate rubric over-mimic check
grep -E "over-mimic|mitigation" \
  copywriting-toolkit/skills/copywriting-voice-tone-stage/rubrics/voice-consistency-gate.md
```

### End-to-end smoke tests

| # | Scenario | Expected load |
|---|---|---|
| 1 | `voice_reference=糸井 / output=ja / quadrant=Q3` | jp-copy-craft-lineage.md + meta-core ONLY |
| 2 | `voice_reference=Didion / output=en / quadrant=Q2 / position=center` | meta-core + meta-detail + en-q2-anchors.md §Landmark: center |
| 3 | `voice_reference=谷崎 / output=zh-TW / quadrant=Q2 / position=toward-Q1` | meta-core + meta-detail + zh-q2-anchors.md §Landmark: toward-Q1 + jp-q2-anchors.md §Landmark: toward-Q1 (cross-ref STRONG) |
| 4 | `voice_reference=null / output=ja / no Pass 3 trigger` | NO meta load (if Option 4 full) OR meta-core only (if audit forces Phase 8 need) |
| 5 | `voice_reference=Hemingway` with robotic he-said/she-said | voice-consistency-gate FAIL with "over-mimic: dialogue-tag chains > 2 per 50 words" |

### Rollback

Revert PR 3. Pass 3 falls back to v1.4.1 behavior (content populated but Pass 3 load logic still pre-refactor; register-signal path may not trigger cleanly — acceptable interim).

## Token cost analysis (with optimizations 1-4)

### Baseline vs pre-optimization vs optimized

| Path | Trigger rate | Baseline (current) | Pre-opt (original plan) | **Post-opt (this plan)** |
|---|---|---|---|---|
| No Pass 3 (short-form, no ref) | ~10% | ~20K | ~25K | **~20K** (meta not loaded) |
| Craft gate (existing 6 masters) | ~20% | ~24K | ~28-30K | **~25-27K** (meta-core only, +~2K) |
| Register signal, no cross-lang, position-targeted | ~40% | N/A | ~28K | **~26.5K** (landmark section ~1.5K vs whole file ~3K) |
| Register signal, JP→zh-TW STRONG | ~20% | N/A | ~31K | **~28.5K** (both files section-targeted) |
| Axis extreme MVP | ~5% | N/A | ~27K | **~24K** (meta-core + axis placeholder) |

**Weighted per-run avg**:
- Baseline: ~22K
- Original plan: ~28.7K (+30%)
- **With optimizations 1-4: ~26K (+18% vs baseline, but ~-9% vs original plan)**

### Savings from each optimization

| Optimization | Weighted saving | Mechanism |
|---|---|---|
| ① Meta split (core/detail) | ~-1K | Only load detail when needed |
| ② Landmark-targeted quadrant load | ~-1K | ~1.5K section vs 3K whole file |
| ③ Lazy cross-ref registry | ~-0.3K | Only on cross-lang trigger |
| ④ Meta Pass-3-only (pending audit) | ~-0.5K | No always-load |
| **Combined** | **~-2.7K** | Multiplicative savings |

### Audit-dependent branch

Option 4's full benefit requires Phase 7/8 not needing meta. If audit shows Phase 8 8b needs meta-core:

- Option 4 becomes partial: meta-core becomes Phase-6-always-load (+2K baseline), meta-detail stays Pass-3-conditional
- Weighted saving drops from -2.7K to -2.2K
- Still a win vs original plan

### v1.5 optimization triggers (escalation path)

Activate further optimization only if real-usage audit shows:
- Average pipeline exceeds 35K voice-stack tokens (5K over post-opt target)
- Perceived latency > 15s for Pass 3 skills
- Voice-stack token cost > 50% full pipeline token cost

Below thresholds, this plan's 4 optimizations are sufficient.

## Content sources per file

| Target file | Source docs |
|---|---|
| voice-anchor-meta-core | voice-anchor-layer-0-research.md (over-mimic registry + rubric) + voice-anchor-research.md (schema) |
| voice-anchor-meta-detail | voice-anchor-layer-0-research.md (lineage map + label rubric) + voice-anchor-gap-research.md (corrections) + voice-anchor-archived-references.md (KC Tsang correction note) |
| jp-q1-anchors | voice-anchor-gap-research.md §JP Q1 |
| jp-q2-anchors | voice-anchor-research.md §JP + voice-anchor-layer-0-research.md §JP literary |
| jp-q3-anchors | voice-anchor-research.md §JP + voice-anchor-layer-0-research.md §JP literary + voice-anchor-gap-research.md |
| jp-q4-anchors | voice-anchor-gap-research.md §JP Q4 |
| zh-q1-anchors | voice-anchor-gap-research.md §zh-TW Q1 |
| zh-q2-anchors | voice-anchor-research.md §ZH + voice-anchor-layer-0-research.md §ZH literary + voice-anchor-archived-references.md §3.0 KC Tsang entry |
| zh-q3-anchors | voice-anchor-research.md §ZH + voice-anchor-gap-research.md §zh-TW Q3 + Z10 re-class |
| zh-q4-anchors | voice-anchor-research.md §ZH + JP cross-ref |
| en-q1-anchors | voice-anchor-research.md §EN + voice-anchor-layer-0-research.md §EN literary |
| en-q2-anchors | voice-anchor-research.md §EN + voice-anchor-gap-research.md §EN Q2 extreme |
| en-q3-anchors | voice-anchor-research.md §EN + voice-anchor-layer-0-research.md §EN literary + voice-anchor-gap-research.md §EN Q3 extreme |
| en-q4-anchors | voice-anchor-research.md §EN + voice-anchor-archived-references.md §3.0 Bill Jayme entry |
| axis-extreme-anchors | placeholder (V2 research) |

**Archived anchors** (NOT in inventory): all entries in `voice-anchor-archived-references.md` stay archived per prior decision.

## Branch strategy

```
main
├── research/copywriting-voice-anchor-expansion    # research docs (stays unmerged unless deemed reference-worthy)
├── fix/copywriting-team-zh-lineage-drift-v4.17.0  # upstream domain-teams (PR 2 prereq)
├── feat/copywriting-toolkit-voice-anchor-foundation-v1.4.0     # PR 1
├── feat/copywriting-toolkit-voice-anchor-jp-zh-v1.4.1          # PR 2
└── feat/copywriting-toolkit-voice-anchor-en-pipeline-v1.4.2    # PR 3
```

**Merge order**: upstream fix → PR 1 → PR 2 → PR 3. Each depends on previous.

## Cross-cutting concerns

### Tier 1 byte-identical discipline

- **Existing jp-copy-craft-lineage.md**: NO changes any PR
- **Existing zh-copy-craft-lineage.md**: PR 2 only changes = Z5-Z11 sync; byte-identical after
- **15 new toolkit-originated files**: follow zh-copy-craft-lineage.md v1.0.1 precedent — immutable canon, no upstream diff target, no DIVERGED header required

### CC CI type whitelist

Per `feedback_cc_type_whitelist`: only {refactor, feat, fix, chore, docs} allowed. All commits verified compliant. No `test:` / `ci:` prefixes.

### Schema governance

`voice_quadrant.position` is additive optional field in PR 3. Downstream skills still treat `voice_quadrant.primary` as required (Q1-Q4 enum). Position fallback = "center" when missing.

### Version bumps

- v1.3.0 → v1.4.0 (PR 1) → v1.4.1 (PR 2) → v1.4.2 (PR 3)

## Risks

1. **Upstream sync conflict**: keep upstream PR drift-only; merge; immediately sync.
2. **Anchor content drift during population**: entry template enforces verbatim quotes + primary source URL; spot-check review before commit.
3. **Pass 3 load regression**: Tier-1 craft-gate branch preserves existing behavior exactly; new register-signal/axis-extreme branches only activate for non-craft-gate voice_reference values.
4. **Landmark-targeted section read fragility**: Pass 3 agent needs robust section-parsing. Risk: if section markers drift (e.g., typo), full-file fallback activates (slightly higher token cost but no correctness loss).
5. **Phase 7/8 audit reveals meta dependency late**: audit happens in PR 3, but meta split landed PR 1. If audit forces meta-core to be always-load, PR 3's Pass 3 refactor accommodates (documented in audit commit).
6. **File discovery inflation**: 15 new files in flat `standards/`. Naming convention (`{lang}-q{N}-anchors.md` + `voice-anchor-meta-{core,detail}.md`) makes purpose obvious.
7. **Axis-extreme V2 deferral**: placeholder file may stay empty. Acceptable; `last-reviewed` date tracks staleness.
8. **zh-HK coverage thin**: only 朱家鼎 鐵達時 + 王家衛 HK anchors in zh-q2. Acceptable per scope decision (zh-HK ref pool, not output target).

## Out of scope

- Korean (KR) anchor inventory — archived
- Visual-dominant skip-list promotion to anchor — archived
- Continuous coordinate schema `(x, y)` migration — discrete sufficient
- Bidirectional cross-ref (TW→JP, EN→ZH etc.) — only JP→zh-TW STRONG implemented in v1.4

## Open dependencies

1. Upstream `domain-teams/copywriting-team` version must support Z5-Z11 corrections
2. Review bandwidth for 3 sequential PRs
3. Plugin.json current version confirmed at v1.3.0

## Checklist before starting PR 1

- [ ] 6 research docs reviewed
- [ ] 8 architecture decisions confirmed (incl. 4 optimizations)
- [ ] plugin.json current version = v1.3.0
- [ ] Entry template + landmark section structure reviewed
- [ ] Smoke test scenarios reviewed

## Next action

Begin PR 1 scaffold:
1. Branch from `main`: `feat/copywriting-toolkit-voice-anchor-foundation-v1.4.0`
2. Write `voice-anchor-meta-core.md` (schema + rubric + over-mimic index)
3. Write `voice-anchor-meta-detail.md` (lineage + cross-ref + corrections detail)
4. Scaffold 12 `{lang}-q{N}-anchors.md` + `axis-extreme-anchors.md` with landmark sections
5. Version bump + CHANGELOG
6. Verification + local test
7. Push + open PR
