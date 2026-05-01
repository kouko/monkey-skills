# 4DX D1 — Team WIG Cascade

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> あなた（leader-of-leaders）を coach または audit し、設定済みの組織 Primary WIG を 3-7 の subordinate team の Team WIG へ Ch 7 の 4 ルールで翻訳する／既存 cascade を診断する。**2 つのモード**: coach（ゼロから組み立て）+ audit（既存 cascade map + 下のリーダーの不満を診断）。

## このスキルが起動するとき

**Coach-mode（ゼロから組み立て）:**
- 「上から降りた WIG をチーム単位に落とす」
- 「直属マネージャー毎の Team WIG をどう決める」
- 上位から WIG が降りてきて分解する必要がある
- 多階層組織で region → district、division → team と段階的に降ろす

**Audit-mode（既存 cascade を診断）:**
- 「うちの cascade を診断して、下のリーダー達が文句言ってる」
- 「cascade map 見て何がダメか」
- 下のリーダーが「押し付け」「上に繋がらない」「色々やらされる」と言っている
- 初回 cascade で Battle WIG が 7+ になった／全チーム同一 WIG → 診断したい（rebuild ではなく）

## 何をするか

Leader-of-leaders の consultant。2 つの protocol（必要時に load）:

### `protocols/coach-mode.md` — Socratic 10 ステップ build

最重要: **Rule 3 — veto, don't dictate** の徹底。

1. 上流の Primary WIG 確認（X→Y→When）
2. subordinate team 列挙（3-7 が理想）
3. cascade 形状分類（diverse か similar か）
4. Key Battles 抽出（Opryland: 17 → 3、典型 2-3）
5. 各 team-leader から Team WIG 提案を募る（pull, not push）
6. ladder-up テスト（vibe ではなく算数）
7. veto テスト（accept か差し戻し、書き換えない）
8. One-WIG-per-individual
9. cascade 深度 check（2 層超？各層で再走）
10. cascade map 出力

### `protocols/audit-mode.md` — 既存 cascade への consultant 診断

cascade map + 下のリーダー批評を読み → per-rule verdict 表 → 修正案 + 再交渉スクリプト。

- 「押し付け」 → Rule 3 違反
- 「上に繋がらない」 → Rule 2 違反
- 「色々やらされる」 → Rule 1 違反
- 「達成判定できない」 → Rule 4 違反
- 5+ Battles → Battles-count 不合格（narrowing 不十分）
- アクションリスト型 Team WIG → Targets-not-Plans 不合格

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 組織 Primary WIG が未確定 | `4dx-d1-wig-formulation` |
| leader が 1 team のみ（subordinate team-leader 不在） | `4dx-d1-wig-formulation` |
| solo / 個人目標 | `4dx-d1-wig-formulation` |
| 単一 Team WIG の audit（cascade 無し） | `4dx-d1-wig-formulation` audit-mode |
| Cross-layer audit（cascade + leads + scoreboard + cadence） | `4dx-audit`（full-stack） |
| OKR / KR / 四半期目標 cascade | `using-four-dx-coach` |
| 固定終点の single-shot project | プロジェクトマネジメント（WBS / Gantt） |
| 方法論の適合性が未確認 | `4dx-meta-strategy-triage` |

## 出典

*The 4 Disciplines of Execution* 第 2 版（2021）第 7 章 Translating Organizational Focus Into Executable Targets より蒸留。3 anchor case: Opryland Hotel（functionally diverse cascade — 75 team、17 → 3 Battles）、多店舗 retailer（functionally similar cascade、leaf 層に Battle 選択自律性）、Sydney 会計事務所（小規模 cascade、中間 Battle 層を畳む）。

Orchestrator は [`SKILL.md`](SKILL.md)、Socratic 10 ステップ build（Rule 1-4、Targets-not-Plans、cascade-too-deep-in-one-pass anti-pattern を含む）は [`protocols/coach-mode.md`](protocols/coach-mode.md)、既存 cascade artifact への consultant verdict matrix は [`protocols/audit-mode.md`](protocols/audit-mode.md) を参照。
