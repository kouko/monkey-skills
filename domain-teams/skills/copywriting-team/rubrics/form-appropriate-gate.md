# Rubric: Form-Appropriate Gate

SHOULD gate (qualitative flag-based). Triggers: 文案 artifact 已完成
(長／中／短 いずれか)。evaluator は artifact の form type を最初に
判定し、form に該当する dimension set のみを評価する。

## Scope Boundary

本 gate が review する：
- **長文案** (PASONA 系列)：段階間 flow、離脱防止設計、字數比例、
  PASBECONA 中段 (B/E/C) 説得厚
- **中文案** (BEAF)：Benefit-first 明確度、Evidence 具体性、Advantage
  対比清晰度
- **短文案** (キャッチコピー)：3 秒 land 能力、7-15 字紀律、掛詞／
  音韻技法、5 種切入点明確性

本 gate が review しない：
- Framework 段階存在／順序（binary pass/fail）→ `../checklists/persuasion-framework-adherence-checklist.md`
- Voice / Tone 一貫性 → `voice-consistency-gate.md`
- 倫理／法律邊界 → `../checklists/ethics-checklist.md`

本 gate は**構造違反の有無**（checklist 担当）ではなく**構造が適切
レベルで執行されているか**の質的評価を担う。

## Primary Sources

- `../standards/long-form-pasona-canon.md` — 字數比例経験則 (旧 PASONA
  P:A:So:N:A ≒ 2:2:3:2:1、PASBECONA P:A:S:B:E:C:O:N:A ≒
  1:1:1:1:2:2:1:0.5:0.5) + 段階間 flow 設計原則（離脱点明示）+
  B/E/C 挿入の論理（抽象→客観→具体）+ Affinity 厚さ基準。
- `../standards/mid-form-beaf-canon.md` — Benefit-first 順序 canonical
  根拠 + Evidence の客観情報要件 + Advantage の具体的比較要件。
- `../standards/short-form-catchcopy-canon.md` — 3 秒ルール推奨構造
  + 7-15 字黃金範囲 + 掛詞／音韻技法（眞木準 canonical）+ 5 種切入点。
- grounding SSOT: `../research/grounding-v4.12.0.md` §2-3 + §8
  Load-bearing claims（PASONA 字數 / BEAF 順序 / 7-15 字 実測）。

## Form Type 判定 (evaluator first step)

1. artifact 字數／媒体／宣言 framework を確認
2. form_type = **long** / **mid** / **short** を決定
3. 該当 form の dimension set のみ評価、他 form の dimension は
   `not_applicable`

---

## Dimensions — Long 文案 (PASONA 系列)

### RUB-CTW-FA-L1: Flow / Progression

段階間 transition が平滑か。接続詞／小見出し／問いかけで「次段への
橋渡し」が明示されているか。

- 🔴 **Fatal**：段間に跳躍感。Affinity の共感から Solution へ飛ぶ
  際に「私も同じでした → 実は解決法があります」のような突飛な転換。
  特に PASBECONA の B→E 境界（期待を証拠で受ける）と C→O 境界
  （具体から提案へ）の transition が欠落。読者の認知慣性を切断。
- 🟡 **Warning**：全体としては flow するが 1-2 段間で断層感
  （接続詞なしの唐突な場面転換、小見出しの論理不整合）。
- 🟢 **Clear**：全段間 transition が自然。接続詞／問いかけ／小見出し
  が論理的に次段を予告する。

### RUB-CTW-FA-L2: 離脱防止設計

長文では段末で読者が離脱しやすい。各段末に「次段を読ませる仕掛け」
が設計されているか。

- 🔴 **Fatal**：離脱防止設計ゼロ。段末が全て「事実の羅列」で終わり、
  次段を読む動機がない。特に中盤 (Solution / Benefit / Evidence) で
  読者を引き付ける仕掛けがなく、離脱率が高いと推定される。
- 🟡 **Warning**：部分的に設計あり。冒頭 (Problem/Affinity) と末尾
  (Action) 付近は工夫あるが、中盤段階 (Solution/Benefit/Evidence) で
  段末フックが弱い。
- 🟢 **Clear**：全段末に「続きを読ませる」仕掛け（未解決の問い、
  小さい驚き、次段への予告、意外性のある接続）が設計されている。

### RUB-CTW-FA-L3: 字數比例

`long-form-pasona-canon.md` §段階間 flow 設計原則の canonical 比例
目安に沿っているか。
- 旧 PASONA: P:A:So:N:A ≒ 2:2:3:2:1
- PASBECONA (5,000 字): P:A:S:B:E:C:O:N:A ≒ 1:1:1:1:2:2:1:0.5:0.5
- 要旨：**Problem+Affinity 20-30% / Solution+Offer 40-50% / Narrow+Action 10-20%**
  （PASBECONA では Evidence + Contents が中段 40-50% を占める）

