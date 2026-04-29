# philosophers-toolkit

> 12 個の哲学的思考フレームワークをインタラクティブな Claude Code skill に変換 — 講義ではなく、問いで思考を導く。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**: 1.0.4
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

## Background

「思考フレームワーク」を謳う多くのツールは、チェックリストを投げて
立ち去る。本 plugin はその逆を行く。各 skill は Claude を
哲学的な対話相手に変え、フレームワークを**あなたと一緒に**実行する
— 適切なタイミングで適切な問いを発し、結論を先取りせず、
最終的な判断はあなたに委ねる。

本 toolkit は二つの伝統を組み合わせる：

- **Western philosophy（西洋哲学）** — Socrates、Aristotle、Descartes、
  Hegel、Popper。分解・対話・反証の方法論。
- **日本哲学** — 守破離、生き甲斐、改善、反省、侘寂。
  段階診断・存在意義・継続改善・blame-free な振り返り・
  good-enough の方法論。

すべての skill は slash command として呼び出せる。どれを使うか
迷ったときは、router skill（`/think`）が選定を支援する。

## Install

本 plugin は `monkey-skills` marketplace に収録されている。

```bash
# Claude Code 内で
/plugin marketplace add kouko/monkey-skills
/plugin install philosophers-toolkit
```

## Usage

使いたい method が決まっている場合は、直接 skill を呼び出す：

```
/philosophers-toolkit:socratic
/philosophers-toolkit:first-principles
/philosophers-toolkit:dialectics
```

迷っている場合は router に任せる：

```
/philosophers-toolkit:think
```

router は「何をしたいのか？」と一度だけ問い、最適な skill を
案内する。

## Skills

### Western philosophy（西洋哲学）

#### Socratic method（ソクラテス式問答）

| 項目 | 内容 |
|-------|-------|
| Origin | 古代アテネ、紀元前 5 世紀ごろ |
| 哲学者 | Socrates（Plato の対話篇を通して） |
| Core idea | Maieutics（産婆術）— アイデアの「産婆」。知識は学習者から引き出されるもので、注ぎ込むものではない。 |
| Method | Claude は講義しない。すべての応答が問いで終わり、ユーザーに自分の考えを言語化させる。 |
| Use when | 開かれた対話を通じて自分の思考を吟味したいとき。「教えて」「行き詰まった」と言ったとき。 |
| Command | `/philosophers-toolkit:socratic` |

#### Aristotle's Four Causes（四原因説）

| 項目 | 内容 |
|-------|-------|
| Origin | 『自然学』『形而上学』、紀元前 350 年ごろ |
| 哲学者 | Aristotle |
| Core idea | 存在するものはすべて 4 つの説明原因（質料・形相・作用・目的）を持つ。4 つすべてを検討して初めて完全な理解に到達する。 |
| Method | Claude は 4 つのレンズで分析を構造化する：何でできているか、何がそれを「それ」たらしめているか、何が引き起こしたか、何のためにあるか。 |
| Use when | システム・製品・概念の本質を深く理解したいとき。 |
| Command | `/philosophers-toolkit:four-causes` |

#### First Principles（第一原理）

| 項目 | 内容 |
|-------|-------|
| Origin | Aristotle『分析論後書』；現代エンジニアリング実践で再評価 |
| 哲学者 | Aristotle |
| Core idea | これ以上分解できない根本的真理まで分解し、そこから再構築する — 類比による推論を拒否する。 |
| Method | Claude は「best practices」や慣習を剥ぎ取り、不可分の事実だけを残してから上に向かって推論する。 |
| Use when | 既存の前提が新しい思考を縛っているとき。問題をゼロから考え直したいとき。 |
| Command | `/philosophers-toolkit:first-principles` |

#### Hegelian Dialectics（ヘーゲル弁証法）

| 項目 | 内容 |
|-------|-------|
| Origin | 19 世紀初頭ドイツ観念論 |
| 哲学者 | Georg Wilhelm Friedrich Hegel |
| Core idea | あらゆる立場は自身の矛盾の種を内包する。正→反→合により、対立が解消する高次の枠組みに至る。 |
| Method | Claude は対立を明示化し、妥協ではなく synthesis を志向する。 |
| Use when | 二者択一、競合する優先順位、対立する立場を持つ stakeholder に直面しているとき。 |
| Command | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability（反証可能性）

| 項目 | 内容 |
|-------|-------|
| Origin | 『科学的発見の論理』、1934 |
| 哲学者 | Karl Popper |
| Core idea | 主張が意味を持つのは、それを誤りと示す証拠を特定できる場合に限る。すべてを説明する理論は、何も説明しない。 |
| Method | Claude は曖昧な主張を検証可能な仮説に変換し、それを反証しうるテストの設計を支援する。 |
| Use when | 検証すべき前提があるとき。「X は Y より良い」と言ったが測定可能な基準がないとき。 |
| Command | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt（方法的懐疑）

| 項目 | 内容 |
|-------|-------|
| Origin | 『省察』、1641 |
| 哲学者 | René Descartes |
| Core idea | 疑う理由が少しでもあれば偽として扱え — 疑い得ないものに到達するまで。そこから岩盤の上で再構築する。 |
| Method | Claude は不確実性の層を一つずつ体系的に剥ぎ取り、最大の懐疑にも耐えるものを浮かび上がらせる。 |
| Use when | 信頼の前提を audit するとき。証拠を評価するとき。資源を投入する前に計画を stress-test するとき。 |
| Command | `/philosophers-toolkit:doubt` |

### 日本哲学

#### 守破離（Shu-Ha-Ri）

