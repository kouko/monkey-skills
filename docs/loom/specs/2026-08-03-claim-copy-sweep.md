# Brief — claim-copy sweep（修補側 sweep）

- **Date**: 2026-08-03
- **Origin**: `docs/loom/backlog/2026-08-03-review-scope-resolver-close-out.md`
  的隊列第 3 項；規則本體在
  `docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`

## Design-side on-ramp

Axis 0 未觸發 — 這是 repo 自身流程用的內部 CLI 工具，無使用者介面、非
product-shaped，family reception 的 on-ramp 各列皆不適用。

## Problem

改一處聲明的人，改完之後同一個聲明的其他副本還留在原地，而且**沒有任何訊號告訴
他有其他副本**。他修完、驗證通過、出貨，錯的那幾份繼續在文件裡指揮下一個讀者。

規則已經寫下來了（「改任何一份之前，先列舉全部」），但那條規則要求人**記得執行
一個他必須自己組出來的 grep**。這個弧的證據是：寫下那條規則的作者，在幾小時後
自己違反了兩次。

Job story：**當我要修一個可能不只出現在一處的聲明時，我想要一次拿到它所有副本的
清單、並且知道哪些是不該動的歷史紀錄，這樣我才不會修一半就以為修完了。**

## Users

這個 repo 的修補者——人或 agent——正要編輯一份 `.md` 裡的一句聲明（一條規則、
一個數字、一個歸因）。條件：

- 語料是 `docs/loom/**.md` 加上 repo 內其餘 `.md`。**本文刻意不寫檔案數**：這份
  spec 自己就在被計數的語料裡，寫下的任何數字在它落地的那一刻就過期了（第一版
  寫了 646 / 2766，兩個都在同一條分支內就失準）。要數就跑
  `find . -name '*.md' -not -path './.git/*' | wc -l`，並注意它含未追蹤檔案，與
  乾淨 clone 的 `git ls-files '*.md' | wc -l` 是兩個不同母體；
- 散文**硬換行**（`docs/loom/memory/` 的行長中位數 69、p90 81），所以任何跨兩個
  以上單字的引句都可能被 newline 切斷；
- 修補者手上有的是**要改的那句話**，不是一個正規表示式；
- 語料裡有**必須保持原樣的歷史紀錄**（`docs/loom/archive/`、20 份 `CHANGELOG.md`、
  dogfood 紀錄），把它們一起改掉等於竄改歷史
  （`docs/loom/memory/big-rename-operative-frozen-sweep.md` 記錄過這個災情：
  一條說「文件封存不會被改名」的 CHANGELOG 行，自己被 sweep 改掉了）。

## Smallest End State

一支 stdlib-only CLI：**吃一句聲明的字面文字，吐出 repo 裡每一份副本的位置，
分成 operative / frozen 兩欄，並在結尾逐條列出它抓不到的形狀。**

**它只報告，永不編輯。** 這是刻意的：規則的名字是「列舉」不是「取代」，而
big-rename 那次災情正是自動改寫造成的。編輯留給人或 agent，工具只負責讓「我以為
只有一處」變成不可能。

比對必須是 **wrap-insensitive**：兩側都先做 `re.sub(r"\s+", " ", text)` 再比，
否則跨換行的副本靜默漏掉——而那正是
`docs/loom/memory/verbatim-phrase-guards-break-on-hard-line-wrap.md` 記錄的、
已經害過一次的形狀（一個 seven→six 的更正 no-op，而它的驗證 grep 確認了那個
假成功）。

不在最小集裡：把它接成任何流程的義務關卡。

## Current State Evidence

- **Forward（誰會呼叫）**: 目前無人。規則只存在於
  `docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`
  的 How-to-apply 散文裡，沒有任何 skill、hook 或腳本引用它。本變更**不**新增
  呼叫端，只把散文指令換成一個可執行的動作。
- **Reverse（SSOT 方向）**: `scripts/` 是 repo 自身流程工具（`backlog_index.py`、
  `check_loom_memory_integrity.py`），不隨 plugin 發佈；`loom-code/scripts/` 是
  plugin 內容，改動需版本 bump。規則本體住在 repo-native 的 `docs/loom/memory/`，
  所以工具同住 `scripts/`，**不進 plugin**、不需 bump。
- **Error（既有錯誤慣例）**: `scripts/check_loom_memory_integrity.py:179,184,188`
  — `main()` 回 `0` / `1`，`sys.exit(main())`。`loom-code/scripts/check_doc_citations.py:431`
  用手寫 arg 迴圈（無 argparse）＋ `--repo-root` 旗標。兩者皆 stdlib-only。
- **Data（語料）**: 全部 `docs/loom/**.md`（數量見上方 §Users，本文不寫死）；frozen 候選＝`docs/loom/archive/`（3 份）
  ＋ 20 份 `CHANGELOG.md` ＋ `docs/loom/dogfood/`。
- **Boundary（邊界）**: `check_doc_citations.py` 對 fenced code block / blockquote /
  表格儲存格**完全沒有處理**（grep 該檔零命中，與其自述的 parser v1 限制一致），
  並因此在自己的 dogfood note 上產生 2/2 誤報。本工具面對同一個邊界，必須明確
  選邊：處理，或明講不處理。

## Decision

