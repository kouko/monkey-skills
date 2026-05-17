---
title: wiki-ingest language policy — design
date: 2026-05-18
status: design-approved
target_skill: obsidian/skills/wiki-ingest (+ wiki-cross-linker / wiki-query / wiki-lint / wiki-auto-research / wiki-setup)
target_branch: feat/wiki-ingest-language-policy
upstream_spec: ~/kouko-obsidian-vault/research/2026-05-18 wiki-ingest 語言策略優化設計研究.md
brainstorming_skill: code-toolkit:brainstorming
predecessor: docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (v3.10.0, MERGED PR #307)
---

# wiki-ingest language policy — design

接續 v3.10.0（zero-prompt + oldest-first auto-batching）。本次處理**正交軸：body language policy**。Upstream design note 提出 4-strategy 全套；本 design 收斂到 **1-mechanism binary switch + decision-tree-driven** 模式（5 個 ambiguity 全部釘完）。

## Problem

`wiki-ingest` 對「wiki/ 頁面內文用什麼語言」**無任何明文規則**，行為靠 LLM 訓練資料的隱性偏好 — 預設英文 + CJK loanword 保留（如「余白」「侘寂」「職務著作」）。對英語為主的 vault 沒問題，但對多語 vault（kouko's：ja + zh-TW + en + ko 並存來源、日常閱讀以 zh-TW 為主）造成：
- 每次查閱要做「概念→英文」反向翻譯
- `wiki-cross-linker` 跨語連結偵測失效（中文「余白」找不到英文 page 內的 "yohaku"）

JTBD（Klement format）：
> *When* I run `/wiki-ingest` on a multi-language vault,
> *I want* wiki pages 用我日常閱讀語言（而非 LLM 隱性英文偏好），
> *so I can* 直接消費 wiki 而不用反向翻譯 + 跨語連結能 resolve。

## Users

kouko（vault 已 80+ wiki 頁、多語 source、日常 zh-TW 閱讀）+ 其他多語 / 單語 vault 使用者。設計目標：multi-language vault 是主要 use case，但機制要能優雅退化到 single-language vault。

## Smallest End State

MVP = Layer A-D + aliases conditional MUST + distribute.py SSOT + wiki-lint 新規則。**新頁生效**；既有 80+ 頁不動（自然 drift on source modify）。

`/wiki-relang` migration、`auto` strategy、`source-language` strategy → Phase 2 future PR。

## Current State Evidence

- **Forward**：`obsidian/skills/wiki-ingest/SKILL.md` v3.10.0（PR #307 已 merged）— STEP 1 decision table、STEP 2 hash+bucket、STEP 3 select-batch.py、**STEP 4c "For each target wiki page"** 是 body language 注入點
- **Reverse**：`obsidian/skills/wiki-ingest/references/page-format.md:1-3` 明寫「Other skills (`wiki-lint`, `wiki-cross-linker`, `wiki-auto-research`) reference their own copies of the relevant fragments — **do not cross-link to this file**」→ 現行 convention 是 option A（各 skill 自帶 copies），即 design note 提到的「page-format.md 已有此前科」
- **Error**：`wiki-cross-linker` 跨語連結偵測，當 slug 用 ASCII 但 body 用 CJK 時，連結 inference 缺少 multi-language aliases 做 anchor → 設計後 frontmatter `aliases` 條件 MUST 由 wiki-lint 強制
- **Data**：`obsidian/skills/wiki-ingest/references/page-format.md:5-17` frontmatter 8 必填欄位（title / type / domain / status / updated / tags / sources_count / summary）— 目前**無 aliases 欄位**；設計後變成 8 + conditional 9th（aliases）
- **Boundary**：`obsidian/skills/` 下 wiki-* family 5 個 sibling skills（wiki-ingest / wiki-cross-linker / wiki-query / wiki-lint / wiki-auto-research）+ wiki-setup（config 範本擁有者）

Evidence paths appendix：
- `obsidian/skills/wiki-ingest/SKILL.md`
- `obsidian/skills/wiki-ingest/references/page-format.md`
- `obsidian/skills/wiki-ingest/references/category-routing.md`
- `obsidian/skills/wiki-setup/SKILL.md`
- 4 sibling skills SKILL.md（references list 已 audit）

## Decision

### §1 Scope（MVP）

- **In**：
  - Layer A: `.obsidian-wiki.config` 3 新 fields
  - Layer B: `references/language-policy.md` 新增（**1 mechanism**，非 N strategies — 見 §2）
  - Layer C: `wiki-ingest/SKILL.md` 3 處 patch（pre-flight 讀 config / lazy-load table 加 1 條 / STEP 4c 加 language resolution）
  - Layer D: `references/page-format.md` 拆 filename rules 與 body language 兩節 + 新增 aliases 條件 MUST
  - `wiki-setup/SKILL.md` config 範本同步
  - `obsidian/scripts/distribute.py` + `verify-drift.py`（仿 code-toolkit byte-identical SSOT 模式）
  - 4 sibling skills 各收 1 份 functional copy of language-policy.md（distribute.py 寫入）
  - `wiki-lint/SKILL.md` 加新 lint rule（slug language ≠ body language → aliases 必填）
  - CI workflow 加 verify-drift step
  - pytest CC-LL-01..05
- **Out** → Phase 2 future PR:
  - `/wiki-relang` migration 命令（80 既有頁重新渲染）
  - `auto` strategy（讀 source.language frontmatter）
  - `source-language` strategy（鏡射源語言、跨來源整合演算法未定）
- **Migration**：自然 drift only — source 修改 → 下次 ingest auto re-render with new policy

### §2 Mechanism（1 個機制，不是 N strategies）

設計收斂從原 design note 提議的 4-strategy enum（primary-only / domain-anchored / source-language / auto）收斂到**單一 mechanism + binary switch**：

```
OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled    → 跑 language-policy.md decision tree
OBSIDIAN_WIKI_LANGUAGE_POLICY=<unset>    → legacy（LLM 隱性英文偏好；backward compat）
```

**Decision tree 永遠有 fallback** 到 `OBSIDIAN_WIKI_PRIMARY_LANGUAGE`。

- 單語 vault：tree 留空，全部走 fallback（等效原 `primary-only`）
- 多語 vault：tree 加 path-based / tag-based rules（等效原 `domain-anchored`）

Rationale: rejected `primary-only` 因為等效於 empty-tree domain-anchored；rejected `auto` 因為 vault notes 大部分無 source.language frontmatter，99% fall back；rejected `source-language` 因為 cross-source 演算法未定且設計者自評可不實作。砍掉 2 strategies + 重命名後，code path / config enum / mental model 全部 -1。詳細 trade-off 見 §Alternatives Considered。

### §3 Config schema 擴充

`.obsidian-wiki.config` 新增 3 個 optional 欄位（向後相容；舊 vault 沿用 legacy 行為）：

```
# Vault primary body language for wiki/ pages. BCP-47 codes.
# Used as fallback in decision tree (§2). Required when LANGUAGE_POLICY=enabled.
OBSIDIAN_WIKI_PRIMARY_LANGUAGE=zh-TW

# Switch: enabled runs the decision tree in language-policy.md.
# Omit (or empty) → legacy LLM heuristic (current v3.10.0 behavior).
OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled

# Optional vault-owned term-preservation list. Terms never translated.
OBSIDIAN_WIKI_PRESERVE_TERMS_FILE=wiki/preserve-terms.txt
```

### §4 Frontmatter schema 變動

既有 8 欄不變（title / type / domain / status / updated / tags / sources_count / summary）。新增：

- **`aliases`** — 條件 MUST：當 slug 語言 ≠ body 語言時必填；否則 MAY
- `title` ↔ body 同語言（slug 永遠 ASCII；不變）
- `summary` ↔ body 同語言（但保留關鍵術語不翻譯）

語意 example（slug `japanese-yohaku-aesthetic`、body zh-TW）：
```yaml
title: "日本余白美學——以「無」為形"
aliases:
  - 余白
  - yohaku
  - 留白
  - white-space
summary: "余白（yohaku）是日本美學的核心概念，..."
```

### §5 Skill 改動清單

| 檔案 | 動 | 規模 |
|---|---|---|
| `obsidian/skills/wiki-ingest/SKILL.md` | pre-flight 加 3 config / lazy-load table 加 1 條 / STEP 4c 加 language resolution | ~20 行 |
| `obsidian/skills/wiki-ingest/references/language-policy.md` | 新增（1 mechanism、decision tree spec、preserve-terms protocol、aliases 規則、worked example） | ~120 行 |
| `obsidian/skills/wiki-ingest/references/page-format.md` | 拆 Filename / Body language 兩節 + aliases 條件 MUST schema 更新 | ~30 行 patch |
| `obsidian/skills/wiki-setup/SKILL.md` | config template 加 3 行 + 註解 | ~10 行 |
| `obsidian/skills/wiki-lint/SKILL.md` + body | 新 lint rule：slug 語言 ≠ body 語言時 aliases 必填 | ~30 行 |
| `obsidian/scripts/distribute.py` | 新增（仿 code-toolkit）— sync language-policy.md byte-identical 到 sibling skills | ~80 行 |
| `obsidian/scripts/verify-drift.py` | 新增（仿 code-toolkit）— CI enforce | ~50 行 |
| `.github/workflows/test-obsidian.yml` | 加 verify-drift step | ~5 行 |
| `obsidian/skills/wiki-cross-linker/references/language-policy.md` | distribute.py 寫入的 functional copy | auto-gen |
| `obsidian/skills/wiki-query/references/language-policy.md` | functional copy | auto-gen |
| `obsidian/skills/wiki-lint/references/language-policy.md` | functional copy | auto-gen |
| `obsidian/skills/wiki-auto-research/references/language-policy.md` | functional copy | auto-gen |

**Total**：6 真改 + 4 auto-gen copies + 2 新 script + 1 CI patch ≈ **~450 LOC**

### §6 Test 計畫

`obsidian/tests/wiki_ingest/test_language_policy.py`（pytest，parametrize CC-LL-01..05）：

- **CC-LL-01**：legacy mode（`LANGUAGE_POLICY` unset）→ 行為跟 v3.10.0 一致（regression guard）
- **CC-LL-02**：enabled + empty tree → 全頁 body = `PRIMARY_LANGUAGE`（單語 vault 等效）
- **CC-LL-03**：enabled + tree 有 path-based rules → 不同 source 路由到不同語言（多語 vault）
- **CC-LL-04**：preserve-terms 生效（指定詞不翻譯，跨語言保留）
- **CC-LL-05**：aliases conditional MUST（slug = ASCII slug、body = zh-TW，frontmatter 必含 aliases）

額外：
- `obsidian/scripts/test_distribute_smoke.py`：distribute.py + verify-drift.py smoke test（sync 正確 / CI 能 catch drift）
- wiki-lint 新規則：unit test for slug-body language mismatch + aliases absence → 報 warning

### §7 Commit 切分（candidate — writing-plans 階段微調）

| Commit | 內容 | LOC 估 |
|---|---|---|
| 1 | config schema + SKILL.md patch + language-policy.md + page-format.md split + wiki-setup template | ~250 |
| 2 | distribute.py + verify-drift.py + 4 functional copies + CI step | ~200 |
| 3 | wiki-lint 新規則 + pytest CC-LL fixtures + dogfood on kouko-obsidian-vault | ~150 |

→ **3 commits / 3 plans (part-1/2/3)** 跟昨天節奏一致

### §8 PR 命名

- Branch：`feat/wiki-ingest-language-policy`（已開）
- PR title：`wiki-ingest: language policy + multi-language frontmatter aliases (v3.11.0)`
- 版本號跳 minor（v3.10.0 → v3.11.0）— 新 feature、backward compat、不破壞既有 explicit 用法

## What Becomes Obsolete

- **LLM 隱性英文偏好**作為唯一行為：當 `LANGUAGE_POLICY=enabled`，行為改由 decision tree 顯式定義。Legacy fallback 仍存在但僅作 backward compat。
- **page-format.md 混合 filename + body rules**：拆兩節後，「filename 規則歸 page-format.md / body 語言歸 language-policy.md」明確分權。
- **frontmatter aliases 的 "好習慣" 地位**：升級為 lint-enforced 條件 MUST，從非結構化善意變成驗證 invariant。

同 PR 內 strip / replace 上述死碼 / 模糊定義。

## Alternatives Considered

### Mechanism 數量（已拍板 1-mechanism binary switch）

- **A. 4 strategies (原 design note)**: primary-only + domain-anchored + source-language + auto. Reject — `source-language` cross-source 演算法未定（設計者自評可不實作），`auto` 99% fall back（vault 大部分無 source.language frontmatter）。
- **B. 2 strategies**: primary-only + domain-anchored. Reject — `primary-only` 等效 empty-tree domain-anchored，命名重複徒增 2 code paths。
- **C. 1 mechanism + binary switch** ✅ — 採用。所有差異移到 language-policy.md decision tree；config 從 enum 收斂為 on/off；單語 vault = empty tree、多語 vault = custom tree。
- **D. 1 strategy: primary-only only**: 砍 decision tree 整體。Reject — 多 domain vault 的 ja-term 表達力會嚴重退化。

### Migration scope（已拍板 natural drift only）

- **A. natural drift** ✅ — 採用。source 修改 → 下次 ingest auto re-render；舊頁 UNCHANGED 桶不會自動重渲染。優：低風險；缺：80 既有頁短期內仍 legacy。
- **B. `/wiki-relang` MVP 內**: Reject — +2-3 hr 實作 + 80 頁 LLM regenerate 30+ 分鐘現場時間 + 大 token cost。/wiki-relang 本身是 Phase 2 PR scope。
- **C. `OBSIDIAN_WIKI_FORCE_RELANG=true` flag**: Reject — 半量緩解，flag 仍要 +30min 實作，且 force-re-ingest 邏輯跟 SHA-256 manifest 機制概念衝突。

### Title 語言（已拍板 same as body）

- **A. title 跟 body 同語言**, slug 不變 ✅ — 採用。aliases 補另語做跨語連結。內容一致 / UX 直覺。
- **B. title 永遠英文**, body 獨立: Reject — 看 title (英) vs body (中) 認知負擔。
- **C. 加 `title_lang` 欄位**: Reject — over-engineered，沒人這麼設。

### aliases 必要性（已拍板 conditional MUST）

- **A. 條件 MUST**（slug 語言 ≠ body 語言時必填） ✅ — 採用。wiki-lint 加新規則執行。Schema 8 欄 + conditional 9th。
- **B. MAY (advisory)**: Reject — 跨語連結沉默失效；design note Layer B 明說 "REQUIRED"。
- **C. 無條件 MUST** (所有頁面強制): Reject — 大部分英文 vault 用不到 aliases；強制變成 8 欄 + 空陣列雜訊。

### SSOT 部署（已拍板 C distribute.py byte-identical）

- **A. 各 skill 自帶 copies** (現行 page-format.md 模式): Reject — design note 自承「page-format.md 已有 drift 前科」，無 enforcement。
- **B. `obsidian/shared-references/` greenfield**: Reject — 需要改 plugin 載入路徑（CLAUDE.md 規定 bundled files 從 skill 目錄相對解析），可能觸發 hook 違規；風險高。
- **C. distribute.py + verify-drift.py byte-identical sync** ✅ — 採用。仿 code-toolkit `_baseline.md` / `_reviewer-discipline.md` 既有模式；不需改載入路徑；CI 強執行。

## Out of Scope

- `/wiki-relang` migration 命令 — Phase 2 future PR（觸發條件：MVP dogfood 後使用者覺得 80 既有頁需要 backfill；或半年後 vault 再多累積 dozens of pages 才有節省成本）
- `auto` strategy（讀 source.language frontmatter）— Phase 2；觸發條件：使用者開始系統化在 source notes 加 `language:` 欄
- `source-language` strategy — Phase 2；觸發條件：明確 cross-source 跨語整合需求出現 + 多數決演算法定案
- preserve-terms 的 per-domain scope（如「余白」JP 設計頁保留但金融頁不保留）— YAGNI；MVP 用 global
- 多語 summary（雙語 summary，前段 zh-TW 後段 en）— design note 未明示，視作 single-language summary
- Cross-skill: wiki-cross-linker / wiki-query / wiki-auto-research 的 SKILL.md 主體不動 — 只新增 `references/language-policy.md` functional copy（由 distribute.py 寫入）。**wiki-lint 是 exception** — 除了 functional copy，主體加新 lint rule（slug 語言 ≠ body 語言 → aliases 必填）；見 §5。

## Open Questions（送 writing-plans / review 階段）

1. **domain-anchored decision tree 的「generic 版」vs「kouko vault 版」**：design note Q1 提到 default tree 可能偏 kouko（如 `investing/` → zh-TW、JP 設計 cluster → ja-term preservation）。MVP 是否做 generic tree（少預設具體類別）讓 vault 自己 fork 客製？或先做 kouko 客製 tree 當 example？傾向 generic + Examples 章節給 kouko-style tree 作參考。
2. **distribute.py 的 SSOT header format**：是否需要 5-line SSOT header（同 code-toolkit `_baseline.md`）？或更輕量的 SHA-256 hash compare？傾向跟 code-toolkit 同 — 5-line BEGIN/END marker 已有讀者熟悉度。
3. **wiki-lint 新規則 severity**：slug 語言 ≠ body 語言時 aliases 缺失 → SHOULD（warning） vs MUST（error）？MVP 傾向 SHOULD（warning + 提示 fix），Phase 2 review 後再決定升 MUST。
4. **kouko vault 80+ 既有頁 migration timing**：MVP 不含 `/wiki-relang`，PR description 是否提供 "手動 `/wiki-ingest --force` 個別 re-ingest" 的 workaround？目前 wiki-ingest 沒有 `--force` flag — 要嘛 PR description 不提（純自然 drift），要嘛 Phase 2 加 force flag。傾向不提，Phase 2 一起處理。

## References

- Upstream design note：`~/kouko-obsidian-vault/research/2026-05-18 wiki-ingest 語言策略優化設計研究.md`
- Predecessor spec (v3.10.0 oldest-first)：`docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md`
- Current SKILL.md：`obsidian/skills/wiki-ingest/SKILL.md`（v3.10.0 head, PR #307 merged）
- Page-format spec：`obsidian/skills/wiki-ingest/references/page-format.md`
- Sibling skill family：`obsidian/skills/wiki-{cross-linker,query,lint,auto-research,setup}/`
- SSOT pattern reference：`code-toolkit/scripts/distribute.py` + `code-toolkit/scripts/_baseline.md`（5-line SSOT marker convention）
- CI pattern reference：`.github/workflows/test-obsidian.yml`（PR #307 新增、可擴充 verify-drift step）
