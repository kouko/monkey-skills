# Skill Judge

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> SKILL.md を 8 つの観点からなる rubric（0–120 点 + A〜F の
> grade）で採点し、修正すべき箇所を可視化する — 表面的な体裁では
> なく、本物の expert 知識の濃度を測る。

ユーザーが明示的に invoke する **evaluation skill**：書きかけの、
あるいは既に ship 済みの SKILL.md について、「これは本当に expert
知識を運んでいるのか、それとも Claude が既に知っていることを圧縮
しているだけなのか」を知りたいときに、この skill を invoke して、
観点ごとのスコアと Critical Issues、優先度付きの改善提案を含む構造
化された report を得る。

この README は GitHub で skill を読む人間向け。Claude が実際に
load する operational ファイルは [`SKILL.md`](SKILL.md)。

---

## なぜこの skill が存在するのか

**繰り返される失敗パターン**：多くの skill は token を浪費する。
著者は「Claude に X について教える」つもりで書き始め、結果的に
tutorial を書いてしまう — PDF とは何か、for-loop の書き方、
一般的な best practice（"clean code を書く"、"error を handle する"）。
それらはすべて Claude が既に持っている内容。context window は共有
資源であり、redundant な内容が本当に重要な部分を押し出してしまう。

著者自身ではこれを確実に検出できない。説明が明快なため skill は
*役に立つように感じる*。「この内容はモデルに既に入っているか？」
という観点で測って初めて浪費が可視化される。

この skill はその測定の規律を捕捉する。中核となる formula：

> **Good Skill = Expert-only Knowledge − What Claude Already Knows**

SKILL.md の各 section は次のいずれかに classify される：

- **Expert** — Claude が本当に知らない；これが価値の源泉
- **Activation** — Claude は知っているが、reminder が役に立つ
- **Redundant** — Claude は確実に知っている；削除すべき

良い skill は Expert 比率が 70% 超。悪い skill は Expert 40% 未満で、
redundant な tutorial 内容が長く続く。

---

## どう動くのか

この skill は任意の SKILL.md に対して 8 つの観点からなる rubric
（合計 120 点）を適用し、以下を出力する：

```
Total: X/120 (X%)  →  Grade A / B / C / D / F
Pattern: Mindset / Navigation / Philosophy / Process / Tool
Knowledge Ratio: E:A:R = X:Y:Z

Dimension scores:
  D1 Knowledge Delta          (20)  ← 最重要の観点
  D2 Mindset + Procedures     (15)
  D3 Anti-Pattern Quality     (15)  ← WHY を伴う具体的 NEVER list
  D4 Spec Compliance          (15)  ← description の品質（WHAT/WHEN/KEYWORDS）
  D5 Progressive Disclosure   (15)
  D6 Freedom Calibration      (15)
  D7 Pattern Recognition      (10)
  D8 Practical Usability      (15)

Critical Issues + Top 3 Improvements
```

rubric は 17 以上の Anthropic 公式 skill から観察された pattern と、
9 つの典型的失敗パターン（"The Tutorial"、"The Dump"、
"The Orphan References"、"The Invisible Skill" 等）を、具体的な
修復ガイドとともに提供する。

---

## こういうときに使う

- ship 前の SKILL.md draft の review
- 「何か違和感がある」既存 skill の audit
- 2 つの skill を一貫した基準で design quality 比較
- rubric の適用を通じた skill design 原則の学習

## こういうときには使わない

- **Behavioral / runtime testing** — [`skill-creator-advance`](../skill-creator-advance/)
  を使う（test prompt と quantitative assertion を持つ eval-loop が
  ある）
- **domain-team skill の convention 強制** —
  [`domain-teams:skill-team`](../../../domain-teams/skills/skill-team/)
  を使う（monkey-skills convention：4-tier gate hierarchy、3-commit
  split、primary-source grounding、~6,000-token cap に対する
  PASS/FAIL gate）
- **一般的な code review** — 道具違い

3 つの skill は補完関係：

| Skill                                             | Mode      | Output                         |
|---------------------------------------------------|-----------|--------------------------------|
| `skill-judge`（この skill）                       | Static    | 0–120 advisory score           |
| `dev-workflow:skill-creator-advance`              | Behavioral| test prompt の pass/fail       |
| `domain-teams:skill-team`                         | Structural| convention gate の PASS/FAIL   |

ある skill が `skill-team` の gate を通過しても、`skill-judge` で
D 評価になる場合がある（convention 違反はないが、内容のほとんどが
redundant）。逆に `skill-judge` で A 評価でも `skill-team` の gate に
失敗する場合もある（内容は良いが directory layout が違う）。それぞれ
測っているものが異なる。

---

## monkey-skills domain-team skill 向けの adaptation

`domain-teams/skills/{team}/` 配下の skill を評価する場合、rubric は
小さな adaptation を適用する：

- **D7 Pattern Recognition**：domain-team skill は構造特性により
  upstream の **Process** pattern に該当する（phased workflow +
  checkpoint + medium freedom）。行数は correlate であり criterion
  ではない — domain-team skill は設計上 upstream の typical 行数を
  超過するが、それを理由に減点しない。
- **D4 / D5 supplementary check**：skill-team の `CHK-SKL-001`
  （40–200 word の description）と `CHK-SKL-010`（~6,000-token cap）
  が失敗した場合は report の **Critical Issues** に surface するが、
  scoring 自体は upstream rubric を任意の cap なしで使う。
- **重点観点**：D4/D5/D8 は skill-team の gate で部分的に cover
  されているため、gate が既に pass している場合は D1/D3/D6 が最も
  新規価値を持つ。

詳細は [`SKILL.md` §Adaptation for monkey-skills domain-team skills](SKILL.md)
を参照。

---

## Attribution

この skill は
[`softaworks/agent-toolkit`](https://github.com/softaworks/agent-toolkit/tree/main/skills/skill-judge)
（MIT、Copyright (c) 2026 Leonardo Flores）から adapt したもの。
upstream は 8 つの観点からなる rubric、E:A:R 知識分類、
evaluation protocol、9 つの典型的失敗パターンを提供する。

kouko による modifications：dev-workflow plugin の convention に
合わせた frontmatter 書き換え；新たな "Adaptation for monkey-skills
domain-team skills" section の追加；scope の曖昧さ排除のための
sibling skill への cross-reference 挿入。完全な upstream chain と
modification summary は [`NOTICE`](NOTICE)、dual-copyright header は
[`LICENSE`](LICENSE) を参照。