- 🔴 **Fatal**：比例から嚴重偏離。例：Problem+Affinity が 50% 以上
  （読者は疲労）、Evidence が 5% 以下（PASBECONA で説得薄）、
  Narrow+Action が 40% 以上（推銷臭）。
- 🟡 **Warning**：小偏（±10% 以内）。canonical 比例を意識した構造
  だが 1-2 段の分量が理想からずれる。
- 🟢 **Clear**：canonical 比例に沿う。または意図的逸脱が artifact
  メタ情報に justification と共に明示されている。

### RUB-CTW-FA-L4: PASBECONA 中段 B/E/C 説得厚

PASBECONA artifact のみ適用。B (Benefit) / E (Evidence) / C (Contents)
は PASBECONA が新 PASONA に追加した 3 段であり、ここの説得厚こそが
長文優位性の源泉。

- 🔴 **Fatal**：B/E/C が空洞。Benefit が抽象的な「人生が変わります」
  で具体像なし、Evidence が「多くの方に愛用」で客観数値／第三者証言
  なし、Contents が商品名の繰り返しで構成要素／使用方法／同梱物が
  不明。
- 🟡 **Warning**：3 段のうち 1 段が薄い。例：Benefit は鮮明だが
  Evidence が数値 1 件のみ、Contents が構成要素列挙だけで使用方法
  なし。
- 🟢 **Clear**：B (抽象的未来像) → E (客観的裏付け 3 種以上：権威／
  実績／顧客の声) → C (構成要素 + 使い方 + 同梱物 + サポート) の
  全段が厚く、読者の「本当か？」「具体的には何か？」に先回り回答。
- **Note**：新 PASONA (6 段) / 旧 PASONA (5 段) artifact ではこの
  dimension は `not_applicable`。

---

## Dimensions — Mid 文案 (BEAF)

### RUB-CTW-FA-M1: Benefit-first 明確度

第一段／第一文が純粋に Benefit か、Feature 混入していないか。

- 🔴 **Fatal**：Feature 先出し（「容量 500ml、原材料は〇〇」等）。
  BEAF canonical 順序の逆転で、商品ページのスキャン読みで離脱誘発。
  FAB 順序（F→A→B）になっている。
- 🟡 **Warning**：第一段が Benefit ベースだが Feature も混在
  （「〇〇な方に、容量 500ml の〇〇」）。純 Benefit ではない。
- 🟢 **Clear**：第一段が完全 Benefit（「成った姿」「読者の生活の
  変化」）。Feature への言及なし。例：「通勤バッグに入れて 1 日分
  の水分が賄える」。

### RUB-CTW-FA-M2: Evidence 具体性

Evidence 段が検証可能な客観情報で構成されているか。

- 🔴 **Fatal**：空話のみ。「多くの方に愛用」「話題沸騰中」「選ばれ
  ています」等、検証不能な主観的曖昧表現しかない。客観数値／受賞
  歴／第三者評価ゼロ。
- 🟡 **Warning**：模糊。数値はあるが出典不明（「95% が満足」と記述
  されているがサンプル数／調査機関の明示なし）、または受賞歴が
  あるが年度／主催者が不明。
- 🟢 **Clear**：具体数字 + 出典。例：「レビュー 4.8/5.0 (2,341 件
  / 楽天市場)」「〇〇賞 2024 受賞（主催：〇〇協会）」「臨床試験で
  保湿率 35% 改善（n=120、〇〇大学 2023）」。検証可能。

### RUB-CTW-FA-M3: Advantage 対比清晰

Advantage 段が競合商品との具体的差異を提示しているか。

- 🔴 **Fatal**：Advantage 欠落 or 意味のない形容詞のみ（「高品質」
  「最高」「業界トップクラス」）。競合比較ゼロ。
- 🟡 **Warning**：含糊な比較。「他社製品より優れた〇〇」等の主語不
  明比較、または比較軸が 1 つだけで読者が差異を理解しづらい。
- 🟢 **Clear**：具体的差異。比較軸 + 数値 + 独自技術／認証の組合せ。
  例：「他社比 2 倍の吸水性（〇〇協会試験 2024）」「業界唯一の〇〇
  特許技術」。

---

## Dimensions — Short 文案 (キャッチコピー)

### RUB-CTW-FA-S1: 3 秒 land 能力

3 秒ルール（1 秒目：興味喚起、2 秒目：主訊息、3 秒目：行動誘発）を
満たすか。第一眼で注意を掴めるか。

- 🔴 **Fatal**：読み返さないと意味が取れない。抽象度が極端に高く、
  ターゲットが「自分事」と認識するまで数秒以上必要。SNS 時代の
  1-3 秒判断で確実に離脱。
