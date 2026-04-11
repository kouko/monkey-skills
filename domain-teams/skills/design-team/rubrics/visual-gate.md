# Visual Design Review Gate

Scope: Garrett's 表層 (Surface) plane
(`standards/garrett-elements-of-ux.md` §Gate Scope Partition). Structure,
navigation, and interaction belong to ui-interaction-gate; temporal
UX and business strategy belong to ux-strategy-gate.

Informed by Japanese aesthetic philosophy:
- **感性工学** (Kansei Engineering, 長町三生): Translate emotional
  responses into measurable design parameters. "What does it make
  the user FEEL?"
- **引き算のデザイン** (Subtractive Design): Every element must earn
  its place. Perfection is when there is nothing left to take away.
- **わびさび** (Wabi-Sabi): Beauty in imperfection, impermanence,
  incompleteness. Not everything needs sterile polish.

## Primary Sources

All Kansei, SD-method, and Japanese-aesthetic claims below derive
from two tier-classified standards — **not** from blog posts,
corporate marketing columns, or Wikipedia. v4.8.0 removes 5 prior
anti-pattern citations; see the "Citation cleanup note (v4.8.0)" at
the bottom of this file for the removal list.

- **感性工学 + SD 法 (Section A 印象評価)** →
  `standards/kansei-engineering-and-sd.md`. Primary sources there:
  長町三生 (1989) 『感性工学—感性をデザインに活かすテクノロジー』
  海文堂出版 (JP-original academic anchor); Mitsuo Nagamachi (1995)
  "Kansei Engineering: A new ergonomic consumer-oriented technology
  for product development", *International Journal of Industrial
  Ergonomics* 15(1):3-11 (peer-reviewed EN primary); Charles E.
  Osgood, George J. Suci & Percy H. Tannenbaum (1957) *The
  Measurement of Meaning*, University of Illinois Press (primary
  source for the Semantic Differential method and the 3-factor
  Evaluation / Potency / Activity structure). Replaces the earlier
  J-SEMS / J-STAGE / AIIT citations; see that standard's §Critical
  Attribution Corrections.
- **日本的感性品質 (Section B)** →
  `standards/japanese-design-aesthetics.md`. Primary sources there:
  原研哉 (2003) 『デザインのデザイン』岩波書店 (引き算 + Ch.6
  「日本にいる私」for 佇まい); 原研哉 (2008) 『白』中央公論新社
  Ch.3 「空白 エンプティネス」(白 / 余白); Kenya Hara (2007)
  *Designing Design*, Lars Müller Publishers (EN companion);
  深澤直人 (2005) 『デザインの輪郭』TOTO 出版 (Without Thought /
  無意識のデザイン); 磯崎新 (2003) 『建築における「日本的なもの」』
  新潮社 (scholarly primary for 間 ma); Leonard Koren (1994)
  *Wabi-Sabi for Artists, Designers, Poets & Philosophers*, Stone
  Bridge Press (canonical Western design entry point for wabi-sabi).
  Replaces the earlier KOGEI STANDARD / ガリバーコラム / studio-tabi /
  Wikipedia / btrax citations; see that standard's §Critical
  Attribution Corrections.
- **Surface plane scope (no overreach into Structure / Skeleton or
  Strategy / Scope)** → `standards/garrett-elements-of-ux.md` §The
  5 Planes + §Gate Scope Partition.
- **Color contrast cross-reference** → `standards/wcag-baseline.md`
  SC 1.4.3 Contrast (Minimum) AA + SC 1.4.11 Non-text Contrast AA.

## Flag Definitions

### Composition & Layout（構図・レイアウト）
Grounded in `standards/japanese-design-aesthetics.md` §1 引き算のデザイン
+ §2 白／余白 + §3 間 ma.

