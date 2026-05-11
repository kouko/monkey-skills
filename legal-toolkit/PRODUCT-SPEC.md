# PRODUCT-SPEC — legal-toolkit

> **Owner**: planning (cross-domain — business + design + technical direction)
> **Companion**: [TECH-SPEC.md](TECH-SPEC.md) — module / data-flow / interface contracts (code-team owned)
> **Source of design**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` (1344 lines, 38+ locked decisions in §11 ledger)
> **Roadmap**: [ROADMAP.md](ROADMAP.md) — v0.1.0 → v1.0.0 phase plan

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-05-11 | kouko | Initial spec extracted from design note §1 + §2 + §九 |

---

## 1. Background & Opportunity

### 1.1 Current pain points (Why)

台灣中小企業 in-house 法務（含個人開發者兼任 / 一人 GC）每週工時分布（design note §1.2 + 法務工作流研究 §4.1）：

| 任務 | 工時占比 | 痛點 |
|---|---|---|
| 合約初審 + 條款比對 + redline | **55%** | 重複工作；每家公司紅線散落在 GC 腦袋裡，新人接手 0 knowledge transfer |
| 跨部門諮詢 + issue spotting | 17% | 業務口語丟過來「能不能做 X」要 issue 矩陣 + 構成要件涵攝 |
| 隱私政策 / ToS 起草 + 法規對照 | 13% | 個資法 2025/11 新制條文記不住，逐條漏 GDPR overlay |
| 個資事故 / 主管機關 / 違約應變 | 8% | 72hr 通報窗口 + PDPC 通報文模板每次重寫 |
| 合約 lifecycle + 法規追蹤 | 7% | 自動續約日 / obligations 死角；法規變動沒人 push |

**核心問題**：BigLaw playbook 設計與工具（Sterling Miller / Harvey / Spellbook）以**百萬美金 deal + Adversarial M&A**為前提，對 SME → 上市櫃 in-house **過度工程**；現有台灣本土工具（Lawsnote / 律果）以判例檢索 + 文書產生為主，**沒有 playbook / 沒有 schema-driven 合約審查**。

### 1.2 Why now

- **Long-context frontier model 可用**：playbook entry < 100 條時，全部塞 prompt 比 RAG 更穩（Addleshaw Goddard 2024 證實）→ 個人 / SME 規模終於跑得起
- **個資法 2025/11 新制即將上路**：72 小時通報義務 + 跨境傳輸 + 未成年保護 → 隱私政策 / DPA / 通報文模板需求暴增
- **Anthropic Cowork 開放 "Work in a Folder"**：local FS mount + Markdown-native → playbook 不必塞 vendor cloud
- **monkey-skills marketplace 起穩定**：12+ plugin shipped (translation-toolkit / copywriting-toolkit / investing-toolkit) → 累積 plugin convention (3-lang README / flat subfolder / byte-identical drift) 可直接 reuse

### 1.3 Opportunity framing

> 給台灣 SME → 上市櫃 in-house 法務一個 **Markdown-first / runtime-portable / disclaimer-driven** 的工具組，把高頻 80% in-house 工作（合約審查 + playbook 維護 + 起草 + 應變 + 諮詢 + 追蹤 + 合規）放進可版控、可 audit、可 transfer 的 workflow。**不取代律師**，取代「散落在 GC 腦袋裡的 tacit knowledge」。

---

## 2. Target Users

### 2.1 Primary user

| 維度 | 值 |
|---|---|
| **角色** | 台灣 SME in-house 法務 / 個人開發者兼任法務 / 一人 GC |
| **規模** | 公司員工 < 200；單一法務或法務團隊 ≤ 3 |
| **產業** | SaaS / B2B 服務業為優先（baseline playbook 從這裡 seed），但設計 cross-industry |
| **司法管轄** | 台灣為主（民法 / 勞基法 / 個保法 / 公司法 / 證交法）；GDPR overlay 必備（跨境客戶）|
| **使用情境** | Claude Code CLI（個人開發者）/ Cowork "Work in a Folder" mount（in-house 共用 working folder） |

### 2.2 Secondary user (Phase 4-5)

| 角色 | 何時加入 |
|---|---|
| 上市櫃 in-house 法務（規模 scale up） | Phase 5 corporate-governance + dd-quickscan 上線 |
| 法務主管 / GC（多人團隊） | Phase 6 multi-playbook inheritance（個人 + 公司 + 客戶律所三層）|
| 法律事務所協同（外部律師討論初稿）| Phase 4-5 escalation flow + redline export |

**明確排除**：BigLaw M&A 律師 / 訴訟律師 / 法庭代理。

### 2.3 誰決策 / 誰付費

- **決策者** = 使用者本人（SME / GC / 法務主管）
- **付費** = 無（免費 open-source 工具，monkey-skills marketplace 公開分享）
- **責任歸屬** = 使用者自負其責（Mandatory Disclaimer 強制每份輸出 + Escalation Override 高風險強警告）

### 2.4 Job Story

> 當我（in-house 法務）收到一份對方草擬的 SaaS MSA 要在 24 小時內回 redline，**我想要** 跑工具 5 分鐘拿到 6 份輸出（issue 矩陣 / redline / memo / escalation / self-grade），**讓我** 把 review 時間從半天壓到 1 小時，並確認我家公司的紅線沒漏抓。

---

## 3. Goals & Non-Goals

### 3.1 Goals (MVP v0.1.0)

| # | Goal | 衡量 |
|---|---|---|
| G1 | Plugin installable from monkey-skills marketplace | `/plugin install` 跑得通 + `using-legal-toolkit` 出現在 skill 列表 |
| G2 | Cold-start works without user playbook | 4 條 bundled fallback 命中率 ≥ 50%（NDA / SaaS / 採購 / 勞動 / DPA 5 份 dogfood） |
| G3 | Contract review 7-layer pipeline 跑完 0 跳步 | 5 份合約 dogfood 全部產出 6 份輸出檔案 |
| G4 | Disclaimer + Escalation Override 觸發正確 | 高風險 finding 100% 觸發 Override；每份輸出 100% 含 Disclaimer footer |
| G5 | Playbook author bootstrap 5 題互動完成 1 條 entry | 一個 first-time user 從 0 到第一條 `legal-playbook/confidentiality.md` < 10 分鐘 |
| G6 | 3-lang README + flat subfolder + byte-identical disclaimer 通過 monkey-skills CI 檢查 | `check-marketplace-description-sync.py` + `check-skill-structure.py` + `validate-skill-folder-structure.sh` 全綠 |

### 3.2 Non-Goals (明確拒絕，非明顯 out-of-scope)

| 非目標 | 為什麼拒絕 |
|---|---|
| ❌ BigLaw M&A playbook 移植 | 對方有 ML team 反推、千萬美金 deal、Adversarial threat model → 與 SME / 上市櫃 in-house mental model 不符 |
| ❌ 訴訟策略 / 複雜談判輔助 | 風險過高（design note §1.3 + 法務工作流 §4.3 排除）；仍須人類律師主導 |
| ❌ General legal assistant（什麼都做） | Harvey expand-then-collapse 教訓 — 先窄後廣 |
| ❌ Word add-in / 證交所 / 金管會 e-mail 打通 | Enterprise CLM 領域，個人 skill 不該做 |
| ❌ 收費 / SLA 化變成 service | 律師法 §48 disclaimer-driven 路線需要 「免費工具非服務」 的法律基礎；改 service 會踩線 |
| ❌ 硬排除「法律意見產出」 | 業界 vendor 沒有任何一家這樣做（Harvey / Spellbook / LawGeex / Lawsnote / 律果 全用 disclaimer）；硬排除 = 否定 Phase 3 issue-spot + research 存在 |
| ❌ RAG / 向量檢索 playbook | 個人規模 < 100 entries，RAG over-engineering（Contract Playbook §6.3 + Addleshaw Goddard 反 RAG 結論） |
| ❌ Hidden dotfolder 設計（v0 反轉）| 法務 mental model = playbook 是核心資產不是工具 config；macOS Finder / Cowork mount 預設不顯示 dotfile |

### 3.3 MVP Definition (Phase 1 v0.1.0)

**Done = 5 條缺一不可**：

1. **3 個 MVP skill scaffold completed**：using-legal-toolkit + legal-playbook-author + legal-contract-review，每個都有 SKILL.md + protocols + assets + 3-lang README
2. **Cold-start fallback 4 條 baseline ship 進 plugin**：confidentiality / governing-law-jurisdiction / auto-renewal / termination-and-survival（flat layout）
3. **Disclaimer + Escalation Override 機制就位**：3 個 skill `assets/` 各帶 `disclaimer-block.md` + `escalation-override.md`（byte-identical，Phase 6 CI gate 後驗）
4. **Pipeline DAG 完整**：7-layer + L0a/L0b/L6.5 TW overlay + ABAC pre-filter + Harvey dual-score self-grade
5. **5 份合約 dogfood pass**：NDA + SaaS MSA + 採購 + 勞動契約 + DPA，全部 6 份輸出 + Disclaimer + 高風險 Override 觸發正確

**不在 MVP**：baseline 完整 8 條（含 LoL / Indemnification / DPA variant-folder） / scripts/*.py（validator / ABAC engine / seed） / binary rubric 定量驗證 — 全部 Phase 1.5 + 1.6。

### 3.4 Future Phases (非承諾，僅 trigger 條件)

詳見 [ROADMAP.md](ROADMAP.md) Phase 1.5 → Phase 6。觸發條件：

- **Phase 1.5**：MVP dogfood passed → schema 穩定 → 開工 DSL infra
- **Phase 1.6**：Phase 1.5 done → answer/source criteria 寫得出來 → eval harness 上線
- **Phase 2**：dogfood corpus > 10 份 → 個資法 2025/11 條文細節 lock → draft + IR
- **Phase 3-4**：使用者實際 ask（issue-spot / lifecycle tracker 真實需求）
- **Phase 5**：上市櫃 Compliance prerequisite research 完成（3-5 位 GC primary interview）

---

## 4. Core Concept

### 4.1 Value proposition (one sentence)

> **把散落在 GC 腦袋裡的 tacit knowledge，變成可版控、可 audit、可 transfer 的 markdown playbook，並用 7-layer schema-driven pipeline 跟它對齊每一份合約。**

### 4.2 Core user scenarios

**Scenario A — 接到一份要 review 的合約**

1. 使用者：`/legal-contract-review` + 合約 path
2. 工具：scan `legal-playbook/`（若存在）/ 退到 bundled fallback（若不存在）→ 跑 L0a-L7 pipeline → 產 6 份輸出 → 加 Disclaimer + Override
3. 使用者：拿 `redline.md` 跟對方來回；拿 `escalation.md` 找老闆簽核；拿 `memo-business.md` 給業務看
4. 使用者：發現 LoL fallback 太鬆 → `/legal-playbook-author revise limitation-of-liability/mid-deal.md` 改紅線
5. 下次同類合約 review 自動套新紅線

**Scenario B — 第一次裝、還沒 playbook**

1. 使用者：`/plugin install legal-toolkit@monkey-skills`
2. 使用者：`/using-legal-toolkit` 「我剛裝好」
3. 工具：→ playbook-author bootstrap mode → 三選一：(a) 從 bundled fallback 4 條複製當起點 / (b) 5 題 interview 從零建第一條 / (c) 先不建直接用 fallback read-only
4. 使用者：選 (a) → 4 條 baseline 落到 `legal-playbook/` → 提示 user 每條都改 `escalate_to` 跟公司 review
5. 5 分鐘後使用者已能跑 contract-review，且輸出帶自己的紅線

**Scenario C — 平常 cumulative refinement**

1. 每次 review 後遇到「我對這條其實有意見」→ `playbook-author revise <clause>` 把 walk_away / fallback 改成符合自己版本
2. 每季回頭 review 一次（建議跟業務一起 align）
3. 每年 major update（隨市場行情 / 法規變動）
4. Phase 4 regulation-watch 上線後，主管機關函釋變動會自動 cross-ref playbook 提示改哪條

### 4.3 Key differentiators

| Vs | 差異 |
|---|---|
| **BigLaw playbook 工具（Sterling Miller / Harvey）** | SME 規模合約優先 + 台灣 jurisdiction overlay + visible playbook ownership 而非 vendor cloud |
| **台灣本土法務工具（Lawsnote / 律果）** | Playbook-driven negotiation（他們沒有）+ 7-layer schema review（他們也沒有）+ markdown-first（他們是 web app） |
| **General LLM chat（直接問 Claude / GPT）** | 結構化 7-layer pipeline 不會跳步 + ABAC 決定性 escalation + 6 份結構化輸出 + Disclaimer / Override |
| **Word add-in（Spellbook）** | Markdown-first / runtime-portable（Claude Code + Cowork + 未來 GPT/Gemini）+ git-trackable |

### 4.4 Design principles

1. **Schema-driven over vibe-driven** — 七層 pipeline 決定性執行；LLM 永遠看單一 matched variant，不讓它 choose
2. **Frontmatter deterministic / Body LLM-comparison** — 升級對象 / walk-away / risk_default 由 frontmatter 鎖死；preferred / fallback prose 給 LLM 自由比對
3. **Visible > hidden** — playbook 跟 outputs 都 visible，讓使用者經常 revise；只有 tool internals 藏進 dotfolder
4. **Disclaimer over feature exclusion** — 法律意見產出不硬排除；用 Mandatory Disclaimer + 高風險 Override 管風險
5. **Cold-start works** — 沒自訂 playbook 也要能跑出有意義輸出，否則使用者第一次跑就會放棄
6. **Markdown-first / runtime-portable** — 不綁 Claude Code / Cowork / 任何 vendor；跨 runtime 工作

---

## 5. UX Direction

### 5.1 Core user flow (entry → primary task → outcome)

```
[entry]
   ↓
