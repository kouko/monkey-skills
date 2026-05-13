# Brief Before Asking

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 非自明な engineering decision question の **前** に（または直接の
> 応答として）agent が届ける 6 ブロック構造化ブリーフィング。
> Mental Model が先頭 — code reference や metric の前に着地する
> plain-English の abstraction bridge。ユーザーは数秒で読み、
> 押し返し、確認できる — agent の質問を一からリバース
> エンジニアリングする必要はなくなる。

主動的にトリガーされる **agent 側 skill**：Claude が複雑な
engineering decision（race condition、perf bottleneck、refactor
方向、tech selection、bug root cause）についてユーザーに質問
しようとするとき、この skill が 6 ブロック構造を強制する —
Claude が context ゼロの yes/no（"OK to proceed?"）や jargon
先行の technical dump にデフォルトで落ちるのを防ぐ。ユーザーが
質問について混乱を示したとき（Mode B）、または説明について混乱を
示したとき（Mode C）にも反応的に発火する。

この README は GitHub で読む人間向け。Claude が実際にロードする
operational ファイルは [`SKILL.md`](SKILL.md)。

---

## なぜこの skill が存在するのか？

繰り返される失敗モードは **「agent が言葉が少なすぎた」でも「多
すぎた」でもない**。ほぼ常に **agent が間違った abstraction level
から始めた** ことが原因。Claude は jargon が埋め込まれた
implementation-level の詳細にデフォルトで落ちる。ユーザーは business
semantics の system-level 理解から始める必要がある。Bridge が
なければ、どれだけ詳細を足しても着地しない — むしろ gap が広がる。

現在の 6 ブロック + 3 mode 設計は **4 回のイテレーション** の後に
落ち着いた。各前イテレーションは異なる失敗モードを直したが、
abstraction bridge 問題を見逃した。完全な物語は
[`references/DESIGN.md`](references/DESIGN.md) を参照。短縮版：

| イテレーション | 試したこと | なぜ失敗したか |
|---|---|---|
| **1** | SCQA + MECE + LLM-bias defense + human-bias alert をスタック（8 手続きステップ）| Ceremony が value を圧倒。実コンテンツに到達する前に ~1500 token の構造的オーバーヘッド。「Framework stack」は厳格に感じたが ritual を生んだ。 |
| **2** | 5 フィールド "Minimum Viable Question"（Where / Fork / Options / Default / Escape）+ 4 階 stakes calibration | 実際の pain を誤読。高頻度低 stakes の fork を想定。実際の pain は本当に複雑な fork でクリーンな default がないもの。 |
| **3** | 5 ブロック briefing（Situation / Why-this-fork / Options / My take / Open ends）+ 厳格な depth rules | 間違った abstraction level から始めた。Situation block が code refs と metrics を要求したが、それらはユーザーが「どこに ref が住んでいるか」を既に知って初めて着地する。 |
| **4**（現在）| 6 ブロック + **Mental Model** が先頭 + 3 trigger mode（Proactive / Reactive-on-Question / Reactive-on-Explanation）| Mental Model が abstraction-level mismatch に直接対処。Iteration 3 の depth rules はブロック 2-6 で保持。Mode C は「長い説明だがまだ混乱」というイテレーション 1-3 全部が見逃した失敗を閉じる。 |

遅れて到来した核心 insight：**abstraction-level matching は word
count に勝る**。Plain English 2 文の Mental Model が 200 行の
technical detail を unblock する。それなしには、200 行はただ
混乱を深めるだけ。

---

## どう動くのか？

### 3 つの trigger mode

| Mode | トリガー | 出力形 |
|---|---|---|
| **A — Proactive** | Agent が「自分は非自明な decision についてユーザーに質問しようとしている」と self-detect | フル 6 ブロック briefing → specific request で終わる |
| **B — Reactive on Question** | ユーザーが *質問* を理解しなかったシグナル（「我不懂」「沒頭沒尾」"clarify"）| Bridge → フル 6 ブロック briefing → **元の質問を briefing-grounded な具体形で再質問** |
| **C — Reactive on Explanation** | ユーザーが *説明* を追えなかったシグナル（「跟不上」「太多術語」"ELI5" "in plain English"）| Bridge → **Mental Model block だけ** + 前 turn の jargon を定義 → **一時停止** してユーザーにどこを掘るか聞く |

