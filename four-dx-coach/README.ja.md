# four-dx-coach

> 『The 4 Disciplines of Execution』のマルチ scope coach —— personal solo・team-leader 主催・team-member 参加の 3 つの scope を全部カバー。Agent は scope によって役割が変わる：solo では peer-witness、leader 相手では consultant、member には personal coach（他人が決めた WIG の中で動く状況のための）。

言語：[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**：0.2.0
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

## あなたの scope は？

| もし ... なら | `...-*` 系統の skill を使う | Agent の役割 |
|---|---|---|
| ... 一人で個人目標を追っている | `personal-*` | peer-witness |
| ... team を率いていて 4DX を導入する側 | `team-*` | leader への consultant |
| ... 4DX を回している team の member | `member-*` | member 向け personal coach |

迷う場合は router (`using-four-dx-coach`) から始める —— 先に scope triage する。

## Skills（合計 26 個 — D1-D4 全 3-scope 対称）

### Personal（7 個）

| Stage | Skill | 役割 |
|---|---|---|
| meta | [`4dx-meta-personal-strategy-triage`](skills/4dx-meta-personal-strategy-triage/) | 始める前に 4DX が目標に合うかを判定 |
| D1 | [`4dx-d1-personal-whirlwind-triage`](skills/4dx-d1-personal-whirlwind-triage/) | 7 日間 time audit で BAU vs WIG 衝突を可視化 |
| D1 | [`4dx-d1-personal-wig-defining`](skills/4dx-d1-personal-wig-defining/) | `From X to Y by When` 形式で WIG を coaching |
| D2 | [`4dx-d2-personal-lead-measure-discovery`](skills/4dx-d2-personal-lead-measure-discovery/) | predictive + influenceable な lead measure を 2–3 個発見 |
| D3 | [`4dx-d3-personal-scoreboard`](skills/4dx-d3-personal-scoreboard/) | 5 秒 test を passable な players' scoreboard を design |
| D4 | [`4dx-d4-personal-wig-session`](skills/4dx-d4-personal-wig-session/) | 20–30 分 weekly WIG Session を運営、agent = peer-witness |
| sustain | [`4dx-sustain-personal-momentum-rescue`](skills/4dx-sustain-personal-momentum-rescue/) | どの layer で cadence が壊れたかを diagnose し、対応する rescue に route |

### Team-leader（8 個）

| Stage | Skill | 役割 |
|---|---|---|
| meta | [`4dx-meta-team-strategy-triage`](skills/4dx-meta-team-strategy-triage/) | team が 4DX を導入すべきかを判定 |
| D1 | [`4dx-d1-team-primary-wig-selection`](skills/4dx-d1-team-primary-wig-selection/) | Battles 2x2 で組織の Primary WIG を選定 |
| D1 | [`4dx-d1-team-wig-cascade`](skills/4dx-d1-team-wig-cascade/) | Org WIG を team WIG に翻訳（Targets-not-Plans の規律で） |
| meta | [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | Direct report の leader を本気で乗せる —— commitment vs compliance |
| **D2** | [**`4dx-d2-team-lead-measure-facilitation`**](skills/4dx-d2-team-lead-measure-facilitation/) | **team で 2-3 個の lead measure を facilitate（veto-not-dictate）** |
| **D3** | [**`4dx-d3-team-lead-scoreboard-design`**](skills/4dx-d3-team-lead-scoreboard-design/) | **team が public で multi-stakeholder legible な players' scoreboard を build するのを facilitate** |
| D4 | [`4dx-d4-team-wig-session-lead`](skills/4dx-d4-team-wig-session-lead/) | facilitator として team の WIG Session を運営 |
| meta | [`4dx-meta-team-xps-evaluation`](skills/4dx-meta-team-xps-evaluation/) | Team 内の 4DX 実装を XPS audit |

### Team-member（5 個）

| Stage | Skill | 役割 |
|---|---|---|
| D1 | [`4dx-d1-member-team-wig-comprehension`](skills/4dx-d1-member-team-wig-comprehension/) | 与えられた team WIG を理解する |
| **D2** | [**`4dx-d2-member-lead-measure-influence`**](skills/4dx-d2-member-lead-measure-influence/) | **inherited lead measure に対する sphere of influence を特定** |
| **D3** | [**`4dx-d3-member-scoreboard-reading`**](skills/4dx-d3-member-scoreboard-reading/) | **team scoreboard を read + 自分の貢献位置を locate + 必要時 escalate** |
| D4 | [`4dx-d4-member-commitment-prep`](skills/4dx-d4-member-commitment-prep/) | 次の WIG Session 用の自分の commitment を準備 |
| D4 | [`4dx-d4-member-account-debrief`](skills/4dx-d4-member-account-debrief/) | session の前後で正直に self-account する |

### Topic-routers（5 個）—— topic 既知 / scope 不明確な query 用

| Topic | Skill | Routes between |
|---|---|---|
| meta-triage | [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | personal vs team strategy-triage |
| D1 WIG | [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | personal-define / team-select / member-comprehend |
| **D2 leads** | [**`4dx-d2-lead-measures`**](skills/4dx-d2-lead-measures/) | **personal-discover / team-facilitate / member-influence** |
| **D3 scoreboard** | [**`4dx-d3-scoreboard`**](skills/4dx-d3-scoreboard/) | **personal-design / team-lead-design / member-read** |
| D4 cadence | [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | solo-session / team-lead-session / member-prep / member-debrief |

Topic-router は「topic は明確、scope / role は曖昧」な query にのみ activate し、Socratic な disambiguation 質問を 1 つしてから atomic skill に振り分ける。

### Plugin router（1 個）

| Skill | 役割 |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | Entry point —— cold-start / cross-topic / 4DX 圏外の query 用；scope triage（personal / team-leader / team-member）し、4DX 非適用時は hand-off |

## 使うべき場面

✅ **activation signal**：

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

❌ **hand-off 対象**：

- 多 team への enterprise rollout → 書籍 Part 2（第 6–10 章）を直接読むか、FranklinCovey に相談
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

各 atomic skill の Boundary section に `### Industry-experience addendum` を備え、書籍以外の academic / regulatory / credentialed-author primary source を引用 —— 書籍の selection bias と member-POV ギャップを補強。各 skill の `references/industry-grounding.md` に検証済 citation を列挙：

- D2 lead-measure-discovery：Goodhart 1975 / Strathern 1997 / CFPB 2016（Wells Fargo）/ VA OIG 2014 / GBI 2011（Atlanta APS）—— Goodhart 失敗事例
- D1 personal-wig-defining：Christensen 1997 / March 1991 / Dweck 2006 —— 過集中リスク + exploration vs exploitation
- D3 personal-scoreboard：Tufte 1983 / Few 2006 / Ware 2012 —— 5 秒 test の知覚科学根拠
- D4 personal / team WIG-Session：Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 —— 会議科学の実証
- Member skills：Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 —— 書籍 leader-POV ギャップ補完
- Team-leader skills：Akao 1991 / Doerr 2018 / Kaplan-Norton 2001 / Ryan-Deci 2017 / Argyris 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick-Fredrickson / CMMI / McKinsey OHI / Gallup Q12

16 skill × 48 verified primary-source citation。

## 多言語 trigger

Skill の `description` と trigger signal は **English / 日本語 / 繁體中文** に対応 —— 三言語のいずれでも問える。Skill body（Interpretation / Execution / Boundary）は portability のため English で統一。

## 推奨 progression

### Personal（solo）—— ゼロから始める場合

1. `4dx-meta-personal-strategy-triage` —— 4DX が目標に合うかを確認（or hand-off）
2. `4dx-d1-personal-whirlwind-triage` —— BAU vs WIG 仕事を明確化
3. `4dx-d1-personal-wig-defining` —— WIG を書く（X → Y → When）
4. `4dx-d2-personal-lead-measure-discovery` —— 2–3 個の lead measure を発見
5. `4dx-d3-personal-scoreboard` —— 一目で分かる scoreboard を design
6. `4dx-d4-personal-wig-session` —— weekly cadence を始動
7. `4dx-sustain-personal-momentum-rescue` —— momentum が落ちたら on-demand load

### Team-leader —— ゼロから始める場合

1. `4dx-meta-team-strategy-triage` —— 4DX が team の進む道か確認
2. `4dx-d1-team-primary-wig-selection` —— Battles 2x2 で Primary WIG を選定
3. `4dx-d1-team-wig-cascade` —— Targets-not-Plans で org WIG を team WIG に cascade
4. `4dx-meta-team-leader-onboarding` —— Direct report から commitment（compliance ではなく）を獲得
5. `4dx-d4-team-wig-session-lead` —— facilitator として weekly WIG Session を運営
6. `4dx-meta-team-xps-evaluation` —— team の 4DX 実装を定期的に audit

### Team-member —— 既に 4DX を回している team に加わる場合

1. `4dx-d1-member-team-wig-comprehension` —— 与えられた team WIG を理解
2. `4dx-d4-member-commitment-prep` —— 次の session 用の commitment を準備
3. `4dx-d4-member-account-debrief` —— session 前後で正直に self-account

## 出典

『The 4 Disciplines of Execution』（第 2 版 2021）—— Chris McChesney / Sean Covey / Jim Huling / Scott Thele / Beverly Walker（Simon & Schuster）から蒸留。Pipeline：`tsundoku:book-distill`（RIA-TV++、kangarooking/cangjie-skill から adapt、MIT）。詳細は [ATTRIBUTION.md](ATTRIBUTION.md)。

## 関連 plugin

- [`tsundoku`](../tsundoku/) —— 本 plugin を産出した book→skill 蒸留 pipeline
- [`philosophers-toolkit`](../philosophers-toolkit/) —— 姉妹「個人思考 method」プラグイン
