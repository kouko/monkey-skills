# 對抗者冷讀的三方歸屬要用多次量測決定，而不是再改一句話
originator: kouko
kind: engineering
needs-design: no — 只加冷讀量測工具與 evidence 語料、視結果改一段契約文字；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-reviewer-and-adversary-positioning/blind-run-report.md, docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-adversary.txt, docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-findings-list.txt]
status: confirmed 2026-09-04

## Problem
2026-09-04-reviewer-and-adversary-positioning 用同一份 8 條混合 finding 清單冷讀三輪：只讀對抗者契約的 agent 在「是不是我的」這條軸上 8/8，但「不是我的那些是讀者的還是實作者的」三輪分別 7/8、7/8、6/8，從沒全對——第三輪把「報告誇大」「文件漏寫」判給實作者，其實是讀者的對帳工作。這在現行流程裡不掉 finding（讀者獨立派出、自己會認領），所以 #787 判為不擋；但它是一個**沒量過的**性質：每輪只跑一次，錯的條目每輪不同，看不出是措辭問題、模型雜訊、還是清單本身模糊。第二輪修正也證明「再補一句」會讓對抗者在「該讓給誰」上更保守而不是更準。要把三方歸屬變成契約的保證，得先有分佈，不是再一次的單點。字數帽重設計（2026-09-04-positioning-paragraph-cap-redesign）會在對抗者段補一句三方歸屬並明講不當驗收——本 intent 是接在它之後、把那句話的效果量出來的那一步。

## Proposed outcome
1. 一支可重跑的冷讀量測腳本（放 `loom-code/scripts/`，只依賴 `claude -p`）：輸入契約檔路徑、混合清單與預期標籤（固定 fixture，存在 evidence），跑 N 次（預設 10），輸出每條 finding 的三方歸屬分佈、own/not-own 分數、與逐次 transcript。命令列與旗標寫進輸出檔，不靠散文描述方法。
2. 先在**現行**契約上量一次基線（N=10，讀者契約與對抗者契約各一），再在字數帽 change 落地後的契約上量一次；兩次分佈並列寫進 evidence。
3. 只有當基線顯示三方歸屬的錯是**系統性的**（同一條在 ≥50% 的跑次錯、且錯向一致），才改契約措辭；改完再量一次證明分佈移動。雜訊型（每次錯不同條、無一條過半）則不改措辭，改成把三方歸屬寫進 README 的角色觸發節當說明，並在 intent 記錄「量過、不是措辭問題」。
4. 讀者側同樣量（它目前 8/8 但只有三個樣本），當作對照。

## Acceptance
1. `python3 loom-code/scripts/coldread_role_split.py --contract <path> --fixture <path> --runs 10 --out <dir>` 跑得完，產出 `summary.json`（每條 finding 三個標籤的計數、own/not-own 正確率、N）與 `run-<i>.txt`（含命令列）；固定 fixture 檔在 evidence 下，8 條清單與預期標籤逐字等於 #787 用的那份。
2. evidence 下有兩份基線：現行契約（字數帽 change 前）與字數帽 change 後，各 N=10、讀者與對抗者各一；盲跑報告用使用者看得懂的話講「錯是集中在哪幾條、還是散的」。
3. 若改了契約措辭：改前改後各一份分佈並列，改後對抗者側三方歸屬在錯最多的那條至少從 ≥50% 錯降到 ≤20% 錯；若沒改：intent 記錄理由與數字，README 角色觸發節多一段三方歸屬說明。
4. 腳本有單元測試（用假的 `claude` 替身，不真的打 API）；整包測試綠；不加 checker 規則；loom-code 版本 bump（patch）。

## Constraints
- 排在 2026-09-04-positioning-paragraph-cap-redesign 之後（需要它騰出的字數空間與它補的那一句）。
- 量測用 `--model sonnet`，跟三輪冷讀同款；N 與 seed 記進輸出。
- 契約文字不引用 `docs/` 下的量測檔（可攜性規則）；量測結論只進 intent／plan／README。

## Out of scope
- 「同時讀兩份契約」的冷讀（另一個未驗項，可用同一支腳本但不在本 intent）。
- 把量測腳本接進 CI（每次 10 個 API 呼叫，不該在 CI 跑）。

## Open questions
- none
