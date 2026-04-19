# Design Spec: investing-toolkit v1.11.0 — Cross-country Consistency Refresh

**Date**: 2026-04-19
**Topic**: 5-country coverage asymmetry reduction + grounding vintage refresh
**Previous release**: v1.10.0 (PR #93, merged 2026-04-19) — PMI (OECD CLI proxy) + JP real-rates multi-source (C+D+E) + US swap spread

## 1. Goal

v1.10.0 close 3 items 後，audit 發現 5 國 toolkit coverage 存在顯著 asymmetries：

1. **PMI asymmetry** — US 有 OECD CLI proxy 但 JP/TW/KR/CN 全 N/A URL-only；CN Caixin + NBS PMI **事實上免費可抓**（akshare 既有 adapter）卻尚未接入
2. **Grounding vintage drift** — 5 份 `thresholds-*.md` 全部 vintage 為 2026-Q1（v1.9.0 audit 2026-04-18），到 v1.11.0 時已 3-4 個月未刷新
3. **No consolidated cross-country coverage view** — 5 國 × N signal 的 coverage 資訊散佈在 10+ 個檔案，使用者無單頁可查

v1.11.0 目標：**以 cross-country 對稱性為主軸**，削減 asymmetries，不做單國深化。

明確拒絕的方向：**不做 JGBi YTM solver**（原 v1.11.0 候選）— 該方案會讓 JP 成為 5 國中唯一做 bond math derivation 的異類，打破「country-macro = pure data layer」原則，且業界無 free-tier 先例（Bloomberg / Refinitiv 才做）。

## 2. Context

### 2.1 v1.10.0 merge 後的 5 國 coverage asymmetry matrix

| Signal | US | JP | TW | KR | CN |
|--------|-----|-----|-----|-----|-----|
| Growth proxy | ✅ nowcast 4 series | ✅ CI trio | ✅ 景氣燈號 | ✅ K253 | ✅ 三大数据 |
| Inflation | ✅ CPIAUCSL | ✅ 全国 CPI | ✅ DGBAS | ✅ K401 | ✅ NBS CPI |
| Policy rate | ✅ | ✅ | ✅ | ✅ | ✅ |
| Real-rate (market) | ✅ daily (T5YIE/DFII5...) | ⚠️ partial C+D+E | ❌ Not available | ❌ Deferred (KTBi) | ❌ Not available |
| **PMI** | ✅ OECD CLI proxy | ❌ **N/A URL only** | ❌ **N/A URL only** | ❌ **N/A URL only** | ❌ **N/A URL only ⚠️ closable** |
| Swap spread | ✅ T-SOFR 3M | ❌ N/A | ❌ N/A | ❌ N/A | ❌ N/A |

關鍵 asymmetry：
- **CN PMI closable**：akshare 既有 adapter 可取得 Caixin Manufacturing / Services PMI + NBS 官方 PMI (manufacturing + non-manufacturing)
- **Other APAC PMI not closable on free-tier**：JP au Jibun Bank / TW 中經院 / KR S&P Global 皆 licensed；可 formalize URL-only references 作為對稱聲明
- **Real-rate asymmetry 結構性無解**：僅 US 有 pre-computed TIPS (NY Fed 發布)；其他 4 國要嘛無 linker market (TW/CN) 要嘛需付費 API (KR KTBi) 要嘛需自建 solver (JP JGBi)。v1.10.0 JP partial 是誠實姿態，v1.11.0 不改動

### 2.2 Grounding vintage drift

v1.9.0 grounding (2026-04-18 audit) 以來的已知政策變動：
- **CN**: 2025 政府工作報告 CPI 目標 3% → 2% （v1.9.0 Q1 已 captured；2026 年度工作報告 stance 延續?）
- **JP**: 2024-03 YCC exit → 2024-07 0.25% → 2025-01 0.50% → 2025-12 0.75% (30 年新高，v1.9.0 已 captured)；2026 年 BOJ 路徑?
- **US**: Fed FAIT → FIT (2025-08 已 captured)；2025-12 / 2026 FOMC SEP 更新?
- **TW**: CBC 2026-Q2 理監事 + NDC 景氣燈號 2024 修訂 (已 captured)；無重大新增
- **KR**: BOK 基準利率 2.50% since 2025-05-29 (已 captured)；無重大新增

**Change velocity**：
- CN / JP：高（政策 stance 可能有 Q2 進一步變化）
- US：中（Fed 每季 SEP 更新，有 delta 但架構穩定）
- TW / KR：低（目前政策路徑穩定）

→ 採 **mixed strategy**：CN + JP full re-audit；US/TW/KR delta addenda。

### 2.3 why NOT JGBi YTM solver (rejected path)

在 brainstorming phase 詳細評估後拒絕：
- **架構不一致性**：5 國 country-macro 全為 pure data fetcher，加 bond math solver 使 JP 成異類
- **業界 free-tier 先例不存在**：Bloomberg / Refinitiv 才做，FRED / ECB / OECD 都不做
- **Slippery slope 風險**：做了 JP 後，KR KTBi / TW 零星 linker / CN shadow-rate 全會變成「為什麼不做」的壓力
- **機會成本高**：同樣 5-7 天做 cross-country symmetric improvement 而非單國深度

詳細論述見 conversation `0912f7b3-644d-4e33-8c43-a9a849c73e9b.jsonl` (v1.11.0 brainstorm section)；未來若需重啟此方向，建議定位為「研究專案」而非 toolkit 擴展。

## 3. Scope — Single v1.11.0 PR, six commits

### 3.1 Commit 1 — china-macro `pmi` group

**Files modified**:
- `investing-toolkit/skills/china-macro/SKILL.md` — new `pmi` group with 5 presets
- `investing-toolkit/skills/china-macro/references/indicators-china.md` — new PMI section (Caixin methodology + NBS methodology + Caixin vs NBS delta)
- `investing-toolkit/skills/china-macro/references/indicator-index.md` — add 5 PMI entries

**Data source**:
- Primary: akshare existing adapter (already in investing-toolkit v1.6.0)
- Probe at implementation time for exact akshare function names; candidates:
  - `ak.index_pmi_em()` or similar Caixin mfg
  - `ak.index_pmi_em_services()` or similar Caixin services
  - `ak.macro_china_pmi()` for NBS 官方 PMI

**Presets (5)**:
- `caixin-mfg-pmi` — Caixin Manufacturing PMI (diffusion index, monthly)
- `caixin-svc-pmi` — Caixin Services PMI (diffusion index, monthly)
- `nbs-mfg-pmi` — NBS 官方 Manufacturing PMI
- `nbs-nonmfg-pmi` — NBS 官方 Non-manufacturing PMI
- `nbs-composite-pmi` — NBS 综合 PMI

**Signal thresholds** (standard diffusion index convention): `> 52` Expansion / `50-52` Near-neutral / `< 50` Contraction.

**Reference content must cover**:
- What is Caixin PMI (S&P Global + Caixin partnership since 2015; replaced HSBC/Markit)
- What is NBS 官方 PMI (差異 sample: 官方 涵 ≥ 3000 enterprises incl. 國企; Caixin sample ~430 enterprises SME/民企 concentrated)
- Caixin vs NBS delta (Caixin 往往 lead NBS 1-2 月；SME lean vs SOE lean)
- Historical regime shifts (2015 匯改後 Caixin 率先 < 50；2020-02 COVID 兩者同步破底；2022 上海封控 Caixin 45.6 vs NBS 47.4)

### 3.2 Commit 2 — APAC PMI probes + URL references

**Files modified**:
- `investing-toolkit/skills/japan-macro/SKILL.md` — PMI URL-only subsection (au Jibun Bank PMI licensed)
- `investing-toolkit/skills/taiwan-macro/SKILL.md` — PMI URL-only subsection (中華經濟研究院 PMI 公開性待 probe)
- `investing-toolkit/skills/korea-macro/SKILL.md` — PMI URL-only subsection (S&P Global Korea Manufacturing PMI 授權)
- Each country's `references/indicator-index.md` — add PMI entry (URL reference only)

**Probe procedure per country (~1 hour each)**:
1. WebFetch/WebSearch for free-tier PMI access routes
2. Check each country's 政府 stat department / 央行 / 學術 / 業協會 網站
3. Document findings:
   - If free access found → add preset to `pmi` group
   - If licensed / ToS-restricted → formalize URL-only reference

**Expected outcomes**:
- **JP**: au Jibun Bank PMI licensed via S&P Global; fall back to URL reference https://www.spglobal.com/spdji/en/ or equivalent
- **TW**: 中經院 PMI — probe 網頁 public accessibility; 若 ToS 允許 URL reference
- **KR**: S&P Global Korea Manufacturing PMI licensed; BOK 기업경기실사 BSI survey 已在 v1.8.1 korea-macro K-series，可 cross-reference 作為 PMI proxy 替代

若 probe 意外發現免費 API：加入相應 country-macro 的 `pmi` group。

**合規原則**：完全對齊 v1.10.0 JBTS ToS 教訓 — 不 scrape licensed sources，只 URL reference。

### 3.3 Commit 3 — CN + JP full grounding refresh

**Files modified**:
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-china.md` — full rewrite to 2026-Q2 vintage
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md` — full rewrite to 2026-Q2 vintage

**Execution**:
- Dispatch 2 parallel `general-purpose` agents (仿 v1.9.0 5-parallel model, scaled to 2 focused countries)
- Each agent: native-language research (simplified Chinese / Japanese), target 2026-Q2 vintage
- Verify since 2026-Q1:
  - Policy rate trajectory
  - r* anchor (new academic papers or central bank updates)
  - CPI target (CN 2026 工作報告 stance)
  - Currency / reserves / 貨幣政策決議 updates
  - 景氣信號 / 短観 等週期性指標 latest

**Historical preservation**:
- Keep v1.9.0 correction labels as historical record (不清理)
- Add "v1.11.0 full refresh (2026-04-19)" block clearly demarcating updated sections
- Format: v1.9.0 corrections → v1.9.0 supplementary (2026-04-18) → **v1.10.0 addendum (2026-04-19 JP only)** → v1.11.0 full refresh (2026-04-19)

**Expected change magnitude**:
- CN: 5-10 corrections expected (2026 工作報告 stance, 2025 年末數據 updates, 2026 annual plenum decisions)
- JP: 5-10 corrections expected (BOJ 2025-12 decision rationale, 2026 spring 春闘, r* latest estimate)

### 3.4 Commit 4 — US + TW + KR grounding delta addenda

**Files modified**:
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-us.md` — v1.11.0 addendum block
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-taiwan.md` — v1.11.0 addendum block
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-korea.md` — v1.11.0 addendum block

**Delta scope per country** (no full re-audit; only delta since 2026-Q1):
- **US**: 2025-12 FOMC SEP; 2026 Fed chair transition (Powell 任期); r* latest update; balance sheet runoff status
- **TW**: 2026-Q2 CBC 理監事 (2026-03 應已開會) decision; 2026 CPI 年均 projection; 景氣燈號 2026 Q1 readings
- **KR**: BOK 통화정책방향 latest (2026-Q1/Q2); 삼성+SK 하이닉스 KOSPI 集中度 更新; 가계부채/GDP 最新值

**Format**: v1.10.0 JP addendum pattern — append block inside Grounding Status, not rewrite main body.

**Execution**:
- Lightweight research (WebSearch + 1-2 primary source checks per country)
- No full parallel agents; inline execution OK
- ~20-30 min per country

### 3.5 Commit 5 — `grounding-v1.11.0.md` consolidated audit

**Files created**:
- `investing-toolkit/skills/macro-regime-snapshot/research/grounding-v1.11.0.md` (~300-400 lines)

**Structure** (仿 v1.9.0 + v1.10.0 pattern):

```markdown
---
title: "v1.11.0 cross-country consistency refresh"
date: 2026-04-19
refactor_version: v1.11.0
tags: [research, investing-toolkit, macro-regime-snapshot, grounding, cross-country]
---

## TL;DR
## Scope and methodology (mixed strategy: CN/JP full + US/TW/KR delta)
## CN full re-audit findings
## JP full re-audit findings
## US delta refresh
## TW delta refresh
## KR delta refresh
## CN PMI source vetting (new)
## APAC PMI probe findings (JP/TW/KR)
## Cross-country asymmetry summary (v1.11.0 state)
## Deferred (v1.12.0+)
## Primary-source URLs (consolidated)
## Sign-off
```

**Must document**:
- Mixed strategy rationale (why not full 5-parallel)
- CN/JP corrections with verified primary sources
- US/TW/KR delta findings (or lack thereof — absence of change is also evidence)
- CN PMI new sources (akshare adapter + Caixin / NBS methodology)
- APAC PMI rejection rationale (licensed + URL references)

### 3.6 Commit 6 — macro-regime-snapshot integration + plugin-level sync

**Files modified**:

1. `investing-toolkit/skills/macro-regime-snapshot/SKILL.md`:
   - **Block 1 PMI row update**: CN column from `N/A URL-only` → live value with 2 series (Caixin composite + NBS composite)
   - **Data Source Architecture section expansion**: 5×9 grid table (5 countries × 9 signals) with coverage tier per cell (✅ live / ⚠️ partial / ❌ not available / ❌ deferred + reason)
   - Cross-links to `thresholds-*.md` for details
   - Replaces the coverage-matrix.md idea (Option X decision) — doc consolidated into existing SKILL.md section

2. `investing-toolkit/skills/using-investing-toolkit/SKILL.md`:
   - `china-macro` row: +pmi group (~38 indicators)
   - `macro-regime-snapshot` row: v1.11.0 coverage grid + grounding refresh
   - Footer: "All skills through v1.11.0 are now available."

3. `investing-toolkit/README.md`:
   - Version 1.10.0 → 1.11.0
   - Version Highlights entry prepended for v1.11.0

4. `investing-toolkit/ROADMAP.md`:
   - v1.10.0 demote from (current) to done
   - v1.11.0 promote to (current) with 6-phase breakdown
   - v1.12.0+ candidates list update (JGBi YTM solver 移除 v1.11.0 slot, 改標 "deferred or rejected"; KR KTBi 保留)

5. `investing-toolkit/.claude-plugin/plugin.json`:
   - `version` 1.10.0 → 1.11.0

## 4. Data Flow

```
Commit 1 (CN PMI):
  akshare adapter → china-macro scripts/akshare_client.py
  → china-macro/SKILL.md pmi group (5 presets)
  → macro-regime-snapshot/SKILL.md Block 1 CN PMI row live

Commit 2 (APAC probes):
  WebSearch / WebFetch → document findings
  → each country-macro SKILL.md URL reference section
  → grounding-v1.11.0.md APAC probe findings section

Commit 3 (CN+JP full audit):
  2 parallel native-language research agents
  → thresholds-china.md + thresholds-japan.md v1.11.0 full refresh blocks
  → grounding-v1.11.0.md CN/JP full audit findings sections

Commit 4 (US/TW/KR delta):
  Inline WebSearch + primary source checks
  → 3 thresholds-*.md v1.11.0 addenda
  → grounding-v1.11.0.md US/TW/KR delta refresh sections

Commit 5 (grounding-v1.11.0.md):
  Consolidate above into single audit trail doc

Commit 6 (integration + sync):
  macro-regime-snapshot SKILL.md: Block 1 CN PMI live + Data Source grid
  Plugin-level: using-investing-toolkit / README / ROADMAP / plugin.json
```

## 5. Error Handling

- **akshare CN PMI series discontinuation**: if any of Caixin / NBS PMI adapters fail at implementation, document in reference + keep partial group with available subset
- **APAC PMI probe finds unexpected paid barrier**: formalize URL-only reference, don't attempt workaround (ToS 合規優先)
- **CN/JP full audit reveals major regime shift**: if something like "BOJ emergency rate cut" happened, audit block may exceed 10 corrections; extend thresholds-*.md rewrite to accommodate
- **US/TW/KR delta finds more change than expected**: promote to full re-audit in this PR (scope creep, but acceptable if justified)
- **WARP / archive access for any source**: avoided entirely in v1.11.0 (no historical backfill work)

## 6. Testing & Verification

Per-commit verification:

| Commit | Command / Check |
|--------|-----------------|
| 1 | `uv run scripts/akshare_client.py --preset caixin-mfg-pmi --periods 12` returns ≥ 10 months of clean data; 同樣驗證其他 4 presets |
| 2 | Each country-macro SKILL.md has PMI URL reference section; Markdown validates; no broken links |
| 3 | `thresholds-china.md` + `thresholds-japan.md` have v1.11.0 full refresh block; v1.9.0 correction labels preserved as historical record |
| 4 | 3 thresholds-*.md have v1.11.0 addendum block (pattern matches v1.10.0 JP addendum style) |
| 5 | `research/grounding-v1.11.0.md` exists, covers all required sections |
| 6 | `macro-regime-snapshot/SKILL.md` Block 1 shows CN PMI live; Data Source grid has 5×9 table; `plugin.json` version = 1.11.0 |

Global check before PR:
```bash
cd investing-toolkit
bash scripts/sync-scripts.sh && bash scripts/sync-check.sh
cat .claude-plugin/plugin.json | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])"
# Expected: 1.11.0
```

## 7. Explicit Non-Goals (v1.11.0)

- **No JGBi YTM solver** — architecturally inconsistent (audit above); if demand returns, reframe as research project not toolkit extension
- **No KR KTBi integration** — ECOS API key registration barrier unchanged; keep deferred to v1.12.0+
- **No JP au Jibun Bank PMI fetch** — licensed (S&P Global); URL reference only
- **No TW 中經院 PMI fetch unless probe finds unambiguous free access**
- **No new scripts** — all work via existing akshare_client + markdown edits + WebSearch research
- **No new Python dependencies** — zero
- **No CLAUDE.md architectural principle changes** — "Data/Analysis separation" + "country-macro = data layer" preserved
- **No 5-parallel full re-audit** — mixed strategy intentional; reserves 5-parallel for future major refresh (~2026-Q3+)
- **No coverage-matrix.md new file** — consolidated into macro-regime-snapshot/SKILL.md Data Source Architecture section

## 8. Branch + PR Plan

```
Branch: feat/cross-country-consistency-v1.11.0
PR title: feat(investing-toolkit): v1.11.0 cross-country consistency refresh
PR base: main
Stack: 6 commits (as §3)
```

## 9. Self-Review

- **Placeholder scan**: None. §3.1 akshare adapter probe names are known-unknowns (documented as implementation-time probes) not placeholders.
- **Internal consistency**: 6-commit structure aligns with v1.9.0 / v1.10.0 patterns; each commit has clear single responsibility; no cross-commit file overlap until Commit 6 integration.
- **Scope check**: 4 thematic blocks (CN PMI / APAC probes / mixed grounding / integration), single PR, ~6.5 days — appropriately sized. Larger than v1.8.1 (single-skill), smaller than v1.9.0 (5-country full refresh) or v1.10.0 (3 items + pivot).
- **Ambiguity check**:
  - "Mixed strategy CN/JP full + US/TW/KR delta" — explicitly defined which country gets which treatment
  - "APAC probe outcomes" — A/B branch explicit (free → add preset; licensed → URL reference)
  - "Coverage matrix location" — Option X resolved (in macro-regime-snapshot SKILL.md Data Source section, no new file)
  - "v1.9.0 correction label preservation" — decided: keep as historical record

## 10. Deferred to v1.12.0+

- KR KTBi via BOK ECOS API key registration
- JP au Jibun Bank PMI licensed access (unchanged)
- TW 中經院 PMI licensed / public status resolution
- Full 5-parallel grounding re-audit (~2026-Q3 cadence)
- JGBi YTM solver (rejected for architectural reasons; if revisited, frame as research project)
- Swap spread expansion to other countries (not planned; US-unique signal by design)
- New country skill (eu-macro / india-macro)
