# spec review round 1 — Claude leg (opus, fresh context) — verbatim

已讀完 intent、spec、concept-model 與四份量測 evidence。

---

**verdict: NEEDS_REVISION**（2 個 🔴）

**dimension_scores**
- omission — **fail**：UI flows 只有快樂路徑；REQ-9 已知量測未達標未載明（F3、F7）
- ambiguity — **fail**：REQ-6 checker 規則、REQ-7「三項觀察指標」皆為不完整列舉（F9）
- inconsistency — **fail**：REQ-1 與同份 spec 的 UI flows 第 4 項直接矛盾（F2）
- incorrect-fact — **fail**：REQ-2「只多一次授信」與 q4 實測衝突；一條 Alternatives 理由無證據（F5、F8）
- missing-population — **fail**：checker 規則集與使用者可見畫面兩處都只列子集（F3、F9）
- spec-conformance — **fail**：Acceptance #4 零 REQ 覆蓋；兩條 Open question 被寫成硬要求（F1、F4）
- user-judgment-leak — **pass**：三個決策點與單向門問法皆為後果形，沒有任何一處要使用者判斷工程品質。F6 是段落歸屬問題，不是洩漏

---

**findings**

**F1 🔴 spec-conformance** — `spec.md §Requirements`
Acceptance #4（「拿三個 2026-08-20 之後真實合併的 change 重走一遍，commit 數、審查派工數、人類決策點都不多於今天」）**沒有任何 REQ 指向它**。這不是可有可無的一條：`evidence/ceremony-cost-old-vs-new.md:114-124` 量到 v7 模型的人類決策點是 **10 vs 今天 6，三個 change 每個都 +1**，並寫「heavier on all three changes」。v10 刪掉 approval-only commit 後數字會變，但 spec 沒有把這個唯一擋住「重設計反而更重」的驗證帶進來，write-plan 就不會排 replay 任務。
fix：新增 `REQ-10 — 不比今天重：三個 2026-08-20 後已合併 change 的 replay，commit／審查派工／人類決策點三項皆 ≤ 今天實測值（基線見 evidence/ceremony-cost-old-vs-new.md §Totals）。→ Acceptance #4`

**F2 🔴 inconsistency** — `spec.md §Requirements REQ-1` vs `§UI flows`
REQ-1：「使用者只在 intent 確認、product 的 spec 可見行為確認、盲跑報告驗收**三處**被問；其餘決定 agent 做」。但同份 spec 的 UI flows 開頭寫「使用者看到的只有**三種**對話」卻列了 **4 項**，第 4 項是「單向門（必問，不靠判斷）」。concept-model §4 說單向門 product 併進決策點②、**engineering 在 write-plan 前**——那對 engineering 就是第三個停點，與 Acceptance #3「engineering ≤ 2」相牴觸。write-plan 讀到這裡無法判斷該不該把單向門建成一個受計數的決策點。
fix：REQ-1 改為「engineering 2 處（intent 確認、驗收）、product 3 處（加可見行為確認）；單向門合成一次問，product 併入決策點②不另計，engineering 併入決策點①一併問完（不新增停點）」；UI flows 標題的「三種」改「四種」。

**F3 🟡 omission / missing-population** — `spec.md §UI flows`
只寫成功路徑。REQ-2 自己就寫了 Codex 的 `/hooks` 授信，concept-model §7a 說未授信時 **BLOCK 並指名「請在 Codex 跑 /hooks」**——那是一個使用者看得見、Acceptance #2 直接點名的畫面，UI flows 沒有。同樣缺的還有：`kind: product` 且無 ratified PRINCIPLES.md 時的**拒收**訊息（§8）、standing docs 缺件的三行 WARN（§8）。
fix：UI flows 增列第 5 項「首次在 Codex 使用此 repo：agent 說明已寫入 hooks、請跑 `/hooks` 授信，授信前不繼續」，第 6 項「缺 PRINCIPLES.md 的 product change：說明缺什麼、給模板、可選擇靜音」。

**F4 🟡 spec-conformance** — `spec.md REQ-8`、`REQ-3`
REQ-8「名詞 ≤ 40」標 `→ Acceptance #5`，但 Acceptance #5 只講 skill 36→18、注入減半、文件形狀 ≤5，**沒有名詞數**；名詞 ≤40 在 intent 是 **Open question**（「規則本身可能還要調」）。REQ-3 的「host 有第二 vendor 時**必用**」同理——跨 vendor 成本可不可接受，intent 也列在 Open questions。spec 把兩條未定事項升格成硬要求。
fix：REQ-8 拆出名詞條並標 `（intent Open question，replay 量過後定案，暫不入 CI 紅燈）`；REQ-3 補一句「成本量測未完成前，跨 vendor 為預設而非 CI 紅燈條件」。

