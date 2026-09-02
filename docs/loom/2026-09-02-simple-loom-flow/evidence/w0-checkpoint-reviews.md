# W0 checkpoint 審查紀錄 — 2026-09-02

## after-task（W0-03，checker 24b7be54..8a5a3b2f）

| reviewer | lens | verdict | 致命 | 摘要 |
|---|---|---|---|---|
| opus-review-code-1 | code（含六個對抗探針） | NEEDS_REVISION | 3 | branch_base 只認 main→needs-design 重算靜默放行；push 對 review.json 無 schema 檢查（空殼檔過閘）；package-tests probe 純信自述。另 8 🟡（status 前綴比對、--commit-msg 可選、dispatch 讀工作樹、git 失敗＝空、無 timeout、change-id 未白名單、死參數 --base、verdict reviewer 未綁 dispatch） |
| sonnet-review-spec-1 | spec-conformance | PASS_WITH_NOTES | 0 | 16 條規則全對映 §7/§8、無多餘規則；spec-pass 未查對抗 probe；probe 未綁 branch；manifest `scope` 欄位無 §2e 背書 |

處置：7a41e13f 全部修（新規則 `push.review-schema`；probe 加 `sha`；spec-pass 要求 adversarial probe；trunk 候選四個＋upstream，全不解 exit 2；timeout 30）。

## wave-end（W0 全部，含 52aaae99 / 3ad2ad61 / 3515431d / 7a41e13f）

| reviewer | lens | verdict | 致命 | 摘要 |
|---|---|---|---|---|
| opus-review-code-2 | code＋跨任務一致性 | NEEDS_REVISION | 4 | 先前 12 條全關（逐條有證據）。新：F1 `push` 在 stdin 非 tty 且未關時永久卡住（掛 PreToolUse 會凍 session）；F2 push regex 放行 `git -C … push`／`eval "git push"`；F3 Codex scaffold 副本缺 git_exec 與 contract，`--probe` 兩種結果皆誤報；F4 dispatch 契約散文改為 review.json `dispatch[]` 但 manifest／checker 未跟。🟡 F5 package-tests 未自跑；F6 dismissed 不驗身分；F7 CHANGELOG 版本段找不到時退化全檔掃描；F8 R4 不驗 eval 路徑存在（17 筆指向未來的 cold-read）；F9 `class` 未驗、host-hygiene 無邊界；F10 §11 逐欄位未落地。🟢 F11 session-start set -e；F12 hooks-probe 死預留 |
| sonnet-review-consistency-2 | docs 5 維＋plan 對應 | NEEDS_REVISION | 3 | backlog-README 模板仍在（plan 說刪）；memory 模板殘留 backlog 舊詞；mechanisms 只登 artifact 不登欄位（§11 明寫欄位層級）。🟡 session-start 決策點②未提單向門；review-dispatch 成第六種 artifact 無 §2a/§2e 定義；KICKOFF 模板 glob 少兩個；JSON 鍵是否算名詞未定。名詞粗估 61（§3 ≤40 待 W3-06 正式手數） |

處置：979b1668（文件面：dispatch 併入 review.json、§3 計 JSON 頂層鍵、§11 逐欄位、模板與 session-start 措辭、plan 註明 backlog-README 留到 W1-06）；checker／scaffold 面另派 implementer（見 review.json W0 輪）。

## 教訓（進 memory）
- 平行派工的接縫只有真打一次才抓到：hooks matcher＝工具名 → checker 必須讀 payload；兩個 implementer 各自都對。
- 「文件先改、程式後跟」在同一個 wave 內就會被下一個 reviewer 當成矛盾抓——契約改動要和程式同 commit，或在 review.json 記 pending。
- 對抗（red-team）與讀（review）抓到的東西幾乎不重疊：四輪讀之後的一次對抗仍出六條致命。

## wave-end 複審（6f8f7970 / d9ed517e / d3b6aefd / 979b1668 / 3c8568d4）

| reviewer | lens | verdict | 閉環 | notes |
|---|---|---|---|---|
| opus-review-code-3 | code | PASS_WITH_NOTES | F1–F12＋spec-G 全部實跑驗證關閉（7 種 push 形狀 rc=2、4 反例 rc=0；scaffold 真副本 shim 擋、破壞後 probe 報 gate broken；probe exit(1) BLOCK、髒樹 BLOCK；dismissed by implementer BLOCK；R3 無版本段紅；R4 缺檔紅＋pending 紅；R0 未知 class；contract 63/63） | N1 `bash -c`／`xargs` 放行；N2 host-hygiene 跳過 R4；N3 `contract --require` 主版本低時訊息反向；N4 `shell=True` 執行 review.json 的 command 需在 §7 寫信任邊界；N5 plan 仍列 hooks-probe |
| sonnet-review-docs-3 | docs | PASS_WITH_NOTES | 1–7 全關 | plan W0-01 模板清單仍列 review-dispatch.json；REQ-1 漏「不動既有資料」；§3 的 18 含 reference 與 plan 的 17 對不上；§8 的 standing 規則無 REQ 直指 |

處置：docs notes → 3c8568d4、0f1dd2fe；N1–N3 → sonnet implementer（見 review.json W0 輪）。