/using-legal-toolkit （router, intent recognition）
   ↓
   ├── 合約 review/redline/nda → /legal-contract-review
   ├── 建 / 改 playbook → /legal-playbook-author (bootstrap/extend/revise)
   ├── Phase 2-5 sub-skill → not-yet-available + 列 cluster 選單
   └── 識別失敗 → 6-cluster 選單請使用者選
   ↓
[primary task]
   ↓
contract-review → 7-layer pipeline → 6 outputs → legal-outputs/<timestamp>-<contract-name>/
   ↓
[outcome]
   ↓
使用者拿 outputs 跟對方來回 / 跟業務溝通 / 找老闆簽核 / 找律師 escalate
   ↓
[loop back]
   ↓
revise playbook → 下次同類合約 review 自動套新紅線
```

### 5.2 Interaction model

- **CLI invocation**：`/using-legal-toolkit` 或直接 `/legal-contract-review <path>`
- **Question batching**：playbook-author bootstrap 一次問 5 題（避免逐題打斷流程）
- **Per-question persist**：每答一題立即寫回 `legal-playbook/<clause>.md`，中斷不遺失（design note §3.2 決定 14）
- **Progressive disclosure**：bootstrap 三選一（complete / interview / fallback-only）
- **Output is permanent**：6 份輸出檔案落 disk，不靠 chat scrollback；後續可 cite path

### 5.3 Key design constraints

| 約束 | 設計取捨 |
|---|---|
| **Language Policy: 英文骨架 + 中文血肉** | SKILL.md / protocols / scripts / JSON keys = EN（LLM instruction-following 較強）；法條 / playbook body / user output = zh-TW（原文保留） |
| **Skill folder flat subfolder convention** | `<subfolder>/` 內不可再開 subfolder（Anthropic 規範，monkey-skills hook 擋）→ baseline assets 用 prefix-naming flat 或 archive 模式 |
| **3-lang README required** | en / ja / zh-TW 三份（PR #150）— plugin-level + per-skill 都要 |
| **Cowork FUSE pre-existing-file bug** | Phase 2 補 onboarding step；Phase 1 暫不支援 Cowork-native（仍可 mount，但首次 init 體驗有 quirk）|

---

## 6. Cross-Domain Considerations

### 6.1 Business direction

- **Distribution model**：**永遠免費 / open-source**（律師法 §48 disclaimer 的法律基礎），不轉 SaaS / commercial license
- **Sustainability**：依賴 monkey-skills marketplace + Claude Code / Cowork ecosystem；無自有 hosting / 無 user account / 無 billing
- **License**：MIT (plugin code) — 跟 monkey-skills 一致
- **Brand boundary**：明確標 「非律師意見」「免費工具」「使用者自負其責」— 不營造 advisor-client 暗示

### 6.2 Design direction

- **Information design**：6 份輸出檔案各自有清楚 mental model（issues = 矩陣 / redline = 條款替代 / memo-legal = CRAC 完整版 / memo-business = Why-What-Whatif / escalation = 誰簽 + 為什麼 / self-grade = answer/source 雙分）
- **Visual design**：純 Markdown / Github-flavored / Obsidian-compatible callout（>[!important] / >[!warning] / >[!danger]）；無 PDF / 無 HTML / 無 PowerPoint
- **Naming convention**：clause_id = English-kebab-case（confidentiality / limitation-of-liability）；variant_id = English-kebab-case（small-deal / tw-only）；output filenames = English（issues.md / redline.md / memo-legal.md）

### 6.3 Technical direction

詳見 [TECH-SPEC.md](TECH-SPEC.md)。本節僅列關鍵方向：

| 維度 | 方向 | TECH-SPEC 章節 |
|---|---|---|
| **Plugin layout** | flat per-skill 目錄；assets/protocols/scripts/checklists/references 並列 | §2 Architecture |
| **Playbook schema** | per-clause `.md` flat + `<clause-id>/_clause.md + variant.md` 混合 | §4 Interface |
| **Discovery** | cwd → 5 層 ancestors → BFS 深度 5 → bundle | §4 Interface |
| **LLM consumption** | Long context + ABAC pre-filter + structured output（不 RAG） | §4 Interface |
| **Output** | 6 份 .md + 6 個 JSON schema validate | §4 Interface |
| **Cold-start fallback** | 4 條 bundled baseline + L7 fallback branch + escalate_to 佔位符 warning | §6 Cold-Start Fallback chapter |
| **Disclaimer / Override** | 各 skill `assets/{disclaimer-block,escalation-override}.md` byte-identical（Phase 6 CI gate） | §7 Conventions |

---

## 7. Anti-Patterns & Counterfactuals

對應 design note §七 5 種反模式：

| Anti-pattern | 落地防禦 |
|---|---|
| **Bloat（過長無人用）** | entry count SHOULD ≤ 24 條 + body ≤ 200 行（Phase 1.5 validator 警告） |
| **Drift（過期）** | `last_updated` + 180 天 staleness warning（Phase 1 contract-review session start emit） |
| **Conflict（衝突）** | duplicate clause_id + overlapping gates detection（Phase 1.5 `detect_conflicts.py`） |
| **Static（無 enforcement）** | playbook 是 contract-review L7 的 MUST-CHECK 步驟，跳過 = pipeline incomplete |
| **Over-Rigid（律師繞過）** | 每條 entry 必含 `## 為什麼這條重要`（business translation）+ Advisory mode 給沒 playbook 條目時 + escalation 而非 reject |

---

## 8. Open Questions

> 設計階段已 lock 38+ 條決定。仍 open 的 10 條保留給後續 session，**不擋 MVP**。

詳見 design note §10（未複製到本 spec，避免兩處 drift）。會在後續 phase 動工時逐項 close。

---

## 9. References

- **ROADMAP**: [`ROADMAP.md`](ROADMAP.md)
- **TECH-SPEC (companion)**: [`TECH-SPEC.md`](TECH-SPEC.md)
- **Design note (SoT)**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`
- **Parent research (input to design note)**:
  - `2026-05-07 法務工作流與思考方法論——Agent Skill 設計研究.md`
  - `2026-05-07 Harvey.ai 法務 AI 產品方法論深度研究.md`
  - `2026-05-09 法務 Contract Playbook 深度研究——從 BigLaw 到 Agent Skill 的設計原語.md`
- **Phase 5 prerequisite research outline**: `<obsidian-vault>/research/2026-05-09 上市櫃 in-house Compliance 工作流深度研究——大綱與議題清單.md`
- **Repo conventions**: `monkey-skills/CLAUDE.md` / `monkey-skills/scripts/check-marketplace-description-sync.py`
