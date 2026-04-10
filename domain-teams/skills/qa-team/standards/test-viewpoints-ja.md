# Test Viewpoints (テスト観点) — Japanese Methodology Reference

Authoritative reference for the Japanese QA concept of **テスト観点 (test viewpoints)**
and its three dominant extraction methodologies. Used by worker when running
`protocols/test-viewpoint-extraction.md`, and by evaluator when running
`rubrics/viewpoint-coverage.md`.

## Concept: What is a テスト観点?

A **test viewpoint** is a *lens or angle* for thinking about what to test —
"テストしたいと思うモノやコト" (something you want to test). It is a **thinking
framework**, not a process classification.

The Japanese QA community treats viewpoint extraction as the **most important
upstream activity** in test design. ASTER's テスト設計コンテスト U-30 審査基準
allocates **30 out of 135 points** to detailed design + 10 points to workflow
consistency, which together weight viewpoint quality heavily — reflecting the
community's consensus that coverage thinking outranks execution detail.

### How viewpoints differ from ISTQB test types

This is a synthesis from comparing ISTQB CTFL v4.0 §2 test types with Qbook
and VSTeP definitions of テスト観点 — no primary source directly compares the two.

| Axis | ISTQB test type | Japanese test viewpoint |
|------|-----------------|-------------------------|
| **Granularity** | Coarse (4 categories) | Fine (multi-axis hierarchy) |
| **Structure** | Flat list | Tree / mind map |
| **Purpose** | Process classification | Coverage-gap prevention through structured thinking |
| **Representation** | Text definition | Diagram (NGT tree, 6W2H tree, mind map) |

Viewpoints and types are **complementary, not competing**: use viewpoints to
ensure coverage breadth, then classify each viewpoint into an ISTQB type for
execution planning.

## Three Dominant Methodologies

### 1. VSTeP / NGT — Viewpoint-based Software Test Engineering Process

- **Originator**: 西康晴 (電気通信大学), ASTER 理事, ISO/IEC JTC1/SC7/WG26 国内委員会委員長, SQiP 品質委員会副委員長
- **Commercial tooling**: ベリサーブ GIHOZ (2023)
- **Notation**: NGT (Notation for Generic Testing) — tree with `<<relationship>>` stereotypes

**Process**: test viewpoint modeling → NGT tree (with MECE verification) → test container grouping → test frame → test case.

**When to use**: enterprise systems with cross-cutting quality concerns (security × performance × accessibility interacting); teams with dedicated QA roles.

### 2. HAYST法 — Highly Accelerated and Yield Software Testing

- **Originators**: 秋山浩一, 吉澤正孝, 仙石太郎 (富士ゼロックス)
- **Publication**: 日科技連出版 book + JSQC 査読論文
- **Basis**: orthogonal arrays for combinatorial test reduction

**Four components**: 6W2H tree (factor extraction) → FV表 (Function Verification) → ラルフチャート (input/output/state/noise) → FL表 (final factor-level).

**When to use**: configuration testing, feature flag combinations, compatibility testing, factor-interaction-dominant systems. Can collapse 1024 combinations to 16 via 2-factor orthogonal coverage.

### 3. ゆもつよメソッド — Yumotsuyo Method (湯本剛, 2007〜)

**Components**: 論理的機能構造 (logical function structure) + テストカテゴリ (orthogonal concerns) + 仕様項目特定パターン + テスト分析マトリクス (function × category grid).

**When to use**: greenfield projects, specs-in-progress, QA in requirements analysis.

### Bonus: Mind Map — 池田暁, 鈴木三紀夫

『マインドマップから始めるソフトウェアテスト』(技術評論社, 2007/2019). Divergent viewpoint enumeration via mind map, then convert to NGT for MECE verification. Good for early discovery and brainstorming with non-QA stakeholders.

## Selection Decision Tree

| Situation | Recommended methodology |
|-----------|-------------------------|
| Enterprise system, cross-cutting concerns, dedicated QA team | **VSTeP / NGT** |
| Configuration matrix, factor interactions dominant | **HAYST法** |
| Greenfield project, specs evolving, QA in requirements | **ゆもつよメソッド** |
| Early discovery, cross-functional brainstorming | **Mind map** → convert to NGT |
| Small project, single developer | Any method — pick the simplest (6W2H or mind map) |

## 6W2H as Universal Starting Point

6W2H is HAYST法's Phase 1 but works as a universal warm-up:
**When / Where / Who / Whom / What / Why / How / How much**

Use it when you don't yet know which full methodology fits, or as a checklist
review tool after another method has produced a draft viewpoint list.

## DR (Design Review) Integration

Japanese QA culture embeds viewpoint review in **設計レビュー (design review)** —
a formal upstream checkpoint where non-authors (peers, architects, QA leads)
audit the viewpoint list before test execution begins. This is the Japanese
incarnation of "shift-left" and is the operational mechanism behind the
「品質は工程で作り込む」 philosophy (see `quality-philosophy.md`).

A viewpoint list that cannot pass DR is incomplete regardless of internal
consistency. This is why `rubrics/viewpoint-coverage.md` includes a
**DR Readiness** dimension.

## Sources

- [JaSST'16 東北 S1 — 西康晴 VSTeP](https://www.jasst.jp/symposium/jasst16tohoku/pdf/S1.pdf) — VSTeP process and NGT notation
- [JaSST'13 Tokyo A2-4 — VSTeP digest](https://www.jasst.jp/symposium/jasst13tokyo/pdf/A2-4.pdf)
- [JaSST'13 Tokyo A2-3 — 湯本剛 ゆもつよメソッド](http://jasst.jp/symposium/jasst13tokyo/pdf/A2-3.pdf)
- [Qualab — VSTeP 資料 2013.05.10](https://qualab.jp/materials/VSTeP.130510.color.pdf)
- [researchmap — 西康晴 profile](https://researchmap.jp/Yasuharu.Nishi) — academic and standards-body roles
- [ベリサーブ GIHOZ VSTeP 実装 (2023)](https://gihoz.zendesk.com/hc/ja/articles/44596214451737) — commercial adoption evidence
- [Sqripts — HAYST法解説](https://sqripts.com/2022/09/29/20377/) — HAYST法 framework overview
- [J-STAGE — 直交表を用いたソフトウェアテスト因子選択 (JSQC 論文)](https://www.jstage.jst.go.jp/article/quality/42/4/42_KJ00008275443/_article/-char/ja/) — peer-reviewed HAYST法 paper
- [ベリサーブ HelloQualityWorld — HAYST法連載](https://www.veriserve.co.jp/helloqualityworld/media/20240719001/)
- [秋山浩一 note — 6W2H](https://note.com/akiyama924/n/n465029aa31fc)
- [技術評論社 — マインドマップから始めるソフトウェアテスト](https://gihyo.jp/book/2019/978-4-297-10506-8)
- [ASTER テスト設計コンテスト U-30 審査基準](https://www.aster.or.jp/testcontest/u30.html) — 30-point weighting for detailed design
- [Qbook — テスト観点とは](https://www.qbook.jp/column/644.html) — community definition of test viewpoint
