# W1 checkpoint 審查紀錄 — 2026-09-02

## after-task（W1-01 write-plan，4cbb40d0）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-coldread-writeplan-1 | 冷讀 Task A | 7 猜測 | needs-design 判準沒寫、kind 值域、第二家 CLI 未排除 host、slug 規則、review.json 誰建、contract 規則 id、KICKOFF 不存在 |
| opus-review-writeplan-1 | spec-conformance＋docs | NEEDS_REVISION | 🔴 needs-design 判準缺；🔴 Codex 首次 scaffold＋授信步缺；🟡 standing.* 表歸屬、checkpoint vs wave 上限、after-task wave 必跑、second-vendor 偵測、(b)(c)(e) 未標 gate；🟢 維度名、無 spec 時 user-decided 落點、測試只驗形狀 |
處置：dc6e8bf7；冷讀第二輪 4 猜測（2 任務事實、2 真缺口）→ dead30e5；task-size 措辭 → d1496688。

## wave-end（423efe92..106fe734）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w1 | docs 5 維＋conformance | NEEDS_REVISION | 🔴 W1 沒派 adversary → `push.probes-adversarial` 會擋；🔴 五張站序表漏列該規則；🔴 adversary.md 指錯 catalogue 路徑；🟡 build BLOCKED 分支「stop and ask」違反 §4；🟡 決策點①②的問題無 questions[] 回填路徑；🟡 docs/loom/ATTACK-CATALOGUE.md 陳舊；🟢 SKILL 版本欄不一、check_field_microstructure 偏離 plan 無理由行、root README 缺 loom-design（既有） |
| sonnet-blindrun-w1 | 盲跑（scratch repo，四站走完到 ship step 4） | 走得通 | 六種產物與表一致；指令全 exit 0；9 落差：`which` 抓到 alias 誤判第二家 CLI；references 路徑基準未講；**沒說要開 feature branch**；KICKOFF 模板 stamp 註解；package-test 偵測無 fallback；intake 指令段落位置；最小 plan 時 wave-end＋branch-end 重複；≤5 是否含 branch-end；push 輸出看不出 adversarial 有無重跑 |
| opus-review-code-w1 | code＋跨站＋探針 | NEEDS_REVISION | 🔴 root `scripts/` 一支測試 collection error 讓 CI pytest 整包不跑（＝本 wave 537 測試在 CI 從沒跑過）＋46 個舊守衛測試紅；🔴 ship 引用 loom-workflow 內部路徑違反 plugin 邊界；🔴 adversary.md 目錄路徑不存在；🟠 spec 紅隊 probe 不帶 scope 可被 code 輪冒充（唯一 fail-open）；🟠 ship §2/§3 自相矛盾（questions[] 寫進 amend）；🟠 五張站序表 12 格分歧＋write-plan 第五種寫法；🟡 R3 基線近似假象、codex-plugin longDescription 陳舊、integration 兩支舊名、兩份攻擊目錄並存、docstring drift、三處死路徑。四組對抗探針（probes-adversarial ×3、questions 壞條目、spec-pass 影子、dismissed 身分）全部照設計擋住 |
| opus-adversary-w1 | 對抗（skill／gate，13 支可執行探針） | NEEDS_REVISION | 擋住 6：無 dispatch 記錄、untracked 介面檔、contract 版本、review.json 重放、誠實 push 寫法、dismissed 身分。逃脫 7：**P04 probe command 寫 `true` 過閘（致命，reviewer 鏡頭不看 command）**；P13 平行 implementer 覆寫 review.json；P11 KICKOFF 縮小 interface-surfaces 無下限；P07 second-vendor 缺席無指示；P02 after-task 超預算純散文；P03 rename 藏刪除；P06 問題型別只驗 enum。接受：P10 全捏造、P12-B 規避寫法（§0 已記）。adversary.md 目錄路徑錯 |

## wave-end 複審（114ea813 / 4558a4ce / 2cc406a8 / babe8bb1）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w1b | docs 閉環＋冷讀 r3 | PASS | 18 條全關（逐條引文）；冷讀 Task A **零猜測**，開檔 2 |
| opus-review-code-w1b | code 閉環＋自打 11 支探針 | NEEDS_REVISION | 15 條全關、13 支對抗探針全擋（但 5 支是被 package-tests 規則擋的，非目標規則）；新 🔴 N1 adversarial `command` 提到 artifact 用子字串比對，寫進 `#` 註解就過；🔴 N2 本 repo 無 `package-tests:` 行，fallback 指令在根目錄 rc=3 → 本分支用自己的閘推不出去；🟡 N3 task 行加項目符號不計；N4 fallback 任意字串消音；N5 零 Task trailer 時身分鏈真空；🟢 N6 ROUTINE.md 死指標被測試釘住 |
處置：同一 implementer 修 N1–N6 → 第三輪 code 複審。

## wave-end 複審第三輪（2260fe69）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| opus-review-code-w1c | code＋gate | NEEDS_REVISION | N1–N6 全關；🔴 F1 `python3 attack.py ; true` 洗白 exit（根因＝執行記錄字串）→ 改為執行 artifact／宣告指令、不經 shell；🔴 F2 零 trailer 閘只看分支彙總，docs commit 帶 trailer 即可掩護無 trailer 的 code commit → 改逐 commit 要求；🟡 fallback 用 match 非 fullmatch；🟡 `#` 剝除不認引號；🟢 review-only-head 失敗即 early return。並確認 13 支對抗探針中 5 支是被 package-tests 泛用規則擋而非目標規則（fixture 未宣告測試指令）→ 改 fixture |

## wave-end 複審第四輪（96d90f1b）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| opus-review-code-w1d | code＋gate | PASS_WITH_NOTES | F1–F3 全關；13 支閉環探針（`; true`／`\|\| true`／不可執行 artifact／`..` 逃逸／宣告指令帶 metachar／引號解析／逐 commit trailer 三型／fullmatch）0 mismatch；timeout 兩分支 fail-closed；evil merge 被擋。notes：🟠 artifact 內容無機械約束（空殼檔合格）＝最弱環，§7 已記；🟠 對抗套件 fixture 缺 trailer 致 F2 規則遮蔽判定（p06 真逃脫＝散文限制，設計接受）；🟡 §7 句自相矛盾（已修）、死常數、測試 `or` 恆真、timeout 無回歸測試 |
處置：§7／intent Open question（a3d6da53）；notes #3–#6＋探針套件移入 evidence/probes-w1/（sonnet）。W1 輪＝PASS_WITH_NOTES，reviewed_sha → 96d90f1b。
