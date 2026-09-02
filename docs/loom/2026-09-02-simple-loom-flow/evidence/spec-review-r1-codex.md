verdict: NEEDS_REVISION

dimension_scores:
  omission: fail — Acceptance #4 沒有任何 Requirement；Codex `/hooks` 授信也缺少 UI flow。
  ambiguity: fail — 「只有三種對話」與額外單向門／判斷型岔路並存，會讓 write-plan 對停問次數產生兩種解讀。
  inconsistency: fail — code-only 的 `needs-design: yes` 路徑要求使用者手寫 spec，違反只回答三類問題且不讀 spec 的目標。
  incorrect-fact: fail — `113 名詞` 的精確值未受 evidence 支持；來源自己註明 workflow 清單約 38、仍待重數。
  missing-population: fail — session-start「減半」、機制淨數、名詞數都缺固定基線或可機械重算的 population。
  spec-conformance: fail — Acceptance #4 無 REQ；多個複合 REQ 只有部分內容真正對應標示的 Acceptance。
  user-judgment-leak: fail — code-only 使用者會被要求自行撰寫工程 artifact `spec.md`。

findings[]:
  - severity: 🔴 fatal
    dimension: user-judgment-leak
    anchor: concept-model.md:§4（第 115–120 行）
    text: 「只裝 loom-code」且 `needs-design: yes` 時，使用者要「裝 loom-design 或照 §2c 手寫 spec.md」。這要求基本知識使用者產出並自行判斷 spec，直接違反 intent Acceptance #1 的「不讀 spec、plan 或 diff，只回答三種問題」，也使 loom-code 獨立安裝的 product／TUI 路徑無法符合目標。
    fix: 把手寫 spec 改成 loom-code 依其 contract template 自動產生最小 spec、照同一 review gate 審查；使用者只確認可見行為。

  - severity: 🔴 fatal
    dimension: inconsistency
    anchor: spec.md:§Requirements REQ-1、§UI flows（第 6–7、48–54 行）；concept-model.md:§4
    text: UI flows 先宣稱「使用者看到的只有三種對話」，隨後列出第 4 種「單向門」，再允許 agent 在其他「判斷型岔路」停問。concept-model 同時宣稱 engineering 固定 2 個、product 固定 3 個決策點。write-plan 無法判斷這些停問算既有決策點內的問題，還是額外決策點。
    fix: 明定所有單向門與判斷型岔路不得新增停點：engineering 一律併入 intent 確認，product 一律併入 intent 或可見行為確認；刪除「決策點之外停下來問」的路徑。

  - severity: 🔴 fatal
    dimension: spec-conformance
    anchor: intent:§Acceptance #4；spec.md:§Requirements
    text: Acceptance #4 要求用三個指定時段後的真實 merged changes replay，且 commit、review dispatch、人類決策點均不得增加；REQ-1 至 REQ-9 沒有任何一條要求這項 replay 或其 PASS 結果。write-plan 因而可以完全不實作這項 ground-truth 驗收。
    fix: 新增獨立 REQ，固定三個 replay 對象、today baseline、三項計數規則及「每項逐 change 不增加」的 PASS 條件。

  - severity: 🔴 fatal
    dimension: missing-population
    anchor: spec.md:REQ-7；concept-model.md:§11；intent:Acceptance #7
    text: 「新增任何機制」與「淨數不增」沒有可機械辨識的 mechanism population。§11 的三個紅燈只數 skill、artifact、session-start 字數；新增 checker、hook、action 或散文 gate 而不增加這三項時，CI 仍可能通過，無法保證 Acceptance #7。
    fix: 定義 machine-readable mechanism inventory、每個 mechanism 的 regression-eval 關聯、增刪差額算法及 budget-exception grammar；CI 直接驗證這份 population。

  - severity: 🟡 important
    dimension: omission
    anchor: spec.md:REQ-2、§UI flows；concept-model.md:§7a
    text: REQ-2 明定 Codex 多一次 `/hooks` 授信，但 UI flows 沒有涵蓋「hook 寫入 → probe 失敗 → BLOCK 訊息 → 使用者執行 `/hooks` → 下次 probe 成功」這個完整可見互動。現有「只有三種對話」也排除了它。
    fix: 補一條非決策型 UI flow，逐項定義 BLOCK 文案、使用者動作、重試與成功狀態，並註明它不計入決策點。

  - severity: 🟡 important
    dimension: spec-conformance
    anchor: spec.md:REQ-3、REQ-6、REQ-8
    text: 複合 Requirement 的箭頭只覆蓋部分義務：REQ-3 的「對抗動作」不是 Acceptance #1 的內容；REQ-6 的 needs-design／probe／身分重算不等同 Acceptance #7 的新機制准入；REQ-8 的「名詞 ≤40」不在 Acceptance #5。這些箭頭會讓 write-plan 誤以為已完成雙向 trace。
    fix: 每個 REQ 只保留可直接追到該 Acceptance 的義務；其餘拆成有正確來源的 REQ，或留在 Design decision 而不偽稱 Acceptance trace。

  - severity: 🟡 important
    dimension: missing-population
    anchor: spec.md:REQ-8；intent:§Open questions；concept-model.md:§3、§11
    text: 「skill 36 → 18」把 Acceptance 的 `≤18` 寫成看似精確的 18；「session-start 注入減半」沒有 baseline SHA、渲染範圍或字數算法；名詞計數規則仍被 intent 標為 open。三項都不能產生穩定驗收結果。
    fix: 改成 `skill ≤18`；釘住 session-start baseline SHA、輸入表面與計數命令；先封閉名詞 canonical list／規則，否則從 Requirement 移除名詞目標。

  - severity: 🟡 important
    dimension: incorrect-fact
    anchor: spec.md:§Current state evidence（第 45 行）；evidence/current-state-diagnosis.md:§1；evidence/loom-workflow.md:§Totals
    text: spec 把「113 名詞」當成確定資料，但 supporting evidence 寫明 workflow 名義值為 25、逐項清單實列約 38 且「待重數」。因此 44＋44＋25＝113 不是由清單支持的已驗證總數。
    fix: 在重數前改成「基線未定」；完成 canonical 去重清單後再寫精確數字與計數命令。

  - severity: 🟡 important
    dimension: ambiguity
    anchor: spec.md:REQ-9；intent:Acceptance #6；concept-model.md:§12
    text: REQ-9 寫「15 分鐘內零猜測走完一個任務」，而 Acceptance #6 與 concept-model 要求的是「說出會產生哪些檔、誰決定什麼、checker 何時擋、review 何時跑」。前者可被解讀成真的完成實作，會導致完全不同的驗收測試。
    fix: 逐字採用 Acceptance #6 的四項輸出，並指定一個 given task 作為冷讀測例。

