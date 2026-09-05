# 畢業探針不得依賴本機分支歷史 — 我試了什麼、發生了什麼

2026-09-06 在一份乾淨的專案副本上試的（分支結束檢查點），版本號前七碼 `8e765e58`。這是分支結束的驗收：第 1、2、3 條這次都真的照做並看到結果；第 4 條目前只有「合併前」的證據——這個分支還沒合併進 main，合併後在 main 上再跑一次確認的那一步還沒做，下面第 4 條會說清楚。

## 你要的東西，一條一條試

### 1. 在任一分支下一個命令，它自己建出像 CI 的乾淨副本跑畢業探針，列出每支失敗與每支跳過的理由；本機綠、副本紅時結束碼非 0，全綠結束碼 0

- **我怎麼試的**：在乾淨副本上直接跑這個新命令（不帶任何參數），看它自己印出的內容；接著另外用你們自動化檢查實際用的直譯器版本再跑一次同一個命令，確認不是只有我這台機器的版本才綠。然後另外搭了一個一次性的小型測試專案，專門驗證「結束碼」這件事：先放一支故意讀「本機才有的 main 分支」的假探針直接跑；改寫成「先試遠端的 main、都沒有才跳過」再跑一次；最後把遠端 main 也拿掉，確認「跳過」這條路徑本身也會被列出來、理由也讀得到，而且結束碼仍是 0。
- **發生了什麼**：
  - 真正的專案，這台機器的直譯器：

    ```
    $ python3 loom-code/scripts/rehearse_probes.py
    Rehearsed 8e765e58fd3812dd1aaf8b15d85cdb101bfd989e (…/blind-be2)

    FAILED (0)
    SKIPPED (1)
    SKIPPED loom-code/scripts/test_probes_rehearsal_no_history_class_skips_on_main.py::test_no_history_class_skips_on_main: already inside a rehearsal clone (REHEARSE_PROBES_NESTED='/var/folders/m5/4cb4p8h938qc4qcpdykwz2480000gn/T/rehearse-probes-f6ddj0zg'); a nested clone-and-run would recurse

    ........................................................................ [ 17%]
    ........................................................................ [ 34%]
    ........................................................................ [ 51%]
    ........................................................................ [ 69%]
    ...........................................s............................ [ 86%]
    ..x.....................................................                 [100%]
    414 passed, 1 skipped, 1 xfailed in 64.45s (0:01:04)
    EXIT:0
    ```

  - 同一個命令，換成你們自動化檢查實際用的直譯器版本（用 `uv` 借出一個乾淨的 3.11 環境跑，不動這台機器本身）：

    ```
    $ uv run --python 3.11 --with-requirements requirements-dev.txt --with wcwidth -- python loom-code/scripts/rehearse_probes.py
    Rehearsed 8e765e58fd3812dd1aaf8b15d85cdb101bfd989e (…/blind-be2)

    FAILED (0)
    SKIPPED (1)
    SKIPPED loom-code/scripts/test_probes_rehearsal_no_history_class_skips_on_main.py::test_no_history_class_skips_on_main: already inside a rehearsal clone (REHEARSE_PROBES_NESTED='/var/folders/m5/4cb4p8h938qc4qcpdykwz2480000gn/T/rehearse-probes-a8zy1zxo'); a nested clone-and-run would recurse

    414 passed, 1 skipped, 1 xfailed in 47.81s
    EXIT:0
    ```

    兩個版本的結果一致：0 失敗，只有 1 支跳過，結束碼 0（這支跳過屬於哪一類、為什麼不算數，寫在第 4 條）。
  - 假探針讀本機 main、乾淨副本裡讀不到：

    ```
    $ python3 loom-code/scripts/rehearse_probes.py --repo <一次性測試專案路徑> -- loom-code/scripts/test_probes_toy_reads_local_main.py
    Rehearsed ddcb1a2d9457ddbd696498826086cd422aa9157c (<一次性測試專案路徑>)

    FAILED (1)
    FAILED loom-code/scripts/test_probes_toy_reads_local_main.py::test_toy_reads_local_main
    SKIPPED (0)

    F                                                                        [100%]
    AssertionError: no local main branch found
    assert 128 == 0
    1 failed in 0.11s
    EXIT:1
    ```

  - 改寫成先試遠端 main、都沒有就跳過，並把這個一次性專案裡連遠端都沒有一個叫 main 的東西之後，再跑一次：

    ```
    $ python3 loom-code/scripts/rehearse_probes.py --repo <一次性測試專案路徑> -- loom-code/scripts/test_probes_toy_reads_local_main.py
    Rehearsed 176f090cc132e933f5dcfa50b2baac4baba7ab32 (<一次性測試專案路徑>)

    FAILED (0)
    SKIPPED (1)
    SKIPPED loom-code/scripts/test_probes_toy_reads_local_main.py::test_toy_reads_local_main: no origin/main ref available in this clone

    s                                                                        [100%]
    1 skipped in 0.10s
    EXIT:0
    ```

    跳過不會讓命令變紅——這條路徑本身也印出了理由，而且結束碼仍是 0。