Mode C は Mode B と構造的に違う。ユーザーは既に jargon で
溺れた — もう 6 ブロックをダンプすればまた溺れるだけ、並べ替えても
同じ。修正は Mental Model を先に着地させ、ユーザーに drill 方向を
選ばせること。

### 6 つのブロック

```
Mental Model     1-2 文 plain-English: system のどこ + なぜ重要（jargon なし）
Situation        Technical state: code refs, metrics, 行った investigation
Why-this-fork    Trigger 条件 + constraint + 質問しなかったら何が起こるか
Options          2-4 の real option を depth 付き（具体 diff、抽象 pros/cons でなく）
My take          Lean（A/B/C）+ ≥3 ステップの reasoning chain + conditional reversal
Open ends        Agent が知らないこと / 答えを flip させる条件 / ユーザーの value call が要るもの
```

各 block は独自の depth 要件と forbidden pattern を持つ。完全な
ruleset は [`SKILL.md`](SKILL.md) にある。短縮版：

- **Mental Model** — code refs なし、metrics なし、未定義 jargon なし。「system のどこにいるか」を business semantics で、「ユーザー視点でなぜ重要か」を答えなければならない。ユーザーが知らないかもしれない term は inline 定義するか flag する。
- **Situation** — ≥1 code ref（filename:lineno）、≥1 quantitative metric、行った investigation。禁止：「looks complex」/「seems slow」。
- **Why-this-fork** — trigger（なぜ今聞くか）、constraint（agent 単独では決められない理由）、聞かなかった場合の cost。
- **Options** — 最小 2 個、最大 4 個、等深さ扱い（「A を 5 行、B を 1 行」は禁止）。各 option は concrete approach、quantitative impact、trade-off、reversibility（two-way vs one-way door）、downstream implications を必要とする。禁止：「simpler」/「modern」/「industry standard」。
- **My take** — 明示的 lean（A / B / C）、≥3 causal step の reasoning chain、conditional reversal（「ただし X が holds なら Y に switch」）。禁止：「either works」/「your call」/「no preference」（agent は code を読んだ；中立を装うのは嘘）。
- **Open ends** — agent が持たない context（ユーザーが持つ info）、答えを flip させる条件、ユーザーの value judgement が要るもの。禁止：「need more context」（vague）、agent 自身で答えられる fake question、disclaimer fluff。

### Mental Model First（荷重を支える insight）

誰もがスキップしたい block。それ以外をすべて着地させる block。
「before」失敗モードはこう見える：

> ❌ "OrderService has a race condition under high concurrency and needs idempotency."
> （jargon 3 つ、plain English ゼロ、system location なし。）

「after」はこう：

> ✅ "This is the async 'deduct inventory after checkout' flow: once an order is written, a message is sent to InventoryService to deduct stock. Problem: the same message sometimes gets processed twice, causing the same order to deduct stock twice (oversells)."
> （Business semantics、jargon なし、結果が把握可能。）

Agent は依然として race condition、saga pattern、idempotency key
を話す必要がある — しかしそれらは Situation / Options / My take で
着地する、ユーザーが map を持った後で。

---

## Worked Example（Mode A、圧縮版）

**設定**：agent が遅い orders-list endpoint に対する index-vs-pagination
refactor についてユーザーに質問しようとしている。

