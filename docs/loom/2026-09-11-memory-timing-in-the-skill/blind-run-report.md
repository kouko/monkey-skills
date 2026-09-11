# 盲跑報告 — 2026-09-11-memory-timing-in-the-skill

執行對象：commit `6c932df2ea4bad09c9de4b7d55fb1256c98fe706`
（`fix(loom): scope every assertion to its clause's home`），即這次改動的
HEAD。工作目錄：`.worktrees/2026-09-11-memory-timing-in-the-skill`（乾淨
worktree，未動過的樹）。

說明：本報告完全依我自己在這棵樹上的操作寫成，**沒有讀取**先前那份針對舊樹跑
出的 `blind-run-report.md`（也沒有先讀 plan.md 或 commit 訊息內容——只在確認
HEAD 時看過一行 commit 標題，這是取得 SHA 的必要副產品，不影響下面每一條的
獨立驗證）。

> **2026-09-11 補記（非盲跑者所寫）**：本報告跑在 `6c932df2e`。之後的
> `0923f213a` 依本報告 Acceptance 4 的 PARTLY 判定改寫了 plan.md W1-02 的
> Risk 行，也就是下面點名的那個缺口；其餘五條不受該 commit 影響。此後分支又
> rebase 到 `origin/main`（#823、#744 之上），內容未變。

---

## Acceptance 1 — 規則要能只靠複製出去的資料夾讀到

**做法**：把 `loom-workflow/skills/loom-memory/` 整個資料夾複製到 repo 外的暫存
目錄（`scratchpad/a1-copy/`），確認裡面沒有任何 `docs/` 目錄，再單獨讀複製出去
的 `SKILL.md`。

**觀察**：複製出去的資料夾裡完全沒有 `docs`（`find … -iname docs` 沒有任何輸
出）。`SKILL.md` 的 `### Record` 一節裡就寫著「**When:** before the branch
closes. A fact already known while the branch is still open … belongs in that
same branch, never a separate post-merge branch」,不必翻任何 repo 資料檔就讀
得到。

**結論：PASS。**

---

## Acceptance 2 — Record 文字本身講得夠具體、evals 報告誠不誠實

**先自己判斷再看報告**：在讀 `evals/record-timing.md` 之前，我自己讀了
`SKILL.md` 的 Record 一節。它明確給出三件事——時機（分支關閉前）、例外（只有
合併後/安裝後才觀察得到的事實，且要求批次處理）、量的門檻(「幾乎沒有東西夠格」
「每個 change 正常是零到一條」)。一個沒讀過 2026-07 那段歷史的讀者,照著這段文
字走,應該會在分支還開著時就記,而且會拒掉大多數候選——這是我讀完文字後、看報
告前的判斷。

**再看 `evals/record-timing.md`**：裡面記了兩次跑法（11 候選 / 12 候選），兩次
都判定 PASS,但報告誠實地列出兩次彼此不合、也都跟「地面真相」不完全一致的表格
（例如候選 2、候選 12 兩次結果不同）,並且明講「兩次跑法都往拒絕的方向偏,而不
是往浮濫記錄的方向偏——這正是這條款要防的失效方向」。特別是候選 12(「斷言釘的
範圍比它要守的條款寬」——也就是這次改動自己審查中反覆出現的那個缺陷)第二次跑
被判 REJECT,報告自己承認「如果之後的跑法也拒絕它,代表這條款低估了『同一缺陷
出現四次』這種復發訊號」——這是把對自己不利的結果講出來,不是硬拗成通過。

**結論：PASS。** 文字本身足以在無歷史脈絡下引導讀者往正確方向,兩次評測結果不
一致但報告誠實揭露、未美化。

---

## Acceptance 3 — 例外與批次處理寫清楚

已在上面 SKILL.md 引文中看到：「The one exception is a fact only confirmable by
observing real post-merge or installed behavior; that genuinely needs a
follow-up branch, and those are batched rather than one pull request per
discovery.」以及緊接著補一句涵蓋「審查已無可再讀內容之後才浮現的教訓」也算同
一種情況、一樣批次搭下一個 change 的便車。

**結論：PASS。**

---

## Acceptance 4 — 時機 / 稀少性兩半各自有機制守住 + 守衛自我解釋 + intent/plan 不描述機制性質

**① 刪除擋得住（親手做突變,不採信現成測試）**
我自己在 `SKILL.md` 的 Record 段落裡把片語「pure overhead」改成「extra work」
（跨行片語,用 Edit 工具精確替換),然後在 `loom-workflow/skills/loom-memory`
下跑 `pytest scripts/test_skill_contract.py`。結果：
`test_record_contract_states_when_to_record` 和
`test_record_section_matches_the_digest_the_cold_reader_eval_was_run_against`
兩支具名測試都轉紅,錯誤訊息點名「the Record contract no longer states 'pure
overhead'」並附上完整的 #515／loom 1.0 誤刪歷史說明。驗證完立刻用 Edit 改回原
字、清掉測試殘留的 `__pycache__`,`git status` 確認樹乾淨。

