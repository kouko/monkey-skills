# Visual Design Review Gate

Informed by Japanese aesthetic philosophy:
- **感性工学** (Kansei Engineering, 長町三生): Translate emotional
  responses into measurable design parameters. "What does it make
  the user FEEL?"
- **引き算のデザイン** (Subtractive Design): Every element must earn
  its place. Perfection is when there is nothing left to take away.
- **わびさび** (Wabi-Sabi): Beauty in imperfection, impermanence,
  incompleteness. Not everything needs sterile polish.

## Flag Definitions

### Composition & Layout（構図・レイアウト）
- 🔴 **Fatal**: 視覚的階層が存在しない — 閲覧者がどこを最初に見るべきか判断できない
- 🟡 **Warning**: グリッドに一貫性がなく、要素の配置に意図が感じられない
- 🟡 **Warning**: 余白が窮屈、もしくは意味のない空白になっている — 間（Ma）としての意図性がない。要素と要素の間に生まれる空隙が「呼吸」として機能していない
- 🟢 **Clear**: 構図にバランスがあり、視線が自然に導かれる。余白が「意味を帯びた空隙」として機能している

### Typography（タイポグラフィ）
- 🔴 **Fatal**: 本文が読めない（媒体に対してサイズ・ウェイト・行間が不適切）
- 🟡 **Warning**: 文字の階層が不明瞭 — 見出し・本文・キャプションの視覚的区別が弱い
- 🟡 **Warning**: フォントの組み合わせに違和感がある（スタイルやウェイトの相性が悪い）
- 🟢 **Clear**: タイポグラフィに調和があり、階層が一目で把握できる

### Color（色彩）
- 🔴 **Fatal**: テキストが WCAG AA のコントラスト基準を満たしていない、かつ装飾目的として明示されていない（`standards/wcag-baseline.md` 参照）
- 🔴 **Fatal**: 色だけが情報伝達の唯一の手段になっている（アイコン・パターン・ラベルによる補完がない）
- 🟡 **Warning**: 色彩の感性特性（情緒的トーン）がブランド・製品の意図と一致していない。配色から受ける印象が、伝えたい世界観と乖離している
- 🟡 **Warning**: ダーク/ライトモード両方で使用される製品なのに、片方しか考慮されていない
- 🟢 **Clear**: パレットに調和がある。コントラストは基準を満たし、色彩の感性特性がブランド意図と一致している

### Brand Consistency（ブランド一貫性）
- 🔴 **Fatal**: 既存のブランドスタイルガイドと直接矛盾している（ロゴ・色・トーンの誤用）
- 🟡 **Warning**: 画面間やデリバラブル間でアセットの使い方に揺れがある
- 🟢 **Clear**: ブランドガイドラインに準拠。媒体を跨いだ一貫性が保たれている

### Craft（仕上げの丁寧さ）
- 🟡 **Warning**: 整列のズレやピクセルレベルの不整合が目に見える。佇まい（内部設計から自然と滲み出す品格）が損なわれている
- 🟡 **Warning**: 対象媒体に対して書き出し品質が不十分
- 🟢 **Clear**: 本番品質。細部を見るほど丁寧さが伝わる。佇まいがある

## 感性チェック (Kansei Check)

Flag Definitions で構造的な品質を確認した後、以下の三つの観点から
デザインの感性品質（emotional quality）を評価する。

### A. 印象評価 (SD法ベース)

SD法（セマンティック・ディファレンシャル法）の形容詞対でデザインの印象を構造化する。
各対について、デザインがどちら寄りかを判断し、その印象プロファイルが
製品・ブランドの意図と一致しているかを確認する。

参考: J-SEMS, J-STAGE (Osgood三因子), AIIT 東京都立産業技術大学院大学

**評価性因子:**
- 洗練された ←→ 野暮な
- 上品な ←→ 下品な

**力量性因子:**
- 高級感がある ←→ 安っぽい
- シンプルな ←→ ごちゃごちゃした

**活動性因子:**
- 先進的な ←→ 古臭い
- 親しみのある ←→ よそよそしい

**判定**: 印象プロファイルが製品・ブランドの意図と乖離している場合、
Flag Definitions の Color セクションにある感性特性の 🟡 Warning を適用する。

### B. 日本的感性品質チェック

英語に直接対応する概念がない、日本固有の美意識に基づく評価項目。
各項目について、デザインがその品質を備えているかを確認する。

参考: KOGEI STANDARD (間と余白), ガリバーコラム (引き算のデザイン),
btrax (UXピラミッド), studio-tabi (佇まい), Wikipedia (わびさび)

| チェック項目 | 関連概念 | 評価の問い |
|-------------|----------|-----------|
| **余白の意図性** | 間・余白 | 余白が「何もない」ではなく「意味を帯びた空隙」になっているか。ポジティブ・スペースとネガティブ・スペースが相補関係として機能しているか |
| **引き算の徹底** | 引き算のデザイン | 「無くてもよい情報」が残っていないか。掲載内容に序列があり、最も目立たせたいコトが沈んでいないか |
| **抜け感** | 抜け感 | 視線が自然に遠くへ導かれ、息苦しさがないか。空間の連続性が感じられるか |
| **余韻** | 余韻 | 体験が終わった後も「味わい」が残る設計になっているか。余白が十分にあり、構図全体に上質さを感じ取れるか |
| **佇まい** | 佇まい | 外観の美しさが内部設計の蓄積から自然と滲み出しているか。意図的に「見た目を飾る」のではなく、品格が内在しているか |
| **気配** | 気配 | 明示されないが確かに感じ取れる微細な存在感・雰囲気があるか。意図的に全てを説明しない余地があるか |
| **不完全の許容** | わびさび | 過度に均一・完璧でなく、自然な「表情」があるか。慎ましく質素なものの中に奥深さや豊かさを感じられるか |

**判定**: 複数の項目で品質の欠如が見られる場合、総合的な感性品質の問題として
Flag Definitions の Composition または Craft セクションの 🟡 Warning を適用する。

### C. おもてなし品質チェック

寿司職人の仕事哲学に学ぶ、デザインにおける「おもてなし」の品質。
参考: btrax「寿司職人から学ぶUXデザイン 6つの極意」

| チェック項目 | 評価の問い |
|-------------|-----------|
| **先回りの気遣い** | ユーザーが求める前に、必要なものが提供されているか |
| **隠し要素** | 予期しない小さな喜び（delight）が埋め込まれているか |
| **ストーリー性** | 各要素に文脈や意味があるか。データだけでなく物語があるか |
| **細部の品格** | 普段見えない部分にも丁寧さがあるか（「神は細部に宿る」） |
| **究極のシンプルさ** | 最高品質の素材（要素）で勝負しているか。装飾に頼っていないか |

**判定**: おもてなし品質の欠如は PASS を妨げないが、感性レポートに記載する。
優れたおもてなし品質が確認された場合も、感性レポートで特筆する。

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
