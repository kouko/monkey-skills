# Checklist: Persuasion Ethics

MUST gate (binary pass/fail). Triggers: 文案 artifact 已完成 (長／中／短
いずれか)。本 gate は法律硬邊界 (景品表示法 + FTC) と 倫理軟邊界
(dark pattern + 小霜) の両軌で audit する。

## Primary Sources

- `../standards/persuasion-ethics.md` — 雙軌結構（法律 + 倫理）の
  canonical 定義。FTC Endorsement Guides (2023-07-01 施行) + 景品
  表示法 (2023 改正、2024-10-01 施行) + ステマ告示 (2023-10-01 施行) +
  Brignull dark pattern 12 類 + 小霜「嘘をつかない」原則。
- U.S. Federal Trade Commission, *Guides Concerning the Use of
  Endorsements and Testimonials in Advertising* (16 CFR Part 255, 2023).
- 日本国 消費者庁『不当景品類及び不当表示防止法』.
- Harry Brignull, *Deceptive Design* (deceptive.design, 2010–).
- 小霜和也 (2014) 『ここらで広告コピーの本当の話をします。』宣伝会議.

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's
output. Give `PASS`, `FAIL_FATAL`, `FAIL_FIXABLE`, or `N/A` for each
item, with specific evidence (quoted line or artifact reference).
Failure type for each item is defined below — use the type specified.

`N/A` は **artifact に該当要素が存在しない場合のみ**許可される
（例：testimonial を含まない短文案の CHK-CTW-ETH-006 は N/A）。
該当要素があるが未遵守は `N/A` ではなく `FAIL_*`。

## Checklist

- [ ] **CHK-CTW-ETH-001 (Dark Pattern — confirmshaming / roach motel /
  hidden costs)** [FATAL]: 文案が Brignull 12 類のいずれにも該当
  しない。特に以下を check：
  - **Confirmshaming**: opt-out ボタンのラベルに自嘲／罪悪感煽る
    表現（例：「No thanks, I hate saving money」「いいえ、健康は
    気にしません」）
  - **Roach motel**: 「いつでも解約可能」等の訴求文面に対し、実装
    が解約困難（電話のみ／複雑フロー）な旨の自認
  - **Hidden costs**: 送料／税／手数料が checkout 最終まで隠れる
    訴求文面（「送料込み」表示なしの「〇〇円ぽっきり」等）
  該当 1 件で FATAL。**Grounded in**:
  `../standards/persuasion-ethics.md` §Dark Pattern 反模式清單。
- [ ] **CHK-CTW-ETH-002 (False scarcity / urgency)** [FATAL]: 「限時」
  「残り〇名」「24 時間限定」「本日限り」等の稀少性／緊迫性表現が
  **実際に真実** であることが、artifact メタ情報 or 入力ブリーフで
  確認できる。毎日リセットされる「24 時間限定」や在庫無限の「残り
  3 名」は景品表示法 第 5 条第 2 号（有利誤認表示）に該当し FATAL。
  真実性が confirmable でなく書き手が「例示」と明示してある場合は
  FIXABLE（実装時に真実性担保が必要）。**Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法要點 §有利誤認表示 +
  §Dark Pattern (False scarcity)。
- [ ] **CHK-CTW-ETH-003 (優良誤認表示 — 品質／規格の誇大)** [FATAL]:
  景品表示法 第 5 条第 1 号違反となる以下表現が**根拠なし**で使用
  されていない：
  - 「業界最高品質」「世界初」「世界一」「No.1」「最高峰」等の最
    上級表示
  - 性能データの改ざん／恣意的條件選択の疑い
  - 不当な比較優位表示（競合を虛偽に劣位として描く）
  根拠（受賞／統計／第三者評価）が artifact または入力ブリーフに
  示されている場合は PASS。根拠なしの最上級表示は FATAL。
  **Grounded in**: `../standards/persuasion-ethics.md` §景品表示法
  要點 §優良誤認表示 + §Anti-Patterns。
- [ ] **CHK-CTW-ETH-004 (有利誤認表示 — 価格／取引条件)** [FATAL]:
  景品表示法 第 5 条第 2 号違反となる以下表現が存在しない：
  - 虚偽の「通常価格」比較（二重価格表示）：実績のない「通常
    〇〇円 → 今だけ〇〇円」
  - 架空の「期間限定」「数量限定」（CHK-002 と併発可能）
  - 隠れた追加料金の不記載（CHK-001 と併発可能）
  該当 1 件で FATAL。**Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法要點 §有利誤認表示。
- [ ] **CHK-CTW-ETH-005 (打消し表示 — disclaimer の過小字処理)**
  [FIXABLE]: メイン訴求を制限／否定する disclaimer（「※条件あり」
  「※個人の感想です」「※期間限定」等）が存在する場合、以下を
  check：
  - 文字サイズ／色／背景コントラストでメイン訴求と同等に可読
    (8pt 以下の極小字、低コントラストは FIXABLE)
  - メイン訴求を**実質的に否定する** disclaimer でない（実質否定は
    メイン訴求自体が誤認表示になり、この場合は FATAL ではなく
    CHK-003 or 004 で別途 check）
  - 動画／モーショングラフィックスでの表示時間が読める長さ
  消費者庁 2017 ガイドライン準拠。**Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法要點 §打消し表示
  の規範。
