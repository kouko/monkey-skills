# 4dx-meta-strategy-triage（topic router）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 4DX 適合性 triage 的 topic-router。當使用者的 scope（個人 vs team）還不明確時觸發。

## 這個 router 做什麼

捕捉「4DX 適合嗎？」這類沒有 actor 的曖昧問題，用 Socratic 一問把 scope 釐清，再委派給 scope-specific 的 triage skill。它本身不跑 triage。

## 何時觸發

- "Is 4DX a good fit?" / "Should we use 4DX?" / "Is 4DX overkill?"
- 「4DX 適してる？」「4DX 使うべき？」「4DX 合ってる？」
- 「4DX 適合嗎？」「我/我們該用 4DX 嗎？」「4DX 會不會太重？」
- 任何 actor 未指定（沒有「我自己」「我們團隊」這類錨點）的方法論-fit 詢問

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 明說「自己」/ "for myself" / 自分のため | 直接 `4dx-meta-personal-strategy-triage` |
| 明說「團隊 / 組織」/ "for our team" / うちの team | 直接 `4dx-meta-team-strategy-triage` |
| 已過 triage、要問怎麼開始 | `4dx-d1-personal-whirlwind-triage` 或 `4dx-d1-wig-formulation` |
| 是 member、繼承上面給的 WIG | `4dx-d1-member-team-wig-comprehension` |
| 主題是 lead measure / scoreboard / cadence | 對應的 D2 / D3 / D4 atomic skill（不在本 router 範圍） |

## 配下的 atomic skill

| Slug | Scope | 產出 |
|---|---|---|
| `4dx-meta-personal-strategy-triage` | Personal（solo） | 6 verdict 之一: APPLICABLE / habit / portfolio-bet / emergency / creative / no-time-sovereignty |
| `4dx-meta-team-strategy-triage` | Team-leader | team-fit verdict + leader 準備度檢查 |

（member scope 刻意不收 —— member 不 triage 方法論-fit，是繼承上面定的 WIG。）

## 延伸

- [`SKILL.md`](SKILL.md) 完整 routing logic + Socratic 決策樹 + hand-off scripts
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外的問題