> **Mental Model**: orders-list page が遅いのは、database が recent pending を直接ジャンプせず every row をスキャンしているから。
>
> **Situation**: `OrderRepository.findRecentPending`（orders.ts:142）prod で p95 = 12s；orders table 4.2M 行；PK index のみ；`EXPLAIN` が Seq Scan を示す。
>
> **Why-this-fork**: 明日 deploy window；index choice が Q2 に追加する 2 つの mirror table を制約する。
>
> **Options**:
> - **A.** Composite index `(status, created_at DESC)` — 320 MB storage / read p95 → <100 ms / two-way door。
> - **B.** `created_at` 上の cursor pagination — query rewrite ~40 行 / 0 storage / one-way door（API contract change）。
>
> **My take**: **A** に lean。(1) Deploy 圧力が low-blast-radius を有利にする；(2) 使用ログによると read-heavy access pattern は 6+ ヶ月安定；(3) 320 MB storage cost は API contract churn と比べて無視できる。**ただし** orders-list endpoint が Q3 に deprecate される予定なら、B の one-way-door cost が消える — B に switch。
>
> **Open ends**: Q3 deprecation timeline は確認済み？Dev DB storage ceiling？Contract-stability vs storage の trade-off についてあなたの call。

ユーザーは今 (a) A を確認、(b) deprecation timeline を提供して B に
flip、(c) 特定の数字に押し返す — 3 つの response、すべてが質問を
リバースエンジニアリングするより速い。

Worked Mode C example（saga / outbox、ELI5）は
[`references/EXAMPLES.md`](references/EXAMPLES.md) にある。

---

## いつ使うべきか？

### Trigger（agent 側）

- **Mode A — Proactive**: agent が非自明な decision についてユーザー
  に質問しようとしている：race condition、perf bottleneck、service
  boundary change、refactor 方向、tech selection、bug root cause。
- **Mode B — Reactive on Question**: ユーザーが「我不懂」「看不懂」
  「不理解」「什麼意思」「你在問什麼」「沒頭沒尾」「資訊太少」
  「給我完整脈絡」/「I don't understand」/「clarify」/「what?」
  と言う。
- **Mode C — Reactive on Explanation**: ユーザーが「我跟不上」
  「太多術語」「能不能簡單講」「降低 level」「我需要 mental
  model」/「I'm lost」/「ELI5」/「in plain English」/「too much
  jargon」/「where in the system are we」と言う。

長い説明の後の曖昧な「more context」/「補充一下」はデフォルトで
**Mode C**（より安全、Mode C は pause するから）。

### 以下の場合は使**わない**…

- **Trivial decision** — private-code 命名、formatting、log level、
  ≤5 行、reversible、public-API surface change なし。直接やる；
  選択を note する。
- **純粋な factual query** — "what is X" /「X 是什麼」。直接答える。
- **ユーザーが明示的に「just decide, don't ask」と言った** —
  trivial-ize、直接やる、commit/response で選択を note する。
- **既に cross-team architecture review mode** — より重いフレーム
  ワーク（Minto SCQA / formal RFC）にエスカレート。brief-before-asking
  は個別複雑 decision の **daily middleweight**、cross-team consultation
  の heavyweight ではない。

---

## 差別化

### vs SCQA / Minto Pyramid

SCQA は Situation → Complication → Question → Answer で開く。
Consulting report に強い。Engineering decision には弱い — ユーザー
が Situation をパースする前提 context を持たないかもしれない。
**brief-before-asking は Mental Model を前置** — Situation を着地
させる plain-English abstraction bridge。それ以外は構造的に似てる。
SCQA スタイルの heavyweight review にも場所はある；brief-before-asking
は middleweight default で、ユーザー要求（"give me the full
analysis"）で SCQA に escalate する。

### vs シンプルな「ask before doing」

素朴な「ask before doing」は context ゼロの yes/no 質問を生む
（"Should we proceed?" / "OK to refactor?"）。ユーザーは答える前に
agent の reasoning をリバースエンジニアリングする羽目になる。
6 ブロック構造は agent が既に知っていることを surface に出させる
— ユーザーは briefing-grounded な ask を受け取る、guessing game
ではなく。

### vs `superpowers:brainstorming`

Brainstorming は **task-start ideation** — 何を作るか分からない
ときに option space を開く。brief-before-asking は **task-progress
decision** — 作業が済んで fork resolution が要るとき option space
を絞る。違う phase、違う形。

### vs `dev-workflow:proposal-critique`

