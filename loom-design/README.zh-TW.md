# loom-design

> **兩個站，把粗略的想法變成確認過的 intent，以及一份使用者用自己的話讀回的
> spec；另有兩個工具，決定產品的原則與長相。** loom-design 只寫草稿，不打分數。
> 這裡產出的東西一律由 `loom-code` 的 review 站下 verdict，而且下判斷的 agent
> 不是寫草稿的那一個。

**Status**: v1.0.0 — 4 個 skill。Breaking：pre-1.0 的 skill、script 與分檔 README
是刪除，不是改名。見 [CHANGELOG.md](CHANGELOG.md)。
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: [`monkey-skills`](https://github.com/kouko/monkey-skills) 的一部分

---

## 兩個站

| 站 | 產物 | 讀這份 |
|---|---|---|
| `capture-intent` | `docs/loom/intent/<change-id>.md` — 用使用者的話寫下的變更，帶 `status: confirmed` | [SKILL.md](skills/capture-intent/SKILL.md) |
| `write-spec` | `docs/loom/<change-id>/spec.md` — 需求、決策與各自的決定者、現狀證據、UI flows | [SKILL.md](skills/write-spec/SKILL.md) |

一個變更若是從想法而不是從計畫開始，入口就是 `capture-intent`：訪談、寫下
intent、交棒 — 需要設計的交給 `write-spec`，不需要的直接交給 `loom-code` 的
`write-plan`。沒裝 loom-design 時，`write-plan` 會自己做這兩件事，但做得比較差。

## 兩個工具

| 工具 | 產物 | 讀這份 |
|---|---|---|
| `product-principles` | `PRINCIPLES.md` — Who、Non-negotiables（≥3 條）、Won't do、Failure we must avoid、Fixed choices，以及一行由使用者親口說 yes 才寫上的 `ratified-by: <name> <date>` | [SKILL.md](skills/product-principles/SKILL.md) |
| `design-system` | `docs/loom/DESIGN.md` — GUI 的顏色、字級、版面與元件 token；TUI/CLI 則是 conventions stub | [SKILL.md](skills/design-system/SKILL.md) |

工具是你叫它才跑，產出一個檔案就停。`design-system` 永遠不擋變更：沒有
DESIGN.md 只是一句註記，不是閘。`product-principles` 不一樣 —— 變更標為
`kind: product` 時，除非 `PRINCIPLES.md` 存在、至少三條 non-negotiables、且帶
`ratified-by:` 行，否則 loom-code 的 checker 直接拒收，因為除了使用者沒有人
能 ratify。

## 兩個決策點

一次變更總共只問使用者三個問題，前兩個歸 loom-design；第三個（「它做到了嗎」）
歸 `loom-code` 的 ship 站。

1. **① 這是你要的嗎？** — `capture-intent` 用白話把變更覆述一次，問題敘述裡
   不出現檔案路徑、模組名稱或腳本檔名，然後等一個 yes。下游沒有任何一站會
   收非 `status: confirmed` 的 intent。
2. **② 你做 X 就會看到 Y，對嗎？** — `write-spec` 把看得見的行為讀回去，只在
   product 變更問，engineering 變更永遠不問；答案記成 `confirmed-behavior:`。

不可逆的岔路（刪資料、公開介面、單向 migration）不另外開一個問題，而是併進
① 或 ② 之中還開著的那一個，用「之後就會怎樣」的後果形式問。

## 需要 loom-code ≥ 1.0

loom-design 只讀、絕不寫 `loom-code` 的 contract package：
`contract/manifest.yaml` 宣告 artifact 的 schema，`contract/templates/` 放各種
空白模板。`plugin.json` 宣告 `requires-contract: ">=1.0"`，而每個站與工具的
第一步都是

```bash
python3 <loom-code>/scripts/loom_checker.py contract --require 1.0
```

版本對不上就 BLOCK，而不是對著看不懂的 contract 硬寫。checker 是 loom-code 的；
loom-design 不執行任何閘，只點名它們。

## 安裝

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-design@monkey-skills
claude plugin list | grep loom-design     # 應該看到 enabled
```

`loom-code` 用同樣方式安裝，而且是必要的。plugin 之間只透過帶 plugin 名的
skill 名稱（例如 `loom-design:write-spec`）、contract package，以及專案自己的
`docs/loom/` 產物相接 —— 絕不碰別的 plugin 私有的 `hooks/`、`skills/`、
`scripts/` 路徑。

### Codex CLI

Codex 沒有 marketplace，plugin 直接從 checkout 讀，loom-code 的 checker 會被
scaffold 成 repo 內的 `.codex/hooks/loom_checker.py`。指令見 loom-code 的
README；它叫你去跑 `/hooks` 就要去跑 —— 未授信的 Codex hook 會被靜默跳過，
看起來跟檢查通過一模一樣。

## 跑測試

```bash
python3 -m pytest loom-design/scripts/
```

一次呼叫就收齊三個站目錄（`interface/`、`principles/`、`spec/`）。
`scripts/pytest.ini` 設 `--import-mode=importlib`，讓同名的 test 模組能並存；
`pythonpath` 再把站目錄放回 `sys.path`，讓 bare sibling import 還能用。
`test_unified_pytest_root.py` 把這個安排釘住，所以「每個目錄開一個 job」的
fan-out 不會不小心跑回來。

## 授權

MIT，作為 `monkey-skills` 的一部分。
