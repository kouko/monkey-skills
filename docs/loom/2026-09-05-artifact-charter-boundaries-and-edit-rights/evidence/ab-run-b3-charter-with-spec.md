# A/B run B3 — charter plan (941 words) plus the engineering spec (395 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

status: DONE_WITH_CONCERNS

RED found (verbatim, as I would report it):
"params.md 目前有三處木色相關敘述與出貨後的程式碼真值不符（`docs/loom/params.md:75,89,99`），且此檔為純散文、無任何測試涵蓋它（`verify-docs.sh` 只讀 `design-log.md` 與程式碼常數，不讀 `params.md`/`build_mesh.py`/`measurement.py`），故本任務沒有可跑的失敗測試可指——RED 是『與程式碼真值核對後發現的三處記載錯誤』本身，不是紅測試：
1. Line 75（`build_mesh.py --wood-hex` 列）：型別／預設欄寫 `str`／`#6B4A2F`（design-log 核桃木）。但 `blender/build_mesh.py:869` 的 argparse 定義是 `default=None`；真正落地的木色來自 `blender/materials.py:29` 的 `_WOOD_SRGB_HEX = \"#D9B382\"`。此列同時錯在（a）樹種／色碼過期、（b）把 fallthrough 值誤植成該旗標自己的字面預設值。
2. Line 89（`build_scene(wood_hex)` 列）：型別／預設欄本身正確（`str | None`／`None`），但說明文字仍寫「讓 materials 用自己的預設（design-log 核桃木）」——樹種名過期，出貨色已於 2026-08-21 換成檜木 `#D9B382`（`src/kumiko/output/measurement.py:63-68` 的樹種中立錨點註解可證）。
3. Line 99（`kumiko-measure --lstar` 列）：說明文字寫「缺省掃核桃木 L* 加 60/65/70/75/80」。核對 `measurement.py:71-76` 的 `_DEFAULT_LSTARS = (lstar_of(_WOOD_HEX), 60.0, 65.0, 70.0, 75.0, 80.0)`，其中 `_WOOD_HEX=\"#D9B382\"`（檜木）——樹種名同樣過期。"

GREEN criteria as understood (verbatim):
"1. 三處 核桃木 記載都做出更正，核對過的真值分別是：Line 75 → 型別／預設欄改為 `str | None`／`None`，說明文字改為敘明實際落地色來自 `materials.py` 的 `_WOOD_SRGB_HEX`（現為檜木 `#D9B382`），不得把 fallthrough 值寫成本旗標自己的字面預設；Line 89 → 括號內樹種名由核桃木改為檜木（型別／預設欄本來就對，不動）；Line 99 → 樹種名由核桃木改為檜木，對應 `_WOOD_HEX = \"#D9B382\"`。
2. 每一處更正前都對照過程式碼的『實際預設值』（不是抄 T2 分配的 hex 就假設它是對的）——尤其 Line 75 不能把 `#6B4A2F` 直接換成 `#D9B382` 當作 argparse 預設，因為 argparse 的真預設是 `None`。
3. `scripts/verify-docs.sh` 的四項 design-log 檢查照跑 PASS——因為它們本來就不讀 `params.md`/`build_mesh.py`/`measurement.py`，這三個檔案的改動不影響它。
4. 沒有 package-suite green 的驗收子句（spec 明白排除）：`params.md` 是純散文，本任務不需要跑整包測試。"

open_questions:
1. spec.md 內部存在一處字面矛盾：REQ-4 只把 annotate-not-rewrite（原句留著、旁邊加註日期更正）這個慣例列給 "T4/T5/T6/T8/T9"，未列 T7；但緊接著的 Design decision 第二條卻明白寫「T7 follows the same convention, dated 2026-08-22」。我傾向依 Design decision 條文＋`design-log.md` 現存的「2026-08-21 更正」實例慣例（保留原句，旁註更正）來做 T7，但這是 spec 自身兩處文字互相牴觸，值得在動手前跟人類確認一次要用哪一版；若確認結果與我的預設判讀不同，三處改法（annotate vs 直接改寫）會不一樣。

NEEDS_CONTEXT count: 0
(上面那條矛盾我認為可從 spec 的 Design decision 段落＋本 repo 既有的 design-log.md 更正慣例 直接解出結論——annotate、標 2026-08-22——所以不算「答不出來」，只是想在報告裡明白標出這處 spec 內部的用詞落差，供人類過目。)

Files read: `/private/tmp/.../ab-clone-b/PLAN-charter.md` (T7 line, dependency T2), `/private/tmp/.../ab-clone-b/SPEC-engineering.md`, `docs/loom/params.md:75,89,99`, `blender/build_mesh.py:865-877`, `blender/materials.py:1-30`, `src/kumiko/output/measurement.py:55-75`, `docs/loom/design-log.md` (木色選擇/窗內底紙色 rows, for the annotate-convention precedent), `scripts/verify-docs.sh` (confirmed it never reads params.md/build_mesh.py/measurement.py).
