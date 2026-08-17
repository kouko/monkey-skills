# Plan: loom-design merge (6 plugins → 2)

**Source brief**: `docs/loom/research/2026-08-15-loom-plugin-consolidation.md`（vault 研究筆記，Option B 收斂 2 個）
**Goal**: 把 4 個設計側 plugin（discovery / product-principles / interface-design / spec）＋ loom-pipeline 併成單一 `loom-design`；loom-code 原封不動並承接家族基礎設施。plugin 間耦合收斂為：僅兩個 plugin、無退役名殘留、loom-design 不依賴 loom-code 內部實作（見 §6／§9 修訂記錄）。
**Stage**: planning（本文件是遷移藍圖，非可執行 SDD plan；執行時再拆成 writing-plans 格式）
**Status**: 定案（D1/D2/D3 全數拍板）— 執行時每步拆成 writing-plans 格式走正常 git flow

## 0. 目標形（TL;DR）

| 維度 | 現狀 | 目標 |
|---|---|---|
| Plugin 數 | 6 | **2**（loom-code、loom-design） |
| Skill 數 | 27 | **24**（4 個設計 router 併 1） |
| loom-design skill 數 | — | **10**（1 router + 9 member） |
| 依賴方向 | 6 個 plugin 互相引用 | **2 個 plugin**，無退役名殘留；loom-design 不依賴 loom-code 內部實作（詳見 §6／§9） |
| 家族 hooks | loom-pipeline/hooks/ | **loom-code/hooks/**（loom-code 依賴它們） |
| loom-memory | loom-pipeline | **loom-code**（已定，§3 D2） |
| Marketplace entries | 6 | **2** |

**不變的**：`loom-code:*` 全部 13 個 skill 名與 5 個 agentType（440 次派遣的依賴）——熱路徑零衝擊。

## 1. 目標結構

### 1.1 loom-design（新 plugin，設計方法論 + 指揮）

```
loom-design/
├── skills/
│   ├── using-loom-design/        # ← 新，4 個 router 合併（~70% skeleton 重疊）
│   ├── using-loom-pipeline/      # 指揮（自 loom-pipeline 原樣搬入）
│   ├── business-value/           # 自 loom-discovery
│   ├── user-insights/            # 自 loom-discovery
│   ├── product-principles/       # 自 loom-product-principles
│   ├── design-system/            # 自 loom-interface-design
│   ├── interaction-flows/        # 自 loom-interface-design
│   ├── design-critic/            # 自 loom-interface-design
│   ├── spec-expansion/           # 自 loom-spec
│   └── completeness-critic/      # 自 loom-spec
├── scripts/                      # validate_*output.py + mint_critic_verdict.py 去重後
├── examples/                     # spec 的 change-folder 範例
├── assets/                       # loom-pipeline.js（重建後）
├── .claude-plugin/plugin.json    # 1 組 manifest（原 5 組）
└── .codex-plugin/plugin.json    # codex 鏡射（含 interface block）
```

### 1.2 loom-code 新增（家族基礎設施）

```
loom-code/
├── hooks/
│   ├── family-reception.md       # 自 loom-pipeline/hooks/（搬遷，非廢除）
│   ├── family-relay.md           # 自 loom-pipeline/hooks/
│   ├── plain-relay.md            # 自 loom-pipeline/hooks/
│   ├── lang_detect.py            # 自 loom-pipeline/hooks/
│   ├── language-anchor.py        # 自 loom-pipeline/hooks/
│   ├── language-stop-check.py    # 自 loom-pipeline/hooks/
│   ├── session-start             # 與現有 session-start 合併
│   └── hooks.json                # 合併註冊
└── skills/loom-memory/           # 自 loom-pipeline（§3 D2 已定）
```

**理由**：Agent 3 實證 loom-code 用 6 個相對路徑引用 family hooks（`hooks/family-relay.md:117 → ../../loom-code/...`）。hooks 是家族連接組織，放永遠開著的 loom-code 才做到「一份、全家指向」。筆記原案「廢除 reception 卡」修正為「搬遷」——loom-code 依賴它，不能廢。

## 2. 改名對照（引用重指的核心）

| 舊（plugin:skill） | 新（plugin:skill） |
|---|---|
| `loom-discovery:using-loom-discovery` | `loom-design:using-loom-design` |
| `loom-interface-design:using-loom-interface-design` | `loom-design:using-loom-design` |
| `loom-spec:using-loom-spec` | `loom-design:using-loom-design` |
| `loom-product-principles:using-loom-product-principles` | `loom-design:using-loom-design` |
| `loom-discovery:business-value` | `loom-design:business-value` |
| `loom-discovery:user-insights` | `loom-design:user-insights` |
| `loom-interface-design:design-system` | `loom-design:design-system` |
| `loom-interface-design:interaction-flows` | `loom-design:interaction-flows` |
| `loom-interface-design:design-critic` | `loom-design:design-critic` |
| `loom-spec:spec-expansion` | `loom-design:spec-expansion` |
| `loom-spec:completeness-critic` | `loom-design:completeness-critic` |
| `loom-product-principles:product-principles` | `loom-design:product-principles` |
| `loom-pipeline:using-loom-pipeline` | `loom-design:using-loom-pipeline` |
| `loom-pipeline:loom-memory` | `loom-code:loom-memory` |
| `loom-code:*`（13 skill + 5 agentType） | **不變** |

**member skill 保持原名**，只改 plugin 前綴——blast radius 最小化。

## 3. 三個設計決定（待 kouko 拍板）

| # | 決定 | 選項 | 建議 |
|---|---|---|---|
| D1 | 家族 hooks 去處 | (a) 搬進 loom-code；(b) 留 loom-design 當新 hub | **(a)**——loom-code 依賴它們，放 loom-code 才自足 |
| D2 | loom-memory 歸屬 | (a) loom-code（家族資產）；(b) loom-design（筆記原案） | **(a) 已定**——家族實務記憶，使用以 loom-code 為主 |
| D3 | member skill 改名 | (a) 保持原名；(b) 加設計側前綴 | **(a)**——改名只影響前綴，member 名不動 |

## 4. 引用重指（blast radius）

掃描結果：**~380 檔引用 5 個 plugin 名，~160 檔會斷**。分類：

| 類別 | 檔數 | 會斷 | 處理 |
|---|---|---|---|
| (g) driver + 編譯產物 | 11 | **11** | 重建 `assets/loom-pipeline.js`（不可手改） |
| (d) CI / tests | ~134 | ~60 | 更新斷言（含 `test_pipeline_skill_contract.py:45` 的 `loom-pipeline: N/A` 字串） |
| (e) manifests | 12 | **12** | 5 組 → 1 組；marketplace 6 → 2 |
| (b) loom-code | ~26 | ~20 | 重指 family hooks 相對路徑 + 散文引用 |
| (a) 5 plugin 內部 | ~55 | ~40 | 內部互指改 `loom-design:` |
| (c) docs/ | 226 | ~13 | 只改可執行引用；`docs/loom/` 散文屬存檔，可留 |
| (f) root 散文 | 4 | **4** | 改 |

**安全區**：root READMEs、`docs/loom/` 散文、CHANGELOGs（歷史記錄，不回溯改）。

**driver 內嵌名**（`driver_*.js` 源碼，改後重建）：
- 11 個 `loom-*` 限定名 → `loom-design:*`（`loom-code:*` 4 個 agentType 不變）
- `driver_40_seg2.js:127` 硬編碼 `loom-spec/scripts/validate_spec_output.py` → `loom-design/scripts/validate_spec_output.py`

## 5. 分步執行

> 執行時每步拆成 writing-plans 格式（RED/GREEN acceptance）。以下為順序與依賴。

```mermaid
flowchart LR
    S1["S1 建骨架<br/>git mv 5 plugin → loom-design/"] --> S2["S2 併 router<br/>4 → using-loom-design"]
    S1 --> S3["S3 搬 hooks<br/>→ loom-code"]
    S1 --> S4["S4 搬 loom-memory<br/>→ loom-code（D2）"]
    S2 --> S5["S5 重指引用<br/>driver/CI/docs/manifests"]
    S3 --> S5
    S4 --> S5
    S5 --> S6["S6 重建 driver<br/>build_driver.py + drift test"]
    S5 --> S7["S7 收斂 manifest<br/>5→1 組，marketplace 6→2"]
    S6 --> S8["S8 docs sweep"]
    S7 --> S8
    S8 --> S9["S9 驗收<br/>冷讀者路由 + 全 pytest"]
```

- **S1 建骨架**：`git mv` 保留歷史；5 個 plugin 目錄併入 `loom-design/`，subfolder 扁平化（skill 結構規範：subfolder 內不可再嵌 subfolder）。
- **S2 併 router**：4 個 `using-loom-*` 併 1，骨架去重（~70% 重疊）；`using-loom-pipeline` 不併（是指揮不是 router）。
- **S3 搬 hooks**：family hooks + 語言 hooks → loom-code；loom-code 的 6 個相對路徑引用重指；hooks.json 合併註冊。
- **S4 搬 loom-memory**：→ loom-code（D2 已定）。
- **S5 重指引用**：§4 分類逐類處理；driver 源碼改 11 個名 + 1 個路徑。
- **S6 重建 driver**：`build_driver.py`（串接 driver_00→90 → assets/loom-pipeline.js）；`test_pipeline_driver_drift.py` byte-identical 驗證。
- **S7 收斂 manifest**：5 組雙 manifest → 1 組；marketplace.json 6 → 2；codex interface block 保留。
- **S8 docs sweep**：只改可執行引用（§4 (c) 的 13 檔）。
- **S9 驗收**：§6。

## 6. 驗收清單

| 檢查 | 基線 | 目標 |
|---|---|---|
| 冷讀者路由測試 | — | 全新 context agent 只憑 2-plugin 佈局正確路由「產品點子→設計站」與「改 code→loom-code」 |
| driver drift test | — | `test_pipeline_driver_drift.py` 通過（重建 byte-identical） |
| 全 pytest | — | 綠（含更新後的 ~60 個斷言） |
| loom skill 清單 | 27 | **24**（router 4→1） |
| 每 session 注入 bytes | ~9.5K | 下降（reception 卡合併、router 卡併 1） |
| 依賴方向 | 6 向互指 | 恰兩個 loom plugin（loom-code、loom-design）；可執行面無 5 個已退役 plugin 名稱的殘留引用；`loom-design/` 引用 `loom-code/{skills,scripts}/` 的檔案**不得超出下列白名單 9 檔**（逐檔列舉，非類別標籤——新增任何一檔都要在此表補行並說明理由，否則視為違反）：`scripts/interface/{design_md_spec_keys,test_design_md_schema_keys}.py`、`scripts/pipeline/{test_family_relay,test_language_anchor,test_loom_memory_record_contradiction,test_pipeline_ci_workflow,test_pipeline_skill_contract}.py`、`scripts/pipeline/fixtures/fixture_session_tail.jsonl`（歷史 session 錄製資料，內容欄位含當時的路徑字串——測試素材的保真度，非程式依賴）、`skills/spec-expansion/SKILL.md`。共享 `loom-code/hooks/` 不計入（family hooks 是雙方共用的基礎設施，非單向依賴）。驗證指令：`grep -rlE 'loom-code/(skills|scripts)' loom-design/ | grep -v 'CHANGELOG-\|README-'` 應恰好回傳這 9 檔 |

## 7. 風險與反轉條件

**風險**：
- 改名 blast radius ~160 檔——可控（§4 分類逐類處理），但需一次做完，中途半套會壞。
- loom-code 的 6 個 family-hooks 相對路徑引用——S3 必須與 S5 同步，否則 loom-code 當場斷。
- driver 重建必須 byte-identical——改源碼後跑 drift test，不可手改編譯產物。
- `test_pipeline_skill_contract.py:45` 斷言 `loom-pipeline: N/A` 字串——改名後要同步更新。
- codex manifest 的 interface block（category/brandColor）——收斂時保留。

**反轉條件**（出現任一，改變建議）：
- 設計側工作流用量起飛（未來 30 天 ≥5 session 實際呼叫設計站）→ 先跑真實 pipeline 拿行為資料再整併。
- 出現真實子集消費者（只想裝 loom-spec 不裝其他）→ CRP 反對合併。
- Claude Code 推出 extension-pack 機制 → 用 pack 解安裝 UX，合併必要性下降。

## 8. 資料來源

- 研究筆記：`docs/loom/research/2026-08-15-loom-plugin-consolidation.md`（vault，§7 遷移清單為本計畫骨架）
- 盤點（Agent 1）：5 plugin / 14 skill 結構；loom-pipeline 為 hub；knowledge-triage / mint_critic_verdict / validate_*output 三模式重複
- 引用掃描（blast radius）：~380 檔 / ~160 斷，§4 分類
- 基礎設施（Agent 3）：4 router ~70% 重疊可併；family hooks 必須進 loom-code；driver 嵌 11 名；PR #696 已去重家族規則（「4+4+5 重複」已過時）
- 用量（本機掃描，`loom-usage-scan.py`）：loom-code 352 skill / 66 session / 3124 agent；設計側有真實使用（discovery 8/5、spec 12/4、pipeline 58/56）——**與筆記「0 呼叫」不同**（筆記數據來自另一台機器）

## 9. 修訂記錄

- **2026-08-17 §6 依賴列二次修正（whole-branch review 🟡 F4）**：第一版改寫（下兩條）雖然把方向改對了，但把豁免寫成「已記錄的跨 plugin contract test」這個**類別標籤**——任何未來耦合只要被稱作 contract test 就能通過，該條因此不可證偽。已改為**逐檔白名單 8 檔**：新增任何一檔都必須在 §6 表補行說明理由，否則即為違反。證據數字經第二輪審查再次修正為 **9 個檔／9 處引用**：前兩版都漏了 `scripts/pipeline/fixtures/fixture_session_tail.jsonl`（掃描時被誤當成非程式碼而略過），且「`spec-expansion/SKILL.md` 有絕對與相對兩種形式」的說法有誤——該檔符合本條款 pattern 的只有 `:457` 一處（`:234` 指向 `loom-code/hooks/`，條款本身已排除）。白名單首次執行即違反的原因就是漏列 fixture；已補行並附驗證指令，使此條款可被單一指令證偽。**遺留待辦**：`loom-design/skills/spec-expansion/SKILL.md:457` 用 `../../../loom-code/skills/...` 相對路徑跨 plugin 逃逸，違反本 repo CLAUDE.md「委派時使用 plugin name，不使用檔案系統絕對／相對路徑」的跨 plugin 契約；此引用早於本次遷移且深度仍正確，不在本分支範圍內修，已立為 backlog。
- **2026-08-17 同一錯誤的另外兩處**：該反向說法在本文件出現三次——§6 表格列（下條）、§0 目標形表格列（L15）、以及開頭 **Goal** 行（L4）。三處已一併改為同一組不變量；只修 §6 會留下兩處互相矛盾的敘述。
- **2026-08-17 修正 §6「依賴方向」列**：原文聲稱依賴只朝設計站到程式碼站單一方向、且 grep 驗證無反向引用，此說法與實測結果相反，已改寫為上表現況。實測 `grep -rlE 'loom-design(:|/)' loom-code/ --include='*.md' --include='*.py'`（排除 CHANGELOG、`/research/`）命中 **20 個檔案**，逐一檢視後全部是合理的下游消費，例如：
  - `loom-code/scripts/check_scenario_coverage.py` 呼叫 spec 站驗證器 `loom-design/scripts/spec/validate_spec_output.py`
  - `loom-code/skills/brainstorming/SKILL.md` 把設計形問題轉介到 `loom-design:spec-expansion`
  - `loom-code/skills/ui-verification/SKILL.md` 透過 `loom-design:design-critic` / `loom-design:interaction-flows` 消費設計產物

  真實資料流是 design → code，因此「code 側引用 design 產物」方向本身就是對的；會構成缺陷的是反向——loom-design 依賴 loom-code 內部實作。反向掃描（`loom-design/` 下引用 `loom-code(:|/)(skills|scripts)`）找到 8 個檔案，但均為已記錄的跨 plugin contract test／家族中繼一致性檢查（例：`test_family_relay.py` 驗證 loom-code 三個 skill 檔的家族中繼文字、`test_pipeline_ci_workflow.py` 驗證 CI 路徑涵蓋 `loom-code/skills/loom-memory/**`、`design_md_spec_keys.py` 引用 `loom-code/scripts/canonical/README.md` 的 frozen-copy key 定義），屬於刻意維護的雙向契約測試，非功能性耦合，與 family hooks 共享案例同屬允許範圍。