**② 稀釋擋得住**
稀釋這一半不是靠字串測試(文件自己承認字面片語斷言測不到稀釋),而是靠
`evals/record-timing.md` 的冷讀跑法——見上面 Acceptance 2 的分析,兩次跑法都
在分支還開著時記錄、也都拒掉大多數候選,方向正確。而且 `Record` 段落一改動,
`test_record_section_matches_the_digest_the_cold_reader_eval_was_run_against`
就會因為 sha256 摘要對不上而轉紅——我上面的突變測試已經同時證明了這一點:同
一次刪字就讓摘要測試也紅了,逼下一個編輯者去重跑冷讀而不是只改字串清單。

**③ 守衛自我解釋**
`test_skill_contract.py` 裡在這四支測試之前有一大段註解,標題直接寫
「READ THIS BEFORE YOU EDIT OR DELETE ANYTHING BELOW」,講清楚 2026-07-08
(#515)怎麼建立、loom 1.0(#780)怎麼把指示跟測試一起誤刪、紅燈時該做的三步
驟。每支測試失敗訊息裡也附上 `_A4_WHY`,同樣點名這段歷史。這符合「失敗訊息要
說明這段話為什麼在這裡」的要求。

**④ 機制性質只能在測試模組裡敘述——grep intent 與 plan**
- `intent` 裡第 31 行明確寫「這幾個機制各自的性質只在實作它們的測試模組裡敘述
  (匹配的是字面還是語意…)。這份 intent 只說結果」——intent 本身只是在**聲明
  這條原則**,沒有另外斷言匹配機制是字面還是語意,乾淨。
- 但 `plan.md` 沒有這麼乾淨。W1-02 那一列的 Risk 寫著:「A phrase-presence
  assertion is a golden test at string granularity, and its documented failure
  mode is that a red test gets updated rather than investigated」——這句話直
  接描述了這個機制「是什麼粒度的比對(字串層級的 phrase-presence)」以及「它的
  已知失效模式」,這正是 Acceptance 4 第四點要求「只能在測試模組裡敘述」的東
  西,卻同時出現在 plan.md 裡。

**結論：前三點 PASS,第四點 PARTLY——`plan.md`(非 intent)仍含有對機制性質
(字串粒度比對、已知失效模式)的敘述,不是零。**

---

## Acceptance 5 — closing review 裡的那段話

**位置**：`loom-code/skills/review/SKILL.md` 裡,那段話緊接在
`## 4. Converge within one bounded episode` 區塊的 `<!-- /gate -->` 之後、
`## 5. Finalize` 之前——確實落在收斂已關閉、Finalize(產生 attestation)尚未開
始的窗口裡。

**內容檢查**：
- 不點名任何 plugin——只提到路徑 `docs/loom/memory/`,沒有出現
  「loom-workflow」「loom-memory」等 plugin 名稱。
- 不呼叫任何工具——整段是敘述性散文,沒有指令、沒有程式碼區塊。
- 沒有 gate marker——它在 `<!-- /gate -->` 之後,不在任何 `<!-- gate: … -->`
  區塊內。

**跑 `check_mechanisms.py`**,原文輸出逐字如下：

```
class          recomputed registered
skill                  18         18
checker-rule           19         19
hook                    4          3
contract               63         63
prose-gate             15         15
net mechanism count (excl. host-hygiene): 118
baseline net count: 118
exempt from net count: PostToolUse:Skill:language-anchor.py
all clear
```

net mechanism count 與 baseline 相同(118 = 118),腳本回報 `all clear`。（`hook`
一列 recomputed 4 / registered 3 有落差,但腳本判定不影響「all clear」的整體結
論,且與這次改動的檔案無關,我沒有進一步追查它是否為既有基線瑕疵。）

**結論：PASS。**

---

## Acceptance 6 — 記憶腳本本體完全沒被動過

```
git diff origin/main..HEAD -- loom-workflow/skills/loom-memory/scripts/loom_memory.py
```
輸出為空(0 行)。

**結論：PASS。**

---

## 兩個必跑指令的逐字結果

### 1. 套件測試（loom-family）

```
uv run --isolated --with-requirements requirements-package-tests.lock python scripts/run_package_tests.py --loom-family -q
```
此指令跑超過 120 秒背景執行,以 Monitor 等到完成,**exit code 0**。因為原指令
自帶 `| tail -80`,終端只保留輸出的最後 80 行,逐字如下(節錄結尾摘要區塊,全
部是 PASS,沒有任何 FAIL 字樣)：

```
PASS — --verify with no ref exits 1 (usage error)
Unresolvable ref: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
PASS — --verify on unresolvable ref exits 2
No memory trailer found in feef0105a0c25b6a60c05c46b36c0fdd0fcd8bd9
PASS — --verify on Related-only commit C exits 4

================================================================
Summary: 5 PASS / 0 FAIL
================================================================
PASS — compose-commit.md exists
PASS — Privacy gate neighborhood present and runs layer-1 privacy-scan.py
PASS — Privacy gate neighborhood conditionally dispatches the layer-2 judge via privacy-judge-spec.md
PASS — Privacy gate neighborhood states an explicit fail-closed -> BLOCK branch
PASS — Quality advisory neighborhood present (quality_note, non-blocking, points at privacy-judge-spec.md)

================================================================
Summary: 5 PASS / 0 FAIL
================================================================
PASS — Privacy gate neighborhood present (layer-1 script + layer-2 SSOT pointer)
PASS — Privacy gate neighborhood specifies the BLOCKED + escalate-to-human verdict
PASS — Privacy gate neighborhood pins the explicit fail-closed branch (script error / dispatch failure / non-conforming -> BLOCK)
PASS — Privacy gate neighborhood correctly omits the commit-only quality_note block
PASS — Privacy gate heading (line 261) precedes the 'gh pr create' hand-off (line 291)

================================================================
Summary: 5 PASS / 0 FAIL
================================================================
PASS — privacy-judge-spec.md exists
PASS — Dispatch instruction neighborhood present (fresh-context + content-not-commands guard)
PASS — Categories neighborhood lists all four categories + secrets carve-out
PASS — Output schema neighborhood specifies PASS|BLOCK + findings (category/quoted span/why)
PASS — quality_note neighborhood present (optional, commit-only, non-blocking, never escalates)
PASS — Fail-closed neighborhood present (explicit dispatch-failure + non-conforming → BLOCK)

================================================================
Summary: 6 PASS / 0 FAIL
================================================================
PASS — privacy-scan.py exists
denylist: not configured
PASS — clean text → exit 0, empty JSON list
denylist: not configured
PASS — planted AWS key → exit 3, finding names aws_access_key
denylist: not configured
PASS — planted PEM private-key header → exit 3, finding names pem_private_key
denylist: not configured
PASS — planted Slack bot token → exit 3, finding names slack_token
denylist: not configured
PASS — planted generic secret assignment → exit 3, finding names generic_secret_assignment
PASS — redaction: full AWS key literal absent from stdout
denylist: not configured
PASS — stdin path (no --text-file) → exit 0, empty JSON list
PASS — planted deny-list term (via --denylist) → exit 3, finding names denylist
PASS — deny-list term matches differently-cased text (case-insensitive) → exit 3
PASS — short deny-list term ('Visa') never revealed in full in stdout

================================================================
Summary: 11 PASS / 0 FAIL
================================================================
```

跑完後在 `loom-code/scripts/__pycache__` 與
`loom-workflow/skills/loom-memory/scripts/__pycache__` 留下殘留,已清除
（`git status --porcelain` 確認乾淨）。

### 2. 這次改動的對抗探針

```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest docs/loom/2026-09-11-memory-timing-in-the-skill/evidence/probes/ -q -p no:cacheprovider
```
逐字輸出：
```
...........                                                              [100%]
11 passed in 3.23s
```
跑完後在 `evidence/probes/__pycache__` 留下殘留,已清除。

---

## 判斷題:同一缺陷(斷言釘的範圍比它守的條款寬)被抓到四次,現在的守衛範圍對了嗎?

**我的判斷：對了,而且我不是只看說法,是自己重現過。** 理由：

1. `test_skill_contract.py` 裡四支守住 Record 兩半的測試,全部改成先用
   `_section(text, "Record")` 把比對範圍切到 `SKILL.md` 裡 `### Record` 這一
   節本身,而不是整份 skill 文字的聯集;針對 `operations.md` 的那支測試也是直
   接讀 `operations.md` 單一檔案,不混進 `SKILL.md` 的內容。測試模組的註解明講
   「against the union an adversarial probe showed the pin staying green while
   the shipped contract was rewritten, because references/operations.md still
   carried the phrases」——這正是「釘的範圍比條款寬」這個缺陷的具體樣子:條款
   已經被改壞,但因為斷言掃了整份文字聯集,舊版措辭還殘留在別的檔案裡,測試看
   不出來。
2. 我自己動手把 Record 段落裡的「pure overhead」換成「extra work」,只改了
   `SKILL.md` 一個檔案、一個片語,結果兩支測試(片語測試 + digest 測試)當場
   轉紅,而且失敗訊息指名的正是我改動的那個片語——沒有「改了條款但測試沒發
   現」的漏網情況。
3. commit 標題(`fix(loom): scope every assertion to its clause's home`)與
   `docs/loom/2026-09-11-memory-timing-in-the-skill/evidence/probes/` 底下那支
   探針,都獨立佐證這是這次改動最後一輪處理的問題——我自己的突變結果與這些旁
   證方向一致。

我沒有驗證的部分:我沒有另外重新跑一次 `evals/record-timing.md` 的冷讀評測(那
需要另外派一個 agent,而我被要求不能派 subagent),所以「稀釋」這一半的正確性
仍然只能建立在既有的兩次紀錄報告(見 Acceptance 2)之上,不是我自己的第三次獨
立冷讀。

---

## 六條 Acceptance 總表

| # | 結果 |
|---|------|
| 1 | PASS |
| 2 | PASS |
| 3 | PASS |
| 4 | PARTLY — 前三點通過;第四點(intent/plan 不得描述機制性質)在 `plan.md` W1-02 的 Risk 欄位仍殘留「字串粒度斷言」「已知失效模式」等機制性質敘述 |
| 5 | PASS |
| 6 | PASS |