| 項目 | 内容 |
|-------|-------|
| Origin | 武道伝統；遠藤征四郎により合気道で体系化 |
| 伝統 | 武道（budō） |
| Core idea | 習熟は三段階を辿る — 守（型を守る）、破（型を破る）、離（型を離れる）。段階は領域ごとであり、絶対的なものではない。 |
| Method | Claude は特定のスキル・方法論におけるあなたの段階を診断し、段階に応じた指導を行う。 |
| Use when | 「ルールに従うべきか自分流でやるべきか」と迷うとき。技術における自分の習熟度を知りたいとき。 |
| Command | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐（Ikigai）

| 項目 | 内容 |
|-------|-------|
| Origin | 沖縄・本土日本の人生観；4 軸 framework として近年の career・PMF 言説で広く使用 |
| 伝統 | 日本の生きがい伝統 |
| Core idea | 「好きなこと」「得意なこと」「世界が求めること」「報酬を得られること」の交差点が持続的な意義をもたらす。1 軸でも欠ければ何かが空虚になる。 |
| Method | Claude は 4 軸を順に探索し、欠けている軸を診断する。 |
| Use when | プロジェクト・製品の存在意義に迷うとき。PMF が達成できていない感覚があるとき。キャリアの転換期。 |
| Command | `/philosophers-toolkit:ikigai` |

#### 改善（Kaizen）

| 項目 | 内容 |
|-------|-------|
| Origin | 戦後トヨタ生産方式；大野耐一・今井正明により体系化 |
| 伝統 | 製造業；現在は広く適用 |
| Core idea | 今日の仕事を昨日より少しだけ良くする。小さな継続的改善の積み重ねが大きな成果を生む。 |
| Method | Claude は 6 ステップのループで、最小の有効な改善を特定し実行する。 |
| Use when | 「なんとなく非効率」と感じるとき。既存プロセスに摩擦やムダがあるとき。「大きく変えたいが何から始めればいいか分からない」とき。 |
| Command | `/philosophers-toolkit:kaizen` |

#### 反省（Hansei）

| 項目 | 内容 |
|-------|-------|
| Origin | 日本の内省的伝統；トヨタの継続学習文化に統合 |
| 伝統 | 日本の自己研鑽 |
| Core idea | 学びのための振り返りであり、責めではない。「誰のせいか」ではなく「私は何を見落としていたか」を問う。 |
| Method | Claude は 4 段階の内省プロセスを導き、表面的な教訓ではなく構造的な盲点に焦点を当てる。 |
| Use when | プロジェクトが期限超過したとき。機能が採用されなかったとき。判断が裏目に出たとき。四半期・年次の振り返り。 |
| Command | `/philosophers-toolkit:hansei` |

#### 侘寂（Wabi-Sabi）

| 項目 | 内容 |
|-------|-------|
| Origin | 茶道美学；千利休が体系化、松尾芭蕉が深化 |
| 伝統 | 日本の美意識 |
| Core idea | 不完全さ・無常・不完結の中に美を見出す。削れるものを削る。時間と使用が加える価値を認める。意図的な余白が参加を招く。 |
| Method | Claude は問う — その磨き込みは本質を高めているのか、それとも恐怖から逃げているのか？ |
| Use when | 「MVP のままリリースか、もっと磨くか」を悩むとき。API が複雑すぎると感じるとき。完璧主義がリリースを停滞させているとき。 |
| Command | `/philosophers-toolkit:wabi-sabi` |

### Getting started

#### `/think` router

| 項目 | 内容 |
|-------|-------|
| Skill | `using-philosophers-toolkit` |
| Core idea | 意図と method を一致させる。流行のものより、状況に合うものが大事。 |
| Method | Claude は「何をしたいのか？」と一度だけ問い、最適な skill に案内する。 |
| Use when | 思考を深めたいが、どの method が合うか分からないとき。問題が曖昧で、まず明確化したいとき。 |
| Command | `/philosophers-toolkit:think` |

## Design principles

すべての skill に通底する設計原則：

**講義ではなく対話プロセス。** 各 skill は Claude を思考の伴走者に変える。
skill は問う。あなたは答える。skill はさらに掘り下げる。
結論はあなたのものであり、Claude のものではない。

**topic は確認するが、答えは先取りしない。** 各 skill は分析対象を
確認してから始める。synthesis、indubitable な岩盤、適切な段階が
何になるかを先に declare することは拒否する。

**起源の言語で。** 日本由来のフレームワークは日本語のまま — 守破離、
生き甲斐、改善、反省、侘寂 — ローマ字や強引な英訳は使わない。
Western 哲学者名はそのまま保持。概念は元の文化形式で route される。

**操作的、学術的でない。** 各 skill のアウトプットはより鋭い問題定義
またはより包括的な分析であり、哲学論文ではない。各 skill は
具体的なステップを持つ procedure として動作する。

**状況ごとに 1 つの method。** 各 skill の `Do NOT use when` block が
誤った tool 選択時に他へ route する。主張を falsify する、前提を
doubt する、問題を分解する、開かれた問いを対話する — それぞれに
専用の skill がある。

## Roadmap

検討中のフレームワークは [ROADMAP.md](ROADMAP.md) を参照
— Occam's Razor、pragmatism、功利主義・義務論、三現主義、
道家・無為など。

## Contributing

contribution を歓迎する。新しいフレームワークを提案する場合は、
まず issue を起票してほしい。新しい skill は以下を満たすこと：

- 明確な問題クラスに `When to Use` と `Do NOT use when` の両 block でマッピングする
- 静的なリファレンスではなく、対話的な procedure として動作する
- 非西洋フレームワークは起源言語を保持する
- [domain-teams skill-team](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/skill-team) の構造 gate を通過する

PR は [Conventional Commits](https://www.conventionalcommits.org/) に従う。

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。
