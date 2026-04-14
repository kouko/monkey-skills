# Protocol: Copy Audit（既存文案の審稿 / 改善 / A/B 変体提案）

**When to use**：使用者が既存文案に対して審稿 / 改善提案 / A/B 変体生成を要求した時。典型情境為 競合広告のパフォーマンス診断、自社 LP の CVR 改善、既存キャッチコピーのリニューアル、景品表示法 / FTC 対応のための倫理点検、brand voice 刷新に伴う文案全面 audit。撰寫 protocol（write-long / mid / short-form-copy）は**新規生成**を扱い、本 protocol は**既存物の評価**を扱う。

**Output**：審稿報告（issues + 改善提案 + オプション rewrite variants）。issues は重症度順、改善提案は具体的書換例、variants はユーザー要望時のみ 2-3 個を付帯。

**Grounds on**：既存文案の類型により以下 standards を動的参照する。
- 長文：`../standards/long-form-pasona-canon.md`、`../standards/persuasion-psychology-anchor.md`
- 中文：`../standards/mid-form-beaf-canon.md`
- 短文：`../standards/short-form-catchcopy-canon.md`、`../standards/ideation-taniyama-discipline.md`
- 共通：`../standards/voice-and-tone.md`、`../standards/persuasion-ethics.md`

## Phase 1: 類型識別

既存文案の構造を特定し、適用する standards を動的に決定する。

1. **字數帯による 1 次判定**：
   - 7-15 字 → 短文案（キャッチコピー）
   - 数十〜数百字 → 中文案（商品ページ / POP）
   - 1,500 字以上 → 長文案（LP / sales letter）
   - 境界値（500-1,500 字）は媒体で判定（LP なら長文系、商品ページなら中文系）。

2. **framework の識別**：
   - **PASONA 系列**：Problem → Agitation/Affinity → Solution → ... の段階構造があるか
     - 5 段階（P/A/So/N/A）なら 旧 PASONA
     - 6 段階（P/A/S/O/N/A、Affinity 起点）なら 新 PASONA
     - 9 段階（P/A/S/B/E/C/O/N/A）なら PASBECONA
   - **BEAF**：Benefit 冒頭 → Evidence → Advantage → Feature の順序があるか
   - **キャッチコピー**：7-15 字の単独文。5 種切入点（利益 / 恐怖 / 顛覆 / 目標呼喚 / 提問）のいずれか
   - **無 framework**：構造が識別できない場合は「frame-less」と記録

3. **voice lineage の識別**（短文の場合）：糸井 / 岩崎 / 眞木 / 谷山 のいずれかの lineage 特徴が見られるか、または Anglo headline tradition 寄りか、無 voice か。

4. **記録**：類型 / framework / voice lineage / 媒体 / 字數 を草稿冒頭にメタ記述。

## Phase 2: 診断

識別結果に応じて標準項目を適用し、issues を列挙する。

1. **Form-appropriate 診断**（類型ごとに適用）：
   - 長文案 → `long-form-pasona-canon.md` §旧 / 新 / PASBECONA 表の段階任務 / §段階間 flow 設計原則（離脱点 / 字數比例 / Affinity 厚さ / Narrow down-Action 近接）
   - 中文案 → `mid-form-beaf-canon.md` §Benefit-first 順序の重要性 / §BEAF の 4 段階定義
   - 短文案 → `short-form-catchcopy-canon.md` §7-15 字 黃金範囲 / §AIDMA 短文案作用域 / §3 秒ルール

2. **Framework adherence 診断**：
   - PASONA 系列：段階を飛ばしていないか / Affinity を Agitation 化していないか / Offer を省略していないか / Narrow down と Action が隣接しているか（`long-form-pasona-canon.md` §Anti-Patterns）
   - BEAF：Feature 先出しになっていないか / Evidence を省略していないか / FAB の順序と混同していないか（`mid-form-beaf-canon.md` §Anti-Patterns）
   - キャッチコピー：15 字超でないか / AIDMA 全段階を 1 行で済ませていないか / 描写型で止まっていないか（`short-form-catchcopy-canon.md` §Anti-Patterns + `ideation-taniyama-discipline.md` §描写 vs 解決）

3. **Voice 整合性診断**（`voice-and-tone.md` §Voice vs Tone + §Anti-Patterns）：
   - 同一キャンペーン内で voice 漂移がないか
   - headline と body で voice が切断していないか
   - voice guide（brand 提供）との整合性
   - Ogilvy「respect the reader」違反（condescending / 空洞 hype）がないか

4. **倫理診断**（`persuasion-ethics.md` §景品表示法要點 / §FTC Endorsement Guides 要點 / §Dark Pattern 反模式清單）：
   - 景品表示法 優良誤認 / 有利誤認 / 打消し表示 / ステマ告示 の違反がないか
   - FTC §255.1（endorser 真実性）/ §255.2（testimonial 代表性）/ §255.5（material connection）
   - Dark pattern（false scarcity / fake social proof / hidden costs / forced continuity / confirmshaming）
   - 小霜「嘘をつかない」原則違反（誇大 / benefit 捏造 / 声偽造 / 煽り基本戦略）

