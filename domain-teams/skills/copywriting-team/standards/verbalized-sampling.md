---
title: Verbalized Sampling（Zhang et al. 2025）
tier: 2
---

# Verbalized Sampling

Tier 2 standard: 技法レベル。LLM の post-training alignment（RLHF 等）で
生じる **mode collapse（typicality bias）** を緩和する prompt 技法。
Zhang et al. 2025（arXiv:2510.01171）が提案。prompt 上で明示的に
「**複数候補 + 各候補の probability distribution**」を求めることで、
default modality 以外のモードを引き出す。training-free / model-agnostic
／temperature と直交。copywriting-team では Mandal-Art（構造層 diversity）
を補完する **詞彙層 diversity** として運用する。

## Primary Sources

- Jiayi Zhang et al. (2025) "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity" arXiv:2510.01171 https://arxiv.org/abs/2510.01171 — canonical 論文。理論提案、実験設計、8 ベンチマークでの 2-3x diversity 向上測定。
- OpenReview discussion thread for arXiv:2510.01171 https://openreview.net/forum?id=verbalized-sampling — 次級 dual-verify source：査読コメントと限界条件（モデルサイズ効果差）の明示化。
- CHATS-lab/verbalized-sampling (GitHub) https://github.com/CHATS-lab/verbalized-sampling — 公式実装 repository。prompt template と再現スクリプトの one-source 参照。

## Framing

大規模言語モデルは post-training（RLHF, DPO, Constitutional AI 等）で
「無難で typical な出力」にバイアスが寄る。同じ prompt に対する多数
サンプリングが少数の mode に集中し、diversity が失われる現象が
**mode collapse** である。Zhang et al. 2025 は、これを **typicality
bias**（訓練データの中央値近傍への集中）として定式化し、解消するため
の prompt 技法として Verbalized Sampling を提案した。

copywriting 観点では、mode collapse は致命的：広告コピー生成で LLM が
「同じような無難な 10 本」を返すと、散らかす段階の多様性が足りず、
選ぶ段階の選択肢が実質 1-2 本に縮む。Verbalized Sampling はこの
症状に対する training-free の対抗手段である。

## 技術原理

### Baseline（mode collapse が起きる prompt）

```
Prompt: Write a catch copy for product X.
```

LLM は post-training で「無難で typical な一本」を返すバイアスに従う。
100 回サンプリングしても上位 3-5 mode に収束する。

### Verbalized Sampling（mode collapse 緩和）

```
Prompt: Generate 5 catch copies for product X along with their
probabilities. Format:
  1. [copy] — probability: X%
  2. [copy] — probability: Y%
  ...
```

この prompt で LLM に要求するのは：
1. **複数候補を一度に列挙**（single-shot multi-output）
2. **各候補に相対確率を明示**（verbalized distribution）

LLM は確率分布の形で回答を組み立てる過程で、自己の内部分布から**より
多様なモードを引き出す**。結果として top-1 候補以外のモードが prompt 表面
に出てくる。

### なぜ効くか

Zhang et al. 2025 の理論的説明：
- **Typicality bias** は「単一出力を求められた時」に強く現れる。LLM は
  訓練目的から「最も 'らしい' 一本」を返す体質になっている。
- **複数候補 + 確率分布を求める prompt** は、LLM の役割を「典型を返す
  agent」から「分布を描写する reporter」に切り替える。reporter mode で
  は多峰分布を描写するのが自然な振舞いになる。
- **probability 欄が critical**。probability を削ると複数列挙しても
  依然 mode collapse する（論文 §4 Ablation）。probability を verbalize
  させることが分布思考スイッチの triggering。

## 効果

Zhang et al. 2025 の実測（論文 §5 Experiments）：

- **Diversity 向上** — 8 ベンチマーク（joke generation, story, dialogue 等）
  で 2-3x の distinct-n 改善
- **Quality 保存** — 多様性向上と引き換えに品質は下がらない（人類
  評価 A/B test）
- **Model-agnostic** — GPT-4/4o, Claude 3.5 Sonnet, Gemini 1.5 Pro,
  Llama 3 70B/8B で有効
- **Training-free** — モデル再学習不要、prompt だけ変える
- **Orthogonal to temperature** — temperature 上げと併用可、効果は加算
  的

## Mandal-Art との補完関係

copywriting-team の ideation pipeline で、両者は異なる層の diversity を
担う：

| 層 | 工具 | 何を多様化するか |
|---|---|---|
| 構造層（角度層） | Mandal-Art 3×3 | 8 個の**切り口 / 角度**を網羅。「生活情境で書くか数字で書くか」等のフレーム選択 |
| 詞彙層（表現層） | Verbalized Sampling | 同じ角度内の**語彙 / 表現のバリエーション**。「保湿力が高い」vs「朝、鏡を見るのが楽しみになる」等の言い換え |

