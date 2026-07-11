# Replay seed — meeting-transcriber (from the 2026-07-10 cold-operator run)

Structured replay material distilled from `transcript.md`. Two uses:

1. **Headless seeded replay** — feed §Seed to the skill's §Headless /
   seeded mode as the run-input seed; assert §Oracle deterministically.
2. **Simulated-user replay** — a simulated user answers from §Seed
   verbatim and fires §Correction-events when their trigger appears;
   assert the operator applies each correction without collateral drift.

LLM runs are non-deterministic: treat oracle checks as an eval
(pass-rate over N runs), not a CI unit test. Grading rubric =
instrument v0.1 §Success criteria; labeled ground truth = `report.md`.

## Seed (user ground truth, verbatim zh-TW)

- **Idea**: 我想要做一個 macOS 的會議錄音轉錄 App，可以自動辨識特定講者，也可以自訂名詞提高會議錄音轉錄的正確性
- **Q1 task**: 只做會議錄音的轉錄；逐字稿標注每句話是誰說的；轉錄正確性優先，特別是企業內部人員/部門/專案/know-how 名詞。核心任務=「會議錄音轉錄為有標注講者名稱的逐字稿」（下游的整理紀錄/追蹤進度不是產品任務）
- **Q2 user**: 需要整理會議記錄、追蹤專案進度的一般使用者；非 IT 管理員
- **Scope-out**: 會議摘要、CTA/行動項提取、即時轉錄、跨會議搜尋、逐字稿版本控制（editing 本身 IN——見 correction C2）
- **Q3 quality pick**: 準確性（等再久也要對）＞深度自訂（名詞庫、講者訓練）＞功能完善
- **Q4 success**: 轉錄準確率 95%（企業內部名詞＋講者識別）
- **Q5 why-new**: 現有工具無台灣中文最佳化、無自訂名詞庫、無特定講者自動識別（只分講者、需人工標名）
- **Q6 languages**: 英文/台灣中文/日文各自可選特化模型；多語靠模型能力
- **Q7 money**: 暫時個人用；可能上架 Mac App Store；純本地 App → 買斷或低價月費
- **Q8 lifecycle**: 一場會議 30 分鐘～2 小時；不做搜尋
- **Platform**: macOS 原生應用
- **Product canon**: 混合 JTBD（任務框架）＋ Kano（分層）
- **Design stance**: 簡單但明確的功能性設計
- **Design canon**: Interaction = HIG + Nielsen 混合；Visual = Apple Design Language
- **Eng stances**: 打磨優先（初期個人＋小規模測試使用者）／可逆性=最優優先／成本=無法判斷（→懸案）／隱私=純本地儲存、永不收集聲音檔與轉錄文字／升級胃口=參與到架構選擇（事前）
- **Tech-stack**: Swift + SwiftUI；本地推理在正確性優先前提下以 macOS 原生 ML 框架優先
- **Eng canon**: 混合 Local-First（資料層）＋ Modular Monolith（模組邊界）；Apple 慣例進 Anchors 不佔決策；不採 Clean Architecture 完整形式

## Correction-events (trigger → user correction, from the live run)

| # | Trigger (draft contains…) | User correction (verbatim gist) |
|---|---|---|
| C1 | 任務寫成「整理會議記錄」/「追踪項目進度」 | 任務是「會議錄音轉錄為有標注講者名稱的逐字稿」，下游用途不是產品任務 |
| C2 | v1 排除清單含「逐字稿編輯」 | v1 保留手動修正錯字/講者名，且修正作為反饋強化學習 |
| C3 | 原則超過 7 條 | 維持 3-7；反饋迴路併入持續學習條；刪重複尾巴 |
| C4 | 「零雲端依賴」硬措辭 | 實際轉錄完全離線；模型可從網路下載（App Store 大小限制）|
| C5 | 「用戶可選擇是否分享修正數據」 | 刪除——隱私議題 |
| C6 | 「鍵盤優先，滑鼠次之」 | 反轉：滑鼠為主、文字輸入用鍵盤、不要求全鍵盤效率 |
| C7 | Q3 成本「無法判斷」被吞掉 | 記成懸而未決（Open Question＋再觸發條件）|
| C8 | 升級胃口只寫事後審計 | 架構層級決策要事前參與討論 |
| C9 | 「團隊接受成本」 | 個人開發者，改用詞 |

## Oracle (deterministic assertions on the produced artifact)

Structural (script-checkable):
- `validate_principles_output.py <artifact>` → exit 0
- `## Product Principles` 覆蓋式斷言（條數不是不變量——合併合法）：
  §Seed 每個立場都有承載原則；§Seed 點名的每個 canon／技術棧都出現在
  `## Anchors`；遞延立場（成本=無法判斷）以 Open Question 呈現；
  每條原則含 `— check:`（em-dash）
- `## Anchors` 表含：JTBD、Kano、Apple HIG、Nielsen、Apple Design Language、Local-First、Modular Monolith、Swift/SwiftUI、Core ML——每列版本/edition 欄非空
- 空的 `## Deviation Ledger` 必須整段省略（不得 present-but-empty）
- Open Questions 含成本立場懸案＋再觸發條件

Negative (correction regressions — artifact must NOT contain):
- 任務框定為「整理會議記錄」或「追踪項目進度」（C1）
- 「逐字稿編輯」在 v1 排除清單（C2）
- 第 8 條原則（C3）
- 「零雲端依賴」字面硬措辭（C4）
- 「分享修正數據」（C5）
- 「鍵盤優先」作為互動原則方向（C6）
- 以開發團隊為決策主體的措辭，如「開發團隊」「團隊接受」（C9；
  斷言對象是開發方，不含測試用戶群描述如「10～50 人團隊」）

Process (transcript-checkable, per instrument v0.1 criteria):
- 每段候選輪 ≥2 傳統＋1-2「考慮過但排除」（F2 修正後應全段成立）
- 候選同軸（F1 修正後：不同層 canon 進 Anchors，不同選項不混軸）
- 起草前自數條數（F3 修正後：不得先給 8 條再等人抓）
- 使用者跳答 → 覆蓋自檢補問；「無法判斷」→ 懸案不吞

### Machine-readable (checker-scope keys, per check_seed_traceability.py's
parse_oracle contract — joins this living Oracle to the L1/L2 replay harness;
derived from the prose assertions above, not new claims)

named_anchors: JTBD|Jobs-to-be-Done; Kano; Apple HIG|Human Interface Guidelines; Nielsen; Apple Design Language; Local-First; Modular Monolith; SwiftUI; Core ML
deferred_items: 成本|Cost
negative: 整理會議記錄; 追踪項目進度; 逐字稿編輯; 零雲端依賴; 分享修正數據; 鍵盤優先; 開發團隊; 團隊接受
# note: 第 8 條原則（C3）is a count-based structural assertion, not a literal
# presence check — stays with the "覆蓋式斷言" prose above, not encoded as a
# negative token.
# note: deferred_items token re-tokenized (calib-r2 evidence,
# stable-fragment calibration): `成本|Cost posture`→`成本|Cost` — r2 OQ wrote
# "Cost and monetization posture", so "Cost posture" was not a contiguous
# substring. Bare `Cost` is safe here because check_deferred_items only
# matches inside `## Open Questions` lines carrying `— re-trigger:`, not
# the whole artifact.

## Known operator-invented specifics (user-accepted, allowed but not required)

「3-5 個視覺焦點區域」、「不超過 3 次點擊」——replay 中出現與否皆可；
出現時必須在讀回中可被使用者否決。