- 🔴 **Fatal**: 視覚的階層が存在しない — 閲覧者がどこを最初に見るべきか判断できない
- 🟡 **Warning**: グリッドに一貫性がなく、要素の配置に意図が感じられない
- 🟡 **Warning**: 余白が窮屈、もしくは意味のない空白になっている — 間（Ma）としての意図性がない。要素と要素の間に生まれる空隙が「呼吸」として機能していない（see `standards/japanese-design-aesthetics.md` §3 間 ma: 磯崎新 2003; §2 白／余白: 原研哉 2008 Ch.3）
- 🟢 **Clear**: 構図にバランスがあり、視線が自然に導かれる。余白が「意味を帯びた空隙」として機能している

### Typography（タイポグラフィ）
- 🔴 **Fatal**: 本文が読めない（媒体に対してサイズ・ウェイト・行間が不適切）
- 🟡 **Warning**: 文字の階層が不明瞭 — 見出し・本文・キャプションの視覚的区別が弱い
- 🟡 **Warning**: フォントの組み合わせに違和感がある（スタイルやウェイトの相性が悪い）
- 🟢 **Clear**: タイポグラフィに調和があり、階層が一目で把握できる

### Color（色彩）
Contrast grounded in `standards/wcag-baseline.md` SC 1.4.3 AA and
SC 1.4.11 AA.

- 🔴 **Fatal**: テキストが WCAG AA のコントラスト基準を満たしていない、かつ装飾目的として明示されていない（SC 1.4.3 Contrast (Minimum) AA: ≥ 4.5:1 normal text, ≥ 3:1 large text — see `standards/wcag-baseline.md`）
- 🔴 **Fatal**: 色だけが情報伝達の唯一の手段になっている（アイコン・パターン・ラベルによる補完がない）
- 🟡 **Warning**: 色彩の感性特性（情緒的トーン）がブランド・製品の意図と一致していない。配色から受ける印象が、伝えたい世界観と乖離している（calibrate using Section A 印象評価 SD profile below）
- 🟡 **Warning**: ダーク/ライトモード両方で使用される製品なのに、片方しか考慮されていない
- 🟢 **Clear**: パレットに調和がある。コントラストは基準を満たし、色彩の感性特性がブランド意図と一致している

### Brand Consistency（ブランド一貫性）
- 🔴 **Fatal**: 既存のブランドスタイルガイドと直接矛盾している（ロゴ・色・トーンの誤用）
- 🟡 **Warning**: 画面間やデリバラブル間でアセットの使い方に揺れがある
- 🟢 **Clear**: ブランドガイドラインに準拠。媒体を跨いだ一貫性が保たれている

### Craft（仕上げの丁寧さ）
Grounded in `standards/japanese-design-aesthetics.md` §4 佇まい
(原研哉 2003 Ch.6「日本にいる私」).

- 🟡 **Warning**: 整列のズレやピクセルレベルの不整合が目に見える。佇まい（内部設計から自然と滲み出す品格）が損なわれている
- 🟡 **Warning**: 対象媒体に対して書き出し品質が不十分
- 🟢 **Clear**: 本番品質。細部を見るほど丁寧さが伝わる。佇まいがある

## 感性チェック (Kansei Check)

Flag Definitions で構造的な品質を確認した後、以下の二つの観点から
デザインの感性品質（emotional quality）を評価する。
(Section C omitted in v4.8.0 — see Citation cleanup note below.)

### A. 印象評価 (SD法ベース)

Grounded in `standards/kansei-engineering-and-sd.md` §SD Method Full
Definition + §Osgood's 3-Factor Structure.

SD 法（Semantic Differential 法）は Osgood, Suci & Tannenbaum (1957)
*The Measurement of Meaning*（University of Illinois Press）で確立された
**7 段階 bipolar 尺度**であり、評価性 (Evaluation) / 力量性 (Potency) /
活動性 (Activity) の 3 因子に分解される。長町三生 (1989) 『感性工学』
海文堂出版 + Nagamachi (1995) *IJIE* 15(1):3-11 が感性工学における
運用方法を定義している。5 段階や unipolar スケールは Osgood の因子構造を
壊すので使用しない。

