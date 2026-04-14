# Checklist: Persuasion Framework Adherence

MUST gate (binary pass/fail). Triggers: 文案 artifact 已完成 (長／中／短
いずれか)。evaluator は artifact の form type を最初に判定し、
form に該当する項目のみ評価する（非該当項目は `N/A`）。

## Primary Sources

- `../standards/long-form-pasona-canon.md` — 旧 PASONA (5) / 新 PASONA
  (6) / PASBECONA (9) の段階定義、順序、字數比例、Affinity 厚さ基準。
- `../standards/mid-form-beaf-canon.md` — BEAF (Benefit → Evidence →
  Advantage → Feature) の順序、Benefit-first の canonical 根拠、
  FAB との順序逆転注意。
- `../standards/short-form-catchcopy-canon.md` — 7-15 字黃金範囲、
  AIDMA 短版 (A+I 専用)、5 種切入点決策樹 (利益／恐怖／顛覆／呼喚／提問)。
- `../standards/ideation-taniyama-discipline.md` — 「なんかいいよね
  禁止」3 項具体理由ルール、描写 vs 解決 分界。
- grounding SSOT: `../research/grounding-v4.12.0.md` §2 Cluster A /
  §3 Cluster B。

## Form Type 判定 (evaluator first step)

1. artifact 字數と媒体を確認
   - 1,500 字以上 → **long**（PASONA 系列）
   - 数十〜数百字、商品ページ／POP／カタログ → **mid**（BEAF）
   - 7–20 字、headline／キャッチ → **short**（AIDMA 短版）
2. `form_type` を出力 JSON に記述
3. 該当 form の項目のみ PASS/FAIL 判定、他 form の項目は `N/A`

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's
output. Give `PASS`, `FAIL_FATAL`, `FAIL_FIXABLE`, or `N/A` for each
item, with specific evidence (quoted line or paragraph reference).
Failure type for each item is defined below — use the type specified.

## Checklist — Long 文案 (PASONA 系列)

- [ ] **CHK-CTW-PFA-001 (PASONA 段階完整性)** [FATAL]: artifact が
  宣言した framework（旧 PASONA / 新 PASONA / PASBECONA）の全段階が
  存在する。
  - 旧 PASONA: **P / A (Agitation) / So / N / A** 5 段
  - 新 PASONA: **P / A (Affinity) / S / O / N / A** 6 段
  - PASBECONA: **P / A (Affinity) / S / B / E / C / O / N / A** 9 段
  段階が 1 つでも欠落 → FATAL。段階の存在は小見出し／段落トピックで
  判別する。**Grounded in**: `../standards/long-form-pasona-canon.md`
  §旧/新 PASONA/PASBECONA 定義表。
- [ ] **CHK-CTW-PFA-002 (段階順序正確)** [FIXABLE]: 段階の出現順序が
  canonical 順序と一致する。特に以下の禁止順序を check：
  - Offer が Solution より前（新 / PASBECONA）
  - Contents が Benefit より前（PASBECONA — 抽象→客観→具体の逆転）
  - Evidence が Benefit より前（PASBECONA — B/E/C 挿入論理違反）
  - Action が Narrow down より前（緊急性が失われる）
  順序違反が 1 箇所 → FIXABLE。2 箇所以上 → FATAL。**Grounded in**:
  `../standards/long-form-pasona-canon.md` §段階間 flow 設計原則 +
  §Anti-Patterns。
- [ ] **CHK-CTW-PFA-009 (Affinity 厚さ — 新 / PASBECONA のみ)**
  [FIXABLE]: 新 PASONA / PASBECONA で Affinity 段の分量が Problem
  段と同等以上である。薄い Affinity（1-2 文のみ、Problem の 1/3 以下）
  は「共感風の台詞」化し canonical 違反。**Grounded in**:
  `../standards/long-form-pasona-canon.md` §段階間 flow 設計原則。

## Checklist — Mid 文案 (BEAF)

- [ ] **CHK-CTW-PFA-003 (BEAF Benefit-first)** [FATAL]: 第一段／
  第一文が Benefit（読者の生活がどう良くなるか、成った姿）であり、
  Feature（スペック）／Advantage（競合比較）ではない。Feature 冒頭
  は BEAF canonical の逆順（FAB 順序）であり FATAL。「500ml / 原材料」
  等のスペック羅列が冒頭に来る場合 → FATAL。**Grounded in**:
  `../standards/mid-form-beaf-canon.md` §順序の canonical 性 +
  §Benefit-first 順序の重要性。
- [ ] **CHK-CTW-PFA-004 (Evidence 具体性)** [FIXABLE]: Evidence 段
  が存在し、かつ**具体**である。以下は不合格：
  - 「多くの方に愛用されています」「話題沸騰中」等の主観的曖昧
    表現のみ
  - 「高品質」「最高」等の形容詞のみで数値／受賞／顧客数／レビュー
    点数など客観情報なし
  - 「お客様の声」と表記しながら具体的な引用／氏名イニシャル／数値
    なし
  合格例：「レビュー 4.8/5.0 (2,341 件)」「〇〇賞 2024 受賞」
  「臨床試験で保湿率 35% 改善」。**Grounded in**:
  `../standards/mid-form-beaf-canon.md` §BEAF 4 段階定義表 +
  §Anti-Patterns（Evidence 段省略）。