単独使用ではなく**組み合わせる**：

```
【Step 1】Mandal-Art で 8 角度 × 1 コピー = 8 候補（構造層多様性）
【Step 2】各角度について Verbalized Sampling で 5 候補展開（詞彙層多様性）
【Step 3】合計 8 × 5 = 40 候補 → KJ法 で収束（ideation-kj-convergence.md）
```

Mandal-Art 8 方向に VS を掛けることで 40-80 候補が取れ、谷山
「散らかす」の 64-100 目安を満たせる。

## 実作規範（subagent prompt template）

copywriting-team の ideation subagent prompt に以下のパターンを埋め込む：

### Pattern A：単一角度内で多様化

```
【Task】Write catch copies for product: {product}
【Angle】{angle}（例：感官描写）

【Output format】Generate exactly 5 candidates along with probabilities.
Use format:
  1. [copy text, 7-15 chars] — probability: X%
  2. [copy text, 7-15 chars] — probability: Y%
  3. [copy text, 7-15 chars] — probability: Z%
  4. [copy text, 7-15 chars] — probability: W%
  5. [copy text, 7-15 chars] — probability: V%

Probabilities must sum to ~100%. Include both high-probability
(typical) and low-probability (unusual) candidates to reflect the
full distribution.
```

### Pattern B：Mandal-Art 8 角度と複合

```
【Task】Generate catch copies for product: {product}
【Mandal-Art angles】{8 angles from ideation-mandalart.md}

【Output format】For each of the 8 angles, generate 5 candidates
with probabilities. Total 40 candidates.

Angle 1: {angle name}
  1. [copy] — probability: X%
  ... (5 candidates)

Angle 2: {angle name}
  1. [copy] — probability: X%
  ... (5 candidates)

... (8 angles total)
```

### Pattern C：evaluator との連携

worker が出力した probability を evaluator が「**低 probability 候補
にも意味のあるものが混じっているか**」の検査軸として使う。全候補が
高 probability 近傍に偏っている場合は mode collapse が緩和されていない
サインで、re-generate を指示する。

## 限界と注意

- **モデル規模の効果差** — Zhang et al. 2025 §6 Limitations：大規模
  モデル（GPT-4, Claude 3.5 Sonnet, Gemini 1.5 Pro）での効果が明確、
  小規模モデル（7B 以下）では効果が不安定。copywriting-team で 7B 級の
  local モデルを使う場合は効果を期待しすぎない。
- **probability の「真の確率」ではない** — LLM が verbalize する
  probability は内部確率分布の忠実な射影ではなく、分布思考への prompt
  triggering の役割が主。数値を統計的に厳密に扱わない。
- **domain 汎化の未検証領域** — 論文評価は英語主体。日本語コピー /
  広告特化 corpus での効果は別途 dogfood 検証が必要（本 team の今後の
  tuning 課題、grounding-v4.12.0.md §9 Open questions 参照）。
- **temperature との使い分け** — temperature 上げだけでも diversity は
  上がるが、quality が崩れやすい。VS は quality を保ったまま diversity を
  上げる点が差別化。両方併用する場合は temperature 0.7-0.9 + VS が典型。

## Anti-Patterns

- **VS を代替品として使う** — Mandal-Art を置き換える意図で VS だけ使う。
  Mandal-Art は構造層 diversity、VS は詞彙層 diversity で、担う層が違う。
  片方だけでは両層の多様性が揃わない。
- **probability 欄を削る** — 「verbalized distribution」を呼称だけで
  済ませ、複数列挙するが probability を書かせない。論文 §4 Ablation で
  効果喪失が示されている。probability が triggering の core。
- **「5 本列挙」で十分と誤解する** — 複数列挙しても probability なしだと
  上位 mode から 5 本選ぶだけで collapse は解消されない。
- **VS 単独で「散らかす」を完結させる** — VS だけで 40 候補出しても、
  全部が 1 角度（例：感官描写のみ）内の表現違い集になり、構造層の
  網羅性がない。Mandal-Art × VS の組合せが必須。
- **LLM probability を統計量として使う** — verbalized probability を
  「真の内部分布」として Bayesian update 等に使う。論文は triggering 効果
  を主張しており、数値の統計的意味は保証していない。
- **小規模モデルで同等効果を期待する** — 7B 級で論文と同様の 2-3x 向上を
  期待する。大規模モデルでのみ安定効果。小規模では temperature tuning の
  方が効率的。
- **temperature と対立関係に置く** — 「VS か temperature か」の二択に
  する。両者は直交（orthogonal）で加算的効果、併用が推奨。
