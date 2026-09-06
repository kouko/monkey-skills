# 縮減實作途中審閱 — 盲跑報告

第一輪盲跑以乾淨副本 `64edb744` 執行，找出 readiness 繞過、規格自審、計畫欄位超限、replay oracle 誤配及乾淨環境缺少 `wcwidth`。修正輪在同一 branch-end checkpoint 針對這些項目補強，沒有把第一輪失敗改寫成成功。

## 你要求的每一項結果

### 1. 實作前保護完整的正向與負向案例
- **結果**：符合。新 plan 沒有 task、移除全部 `acceptance:`、使用標點或惡意編號、缺少正向或負向／邊界案例，以及留下未決問題，都會受控阻擋。
- **證據**：`test_new_plan_accepts_positive_and_negative_pair` 與 `test_branch_end_adversary_gpt6.py` 的 readiness 案例；修正後對抗檔 11/11 通過。

### 2. 規格審閱依風險啟動且必須獨立
- **結果**：符合。低風險宣告可略過正式規格審閱；高風險宣告要求一位 fresh-context 的 `spec+adversarial` reviewer，且同一 agent 若同時是 implementer 會被阻擋；沒有新欄位的舊規格仍沿用原本兩位 reader 加 spec adversarial probe。
- **證據**：`test_spec_lowrisk_accepted`、`test_spec_legacy_required`、`test_required_spec_rejects_combined_self_review`。

### 3. Build 途中不自動派 after-task 或 wave-end 正式審閱
- **結果**：符合。任務與 dependency boundary 只以測試作為前進條件；legacy `review: after-task` 保持可讀但不觸發派工。
- **證據**：`test_wave_end_never_dispatches_formal_review_in_any_lane` 與 candidate replay 的 0 次 Build-time review dispatch。

### 4. 高風險任務仍採 adversary-first
- **結果**：符合。full lane 的 code 或 gate 任務仍先由獨立 adversary 產生可執行 RED，再交給 implementer。
- **證據**：`test_full_lane_adversary_first_covers_code_and_gate` 及 W0-01 → W0-02 dispatch 順序。

### 5. 所有工作完成後才進入唯一一次 branch-end review
- **結果**：符合。第一輪 Codex 與 Claude 都回傳 `NEEDS_REVISION`，Ship 因此停住；修正完成後，同一組 Codex 與 Claude reviewer 在 round 5 都回傳 `PASS`，才進入使用者驗收。
- **證據**：review round 4 保留原始 findings；round 5 在相同最終 SHA 記錄兩家 reviewer 的通過結果，所有 finding 均已解決或由原 reviewer 駁回。

### 6. 其他 lane、紀錄與 Ship 保護維持
- **結果**：符合目前可機械驗證的部分。full/small/express/gate-only 的 branch-end 差異仍在；manifest 與 Codex scaffold 已同步；plan 的 Files 清單已降到上限內。
- **證據**：相關 station tests、`check_mechanisms.py --baseline origin/main` 與 scaffold self-test 均通過。

### 7. 真實多任務 replay 的等待縮減且不誇大
- **結果**：符合。相同的六個 task patch 產生相同 final tree；Build-time 正式審閱 2→0，已知等待 1,086→0 秒。這只是結構性等待縮減，不是整體交付時間保證。
- **證據**：兩棵 tree 都是 `e6201f8f13d18a36ccd5362204ee1c5d7d5aa2b7`；comparison 已把 canonical target 早已修掉的 two-reader 文案 oracle 改列為 inapplicable，不再拿 stale mirror 冒充同一根因。

## 乾淨環境結果

第一輪盲跑依 README 建立新 venv 時，套件安裝成功，但 `wcwidth` 沒有列在 `requirements-dev.txt`，因此得到 2 failed、2016 passed；第二個失敗是 nested rehearsal 重複同一個根因。第一輪也因乾淨 worktree 的三個 Codex hook 尚未受信任而無法真正啟動完整 Build，沒有把直接 checker 操作冒充完整工作流。

修正後以 `uv run --isolated --with-requirements requirements-dev.txt` 建立隔離依賴環境，執行 KICKOFF 指定的完整 package command，結果為：
- loom-code / scripts / hooks：2025 passed、2 skipped、1 xfailed。
- loom-design：183 passed、1 skipped。
- branch-end adversarial probe：11 passed。

## Review summary

- 第一輪有效找出並保留所有重要問題，沒有駁回 important 或 fatal finding。
- readiness、reviewer independence、runtime contract、Claude CLI adapter、replay oracle、mechanism eval、plan cap、release probes與乾淨依賴已修正。
- 同一組 Codex／Claude reviewer 最終均通過；是否完成仍由使用者依本報告驗收，之後才執行 push gate。

## Questions I asked you

1. 確認保留正負向測試、移除 Build 途中正式審閱、保留 branch-end review。
2. 確認 Claude 作為第二家模型 reviewer。
3. 兩次確認規格行為後開始實作。

## What this did to existing data

沒有讀寫個人資料。變更只涉及 repository 內的 Loom 程式、測試、契約、版本鏡像與審查證據；舊 spec 與舊 plan 採相容讀取，不批次改寫。

## I decided for you

- 舊 plan 只有在沒有 charter 且已存在 Git 歷史時才走 legacy 相容路徑，避免新 plan 靠刪欄位自行豁免。
- Claude reviewer adapter 固定禁用工具、要求 JSON，並只接受 envelope 的字串 `result`，降低非互動呼叫的不穩定性。
- replay 只計可重算的正式審閱等待；缺少 defect-fix 時間時不推估整體加速。