- **證據**：以上四段完整終端輸出，涵蓋兩種直譯器版本（這台機器的、你們自動化檢查用的）與兩個情境（假探針紅、假探針改寫後綠含跳過路徑）。
- **結論**：做到了。

### 2. 用一支故意讀本機 main 的合成探針試它：命令要紅；把探針改成先讀遠端 main、都沒有就跳過，命令要綠

- **我怎麼試的**：同上一條——這條驗證的正是同一組操作，這裡把它單獨列出來對照。
- **發生了什麼**：讀本機 main 的版本在乾淨副本裡讀不到，命令回報失敗、結束碼 1；改寫成先讀遠端 main、都沒有才跳過的版本，命令回報通過（或在遠端也不存在時改成跳過並印出理由）、結束碼 0。
- **證據**：與第 1 條相同的兩段終端輸出（`FAILED (1)` … `EXIT:1`，接著 `SKIPPED (1)` … `EXIT:0`）。
- **結論**：做到了。

### 3. build 站的記憶步驟文字寫明「畢業前跑這命令，紅的不得畢業」，且有測試釘住那句話

- **我怎麼試的**：打開 build 站現在的文字，找「畢業」那一段，看有沒有提到這個新命令、有沒有講紅了不能畢業；接著跑釘住這句話的那支測試。另外，我把自己當成一個只讀過這一段文字、什麼都不知道的人，照著文字做一次「盲跑」：文字要我打哪個指令、看到紅字要做什麼、看到列出的跳過要做什麼。
- **發生了什麼**：
  - 這一段現在確實寫了，而且現在被明確標記成一段「不能改壞」的守則段落，逐字照抄如下（原文英文，我照原樣貼出）：

    > `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rehearse_probes.py <test paths>`
    > clones the repo the way CI checks it out — full history, `origin/main`,
    > no local trunk branch — and runs the copies there (on Codex, the script
    > ships with the loom-code checkout). A red rehearsal blocks graduation
    > until the probe reads `origin/main` first and skips when nothing
    > resolves, and reading every skip it lists matters, since a skip naming a
    > commit or a branch only this tree has verifies nothing on CI.

    意思是：把 change 的探針複製進永久測試目錄之後，接著要用這個新命令（在乾淨副本裡跑一次），紅了就不准把探針算作畢業；還特別交代——列出來的每一條跳過理由都要讀，因為如果跳過的理由講的是「只有這棵樹才找得到的某個 commit 或分支」，那條跳過在真正的自動化檢查裡等於什麼都沒驗到。
  - 釘住這句話、也釘住「這段是守則不能被改壞」的測試：

    ```
    $ python3 -m pytest loom-code/scripts/test_build_station_text.py -q -p no:cacheprovider -k "rehearsal or prose_gate"
    ...                                                                      [100%]
    3 passed, 21 deselected in 0.11s
    EXIT:0
    ```

  - 冷讀盲跑（只照文字做，不看程式碼）：文字裡給的指令樣板是「用這個新命令＋要跑的測試路徑」；但「要跑的測試路徑」具體填什麼，這句指令本身沒講——要往前多讀一段（複製探針那句）才知道是指剛複製進永久測試目錄的那批探針檔案。看到紅字：文字說「紅的不得畢業」，我會照做——回去把探針改成先讀遠端、讀不到才跳過,再重跑一次,不會就地放行。看到列出的跳過：文字說每一條理由都要讀,一旦理由裡點名了「只有這棵樹才有」的東西（某個 commit、某個分支）,那條跳過等於沒驗到,我會當成還沒過關處理,不會直接放行。
- **證據**：這一段文字目前逐字的內容（上面引用區塊）；上面那段測試輸出（3 passed）；上面那段冷讀紀錄，包含唯一需要往前多讀一句才確定的地方。
- **結論**：做到了。

### 4. 這個 change 合併後，在 main 上跑這命令：0 失敗，且跳過理由裡沒有「commit 不在歷史」「change 已 shipped」這兩類

- **我怎麼試的**：在乾淨副本（也就是這個分支目前的樣子，還沒合併）上直接跑了一次完整命令，逐句檢查跳過清單裡的理由。
- **發生了什麼**：0 支失敗。跳過清單只有 1 支，理由是：「已經在一次排練用的乾淨副本裡面了（理由裡直接印出那份副本在磁碟上的路徑），再巢狀地做一次複製再跑一次會沒完沒了」。這是防止命令自己套自己、無限遞迴的保護，不是在講「某個 commit 只有這棵樹找得到」或「這個 change 已經出貨了」——跟你原本問的那兩類完全無關，理由裡也沒有出現「歷史」「squash」「出貨」「自己的分支」這些字眼。原本那兩類——一類是讀某個已經被壓縮合併、本機才找得到的 commit，一類是讀某個 change 是否已經出貨的分支狀態——對應的測試判斷已經不在測試檔裡了：

  ```
  $ grep -rn "_confirm_intent_sha\|_skip_if_language_policy_shipped" loom-code/scripts/test_probes_complexity_wave_end.py loom-code/scripts/test_probes_language_policy.py loom-code/scripts/test_probes_language_policy_branch_end.py
  (no output)
  ```

  這個分支目前還沒合併進 main，所以「合併之後在 main 上再跑一次」這件事本身現在做不到——那一步要等這個 change 真正合併之後才能做,不是我在這個乾淨副本裡能夠代替驗證的東西。
