# Goal Create

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ゴール条件を起草する。2 つの名前付きモード：**SESSION** は長時間実行
> エージェントの run を照合する 4 項目ゴールを書く。**ARC** はリポジトリの
> purpose アーティファクトの草案をユーザーが確定できるよう書く。

---

## 概要 — このスキルは何をするか

このスキルは、ユーザーが何を求めているかで選ばれる 2 つのうちどちらかを
起草する——エージェントが文脈から推測することはない。

- **SESSION モード** は、長時間実行エージェントの run が照合される
  4 項目ゴール条件——`Outcome`、`Constraints`、`Verification`、
  `Stop-when`——を作る（例：Claude Code の `/goal` コマンド向け）。
  項目の順序と各項目の定義は `references/goal-shape.md` の権威内容。
  草案の元になる 2 つの入力スロット、片方が空のときの拒否ルール、各項目が
  持つべき provenance タグは `references/input-floor.md` にある。
  草案を提示する前に、機械的な下限チェック `scripts/goal_lint.py` を通す
  ——構造のみを見る。文章が実際に判定可能に読めるかどうかの判断はしない。

- **ARC モード** は、リポジトリの purpose アーティファクト
  `docs/loom/PURPOSE.md` 向けの `Why` と `Done when` の草案を作る。
  このスキル自身がそのファイルを書くことはない——草案は必ずユーザー自身の
  確認によってのみ確定される。リポジトリに purpose アーティファクトも
  `docs/loom/` ストアも存在しない場合、ARC は自分が適用不可であると報告し、
  何も足場を作らない。

この README は人間向けの概要。このフォルダの `SKILL.md` が実行契約——
両モードと両参照ファイルが読み込まれる出典であり、このファイルはそれを
繰り返さない。

---

## 呼び出し

このスキルは自ら発火しない。ゴールの必要性がすでに見えている 2 箇所——
`loom-workflow:handoff` の Prepare モードと、`loom-code` の purpose-link
チェックが出す未回答 purpose メッセージ——で選択肢として名指しされる。
そこで名指しされることは、呼び出すことではない。

---

## Files

```
goal-create/
├── README.md              <- English README
├── README.ja.md           <- 本ファイル（日本語）
├── README.zh-TW.md        <- 繁體中文 README
├── SKILL.md               <- 実行ファイル（Claude 向け）
├── references/
│   ├── goal-shape.md       <- 4 項目ゴール形状、SESSION の SSOT
│   └── input-floor.md      <- 入力スロット、拒否ルール、基準、provenance タグ
└── scripts/
    └── goal_lint.py        <- SESSION の機械的な下限チェック
```