各対についてデザインがどちら寄りかを判断し、その印象プロファイルが
製品・ブランドの意図と一致しているかを確認する。

**評価性因子 (Evaluation):**
- 洗練された ←→ 野暮な
- 上品な ←→ 下品な

**力量性因子 (Potency):**
- 高級感がある ←→ 安っぽい
- シンプルな ←→ ごちゃごちゃした

**活動性因子 (Activity):**
- 先進的な ←→ 古臭い
- 親しみのある ←→ よそよそしい

**判定**: 印象プロファイルが製品・ブランドの意図と乖離している場合、
Flag Definitions の Color セクションにある感性特性の 🟡 Warning を適用する。
項目の追加と選定方法は `standards/kansei-engineering-and-sd.md`
§Constructing a Valid SD Questionnaire を参照。

### B. 日本的感性品質チェック

Grounded in `standards/japanese-design-aesthetics.md` §1-6.

英語に直接対応する概念がない、日本固有の美意識に基づく評価項目。
各項目について、デザインがその品質を備えているかを確認する。

| チェック項目 | 関連概念 | Primary source | 評価の問い |
|-------------|---------|----------------|-----------|
| **余白の意図性** | 間・余白 | 磯崎新 (2003) 『建築における「日本的なもの」』新潮社 §間 ma + 原研哉 (2008) 『白』中央公論新社 Ch.3 「空白 エンプティネス」 | 余白が「何もない」ではなく「意味を帯びた空隙」になっているか。ポジティブ・スペースとネガティブ・スペースが相補関係として機能しているか |
| **引き算の徹底** | 引き算のデザイン | 原研哉 (2003) 『デザインのデザイン』岩波書店 | 「無くてもよい情報」が残っていないか。掲載内容に序列があり、最も目立たせたいコトが沈んでいないか |
| **抜け感** | 抜け感 | 日本的感性 lexicon（通用）; 補助参照 原研哉 2003 / 2008 + 深澤直人 2005 | 視線が自然に遠くへ導かれ、息苦しさがないか。空間の連続性が感じられるか |
| **余韻** | 余韻 | 日本的感性 lexicon（通用）; 補助参照 原研哉 2008 『白』 | 体験が終わった後も「味わい」が残る設計になっているか。余白が十分にあり、構図全体に上質さを感じ取れるか |
| **佇まい** | 佇まい | 原研哉 (2003) 『デザインのデザイン』Ch.6 「日本にいる私」（「たたずまいは吸引力を生む資源である」） | 外観の美しさが内部設計の蓄積から自然と滲み出しているか。意図的に「見た目を飾る」のではなく、品格が内在しているか |
| **気配** | 気配 | 日本的感性 lexicon（通用）; 補助参照 深澤直人 (2005) 『デザインの輪郭』TOTO 出版 | 明示されないが確かに感じ取れる微細な存在感・雰囲気があるか。意図的に全てを説明しない余地があるか |
| **不完全の許容** | わびさび | Leonard Koren (1994) *Wabi-Sabi for Artists, Designers, Poets & Philosophers*, Stone Bridge Press | 過度に均一・完璧でなく、自然な「表情」があるか。慎ましく質素なものの中に奥深さや豊かさを感じられるか。わびさびは装飾ではなく **受容の態度**（Koren 1994）であることに注意 |

**判定**: 複数の項目で品質の欠如が見られる場合、総合的な感性品質の問題として
Flag Definitions の Composition または Craft セクションの 🟡 Warning を適用する。

> **Philosophical anchor (replaces former Section C):** おもてなしの精神
> — ユーザーが求める前に必要なものを備え、細部まで品格を通す姿勢 — は
> 上記 Section B の諸項目（特に 引き算 / 佇まい / 気配）と
> `protocols/ux-strategy.md` の戦略的な「先回りの気遣い」で既に
> 捕捉されている。このゲートでは独立した load-bearing flag としては
> 扱わず、感性レポートの philosophical framing に留める。詳細は下の
> Citation cleanup note (v4.8.0) を参照。

