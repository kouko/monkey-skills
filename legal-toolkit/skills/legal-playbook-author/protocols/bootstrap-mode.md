# bootstrap-mode — first-time playbook setup

**Trigger**: `legal-playbook/` is missing or empty in the working folder, OR the user explicitly says "first install" / "I just got this plugin" / "從零開始".
**Inverse**: see `protocols/extend-mode.md` for adding a clause to an existing playbook, `protocols/revise-mode.md` for editing one.

---

## Purpose

Bootstrap mode is the **on-ramp** for a brand-new user. Goal: in under 10 minutes, take them from "I just installed the plugin" to "I have a `legal-playbook/` folder I can run `legal-contract-review` against immediately, and I understand how to revise it later."

The mode never forces the user to author from scratch — it always offers the bundled fallback seed as Path A so they can be productive within seconds.

---

## Pipeline

### Step 1 — Detect & confirm

Detect:
- `<cwd>/legal-playbook/` exists? → false
- `<ancestors-up-to-5>/legal-playbook/` exists? → false
- BFS depth 5 → no hit

Action:
- Read the user's working folder. Confirm with them that this is the right place to put the playbook (often it is; sometimes they mean a parent folder).

Prompt to user (zh-TW):

> 偵測到你還沒有 `legal-playbook/`。
> 我打算在 `<absolute path to cwd>/legal-playbook/` 建立你的 playbook。
> 確認嗎？(yes / 改路徑 / 取消)

### Step 2 — Offer 3 paths

Present three choices. Default is Path A.

```
你想怎麼起手？

(a) Seed from bundled fallback (推薦給第一次裝的人)
    從 plugin 內建的 4 條 baseline (confidentiality / governing-law /
    auto-renewal / termination-and-survival) 複製一份到你的 legal-playbook/，
    然後我會逐條提醒你把 escalate_to 跟 owner 改成你公司的版本。
    完成時間：~5 分鐘。

(b) 5-question interview (從零建第一條)
    我問你 5 個問題，產出 1 條 entry。你之後可以再呼叫 extend mode 加更多條。
    完成時間：~10 分鐘 / 條。

(c) Skip — 不建 playbook，先用 bundled fallback read-only 跑 contract-review
    你還是可以馬上跑 review，每個 finding 會帶 banner 標明是 bundled fallback。
    之後想客製化再隨時呼叫 bootstrap。
    完成時間：0 分鐘。
```

### Step 3a — Path A (seed from bundled fallback)

1. Copy these 4 files from the plugin bundle to `<cwd>/legal-playbook/`:
   - `<plugin>/legal-contract-review/assets/baseline-fallback-confidentiality.md` → `<cwd>/legal-playbook/confidentiality.md`
   - `<plugin>/legal-contract-review/assets/baseline-fallback-governing-law-jurisdiction.md` → `<cwd>/legal-playbook/governing-law-jurisdiction.md`
   - `<plugin>/legal-contract-review/assets/baseline-fallback-auto-renewal.md` → `<cwd>/legal-playbook/auto-renewal.md`
   - `<plugin>/legal-contract-review/assets/baseline-fallback-termination-and-survival.md` → `<cwd>/legal-playbook/termination-and-survival.md`

2. For each copied file, **mutate** these frontmatter fields:
   - `source_type: bundled_fallback` → `source_type: user_playbook`
   - `last_updated: <today's ISO date>`
   - `owner: <ask user>`  (interactive prompt: "Who maintains this playbook? Use your name or your team's name.")
   - `escalate_to:` — leave the placeholder `[請編輯為你公司的角色：法務主管 / GC / 部門主管]` for now; remind user to customise in Step 5.

3. Write `<cwd>/legal-playbook/README.md` using the template at the end of this protocol.

4. Proceed to Step 5 (post-seed customisation prompts).

### Step 3b — Path B (5-question interview)

1. Ask which clause to start with. Recommend `confidentiality` (most common, simplest structure) but accept anything.

2. Run the 5-question interview. Answers must be persisted **after each question** (so an interrupted session does not lose work). Persist target is `<cwd>/legal-playbook/<clause-id>.md` (flat layout by default).

   **Q1 — walk_away_triggers** (紅線)
   > 在哪些情況下你絕不接受這條 clause？例如：「單方面（只我方有義務）」或「永久保密」。可以列 2-4 條。

   Persist to: frontmatter `walk_away_triggers`.

   **Q2 — escalate_to** (升級對象)
   > 觸發紅線時要找誰簽核？(法務主管 / GC / 老闆 / 部門主管 / 外部律師)

   Persist to: frontmatter `escalate_to`.

   **Q3 — risk_default** (預設燈號)
   > 對方草擬的版本通常落在哪個區間？(green = 通常都接受得了；yellow = 需要看；red = 通常要改)

   Persist to: frontmatter `risk_default`.

   **Q4 — 偏好立場** (preferred)
   > 我方理想的立場是什麼？一句話到三句話，例如：「雙向、5 年、明確定義機密範圍」。

   Persist to: body section `## 偏好立場`.

   **Q5 — Fallback 1**
   > 如果對方不接受偏好立場，你願意退到哪？例如：「雙向、3 年、加 carve-out 已知資訊」。

   Persist to: body section `## Fallback 1`.

   **Q6 (also)** — 業務翻譯
   > 一句話告訴非法務人員「為什麼這條重要」？例如：「出商業秘密我們扛得起賠償，但對方拿走我們的東西必須有對等義務」。

   Persist to: body section `## 為什麼這條重要`.

