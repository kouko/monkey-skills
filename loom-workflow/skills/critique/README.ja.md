# Critique

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 作り始める前に提案を裁く、2 つのレンズを持つ 1 つの skill：
> `mode: proposal` は list を KEEP / DEFER / DROP に振り分け、
> `mode: complexity` は 1 つの変更を deletion-first で量る。

ユーザーが明示的に呼び出す **gate skill**。plan・backlog・提案された
変更が問題の大きさに見合わないと感じたとき、誰かが動き出す前に
批判的な pass を強制するために呼ぶ。

この README は GitHub でこの skill を読む人間向け。Claude が実際に
ロードする operational ファイルは [`SKILL.md`](SKILL.md)。

---

## なぜこの skill が存在するのか？

失敗モードは 2 つ、根は 1 つ：項目が居場所を勝ち取る仕組みがない。

**寛大な list。** plan を求められると Claude は 7 項目、3 つの選択肢、
実質「全部やる」を優先度で包んだ P0/P1/P2 backlog を出す。多くは
grounding が弱く（「業界標準」「将来への備え」）、必要性も曖昧
（「あると良い」）。押し返しがなければ、その肥大した提案がそのまま
plan になる。

**加算のデフォルト。** どの変更も「何を足すか」で語られ、「何を足さずに
済むか」はまれ、「この変更が何を不要にするか」はさらにまれ。結果として
codebase はエントロピーへ向かう——ファイルが増え、未知の未来のための
柔軟性が増え、誰も頼んでいない行が増える。

`mode: proposal` が前者を、`mode: complexity` が後者を捕まえる。

---

## 動作

**まず mode を選ぶ。** list・plan、または 2 つ以上の supporting claim を
持つ prose 推奨 → `proposal`。1 つの具体的な変更（refactor、既存 code への
feature 追加、技術的負債の掃除、名前の付いた greenfield feature）→
`complexity`。3 つ以上の独立した提案なら、先に triage し、生き残りに
`complexity` を個別に当てる。

### mode: proposal

各項目に 2 つの値を与える——**evidence grounding**（`GROUNDED` /
`HEURISTIC-OK` / `SPECULATIVE`）と**必要性**（`ESSENTIAL` /
`SPECULATIVE`）。triage matrix を通して `KEEP`、`KEEP-WITH-CAVEAT`、
`DEFER`、`DROP` に落ちる。再トリガー条件を言語化できない `DEFER` は
`DROP` に落ちるので、保留の山が駐車場にならない。

### mode: complexity

[`references/`](references/) から mindset を 1 つ読み、名前を挙げてから
3 つの質問を順に：

1. **Q1 — 最小の end state。** 最小の変更ではなく、変更後の codebase の
   あるべき姿。「作らない」も選択肢に含める。
2. **Q2 — 総コード量は減るか。** 行・関数・ファイルの before / after。
   増加は許されるが、名前と costs を明示すること。
3. **Q3 — 何を消せるか。** 提案に含まれる実際の削除であって、後日の
   約束ではない。

verdict は `PROCEED` / `PROCEED-WITH-CAVEAT` / `RESHAPE` / `REJECT` の
いずれか 1 つ。

---

## やらないこと

主張は証拠ではない。不確実性は述べるものであって捏造するものではない。
角を丸めるために `DROP` を `DEFER` に書き換えない。gate をユーザーに
投げ返さない。

対象外：単純な Q&A、行動を伴わない説明の箇条書き、些細な rename、
すでに書かれた diff の縮小、完了前の verification。

---

## Attribution

`mode: complexity` は MIT ライセンスの上流プロジェクト連鎖
（`reducing-entropy`）に由来する。連鎖の全体、各リンクの寄与、ライセンス
本文は [`NOTICE`](NOTICE) と [`LICENSE`](LICENSE) にある。同梱の 4 つの
mindset は `domain-teams:code-team/standards/` の canonical 版を追随する。
