# AI 駕馭工程迭代 Roadmap（2026-07-06）

> 來源：Fable 5 制度外化 session 收尾時的全 repo 開放項掃描（BACKLOG 17 條
> ＋harness-engineering audit 6 建議＋各 plugin parked 項）× 本場一手摩擦數據。
> 排序標準：**哪些直接決定弱模型時代這套制度的存活**，不是完成度。
> 方法論主軸（本場驗證過的迴圈）：診斷拿真數據 → 能機械就機械（hook/lint/CI）
> → 不能機械的寫成盲測過的 rubric → 用 eval 盯衰變。

## 1. G4：Sonnet-vs-Fable review 品質 A/B ⏳有窗口期

- **為什麼第一**：弱模型未來的核心未知數=「Sonnet 級 gate 守不守得住」。
  沒數據前，所有制度都是猜測。Fable 側窗口有期限。
- **設計**（升級自 BACKLOG:65）：用 PR #501 pre-fix 狀態 `1b8e2a5b` 當
  測材——它自帶 5 個磁碟可驗的 ground-truth 發現（2🟡 doc-drift＋3🟢）
  ＋已知正確 verdict（NEEDS_REVISION）。兩 tier 各 2 次盲審（prompt 完全
  相同、不提已知發現），量：已知發現 recall、新發現的磁碟裁決（真/誤報）、
  verdict 值是否通膨、token 成本。
- **驗收**：報告落 `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`，
  含逐發現對照表＋「Sonnet gate 可信度」結論＋二值 verdict 通膨檢驗。
- **狀態**：本 session 開工（2026-07-06）。

## 2. Gate 摩擦削減包

- **為什麼**：gate 貴到一定程度，使用者與弱模型都會繞路——制度從繞路處
  開始爛。本場實測摩擦：verdict/marker 格式撞 3 次、git-guard cwd quirk
  1 次、docs-only 單檔 branch 全額 review 儀式 ×2。
- **內容**：(a) patch-id 放寬 strict-HEAD marker（BACKLOG:33c，摩擦數據
  今日 +2）；(b) verdict schema 驗證器（audit Rec 6——反向用：讓 reviewer
  産出時自檢，不是只在 marker 寫入時炸）；(c) git-guard cwd 解析修正
  （memory: loom-git-guard-evaluates-in-shell-cwd）；(d) marker 格式規格
  寫進 loom-code 文件（dimension_scores 必備、「N passed」格式、
  marker 與 push 分開下）。
- **驗收**：同類摩擦在後續 3 個 PR 週期內出現 0 次。

## 3. 路由健康機械化

- **為什麼**：百餘 skill 的環境，路由是血管；且已確認會**靜默**衰變
  （memory: skill 清單描述被 harness 丟棄、per-skill 1536 chars、
  name-only 無法 auto-trigger、built-in 搶路由）。
- **內容**：(a) description 預算 lint 進 CI（CC 1536 eviction＋Codex 1024
  hard limit 雙上限）；(b) firing harness 離線半套進 CI（audit Rec 5：
  validate_corpus＋grade）；(c) corpus `expected` 過窄修正（BACKLOG:107）；
  (d) `error_max_turns` 記錄正常評分（7/4 dogfood next-touch，6/28 有效
  樣本被誤丟）；(e) **telemetry 探針過濾**（2026-07-06 /insights 後新增）：
  firing/dogfood harness 產生的 session 混入 facets 與 insights
  （App-Prototyping 7 場 not_achieved 實為 A/B 探針）——harness session
  應可識別排除（固定 cwd 前綴或標記），否則挖礦永遠混入自家探針。
- **驗收**：CI 能在 description 超限/corpus 破損時擋 PR；live 清單 spot-check
  無 name-only skill。

## 4. 機械 gate 第二波

- **內容**：audit Rec 2（擋 `git commit --no-verify`）＋Rec 3（Stop hook
  強制 package 級測試）＋TDD Guard pilot（BACKLOG:48，含 zero-new-test
  branch 的 reviewer 義務＋carve-out 事前宣告）。
- **依據**：git-guard 模式已被證實（本場多次正確攔截）；方向=把
  verification-before-completion 從 prose 變 hook。
- **驗收**：pilot 在一次真實 SDD run 量測 latency/spend/false-block 後
  做 adopt-vs-build 決定。

## 5. 證據基礎設施 ✅（2026-07-06 完成）

- `/insights` 已跑（63 sessions 分析）；facets 已暖，distill-sessions
  脫離 heuristic 盲跑。報告採納項落地：CLAUDE.md 注入碼條款（四 host）、
  reception batch-intake 規則、BACKLOG:93 優先級調升。

## 6. 債務清掃 bundle（一個 PR 收完）

- 刪 BACKLOG 已出貨的「SessionStart reception slimming」條目（completed
  即刪慣例）；4 個 🟢 nit（test 註解 bounds、ROADMAP:105、codex manifest
  longDescription、router-card「Skill tool」措辭）；sibling plugin SKILL.md
  frontmatter 版本 drift gate（BACKLOG:122）；本檔＋Codex port 設計書若
  尚未 commit 一併帶入。

## 7. 儀式比例感（2026-07-06 /insights 後新增）

- **證據**：insights 三大摩擦全指向「儀式擋住小請求」——TDD 儀式擋
  小修改、intake 卡 pipeline、session 停在 brainstorming 無產出。
  這是與 token 診斷正交的軸：那邊量錢，這邊量「沒交付」。
- **內容**：(a) 路由層 trivial 識別強化（tdd-iron-law §When-NOT-to-Use
  與 reception negative guard 已存在但觸發不良——需 firing 測試驗證）；
  (b) 引導「quick fix」信號的使用慣例；(c) 測量污染折扣（見 item 3e）。
- **不做**：不在 CLAUDE.md 放「簡單請求跳過 TDD」全域條款（與 iron law
  打架；正解在路由層）。

## 明確不做（本輪）

- **全自動 pipeline**（loom-pipeline parked）——re-trigger（分段模式 ≥3 次
  真實跑穩）未滿足；先把 gate 做便宜、評測做實，再談拿掉人。
- **Codex port 執行**——設計書已備
  （[2026-07-06-codex-port-design.md](2026-07-06-codex-port-design.md)），
  等真實 Codex 工作 session 觸發。

---
Changelog:
- 2026-07-06 初版；item 1 同日開工。