- [ ] **CHK-CTW-ETH-006 (Testimonial — FTC §255 準拠)** [FATAL]:
  artifact に testimonial（顧客の声、before/after、レビュー引用）が
  含まれる場合：
  - endorser が実在（架空でない）— §255.1 違反なら FATAL
  - 結果が typical でない場合、typical な結果を明示（「results not
    typical」単独では不十分、2023 改訂 §255.2）
  - before/after の条件（期間／使用量／併用方法）が明示
  testimonial 非含有 artifact は `N/A`。**Grounded in**:
  `../standards/persuasion-ethics.md` §FTC Endorsement Guides 要點 +
  §Copy 層面的具体反模式（Fake testimonial, Ambiguous before/after）。
- [ ] **CHK-CTW-ETH-007 (広告／編集の区別 — ステマ告示 + §255.5)**
  [FATAL]: 以下のいずれかが存在する場合、明示 disclosure がある：
  - 事業者が第三者になりすます表現（レビュー／SNS 投稿の模倣）
  - インフルエンサー起用で対価提供あり — 「広告」「PR」「Sponsored」
    「#PR」等の明示必須
  - アフィリエイトリンクを含むコンテンツ — 広告性の明示必須
  明示なし → FATAL（2023-10-01 施行のステマ告示 + FTC §255.5 material
  connection 違反）。該当なし（純粋な自社広告、編集コンテンツなし）
  は `N/A`。**Grounded in**: `../standards/persuasion-ethics.md`
  §ステルスマーケティング告示 + §FTC Endorsement Guides 要點。
- [ ] **CHK-CTW-ETH-008 (Affiliate link / promoted post の明示)**
  [FIXABLE]: 「おすすめ〇選」「ベスト〇〇」等のキュレーション文案
  でアフィリエイト収益化が含まれる場合、冒頭 or 近接位置に
  「本記事にはアフィリエイトリンクが含まれます」旨の明示がある。
  近接性／目立つこと／理解可能性の 3 要件（FTC .com Disclosures 2013）
  を満たす位置に disclosure。disclosure 位置が記事末尾のみ or 極小字
  は FIXABLE。**Grounded in**:
  `../standards/persuasion-ethics.md` §FTC Endorsement Guides 要點
  §.com Disclosures + §Copy 層面的具体反模式。
- [ ] **CHK-CTW-ETH-009 (Confirmshaming 用語の検出)** [FIXABLE]:
  CHK-001 の詳細 check。CTA／opt-out 近傍に以下の confirmshaming
  表現が使われていない：
  - 「いいえ、健康は気にしません」「No thanks, I hate saving money」
  - 「私には賢くなる必要はありません」「後で後悔します」
  - 読者を小馬鹿にする／罪悪感を煽る opt-out ラベル
  短文案単体では該当せずとも、CTA セットに含まれる場合 evaluate 対象。
  該当なし（CTA ／ opt-out を含まない文案）は `N/A`。
  **Grounded in**: `../standards/persuasion-ethics.md` §Dark Pattern
  反模式清單 §Confirmshaming。
- [ ] **CHK-CTW-ETH-010 (Agitation 段階 — 煽りの合理範囲)** [FIXABLE]:
  PASONA 系列 Agitation 段 or 短文案「恐怖／痛点」切入点において、
  煽りが合理範囲内：
  - **fear-mongering に推し進めていない**（小霜 2014 の反 PASONA
    論点参照）
  - 健康／医療／金融／保険など専門性高い分野で不安商法化していない
  - 読者の**真実な不利益**を指摘するに留まり、**捏造された恐怖**
    で置換していない
  煽り過度（FATAL 級）は CHK-003 or 004 の優良誤認／有利誤認と
  併発する傾向。単体の tone 問題 → FIXABLE。該当なし（Agitation
  不使用／恐怖切入点不使用）は `N/A`。**Grounded in**:
  `../standards/persuasion-ethics.md` §Anti-Patterns（PASONA
  Agitation 段を fear-mongering に）+ §小霜和也「嘘をつかない」原則。

## Verdict Rules

- 任意 **1 項**が `FAIL_FATAL` → `NEEDS_REVISION`（user へ escalate）
- `FAIL_FIXABLE` のみ（FATAL なし）で **≤ 2 項** → `PASS_WITH_NOTES`
  （auto-revise trigger）
- `FAIL_FIXABLE` が **≥ 3 項** → `NEEDS_REVISION`
- 全項目 `PASS` or `N/A` → `PASS`
- `N/A` 使用条件：該当要素が artifact に存在しない場合のみ
  （testimonial 不含、CTA 不含、Agitation 不含 等）。該当要素が
  あって未遵守は `N/A` ではなく `FAIL_*`。

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "items": [
    {
      "id": "CHK-CTW-ETH-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "note": "Specific evidence (quoted line or artifact ref) + fix instruction if FIXABLE",
      "legal_surface": "景品表示法 §5-1 | 景品表示法 §5-2 | FTC §255 | ステマ告示 | (none — 倫理のみ)"
    }
  ],
  "summary": "1-3 sentence overall assessment + 法律 vs 倫理 breakdown"
}
```
