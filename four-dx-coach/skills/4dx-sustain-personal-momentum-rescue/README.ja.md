# 4DX Sustain & Momentum Rescue

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 4 つの discipline スタックが「実際にどの層で壊れたか」を診断し（D1 / D2 / D3 / D4 / whirlwind / substrate）、「もっと頑張る」ではなく該当する restart に route する。

## このスキルが起動するとき

- 「WIG セッションが続かない」「4DX が止まった」「ここ数週やってない」
- 「scoreboard が空虚に感じる」「記録してるのに何も変わらない」
- 「自分には規律がない」「再開したいがどこから手を付けるか分からない」
- lead はしばらく log していたが lag が動かず、目標は無理だと結論した
- lead は 90%+ 達成しているのに、もう WIG 自体が「wildly important」に感じない
- 実際に外的負荷スパイク（転職・病気・家族の出来事）があり、WIG が押し出された後、自分を「規律がない」と責めている

## 何をするか（プロトコル概要）

非判断的な Socratic 対話で、stack を逆に辿る。各 step で破損層を特定して route。壊れた上流層の上に D4 を再起動しない:

1. **判断せず開く** — 「cadence が崩れたのはいつ頃から？その時、生活で何が起きていた？」
2. **D1 — WIG 自体が今でも wildly important か** — 違うなら `4dx-d1-personal-wig-defining` へ route。死んだ WIG の上に D4 は再起動しない
3. **D2 — lead** — predictive かつ influenceable だったか。lead green + lag flat なら lead が間違い → `4dx-d2-personal-lead-measure-discovery`
4. **D3 — scoreboard** — 5 秒で勝敗が分かったか。隠れていた / coach 用に化けていたら → `4dx-d3-personal-scoreboard`
5. **D4 — cadence** — session を押し出したのは何か。pointless = 上流の問題が変装している（D1-3 へ戻る）；whirlwind crowd-out = 来週再開（make-up しない）
6. **whirlwind エスカレーション check** — 実際の外的負荷スパイクがあったか。あれば `4dx-d1-personal-whirlwind-triage` で容量再設計、または WIG を explicit に pause（pause は failure ではない）
7. **substrate check（off-ramp）** — burnout / 抑うつ / 喪失 / 慢性疲労 → 4DX rescue を停止し、休息 / コーチング / 治療を推奨
8. **shame なしで recognition** — 中断前に user が *実際に* 達成したことを 1-3 個、具体的に言語化（formulaic な「すごい」は禁止）
9. **最小 scope で再 commitment** — *don't skip, don't catch up*。修復ではなく再開。次 7 日に 1 つ tiny commitment

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 初めての 4DX セットアップ | `4dx-meta-personal-strategy-triage` → `4dx-d1-personal-wig-defining` |
| 組織横断 engagement survey / enterprise 診断 | scope 外。このスキルは個人 rescue |
| 臨床的な抑うつ / 慢性 burnout / 喪失 | 専門的支援を。method は care の下流 |
| reactive / 緊急対応領域で whirlwind 自体が業務 | `4dx-d1-personal-whirlwind-triage`。cadence 中断は問題ではないかもしれない |

## 出典

*The 4 Disciplines of Execution* 第 10 章「Sustaining 4DX Results and Engagement」と巻末「The Missing Ingredient」より蒸留。4 つの anchor case: Store 334（D4 追加だけで死にかけ stack が復活）、Stengel の北京 2 AM WIG Session（cadence sacred はリーダーシップ signal）、Mike Crisafulli（説明できない結果を勝ちと認めない＝謙虚さを診断的規律として使う）、Susan / Bianca / Marcus（責めない accountability 対話）。

catch-up trap、Marcus pattern（operator が architect を hijack）、4DX が「この季節にはそもそも合わない」と認める substrate off-ramp を含む完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