建一支 `scripts/claim_copy_sweep.py`：輸入一段聲明文字（`--claim` 或 stdin），
對 repo 的 `.md` 語料做 whitespace-normalized 比對，輸出每個命中的
`path:line`，分 operative / frozen 兩區，並在結尾印出**具名的漏網清單**。

三個承重選擇：

1. **只報告，不編輯。** 避開 big-rename 記錄過的自動改寫災情，也讓工具不需要
   理解「這一份該改成什麼」。
2. **frozen 是預設清單 ＋ 可覆寫，不是猜測。** 預設 frozen = `docs/loom/archive/`、
   任何 `CHANGELOG.md`、`docs/loom/dogfood/`；旗標可加。分類寫在報告裡，讓使用者
   看得見自己在依賴什麼。
3. **同義詞漏網改成「可宣告」而非「無解」。** 見下方 Axis 4 —— 日文生態的
   `textlint-rule-prh` 對「表記ゆれ」的答案是一份**人工宣告的 regex 字典**，不是
   自動偵測。本工具照抄這個形狀：接受 `--also` 傳入同一命題的其他措辭，一起掃。
   同義詞在**一般情況**仍然無解，但「這次我知道還有哪些說法」是可以表達的。

**不建**：任何強制修補者執行它的關卡。使用者本輪已明確表達檢查流程過多的疑慮；
先讓工具存在且好用，義務化是獨立的後續決定。

## Alternatives Considered（Axis 4 — 已搜，EN + JA）

EN 與 JA 生態給的是**不同的答案**，而這個分歧本身是發現。

| 方案 | 誰在用 | 優 | 劣 |
|---|---|---|---|
| **textlint + textlint-rule-prh**（JA 主流） | Sansan、DevelopersIO 等日本工程團隊；YAML regex 字典、markdown 語法感知（自動跳過連結文字）、支援 `--fix` | 成熟、已出貨多年；**對同義詞的答案是宣告式字典**，正面處理了「表記ゆれ」 | Node 工具鏈（本 repo 是 Python stdlib-only）；為常駐 lint 設計，不是「編輯前一次性掃描」；沒有 operative/frozen 概念；要維護一份字典 |
| **`rg -U` 多行 grep** | 通用 | 零建置、已安裝 | 使用者得**每次手寫**一個在每個字之間放 `\s+` 的正規表示式——而那正是最容易寫錯的一步；無分區報告、無 frozen 分類 |
| **結構性單一來源**（EN 主流論述：DITA / content reuse — 根本不要重複） | 技術寫作業界 | 從根源消滅這個缺陷類 | 數百份文件的語料，其中 operative/frozen 的重複是**刻意的**（歷史紀錄必須與現行版本分歧）；改造成 transclusion 等於重寫整個語料 |

EN 側搜尋的結果本身也是資料：**沒有一個現成工具做這件事**，回答一律是
「組合多個工具或自己實作」（eslint/markdown 只有 `no-duplicate-definitions`
這種語法層規則；其餘是通用去重器）。

**My take — Recommend**：自己寫。兩個已出貨方案各自漏掉承重的那一半：wrap 正規化
必須是自動的（不是每次手寫），而 operative/frozen 分區是 repo 特有、且是唯一防止
竄改歷史的機制。**但抄 prh 的形狀**——同義詞用宣告解決，不用假裝偵測得到。
**Conditional reversal**：若這個 repo 之後引入 Node 工具鏈，且需要的是常駐 lint
而非編輯前掃描，textlint + prh 是更好的歸宿。

## What Becomes Obsolete

`docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`
的 How-to-apply 目前寫的是一個**要人自己組出來的 grep**。工具出貨後那段指令過時，
必須在同一個變更裡改成指向這支腳本——否則就是設計上的技術債（規則與工具各說各話，
下一個讀者照舊手寫 grep）。

## Out of Scope

- 任何強制執行的關卡 / hook / skill 義務。
- 自動改寫或 `--fix`。
- 語意層的同義詞偵測（宣告式 `--also` 是刻意的替代品）。
- 進 `loom-code` plugin 發佈（先在 repo 內證明價值）。
- 非 `.md` 檔（程式碼註解裡的聲明副本）。

## Open Questions — both resolved during implementation

1. ~~**fenced code block 要不要跳過？**~~ **決定：不跳過，但逐筆標記
   `[inside fence]`。** `check_doc_citations.py` 不跳並因此在自己的 dogfood note
   上吃了 2/2 誤報；但靜默跳過會漏掉「被 fence 包住的規則原文」——那正是要找的
   副本。兩種靜默行為都不誠實，所以兩邊都報、標明是哪一種，判斷留給讀者。
   理由寫在 `scripts/claim_copy_sweep.py` 的 `fence_state_by_line` docstring。
2. ~~**frozen 預設清單是否涵蓋 `docs/loom/audits/`？**~~ **決定：不涵蓋，audits
   算 operative。** 本 repo 對 audit 的慣例是**附加勘誤**，而附加勘誤本身就是
   一種編輯——一份帶著過期聲明的 audit 仍然在誤導讀者。預設 frozen 只有
   `docs/loom/archive/`、`docs/loom/dogfood/` 與任何 `CHANGELOG.md`；其餘用
   `--frozen` 自行宣告。