- 🟡 **Warning**：勉強すれば意味が取れるが、初見で「?」が残る。
  意図的曖昧性（糸井式）の意図はあるが、ターゲット受眾の解釈能力を
  過大評価している。
- 🟢 **Clear**：第一眼で「これは何で、自分に関係あるか」が判別可能。
  意図的曖昧性を使っている場合でも、曖昧さが魅力として機能し離脱
  させない。

### RUB-CTW-FA-S2: 7-15 字紀律

`short-form-catchcopy-canon.md` §7-15 字 黃金範囲。

- 🔴 **Fatal**：5 字未満 or 20 字超。5 字未満はコピー情報量不足、
  20 字超は「キャッチコピー」ではなくリード文／副題／ボディコピー
  に分類すべき対象。
- 🟡 **Warning**：5-6 字 or 16-19 字。境界範囲で、justification
  （「商品名だけで機能する短語」「複雑商材のため 1 字追加」等）の
  明示が望ましい。
- 🟢 **Clear**：7-15 字。糸井 7 / 岩崎 12-14 / 眞木 10 / Yahoo
  トピック 13 の実測値帯域。
- **Note**：checklist 側 (CHK-CTW-PFA-006) とは異なり本 dimension は
  「範囲内であっても余韻／読みやすさを満たすか」の質的評価を含む。

### RUB-CTW-FA-S3: 掛詞 / 音韻技法辨識

眞木準系（掛詞・音韻）または岩崎系（季節感・韻律）の技法を宣言
している場合、その技法が効果的に機能しているか。技法宣言なし
artifact では `not_applicable`。

- 🔴 **Fatal**：技法宣言ありだが効果なし。「でっかいどぉ／北海道」
  のような音韻リピート＋掛詞 を意図しているが、実際は無理やりな
  駄洒落 or 音韻一致が弱く「ダジャレ寄り」になっている（眞木準の
  「ダジャレではなく、オシャレ」原則違反）。
- 🟡 **Warning**：技法としては成立するが普通の印象。リズムは良いが
  意外性が少ない、掛詞は成立するが意味の二重性が弱い。
- 🟢 **Clear**：巧妙。音韻が滑らかで、掛詞の二重意味が読者に新鮮な
  発見をもたらす。TCC 年鑑級の canonical 風格。
- **Note**：掛詞／音韻技法を宣言していない artifact では `not_applicable`。

### RUB-CTW-FA-S4: 5 種切入点明確性

採用 approach（利益／願望、恐怖／痛点、顛覆常識、目標呼喚、提問互動）
が成品で可辨か。

- 🔴 **Fatal**：含糊。採用 approach が成品から読み取れず、「なんと
  なく良さげ」で切入点が定まっていない。谷山「なんかいいよね禁止」
  違反と併発傾向。
- 🟡 **Warning**：部分的に可辨。採用 approach は推測可能だが、切入点
  の執行が中途半端（「顛覆常識」なのに常識転覆の punch が弱い、
  「提問互動」なのに読者が答える誘因が弱い、等）。
- 🟢 **Clear**：採用 approach が成品の構文／語彙／話法で即座に判別
  可能。切入点選擇と執行が整合。

---

## Verdict Rules

- 任意 1 🔴 fatal → `NEEDS_REVISION`（user へ escalate）
- 🟡 warning **2 個以上** → `NEEDS_REVISION`
- 🟡 warning **1 個**（🔴 なし）→ `PASS_WITH_NOTES`（auto-revise trigger）
- 全 🟢 clear → `PASS`
- `not_applicable` dimension（form 非該当 or 技法宣言なし）は verdict
  計算から除外。

## Rules

- form_type 判定を最初に完了させる。誤判定（例：PASBECONA artifact を
  mid と判定）は評価全体を無効化する。
- checklist との責任分担を守る：構造存在／順序の binary は checklist
  側、構造の**質的執行度**が本 rubric の仕事。
- NEEDS_REVISION 時は代替案（"こう改善すれば 🟢" 例）を 1 つ以上提示。
- 7-15 字紀律（S2）で境界帯（5-6 字 / 16-19 字）を評価する際、文案
  単体の質を見る（字数違反単独で 🔴 にしない。5 字未満・20 字超で
  初めて 🔴）。

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short",
  "framework_declared": "旧 PASONA | 新 PASONA | PASBECONA | BEAF | AIDMA-short",
  "dimensions": [
    {
      "id": "RUB-CTW-FA-L1",
      "name": "Flow / Progression",
      "flag": "red | yellow | green | not_applicable",
      "evidence": "Specific quoted passage + analysis",
      "suggestion": "If red/yellow, 具体改善案"
    }
  ],
  "summary": "1-3 sentence overall assessment + next-step priority"
}
```