## Checklist — Short 文案 (キャッチコピー)

- [ ] **CHK-CTW-PFA-005 (5 種切入点明確選択)** [FIXABLE]: artifact
  メタ情報 or 候補説明に、5 種のうちどの切入点を採用したかが明示
  されている：**利益／願望 / 恐怖／痛点 / 顛覆常識 / 目標呼喚 /
  提問互動**。不明示または「なんとなく」は FIXABLE。切入点 は成品
  から読み取れる必要がある（例：「このままで大丈夫？」= 恐怖／痛点）。
  **Grounded in**: `../standards/short-form-catchcopy-canon.md`
  §5 種切入点決策樹。
- [ ] **CHK-CTW-PFA-006 (7-15 字紀律)** [FIXABLE]: キャッチコピー
  本体が 7-15 字の黃金範囲内である。
  - 7-15 字以内 → PASS
  - 5-6 字 or 16-20 字で合理的 notes あり → FIXABLE (notes 必須)
  - 5 字未満 or 20 字超 → FATAL（「キャッチコピー」ではなく
    リード文／副題／ボディコピーに分類すべき）
  **Grounded in**: `../standards/short-form-catchcopy-canon.md`
  §7-15 字 黃金範囲 + §Anti-Patterns（15 字超を「キャッチコピー」
  と呼ぶ）。
- [ ] **CHK-CTW-PFA-007 (AIDMA 短版 A+I 専用)** [FIXABLE]: キャッチ
  コピー単体で Desire/Memory/Action まで担おうとしていない。以下は
  FIXABLE：
  - 短文内に具体的 CTA（「今すぐ電話！」「クリック」「申込」）を
    含む（D/A を無理に担当）
  - 価格／保証／期限を短文内に圧縮（Offer/Narrow down を混入）
  短文案は A (Attention) + I (Interest) 専用、D/M/A は body copy /
  CTA / repetition が担う分業設計が canon。**Grounded in**:
  `../standards/short-form-catchcopy-canon.md` §AIDMA 短文案作用域。

## Checklist — 全 form type 共通

- [ ] **CHK-CTW-PFA-008 (なんかいいよね禁止 — 3 項具体理由)** [FIXABLE]:
  artifact に候補複数が含まれる場合、各候補に「なぜ良いか」3 項の
  具体理由が付記されている。要件：
  1. **何が読者に何を伝えるか** — 具体的な伝達内容
  2. **既存類似コピーに対する新しさ** — 差別化ポイント
  3. **ターゲットの生活／文脈での共鳴** — 具体的場面
  3 項全て具体化できていない候補は谷山「なんかいいよね」に該当し
  FIXABLE。また「描写型」（「〇〇は△△です」で終わる商品特性の
  言い換えのみ）で解決／意味提示まで届いていない候補も FIXABLE。
  **Grounded in**: `../standards/ideation-taniyama-discipline.md`
  §「なんかいいよね禁止」ルール + §描写 vs 解決。
- [ ] **CHK-CTW-PFA-010 (framework 宣言)** [FIXABLE]: artifact メタ
  情報に採用 framework 名（旧 PASONA / 新 PASONA / PASBECONA /
  BEAF / AIDMA-short）が明示されている。宣言なし → FIXABLE
  （evaluator が form type を判定するには宣言が必要）。
  **Grounded in**: `../standards/long-form-pasona-canon.md` §三框架
  の適用表 + `../standards/mid-form-beaf-canon.md` §字數範囲と適用
  用例 + `../standards/short-form-catchcopy-canon.md` §7-15 字 黃金範囲。

## Verdict Rules

- 任意 **1 項**が `FAIL_FATAL` → `NEEDS_REVISION`（user へ escalate）
- `FAIL_FIXABLE` のみ（FATAL なし）で **≤ 2 項** → `PASS_WITH_NOTES`
  （auto-revise trigger）
- `FAIL_FIXABLE` が **≥ 3 項** → `NEEDS_REVISION`
- 全項目 `PASS` or `N/A` → `PASS`
- `N/A` は form type 非該当の項目に限る（long artifact の CHK-003〜007
  は `N/A`、mid artifact の 001/002/009/005/006/007 は `N/A` など）。
  CHK-008 および CHK-010 は全 form で評価対象。

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short",
  "framework_declared": "旧 PASONA | 新 PASONA | PASBECONA | BEAF | AIDMA-short | unknown",
  "items": [
    {
      "id": "CHK-CTW-PFA-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "note": "Specific evidence (quoted line or paragraph ref) + fix instruction if FIXABLE"
    }
  ],
  "summary": "1-3 sentence overall assessment"
}
```