5. **Issues のレベル分類**：
   - **Critical**：法律違反（景品表示法 / FTC）の疑い。即修正必須。
   - **Major**：framework canonical 違反（順序違反 / 段階省略 / 倫理境界抵触）。修正推奨。
   - **Minor**：voice 漂移 / 字數外れ / 磨き不足。改善提案。

## Phase 3: 改善提案

各 issue について具体的な書換え案を提示する。

1. **重症度順に列挙**：Critical → Major → Minor の順。

2. **各 issue の改善フォーマット**：
   ```
   Issue ID：ISS-NN
   類型：[Critical / Major / Minor]
   違反対象：[違反している standard / canonical の具体参照]
   問題箇所：[原文の該当箇所を引用]
   問題の本質：[なぜ違反か / どう機能していないか]
   改善提案：[具体的書換え案]
   改善理由：[改善後がなぜ canonical に整合するか]
   ```

3. **改善提案の具体性基準**：
   - 抽象的指摘（「Benefit 寄りにする」）は不足。**具体的書換え文**まで提示する。
   - 複数案を提示する場合は 2-3 個に留める（選択肢過多は使用者を疲弊させる）。
   - 書換え案は元文案の voice を維持する。voice 刷新が目的でない限り、voice 変更は別 issue として扱う。

4. **Framework 切替を提案する場合**：
   - 例：「旧 PASONA で書かれているが、awareness level 4-5 なので 新 PASONA 推奨」
   - Phase 1 で識別した framework と Phase 2 で発見した不整合から、別 framework への切替を推奨する場合は明確に書く。
   - ただし切替は大幅書換えを伴うため Critical / Major 級の根本問題がある場合のみ。

## Phase 4: （オプション）Rewrite Variants

使用者が明示的に「A/B 変体が欲しい」と要求した場合のみ実行。通常の audit では Phase 3 で終了。

1. **Variants 生成方針**：
   - 2-3 個の variants を default とする。4 個以上は A/B テスト設計を複雑化する。
   - 各 variant は**異なる切入点 / 異なる voice lineage / 異なる framework** のいずれかで差別化する。全 variant が同一軸の微調整だと A/B テストの意義が薄い。

2. **「なんかいいよね禁止」適用**（`ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール）：
   - 各 variant に「なぜ良いか」3 項を必須明記：
     1. 何が読者に何を伝えるか
     2. 既存の類似コピーに対して何が新しいか
     3. ターゲットの生活 / 文脈で何が共鳴するか
   - 3 項を具体化できない variant は提示しない。

3. **差別化軸の例**：
   - 短文案：利益型 vs 恐怖型 vs 提問型（5 種切入点から 2-3 本）
   - 中文案：Benefit フレーズの表現違い（生活変化フォーカス vs 感情フォーカス vs 社会的認知フォーカス）
   - 長文案：Affinity 起点の voice 違い（糸井系 状態提案 vs 岩崎系 季節感 vs Anglo 直接型）

4. **倫理 self-check を各 variant に適用**：Phase 2 §4 倫理診断 を各 variant でも実行。Phase 3 で除外した dark pattern を variant 側に混入させない。

## Rules

- Phase 1 の類型識別を先に固定する。類型が曖昧なまま診断すると framework adherence の判定基準が揺らぐ。
- 改善提案は具体的書換え文まで提示する。抽象指摘のみは審稿として不十分。
- Issues は重症度順。Critical（法律違反）を Minor（磨き不足）より先に列挙する。
- Rewrite variants はユーザー要望時のみ生成する。要望がないのに勝手に出さない（audit の本分は評価、生成は副次）。
- Variants 生成時は「なぜ良いか」3 項を各 variant に必須付帯。
- 倫理診断では景品表示法 / FTC / dark pattern / 小霜原則 の 4 軸を全て check する。1 軸だけの check は漏れのリスク。
- 撰寫 protocol と本 protocol を混用しない。既存文案の評価は本 protocol、新規生成は `write-*-form-copy.md`。

## Anti-Patterns

- **類型識別を飛ばして全 standard を総当たり適用する**：短文案に PASBECONA の 9 段階 check を適用するなど、類型不適合の診断をする。
- **抽象指摘のみで具体書換えを出さない**：「Benefit 寄りに書き直してください」だけで終わる。改善提案は具体文まで。
- **Critical / Major / Minor の重症度を付けずに issues を羅列する**：使用者が何から直すべきか判断できない。
- **Rewrite variants をユーザー要望なしに勝手に出す**：audit の責務越権。評価と生成は別タスク。
- **Variants 全てが同一軸の微調整で差別化不足**：A/B テストの意義が薄い。切入点 / voice lineage / framework のいずれかで軸を変える。
- **Variants に「なぜ良いか」3 項を付けない**：「なんかいいよね」変体を量産する。
- **倫理診断で景品表示法 / FTC のどちらか一方だけ check する**：市場（JP / US）と媒体（SNS / LP）の両方を見て 4 軸フル check が canonical。
- **voice 漂移を「スタイルの違い」として見過ごす**：同一キャンペーン内の voice 不一致は brand asset の毀損。Minor で済ませず Major 以上で扱う場合もある。
- **framework 切替を軽々しく提案する**：大幅書換えを伴うため、Critical / Major 級の根本問題がある場合のみ。Minor で framework 切替は過剰。
- **改善提案で元文案の voice を無断で変更する**：voice 刷新が目的でない限り、voice 変更は別 issue として扱う。