- **證據**：第 1 條裡真正跑出來的兩段完整命令輸出（0 失敗、1 支跳過，理由如上）；上面那段搜尋舊有兩個判斷式名字的輸出（找不到）。
- **結論**：以現在的分支狀態（尚未合併）試，結果符合要求；合併後在 main 上的最終確認，要等合併發生之後才能真的做,現在只能先說清楚它還沒做、會在哪一步做。

## 對你既有的資料做了什麼

沒有——這個 change 不會動到你已經有的任何東西。這個新命令只會在系統的暫存資料夾裡建一份完整專案的乾淨副本來跑測試，跑完就把那份副本收掉；你的工作目錄本身只被讀取，不會被寫入。刪掉的那幾支舊測試是版本控制內的檔案，仍然能從歷史紀錄裡找回來。

## 我幫你決定的事

- **乾淨副本要「完整歷史、有遠端 main、沒有本機 main」這個形狀，而不是更嚴格的淺層副本** — 因為這正是你們的自動化檢查在真正跑的形狀；改用更嚴格的形狀不在這次的範圍內，之後想測那個形狀要另外開一次改動。
- **命令的結束碼只看失敗、不看跳過** — 跳過是「值得你自己讀一下理由」的資訊，不是自動判定失敗；理由是這次要抓的問題本來就是「探針靠不住的東西」，跳過就是探針老實承認靠不住，跟測試真的紅了不是同一件事。如果之後發現這個判斷太寬鬆（跳過的東西其實根本沒被驗證到），可以改成讓某些跳過也算紅。
- **原本三次事故裡累積的舊測試，選擇刪掉而不是改寫成新形式** — 它們本來就只驗證「本機才有的東西」，改寫等於重寫；被刪的測試名稱跟被刪的理由都寫在那次改動的紀錄裡，可以核對。
- **「畢業前跑這命令」寫進文字提醒，而不是做成擋得住人的機制** — 這次選擇先用文字要求，讓下一次真正犯錯時能看出光靠文字夠不夠；如果不夠，之後要另外把它做成真正擋下的機制。
- **審查過程中有一條「重要」等級的意見被撤回，不算數**：有一位審查者原本認為「盲跑報告用中文寫」是個問題（他讀到的規則版本要求內部文件一律用英文），但另一位審查者指出——依這個專案自己的語言規則，盲跑報告跟提交給你的說明文字本來就是用你看得懂的語言寫的，不受「內部文件用英文」那條規則管，所以這個意見被撤回、沒有改動任何東西。如果你覺得這個判斷是錯的（你其實希望連給你看的報告都用英文），這就是需要你出聲的地方。
- 除了上面這一條被撤回的意見，這個檢查點沒有其他「重要」以上等級卻被放行不處理的審查意見。

## 這份報告本身守不守「內部文件用英文、給你看的東西用你的語言」這條規則

| 檔案類型 | 語言規則守住了嗎 | 證據 |
|---|---|---|
| 給你看的計畫文件（工程語言，內部工件） | 守住——通篇英文 | `docs/loom/2026-09-05-graduated-probes-independent-of-local-history/plan.md` |
| 設計說明文件 | 不適用——這個 change 判定不需要另外寫一份 | plan 開頭 `needs-design: no` |
| 審查記錄裡的意見文字 | 守住——每一條都用「issue / nitpick」這種標準標籤起頭，通篇英文 | 審查記錄裡的意見欄位 |
| 我這次自己補的證據（終端輸出、指令） | 守住——通篇英文 | 上面每一段程式碼區塊 |
| 測試程式的說明文字（若有） | 守住——讀到的都是英文 | 相關測試檔案 |
| 測試名稱 | 大致守住三段式命名（單元、狀態、預期結果）的格式 | 相關測試檔案裡的測試函式名 |
| 提交紀錄的說明文字 | 守住——通篇英文、遵守慣用的提交訊息格式 | 這個分支上的提交紀錄 |
| 這份報告本身 | 守住——用你看得懂的語言寫，因為這份文件本來就是規則裡明訂要用你的語言寫的那一種 | 本文件 |

## 這份報告本身沒查到、你可能還沒想清楚的地方

- 這個新命令目前只是「文字上要求跑」，不是強制擋下推送的機制——如果下一次改動又在真正的自動化檢查裡出現紅字，那就代表光靠文字提醒不夠，得考慮把它做成真正擋得住人的機制。
- 「合併後在 main 上再跑一次確認 0 失敗、0 支歷史類跳過」這件事，要等這個 change 真正合併之後才能做——這份報告只能證明「在還沒合併的這個分支上」結果符合要求，還不能證明「合併之後也一樣」。
