# 4DX D1 — Team WIG Cascade

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> あなた（leader-of-leaders）を coach し、設定済みの組織 Primary WIG を 3-7 の subordinate team の Team WIG へ Ch 7 の 4 ルールで翻訳する。

## このスキルが起動するとき

- 「上から降りた WIG をチーム単位に落とす」
- 「直属マネージャー毎の Team WIG をどう決める」
- 上位から WIG が降りてきて分解する必要がある
- 多階層組織で region → district、division → team と段階的に降ろす
- 初回 cascade で Battle WIG が 7+ になった、または全チームに同一 WIG を割り当てた

## 何をするか（プロトコル概要）

Leader-of-leaders の consultant。最重要の仕事は **Rule 3 — veto, don't dictate** の徹底:

1. **上流の Primary WIG を確認** — *From X to Y by When* 形式が前提
2. **subordinate team を列挙** — N team + 各機能（3-7 が理想）
3. **cascade 形状を分類** — functionally diverse か functionally similar か
4. **Key Battles を抽出** — 最小数（Opryland: 17 → 3）。典型は 2-3
5. **各 team-leader から Team WIG 提案を募る** — pull, not push。代わりに割り当てない
6. **ladder-up テスト** — vibe ではなく算数。contribution 合計 ≥ Battle ≥ Primary WIG
7. **veto テスト（Rule 3）** — accept か再提案差し戻し。書き換えない
8. **One-WIG-per-individual（Rule 1）** — overload を避ける
9. **cascade 深度 check** — 2 層超？各層でこの skill を再走
10. **cascade map を出力** — Primary WIG → Battles → Team WIGs、声に出して確認

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 組織 Primary WIG が未確定 | `4dx-d1-wig-formulation` |
| leader が 1 team のみ（subordinate team-leader 不在） | `4dx-d1-wig-formulation` |
| solo / 個人目標 | `4dx-d1-wig-formulation` |
| 固定終点の single-shot project | プロジェクトマネジメント（WBS / Gantt） |
| 方法論の適合性が未確認 | `4dx-meta-strategy-triage` |

## 出典

*The 4 Disciplines of Execution* 第 2 版（2021）第 7 章 Translating Organizational Focus Into Executable Targets より蒸留。3 anchor case: Opryland Hotel（functionally diverse cascade — 75 team、17 → 3 Battles）、多店舗 retailer（functionally similar cascade、leaf 層に Battle 選択自律性）、Sydney 会計事務所（小規模 cascade、中間 Battle 層を畳む）。

Rule 1-4、Targets-not-Plans 原則、cascade-too-deep-in-one-pass anti-pattern を含む完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