Proposal-critique は既存のリストや plan に対する one-shot KEEP /
DEFER / DROP triage。brief-before-asking は decision を開く；
それを critique するわけではない。組み合わせ可能：agent が
brief-before-asking で decision を surface に出し、ユーザーが
結果の options list が長すぎる場合に proposal-critique を使う。

---

## アンチパターン

クロス block / クロス mode の失敗モード（per-block アンチパターン
は [`SKILL.md`](SKILL.md) の各 block セクションに）：

- **Mental Model をスキップして Situation に直行** — abstraction
  bridge を殺す。最も致命的な失敗モード。
- **Zero-context yes/no**: "Should we proceed?" / "OK?" — どの
  block も荷重を支えない。
- **Reasoning なしの結論先行**: "I recommend Redis, OK?" — 6
  ブロックを 1 つの ask に折り畳む。
- **複数 fork を 1 つの briefing にバンドル** — 1 briefing 1 fork；
  fork が 3 つあれば briefing 3 つ届ける。
- **Mode C trigger なのに agent が pause せずフル 6 ブロックを
  ダンプ** — ユーザーを再度溺れさせる。Mode C は構造的に違うのは
  意図的。
- **Performative objectivity**: "Both options have merit" — agent
  は code を読んだ、lean はある；中立を装うのは嘘。"My take"
  block は honesty を強制するために存在する。

---

## 他の skill との関係は？

- **`dev-workflow:complexity-critique`** — one-shot deletion-first
  gate。直交 — decision の briefing ではなく single proposal への
  critique。
- **`dev-workflow:proposal-critique`** — 既存 list / plan の triage。
  Brief-before-asking の Options list 自体が長すぎる場合に downstream
  で組み合わせる。
- **`dev-workflow:skill-creator-advance`** — この skill のイテレー
  ション用（test-prompts.json + eval loop）。
- **`superpowers:brainstorming`** — task-start ideation；
  brief-before-asking は task-progress decision。
- **`superpowers:verification-before-completion`** — task-finish
  evidence；brief-before-asking は task-progress decision。

---

## Pre-shipped — これは v1.0 draft

| Phase | Status |
|---|---|
| **Phase 1 — Design** | 完了。4 イテレーションが [`references/DESIGN.md`](references/DESIGN.md) に文書化。 |
| **Phase 2 — SKILL.md 執筆** | 完了。6 ブロック + 3 mode 構造、block ごとの depth rules、Mode Detection Heuristics テーブル。 |
| **Phase 3 — Description 最適化** | **保留中。** Router triggering accuracy 調整のため `skill-creator-advance` の description-A/B loop を回す予定。 |
| **Phase 6 — Worked examples + tests** | 完了。[`references/EXAMPLES.md`](references/EXAMPLES.md)、[`test-prompts.json`](test-prompts.json)、[`trigger-eval.json`](trigger-eval.json)。 |
| **Phase 7 — 出力品質 A/B** | **保留中。** Phase 3 完了後に `dev-workflow:skill-tuning` を回す予定。Mode A briefing スタイルは taste-sensitive（簡潔さ、lean の assertiveness、jargon-flag 戦略）— 純粋な rule-following では最良版が surface しない。 |

Skill は v1.0 として shippable、feedback で改善する。特に Mode C
が一番若い設計面；実 session 使用で refinement を予期する。

---

## Files

```
brief-before-asking/
├── README.md           ← English README
├── README.ja.md        ← 本ファイル（日本語）
├── README.zh-TW.md     ← 繁體中文 README
├── SKILL.md            ← operational ファイル（Claude 向け）
├── test-prompts.json   ← Phase 6 — Mode A/B/C 評価 prompt
├── trigger-eval.json   ← router-trigger accuracy probe
└── references/
    ├── DESIGN.md                  ← 4 イテレーション設計 rationale（author-only）
    ├── EXAMPLES.md                ← block ごとの bad-vs-good worked example（runtime conditional load）
    └── IMPLEMENTATION-CHECKLIST.md ← author phase checklist（author-only）
```

---

## Bottom line

```
Briefing depth = decision speed.
価値は abstraction bridge（Mental Model）+ agent が既に知っている
ことを surface に出させる depth rules — 構造それ自体ではない。
```
