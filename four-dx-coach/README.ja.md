# four-dx-coach

> 『The 4 Disciplines of Execution』のマルチ scope coach —— personal solo・team-leader 主催・team-member 参加の 3 つの scope を全部カバー。Agent は scope によって役割が変わる：solo では peer-witness、leader 相手では consultant、member には personal coach（他人が決めた WIG の中で動く状況のための）。

言語：[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**：0.6.0
**所属**：[monkey-skills](https://github.com/kouko/monkey-skills)
**License**：MIT

## 背景

『The 4 Disciplines of Execution』（McChesney / Covey / Huling / Thele / Walker、第 2 版 2021）は FranklinCovey の consultant chain がまとめた execution methodology で、約 4,000 の client engagement で検証されている。処方：

1. **D1 — Wildly Important Goal に focus**（一つの WIG、`From X to Y by When` 形式）
2. **D2 — Lead measure に行動**（predictive AND influenceable）
3. **D3 — Compelling scoreboard を維持**（players' scoreboard、coach's dashboard ではない）
4. **D4 — Cadence of accountability を構築**（weekly WIG Session、peer commitment）

書籍は基本的に「multi-team rollout を主導する leader」向けに書かれている。このプラグインは書籍がカバーしきれない 2 つの scope に methodology を拡張する：

- **Personal** —— 一人の user が個人目標で 4DX を導入する。Agent が書籍の前提する peer-witness 役を埋める。
- **Team-leader** —— 一つの team の中で 4DX を回す leader（multi-team rollout ではない）。Agent は consultant。
- **Team-member** —— team の contributor で、leader がもう WIG を決めている状況。Agent は「うまく参加する」のを助ける。System を再設計する話ではない。

## Architecture

11 個の skill を 3 種類に分類：

- **1 個の plugin router**（`using-four-dx-coach`）—— cold-start / cross-topic / 4DX 圏外 query を捌く dispatcher。
- **5 個の multi-file scope-flex skill** —— 1 つの topic ごとに 2-4 個の protocol ファイルを内包し、personal / team-leader / team-member の variant をカバー。Skill が Socratic な 1 問で scope を自動判定し、対応する protocol を load。これは 2026-04-30 統合前の 15 個 atomic + 5 個 topic-router を置き換える構造。
- **5 個の single-file scope-specific skill** —— 1 つの scope のみを扱う single-file `SKILL.md`。書籍に cross-scope の対応 variant が無い topic は single-file のまま保持。

Multi-file skill は scope 重複の表面積を縮小しつつ primary-source grounding を完全保持：各 protocol は依然 `### Industry-experience addendum` を備え、parent skill の `references/industry-grounding.md` を共有。

## Skills（合計 11 個）

### 1. Plugin router（1）

| Skill | 役割 |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | Entry point —— cold-start / cross-topic / 4DX 圏外 query；scope triage（personal / team-leader / team-member）し、4DX 非適用時は hand-off |

### 2. Multi-file scope-flex skills（5）

各 skill は内部で Socratic な 1 問で scope を自動判定し、`protocols/` の対応 protocol ファイルを load。

| Skill | Topic | 内部 protocols [multi-file scope-flex] |
|---|---|---|
| [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | Pre-D1 fit gate（6-verdict triage） | `personal-mode.md`、`team-mode.md` |
| [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | *From X to Y by When* WIG を書く / 選ぶ / 解読する | `personal-define.md`、`team-select.md`、`member-comprehend.md` |
| [`4dx-d2-lead-measures`](skills/4dx-d2-lead-measures/) | Lead measure を発見 / facilitate / sphere-of-influence をマップ | `personal-discover.md`、`team-facilitate.md`、`member-influence.md` |
| [`4dx-d3-scoreboard`](skills/4dx-d3-scoreboard/) | Players' scoreboard を design / facilitate / 読む | `personal-design.md`、`team-lead-design.md`、`member-read.md` |
| [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | Weekly WIG Session を運営 / 主催 / prep / debrief | `solo-session.md`、`team-leader-session.md`、`member-prep.md`、`member-debrief.md` |

### 3. Single-file scope-specific skills（5）

書籍に cross-scope 対応 variant が無い topic は single-file のまま保持。

| Skill | Scope | 役割 |
|---|---|---|
| [`4dx-meta-whirlwind-triage`](skills/4dx-meta-whirlwind-triage/) | Personal | 7 日間 time audit；BAU vs WIG 衝突を可視化；~20% WIG slot を確保 |
| [`4dx-d1-wig-cascade`](skills/4dx-d1-wig-cascade/) | Team-leader | Primary WIG を Battle WIG に翻訳（Targets-not-Plans）；multi-team 場面のみ出現 |
| [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | Team-leader | Direct-report leader の本気の buy-in（commitment vs compliance） |
| [`4dx-meta-xps-evaluation`](skills/4dx-meta-xps-evaluation/) | Team-leader | Post-quarter XPS audit（0-4 scale；C1-C4 layer） |
| [`4dx-sustain-momentum-rescue`](skills/4dx-sustain-momentum-rescue/) | Personal | 4-discipline stack のどの layer で破綻したかを diagnose し、対応する restart に route |

## Scope 検出の仕組み

Scope は手動で選ばない。3 通り：

1. **Plugin router**（`using-four-dx-coach`）が query 中の scope signal（「我が team」「joined」「*my own* goal」）を読んで dispatch。
2. **Multi-file scope-flex skill** は flow の冒頭で Socratic な 1 問を投げて曖昧さを解消し、対応 protocol を auto-load —— 手動選択は不要。
3. **Single-file scope-specific skill** は signal が既に scope を制約している場合のみ activate（例：cascade → team-leader、whirlwind triage → personal）。

迷ったらそのまま状況を伝えれば router が判定。

## 使うべき場面

activation signal：

- 「この目標に 4DX 使える？」 / 「Should I use 4DX for X?」 / 「4DX 適合我嗎？」
- 「日常業務に追われて目標に手がつかない」
- 「目標がぼんやりしている / 優先順位が多すぎる」
- 「目標はあるが日々何をすれば結果に繋がるか分からない」
- 「ダッシュボードが複雑すぎて見ない」
- 「毎週の振り返りで進捗を保ちたい」
- 「WIG Session が続かなくなった、どう再開すればいい？」
- 「team の Primary WIG を選びたい / org WIG を cascade したい」
- 「leader を本気で buy-in させるには？表面的な compliance ではなく」
- 「team の WIG Session を主催する」
- 「4DX を回している team に加わった、どう参加する？」
- 「明日の WIG Session 用の commitment を準備したい」

hand-off 対象：

- 多 team への enterprise rollout → 書籍 Part 2（第 6-10 章）を直接読むか、FranklinCovey に相談
- Habit formation → atomic habits / habit stacking が正解
- Portfolio bet / multi-startup founder → OKR か lean experimentation
- ER 医師・消防士など firefighting that *is* strategic work
- 純粋な creative output（novelist / artist）—— Goodhart 効果で lead measure が腐食
- Clinical burnout / depression → professional support、4DX ではない

## Install

```bash
# Claude Code 内
/plugin marketplace add kouko/monkey-skills
/plugin install four-dx-coach@monkey-skills
```

Router skill `using-four-dx-coach` が generic query で activate；個別 skill は自身の signal で activate。

## Industry-grounded boundaries

Topical skill（5 個 multi-file + 5 個 single-file = 10 個 atomic-equivalent）の Boundary section に `### Industry-experience addendum` を備え、書籍以外の academic / regulatory / credentialed-author primary source を引用 —— 書籍の selection bias と member-POV ギャップを補強。各 skill の `references/industry-grounding.md` に検証済 citation を列挙：

- D2 lead-measure-discovery：Goodhart 1975 / Strathern 1997 / CFPB 2016（Wells Fargo）/ VA OIG 2014 / GBI 2011（Atlanta APS）—— Goodhart 失敗事例
- D1 personal-define：Christensen 1997 / March 1991 / Dweck 2006 —— 過集中リスク + exploration vs exploitation
- D3 personal-scoreboard：Tufte 1983 / Few 2006 / Ware 2012 —— 5 秒 test の知覚科学根拠
- D4 solo + team WIG-Session：Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 —— 会議科学の実証
- Member protocols：Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 —— 書籍 leader-POV ギャップ補完
- Team-leader skills：Akao 1991 / Doerr 2018 / Kaplan-Norton 2001 / Ryan-Deci 2017 / Argyris 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick-Fredrickson / CMMI / McKinsey OHI / Gallup Q12

Plan U merge 後も 48 件の verified primary-source citation を保持。

## 多言語 trigger

Skill の `description` と trigger signal は **English / 日本語 / 繁體中文** に対応 —— 三言語のいずれでも問える。Skill body（Interpretation / Execution / Boundary）は portability のため English で統一。

## 推奨 progression

### Personal（solo）—— ゼロから始める場合

1. `4dx-meta-strategy-triage` → `personal-mode.md` —— 4DX が目標に合うかを確認（or hand-off）
2. `4dx-meta-whirlwind-triage` —— BAU vs WIG 仕事を明確化
3. `4dx-d1-wig-formulation` → `personal-define.md` —— WIG を書く（X → Y → When）
4. `4dx-d2-lead-measures` → `personal-discover.md` —— 2-3 個の lead measure を発見
5. `4dx-d3-scoreboard` → `personal-design.md` —— 一目で分かる scoreboard を design
6. `4dx-d4-cadence` → `solo-session.md` —— weekly cadence を始動
7. `4dx-sustain-momentum-rescue` —— momentum が落ちたら on-demand load

### Team-leader —— ゼロから始める場合

1. `4dx-meta-strategy-triage` → `team-mode.md` —— 4DX が team の進む道か確認
2. `4dx-d1-wig-formulation` → `team-select.md` —— Battles 2x2 で Primary WIG を選定
3. `4dx-d1-wig-cascade` —— Targets-not-Plans で org WIG を team WIG に cascade
4. `4dx-meta-team-leader-onboarding` —— Direct report から commitment（compliance ではなく）を獲得
5. `4dx-d4-cadence` → `team-leader-session.md` —— facilitator として weekly WIG Session を運営
6. `4dx-meta-xps-evaluation` —— team の 4DX 実装を定期的に audit

### Team-member —— 既に 4DX を回している team に加わる場合

1. `4dx-d1-wig-formulation` → `member-comprehend.md` —— 与えられた team WIG を理解
2. `4dx-d4-cadence` → `member-prep.md` —— 次の session 用の commitment を準備
3. `4dx-d4-cadence` → `member-debrief.md` —— session 後で正直に self-account

## 出典

『The 4 Disciplines of Execution』（第 2 版 2021）—— Chris McChesney / Sean Covey / Jim Huling / Scott Thele / Beverly Walker（Simon & Schuster）から蒸留。Pipeline：`tsundoku:book-distill`（RIA-TV++、kangarooking/cangjie-skill から adapt、MIT）。Plan U merge（2026-04-30）で 26 skill を 11 skill に統合。詳細は [ATTRIBUTION.md](ATTRIBUTION.md)。

## 関連 plugin

- [`tsundoku`](../tsundoku/) —— 本 plugin を産出した book→skill 蒸留 pipeline
- [`philosophers-toolkit`](../philosophers-toolkit/) —— 姉妹「個人思考 method」プラグイン