3. Add other frontmatter fields with sensible defaults:
   - `clause_id` ← from Step 1
   - `contract_types_applicable: [SaaS, MSA, NDA]` (best-effort guess; tell user "I'll set X / Y / Z; correct me if wrong")
   - `last_updated: <today>`
   - `owner: <ask>` (same as Path A)
   - `source_type: user_playbook`

4. Write `<cwd>/legal-playbook/README.md` if not already present.

5. Check for variant-upgrade triggers — see SKILL.md §"Variant-upgrade detection". If triggered, offer to migrate. If user declines, set `variant_upgrade_offered: true` in frontmatter.

6. Proceed to Step 5.

### Step 3c — Path C (skip)

1. Write a tiny note at `<cwd>/legal-playbook/.skipped` (just a timestamp, so bootstrap can offer Path A/B next time without re-prompting noise).

2. Confirm to user: "OK, no playbook authored. You can run `/legal-contract-review` and it will use the 4 bundled fallback baselines automatically. Whenever you want to customise, just re-invoke this skill."

3. Exit.

### Step 4 — (skipped — that was Step 3 sub-paths)

### Step 5 — Post-seed customisation prompts (Paths A & B)

After files are written, the skill displays a **summary** + **next-step prompts**:

```
✅ Wrote N files to <cwd>/legal-playbook/:
   - confidentiality.md          [seeded, customisation needed]
   - governing-law-jurisdiction.md [seeded, customisation needed]
   - auto-renewal.md             [seeded, customisation needed]
   - termination-and-survival.md [seeded, customisation needed]
   - README.md                   [auto-written guide]

⚠️ The seeded entries use placeholder escalate_to values. Run a contract
   review and they'll work, but you should customise them within the first
   week. Suggested next steps:

   - [ ] Review each clause's "## 偏好立場" / "## Fallback 1" — do they
         match your company's actual negotiation position?
   - [ ] Set the real escalate_to for each clause (Who signs off when
         the red line is hit?). Run: /legal-playbook-author revise <clause-id>
   - [ ] Set the real owner field. (currently: <your-name>)
   - [ ] Consider git-tracking the legal-playbook/ folder. (legal-outputs/
         and .legal-toolkit/ should go in .gitignore.)

You can now run /legal-contract-review on any contract.
```

### Step 6 — Optional kickoff

Offer the user a graceful entry into using the playbook immediately:

> 要不要現在試跑一份 contract review？把合約路徑貼上來就行。

If the user provides one, hand off to `/legal-contract-review` with the
path. Otherwise, exit cleanly.

---

## Output contract

The skill's last line(s) to the user end with this fixed block (for
testability and so the router can detect completion):

```
✅ bootstrap-mode complete.
   Files written: <count>
   Path used: A / B / C
   Customisation pending: <count of placeholder fields>
```

---

## `legal-playbook/README.md` template (seeded into user folder)

This file is written into the user's `legal-playbook/` directory the
first time bootstrap mode runs. It is meant for the human user, not
the LLM.

```markdown
# Legal Playbook

這個資料夾存放本公司的合約議價規則（playbook）。
工具 `legal-toolkit` 會在 contract review 時讀這個資料夾。

## 你看到的是什麼

每個 `.md` 檔對應一條合約條款的議價規則，欄位包含：
- 偏好立場（preferred）
- Fallback 退讓階梯
- 紅線（walk_away_triggers）
- 升級對象（escalate_to）

複雜條款開資料夾（例如 `limitation-of-liability/`），
裡面有 `_clause.md` 跟多個 variant 對應不同 deal size。

## 怎麼維護

- 每次 contract review 後，把「我對這條其實有意見」的地方
  寫回對應檔案，呼叫 `legal-playbook-author revise <clause-id>` 即可。
- 每季 review 一次（建議跟業務一起 align）。
- 每年 major update（隨市場行情 / 法規變動）。

## 工具如何使用這份 playbook

`legal-contract-review` 會：
1. Session start 掃這個資料夾建 index
2. 對每條合約條款用 ABAC 過濾出 matched variant
3. 用 frontmatter（gates / triggers / escalate）做決定性判斷
4. 用 body（preferred / fallback prose）給 LLM 比對

## 建議的 Git 工作流

```bash
git init
git add legal-playbook/        # 只 track 這個資料夾
git commit -m "Initial playbook v1.0"

# 每次 revise 後
git add legal-playbook/
git commit -m "Update LoL fallback for enterprise tier"
```

`legal-outputs/` 跟 `.legal-toolkit/` 應該放進 `.gitignore`
（前者是 per-run 結果，後者是工具 internals）。

## 從 bundled fallback 起手的你

如果這個 playbook 是從 bundled baseline seed 出來的，
**請務必在第一週內逐條把 `escalate_to` 改成你公司的實際角色**。
Bundled baseline 用 `[請編輯為你公司的角色：...]` 佔位，
工具偵測到佔位符會在 escalation.md 加 warning callout。

---

> 本 playbook 的內容是「你公司的議價規則」，不是「法律意見」。
> 工具產出的審查結果也帶 disclaimer——請以執業律師為準。
```

(The template above is verbatim what gets written to the user folder.
The Disclaimer footer at the end mirrors `assets/disclaimer-block.md`
but is shortened because the README is internal to the playbook, not
an output to a counterparty.)