traceability:

| Requirement | 宣稱對應 | 審查結果 |
|---|---|---|
| REQ-1 | Acceptance #1、#3 | ⚠️ 部分；核心三處有對應，但 UI flow 4 與額外岔路破壞「只在三處」及 2／3 點上限 |
| REQ-2 | Acceptance #2 | ⚠️ Requirement 有覆蓋；`/hooks` 的可見 flow 缺失 |
| REQ-3 | Acceptance #1 | ⚠️ 兩 reviewer、盲跑獨立性有對應；artifact 型別對抗屬額外義務 |
| REQ-4 | Acceptance #1 | ✅ 盲跑報告逐條對 Acceptance，並作驗收介面 |
| REQ-5 | Acceptance #5 | ⚠️ core 五種有列出，但 evidence 附件是否算 per-change 文件形狀未封閉 |
| REQ-6 | Acceptance #7 | ❌ 箭頭錯置；重算／probe／reviewer 身分不是 Acceptance #7 的機制准入條件 |
| REQ-7 | Acceptance #7 | ⚠️ 意圖對應，但 mechanism population 與 CI 判定方式未定義 |
| REQ-8 | Acceptance #5 | ⚠️ skill、注入量有對應；名詞目標無 Acceptance 對應，且計數仍未定 |
| REQ-9 | Acceptance #6 | ⚠️ 有意對應，但「走完」與 ground truth 的「說出四項資訊」不等價 |

| Acceptance | 對應 REQ | 審查結果 |
|---|---|---|
| Acceptance #1 | REQ-1、REQ-3、REQ-4 | ⚠️ 有覆蓋，但額外停問與手寫 spec 路徑違反目標 |
| Acceptance #2 | REQ-2 | ⚠️ Requirement 有覆蓋；UI flow 有缺口 |
| Acceptance #3 | REQ-1 | ⚠️ 數量可由三處推得，但額外單向門／岔路使上限不封閉 |
| Acceptance #4 | 無 | ❌ gap |
| Acceptance #5 | REQ-5、REQ-8 | ⚠️ 有覆蓋，但字數 baseline、artifact 邊界與 `≤18` 寫法未封閉 |
| Acceptance #6 | REQ-9 | ⚠️ 測試動詞與預期輸出不一致 |
| Acceptance #7 | REQ-7；REQ-6 被標為對應 | ⚠️ REQ-7 尚不可機械驗證；REQ-6 是錯誤 trace |

what_i_did_not_read:
  完整閱讀了 intent、spec、concept-model、`ceremony-cost-old-vs-new.md` 與 `q4-codex-hooks-live-test.md`。按需閱讀了 `batch-review-mechanism.md`、三份 plugin inventory、`current-state-diagnosis.md` 與兩份先前 Codex audit 的相關段落；未全文閱讀這些按需檔案。未開啟 `q2-per-task-review-evidence.md`、`q4-industry-gate-research.md`、`anthropic-playbook-control.md`、`concept-model-v5-pre-fold.md`、`concept-model-v7-human-gates.md`。未開啟 packet 列表以外的任何 evidence path。