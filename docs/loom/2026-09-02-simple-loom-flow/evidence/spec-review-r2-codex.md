findings_status:
  SR1-01: still-open — REQ-10 已指定三個 PR 與逐 change PASS 條件，但只給合計基線 `126／94／6`，仍缺每個 change 的三項基線與計數規則，無法逐項判定。
  SR1-02: still-open — §4 已明定岔路不新增停點，但新增的 UI flow 6 又要求使用者另選「產生／不需要」，形成未併入既有決策點的額外停點。
  SR1-03: resolved — §4 改為 write-plan「自動產生最小 spec.md」且明說「使用者永遠不手寫 spec」。
  SR1-04: still-open — `mechanisms.yaml` 與部分來源母體已加入，但 CI 如何從自由散文辨識「散文閘」、以及 `budget-exception:` 的封閉位置與文法仍未定義；漏登機制仍不可被可靠偵測。
  SR1-05: still-open — UI flow 5 已補 `/hooks` 授信；但 flow 6 未呈現 §8 的固定三行 WARN 與不可豁免的 product PRINCIPLES 拒收，反而提供「不需要」選項。
  SR1-06: resolved — REQ-3 已把跨 vendor 改為預設／WARN，對抗動作移出 Acceptance trace；REQ-6 改對 Acceptance #1；REQ-8 將名詞目標標為 Open question。
  SR1-07: resolved — REQ-2 與 §7a 已固定 `.codex/hooks.json` command 為無版本相對路徑，升級只替換 checker 內容。
  SR1-08: still-open — `skill ≤ 18` 與名詞「約 113、基線待重數」已修；session-start 仍只寫「main 當前」與「CI 命令固定」，沒有釘住 baseline SHA、完整渲染輸入範圍及實際計數命令。
  SR1-09: still-open — REQ-9 已補四項輸出、25 分鐘現況與拆站對策，但把驗收輸入改成「只拿站文件」，仍不符合 Acceptance #6 與 concept-model §12 的「只拿 concept-model.md」。
  SR1-10: resolved — 單向門機制規則已移至 Design decision、掃讀理由改為有錨點的 under-reach，REQ-6/7 也改為引用完整規則集並列出機制類別。
new_findings[]:
  - severity: 🔴
    anchor: spec.md:UI flows 6；concept-model.md:§8
    text: Delta 新增的 flow 6 允許使用者選「這個 repo 不需要產品原則，我就不再提」，但 §8 同時規定 product 缺 ratified PRINCIPLES.md 必須拒收且只有 DESIGN.md 永不拒。選「不需要」後流程既不能繼續，也沒有說明會被拒收；而這次選擇本身又是未併入既有三個決策點的額外停點。
    fix: 將 standing-doc WARN 與 product 拒收拆成明確流程；刪除可繞過 PRINCIPLES 拒收的「不需要」選項，並把產品原則訪談併入既有 intent 決策點，或明確調整 ground-truth 決策點契約。
verdict: NEEDS_REVISION
what_i_did_not_read:
  完整讀取 packet 列出的六個檔案，並只執行指定的 `git diff e75630c5..e11a198f -- docs/loom/2026-09-02-simple-loom-flow/spec.md docs/loom/2026-09-02-simple-loom-flow/concept-model.md`；未開啟任何其他路徑，包括文件內引用的 evidence。