## Context-Aware Review

Adapt flag severity to the medium:
- **App UI**: Platform conventions matter; system fonts and dynamic type
- **Poster / Print**: Viewing distance, CMYK, bleed and margin
- **Brand Asset**: Scalability (favicon to billboard), format versatility
- **Marketing**: Target audience, conversion intent, cultural appropriateness
- **Icon / Illustration**: Consistency within set, metaphor clarity

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Flags**: `[🔴 Dimension]` or `[🟡 Dimension]` with evidence
2. **感性レポート** (Kansei Report): Emotional impression summary
3. **Fix Instruction**: Concrete visual change with rationale
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Note: Visual assets require human creation — your feedback will be
presented to the user, not auto-revised. Be clear about what to change.

## Citation cleanup note (v4.8.0)

The v4.8.0 refactor removed 5 anti-pattern citations plus one
freestanding section from earlier versions of this gate. All
replacements live in the tier-classified standards listed under
Primary Sources above. For the authoritative replacement map see
`standards/kansei-engineering-and-sd.md` §Critical Attribution
Corrections and `standards/japanese-design-aesthetics.md` §Critical
Attribution Corrections.

1. **J-SEMS / J-STAGE / AIIT 東京都立産業技術大学院大学** (previously
   cited in Section A 印象評価 for the SD method). These are Japanese
   academic conferences, a publication portal, and an applied-research
   university — second-level aggregators, not the primary source.
   **Replaced by** Osgood, Suci & Tannenbaum (1957) *The Measurement
   of Meaning*, University of Illinois Press (primary) + 長町三生
   (1989) 『感性工学』 海文堂出版 + Nagamachi (1995) *IJIE* 15(1):3-11,
   via `standards/kansei-engineering-and-sd.md`.
2. **KOGEI STANDARD「日本の美意識 間と余白」column** (previously
   cited in Section B for 間・余白). Corporate brand magazine column,
   not a scholarly primary. **Replaced by** 磯崎新 (2003) 『建築に
   おける「日本的なもの」』新潮社 (scholarly primary for 間 ma) +
   原研哉 (2008) 『白』 中央公論新社 Ch.3 「空白 エンプティネス」
   (余白 / 空白 as active design element), via
   `standards/japanese-design-aesthetics.md`.
3. **studio-tabi 佇まい blog** (previously cited in Section B).
   Personal studio blog, not a scholarly primary. **Replaced by**
   原研哉 (2003) 『デザインのデザイン』Ch.6 「日本にいる私」
   (「たたずまいは吸引力を生む資源である」), via
   `standards/japanese-design-aesthetics.md`.
4. **Wikipedia「わびさび」** (previously cited in Section B).
   Encyclopedia article, not a primary source. **Replaced by**
   Leonard Koren (1994) *Wabi-Sabi for Artists, Designers, Poets &
   Philosophers*, Stone Bridge Press (canonical Western entry point
   for wabi-sabi as a design concept), via
   `standards/japanese-design-aesthetics.md`.
5. **ガリバーコラム「引き算のデザイン」** (previously cited in
   Section B). Used-car marketing column, not a design primary.
   **Replaced by** 原研哉 (2003) 『デザインのデザイン』 岩波書店,
   via `standards/japanese-design-aesthetics.md`.
6. **btrax「寿司職人から学ぶ UX デザイン 6 つの極意」** (previously
   cited as the Section C framework source for an おもてなし品質
   チェック). Corporate blog post; **no primary book exists for the
   6-point framework**. The entire Section C (おもてなし品質チェック)
   has been **removed** in v4.8.0 and replaced with a 1-paragraph
   philosophical anchor under Section B that delegates おもてなし
   coverage to `protocols/ux-strategy.md` (the "先回りの気遣い"
   framing) and to the existing Section B 引き算 / 佇まい / 気配
   checks. Per `standards/japanese-design-aesthetics.md` §Critical
   Attribution Corrections, Section C is omitted rather than
   replaced with a weaker primary.
