# 4dx-meta-strategy-triage（topic router）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 4DX 適合性 triage の topic-router。scope（個人 vs team）がまだ曖昧なときに起動する。

## このルーターの役割

「4DX 使うべき？」のような actor 未指定の曖昧質問を捕捉し、Socratic な 1 問で scope を浮かび上がらせ、scope 別の triage skill へ委譲する。triage 自体は実行しない。

## 起動するとき

- "Is 4DX a good fit?" / "Should we use 4DX?" / "Is 4DX overkill?"
- 「4DX 適してる？」「4DX 使うべき？」「4DX 合ってる？」
- 「4DX 適合嗎？」「我/我們該用 4DX 嗎？」「4DX 會不會太重？」
- actor 明示なし（「自分一人」「うちの team」のいずれも欠けている）の方法論-fit 質問

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 「自分のため」/ "for myself" / 我自己 と明示 | `4dx-meta-personal-strategy-triage` に直接 |
| 「うちの team / 組織」/ "for our team" / 我們團隊 と明示 | `4dx-meta-team-strategy-triage` に直接 |
| triage 済みで始め方を聞いている | `4dx-d1-personal-whirlwind-triage` か `4dx-d1-wig-formulation` |
| WIG を上から渡された member | `4dx-d1-member-team-wig-comprehension` |
| トピックが lead measure / scoreboard / cadence | D2 / D3 / D4 の atomic skill（このルーターの守備範囲外） |

## 配下の atomic skill

| Slug | Scope | Returns |
|---|---|---|
| `4dx-meta-personal-strategy-triage` | 個人（solo） | 6 verdict のうち 1 つ: APPLICABLE / habit / portfolio-bet / emergency / creative / no-time-sovereignty |
| `4dx-meta-team-strategy-triage` | Team-leader | team-fit verdict + leader 準備確認 |

（member scope は意図的に不在 —— member は方法論-fit を triage しない、上から降りた WIG を継承する。）

## 関連

- [`SKILL.md`](SKILL.md) に完全な routing logic + Socratic 決定木 + hand-off スクリプト
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) は cold-start / 4DX 圏外質問を担当