**F5 🟡 incorrect-fact** — `spec.md REQ-2`
「Codex 只多一次每 repo 的 `/hooks` 授信」與 `evidence/q4-codex-hooks-live-test.md:36` 衝突：「Any change to the hook command line re-triggers review」，且 :53 說 `trusted_hash` 蓋的是 hook **定義**不是 script 內容。concept-model §7a 又寫「版本舊就覆寫」並用 `scaffold hooks <version>` commit——只要 command 字串帶版本或變動路徑，每次升級都會再要一次授信，REQ-2 就假了。
fix：REQ-2 補一句「`.codex/hooks.json` 的 command 字串必須固定（不含版本、不含絕對路徑），升級只換 checker 副本內容，以維持一次授信」。

**F6 🟡 ambiguity（段落歸屬）** — `spec.md §UI flows` 第 4 項後半
「框架、語言、資料庫、認證、託管、付費服務、資料格式、模型／演算法都算；能先量的先量；PRINCIPLES.md 或 intent 已釘住的不問；一個 change 合成一次問」——這是 agent 的觸發與門檻規則，卻放在標【使用者可讀】、決策點②要**原文念給使用者**的段落，且違反 concept-model §4「問法不出現機制名詞」。
fix：把該半句移到 §Design decision，UI flows 第 4 項只留那段後果形的範例對話。

**F7 🟡 omission** — `spec.md REQ-9`
REQ-9 照抄 Acceptance #6 的 15 分鐘，但 `concept-model.md:213` 自己記錄 v10 冷讀 **25 分鐘（未達 15）**，並註明對策是「落地後 SKILL.md 各站只載自己那段」。spec 沒帶這個已知缺口，write-plan 不會排「拆站載入」這個為了達標而必須的任務。
fix：REQ-9 後加一句「現況 25 分鐘（concept-model §12）；達標路徑＝各站 SKILL.md 只載自己那段，冷讀量測對象為落地後的站文件而非 concept-model.md」。

**F8 🟢 incorrect-fact** — `spec.md §Alternatives considered` 第 2 條
「只保留最後一次大審：否決，大 diff 下 reviewer **掃讀**」——證據不支持「掃讀」。`q2-per-task-review-evidence.md §C` 全部五筆反而是 whole-branch **抓到** per-task 漏的；唯一相關的是 §C.5「round 3 找 3 條、round 4 再找 2 條」＝首輪 under-reach。
fix：理由改成「大 diff 下 whole-branch 首輪 under-reach（q2 §C.5：round 3 三條、round 4 再兩條）」。

**F9 🟢 ambiguity / missing-population** — `spec.md REQ-6`、`REQ-7`
REQ-6 只列三項重算（needs-design、probe 實跑、reviewer≠implementer），漏掉 concept-model §7 的收件閘與 push 閘（`reviewed_sha == HEAD^`、`open_findings` 全關、`verdicts[] ≥ 2` 與 degraded 偵測）；checker 若照 REQ-6 建就少一半。REQ-7 的「三項觀察指標」對不上 §11——§11 的觀察面是 `needs-design: yes` 數、逾期未確認數、決策點數**與**岔路提問數（四個數）＋手數的名詞數。
fix：REQ-6 句末加「完整規則集見 concept-model §7」；REQ-7 把觀察指標逐項列名或改寫成「§11 所列全部觀察指標」。

---

**traceability**

| REQ | → Acceptance | 反向 | ← REQ |
|---|---|---|---|
| REQ-1 | #1, #3 | #1 | REQ-1, 3, 4 ✓ |
| REQ-2 | #2 | #2 | REQ-2 ✓（F5 事實有疑）|
| REQ-3 | #1 | #3 | REQ-1 ✓（F2 數字未落地）|
| REQ-4 | #1 | #4 | **無 — 🔴 F1** |
| REQ-5 | #5 | #5 | REQ-5, 8 ✓（名詞條超出 #5，F4）|
| REQ-6 | #7 | #6 | REQ-9 ✓（F7）|
| REQ-7 | #7 | #7 | REQ-6, 7 ✓ |
| REQ-8 | #5 | | |
| REQ-9 | #6 | | |

正向 9/9 有指向；反向 6/7 覆蓋，**Acceptance #4 缺口**。

**what_i_did_not_read**
`evidence/` 中的 `anthropic-playbook-control.md`、`concept-model-v5-pre-fold.md`、`concept-model-v7-human-gates.md`、`independent-advisor-codex-run{,-2}.md`、`loom-code.md`、`loom-design.md`、`loom-workflow.md`、`q4-industry-gate-research.md`；`current-state-diagnosis.md` 與 `q2/q4` 只讀了 spec 引用到的段落與 Totals。因此 spec §Current state evidence 的 Forward／Reverse／Boundary 三條路徑錨點未逐一驗證（Data、Error 兩條已對過，數字全中）。任何 loom plugin 的實際原始碼皆未開。
