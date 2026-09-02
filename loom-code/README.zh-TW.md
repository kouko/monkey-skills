# loom-code

> **五個站，把一次變更從計畫送到合併的 PR；外加一個 checker，擋掉「審查
> 其實沒發生」的 push。** loom-code 假設你具備基本軟體工程知識，而不是
> 熟悉這個 plugin：每次變更只問你三個問題，其餘自己決定。因為品質的來源
> 是機器檢查機器 —— 寫的 agent 永遠不會是審的 agent。

**狀態**：v1.0.0 — 5 個 skill。破壞性變更：1.0 之前的 skill、agent、script
是刪除而非改名。詳見 [CHANGELOG.md](CHANGELOG.md)。
**語言**：[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**儲存庫**：[`monkey-skills`](https://github.com/kouko/monkey-skills) 的一部分

---

## 五個站

| 站 | 產物 | 內文 |
|---|---|---|
| `write-plan` | `docs/loom/<change-id>/plan.md` — 任務 DAG | [SKILL.md](skills/write-plan/SKILL.md) |
| `build` | commit，一個任務一個，各帶 `Task: <id>` trailer | [SKILL.md](skills/build/SKILL.md) |
| `review` | `docs/loom/<change-id>/review.json` — verdict、probe、finding | [SKILL.md](skills/review/SKILL.md) |
| `ship` | PR、memory trailer、合併 | [SKILL.md](skills/ship/SKILL.md) |
| `maintain` | 把告警或事故變成一份 intent | [SKILL.md](skills/maintain/SKILL.md) |

說出你要什麼，入口是 `write-plan`。裝了 `loom-design` 時，上游會多出
`capture-intent` 與 `write-spec`；沒裝時，`write-plan` 自己兼這兩件事。

## 會問你的三個問題

其餘全部代你決定，並記下理由。

1. **這是你要的嗎？** —— 在任何程式碼存在之前，用白話覆述你的意圖。
2. **你打 X，會看到 Y，對嗎？** —— 可見的行為。只有 product 變更會問，
   engineering 不問。
3. **做到了嗎？** —— 你讀的是一份盲跑報告，由從未碰過這次變更的 agent
   寫的，不是 diff。

不可逆的岔路（刪資料、公開介面、單向遷移）併進當時開著的 ① 或 ②，
用後果的形式問。

## contract package

`contract/manifest.yaml` 宣告站、action，以及四種 artifact（intent、spec、
plan、review）的每一個欄位。`loom-design` 讀它並宣告 `requires-contract`；
`loom-workflow` 不宣告——只有它的 `decision-map` skill 在一次 delivery
前跑 `contract --require`。只有 loom-code 寫它。空白範本在
`contract/templates/`。

## checker

`scripts/loom_checker.py` 就是整個決定性層 —— 27 條規則（以 `--list-rules` 為準），`--list-rules`
可列出。它掛在 SessionStart hook 與 `git push` / `gh pr create` /
`gh pr merge` 之前，而且是重算而非採信：package 測試與對抗 probe 都由它
自己重跑一次，看退出碼。它擋的是手滑，不宣稱擋得住蓄意作弊。

## 安裝

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-code@monkey-skills
claude plugin list | grep loom-code       # 預期：enabled
```

`loom-design` 與 `loom-workflow` 安裝方式相同。三者可獨立安裝，loom-code
不需要另外兩個；某一站走到選配的交接而該 plugin 不在時，該步驟以 N/A 加理由
回報，並在自身契約允許的範圍內繼續。相接處只有帶 plugin 名的 skill 名（例如
`loom-design:write-spec`）、contract package，以及專案自己的 `docs/loom/`
產物 —— 不會去讀別的 plugin 的 `hooks/`、`skills/`、`scripts/`。

### Codex CLI

Codex 沒有 plugin marketplace，所以 checker 是複製進 repo 的：

```bash
python3 scripts/codex_scaffold.py --repo .
python3 scripts/codex_scaffold.py --self-test
```

前者寫出 `.codex/hooks.json` 與一份帶版本戳的 checker 副本；後者對那份副本
發一次假 push，證明它跑得起來。兩者都證明不了 Codex 會去跑它 —— 未授信的
hook 會被靜默跳過，只有 Codex 自己發出的指令才會經過它的 hook 引擎。真正的
probe（一次注定失敗的 push，答案必須以 `BLOCK push.` 開頭）屬於站本身
（`write-plan` step 0b）：當回答的是 git 而不是 checker，它就請使用者跑一次
`/hooks`。

## 授權

MIT，作為 `monkey-skills` 的一部分。
