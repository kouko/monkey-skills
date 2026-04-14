# Rubric: Voice Consistency Gate

SHOULD gate (qualitative flag-based). Triggers: 跨多段 / 多文案
artifact（複数段・複数候補・series 含む）。単一段・単一短文のみの
artifact では triggers 不満足で gate skip（reason: 跨段評価不能）。

## Scope Boundary

本 gate が review する：
- Voice（跨情境で固定の品牌人格）の stability 跨 artifact 段／候補
- Tone（情境敏感の語氣）の 情境適切性
- Voice 巨匠 reference（糸井／岩崎／眞木／谷山）採用時の風格忠実度
- JP 情緒共鳴 vs Anglo benefit-clear の**選擇の明確性**（対目標受眾）

本 gate が review しない：
- Framework 構造（PASONA 段階順序・BEAF 順序）→ `../checklists/persuasion-framework-adherence-checklist.md`
- 倫理／法律邊界 → `../checklists/ethics-checklist.md`
- 字数紀律 → `form-appropriate-gate.md`

## Primary Sources

- `../standards/voice-and-tone.md` — Ogilvy 1963/1983 + 糸井／岩崎
  JP 情緒傳統 + 18F / Mailchimp Voice 4 軸 + Mailchimp "one voice,
  multiple tones" + Tone 情境切換表（onboarding / error / crisis /
  celebration）。
- `../standards/short-form-catchcopy-canon.md` — 四位 voice 巨匠
  (糸井／岩崎／眞木／谷山) の canonical voice definition。
- grounding SSOT: `../research/grounding-v4.12.0.md` §3 Cluster B.3-B.8
  + §8 Load-bearing claims。

## Dimensions

### Dimension 1: Brand Voice 固定性 (RUB-CTW-VC-001)

跨多段 / 多候補で voice が stable な persona を維持しているか。
Mailchimp 原則：「Voice doesn't change much from day to day」。

- 🔴 **Fatal**：段／候補ごとに人格が別人化（例：1 段目は casual
  friend 口調、3 段目は corporate formal、5 段目は irreverent
  joker）。voice guide が SSOT として機能しておらず、拼湊感を
  読者に与える。
- 🟡 **Warning**：大枠 voice は維持されているが、2-3 箇所で漂移
  （例：Formality 軸で 1 段だけ極端に formal 化、Enthusiasm 軸で
  1 段だけ matter-of-fact 化）。漂移の意図が artifact メタ情報に
  説明されていない。
- 🟢 **Clear**：全段／全候補で voice 4 軸（Formality / Seriousness
  / Respectfulness / Enthusiasm）の position が一貫。例文対比で
  「同じ品牌が書いている」と読める。漂移があっても意図的 tone 調整
  として明示されている。

### Dimension 2: Tone 情境適切性 (RUB-CTW-VC-002)

Mailchimp Tone 情境切換表（onboarding / error / crisis / celebration）
に照らし、情境別 tone が適切か。Voice は不変、Tone は変化する
（Mailchimp canonical）。

- 🔴 **Fatal**：情境錯配。Crisis 状態で celebration tone（明るい
  感嘆符、絵文字、祝祭感）、error state で playful ジョーク、
  onboarding で突然推銷モード切換、など**情境を読み違えた tone**。
  読者の trust を損なう。
- 🟡 **Warning**：情境に対し tone が部分的に合っているが、調整幅が
  不十分（例：onboarding 全体が「enthusiastic welcome」一辺倒で、
  最終段の「次のアクション誘導」で tone の段階変化なし）。または
  crisis-adjacent な情境（incident / API outage 通知）で tone が
  「serious」すぎて voice まで切り替わっている懸念。
- 🟢 **Clear**：全情境で voice を維持しつつ tone が各情境に適切
  調整。特に crisis / error state で「誠実＋不 推諉」、celebration
  で「user を主語にした感謝」、onboarding で「熱情＋擁抱」、が
  明示的に設計されている。

### Dimension 3: Voice 巨匠 Reference 忠実度 (RUB-CTW-VC-003)

artifact メタ情報 or 入力ブリーフで voice 巨匠 (糸井重里 / 岩崎俊一
/ 眞木準 / 谷山雅計) を reference voice として宣言した場合、成品が
該当巨匠の canonical 風格に忠実か。

- 🔴 **Fatal**：名義引用（「糸井風」「岩崎風」を宣言）したが成品は
  風格背離。例：
  - 「糸井風」宣言 → 命令形 CTA 連発（糸井は状態提案型、行動促進型
    ではない）
  - 「岩崎風」宣言 → 仏教無常観も季節感も皆無の promotional 推銷文
  - 「眞木風」宣言 → 掛詞／音韻技法ゼロの literal 直訳コピー
  - 「谷山風」宣言 → 描写型コピーで「解決／新しい意味提示」なし
- 🟡 **Warning**：巨匠 voice の一部要素は捕捉しているが、全体として
  風格「部分神似」に留まる。例：糸井の生活語彙は使えているが曖昧
  性許容が弱い／岩崎の字数帯（10-15 字）は合っているが有限性／
  無常観の情緒が薄い。
- 🟢 **Clear**：巨匠 voice の canonical 特徴（糸井＝状態提案／曖昧
  余地、岩崎＝季節感／有限性／仏教無常観、眞木＝掛詞／音韻、谷山＝
  解決／意味提示）が成品に明確に現れ、巨匠作品と並べて違和感のない
  レベル。
- **Note**：巨匠 reference を宣言していない artifact ではこの dimension
  は `not_applicable`（🟡 ／ 🔴 付与しない）。

### Dimension 4: JP 情緒共鳴 vs Anglo benefit-clear の選擇明確性 (RUB-CTW-VC-004)

対象受眾（JP 市場 / Anglo 市場 / global bilingual）に対して、voice
tradition を clear に選擇しているか。`voice-and-tone.md` の Anti-Pattern
「JP 情緒 voice と Anglo action-oriented voice の直譯転植」を防止する。

- 🔴 **Fatal**：tradition 錯套。JP 市場向け artifact で Anglo
  "Just Do It" 式の直球 CTA + 形容詞 hype 一辺倒（情緒共鳴／余韻／
  掛詞ゼロ）。または逆に、Anglo 市場向け artifact で過度に曖昧／
  余韻志向の「翻訳調」コピー（benefit が読者に直接届かない）。
  ターゲット受眾に合わない tradition の強制適用。
- 🟡 **Warning**：tradition の選擇が artifact メタ情報で明示されて
  おらず、成品からも判別曖昧。例：JP market 向けだが 3 割が Anglo
  直球調、7 割が JP 情緒調の混在で、意図的 hybrid か偶然の不整合か
  読めない。または明示されているが実行が中途半端。
- 🟢 **Clear**：tradition が artifact メタ情報に明示 (例：「JP 情緒
  共鳴路線 / 糸井＋岩崎系を主軸」「Anglo benefit-clear 路線 / Ogilvy
  long-form」) + 成品全体でそれが一貫執行されている。Hybrid の場合
  は hybrid の意図と配分が明示されている。

## Verdict Rules

- 任意 1 🔴 fatal → `NEEDS_REVISION`（user へ escalate）
- 🟡 warning **2 個以上** → `NEEDS_REVISION`
- 🟡 warning **1 個**（🔴 なし）→ `PASS_WITH_NOTES`（auto-revise trigger）
- 全 🟢 clear → `PASS`
- Dimension 3（巨匠 reference）は宣言なし artifact で `not_applicable`。
  `not_applicable` は verdict 計算から除外（🔴 🟡 🟢 いずれにも count
  しない）。

## Rules

- Voice guide SSOT の存否を最初に確認。brand voice guide（4 軸 + side-by-side
  examples）が artifact 入力に含まれない場合、dimension 1/2 は「推定
  voice」で評価し `note` に「voice guide 未提供、成品から推定」を記載。
- 巨匠 reference を「nominal only」で宣言する誘惑に対し厳格に。名義
  引用は canonical 忠実度で判定されるべき。
- Tone 変化を voice 変化と誤認しない。voice 不変・tone 可変が canon。
- Gatekeeper にならない。PASS_WITH_NOTES で revision spec を具体化し、
  NEEDS_REVISION でも代替案（"こう書き直せば 🟢 になる" 例）を 1 つ
  以上提示する。

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "dimensions": [
    {
      "id": "RUB-CTW-VC-001",
      "name": "Brand Voice 固定性",
      "flag": "red | yellow | green | not_applicable",
      "evidence": "Specific quoted examples showing drift / stability",
      "suggestion": "If red/yellow, 具体改善案"
    }
  ],
  "voice_guide_provided": true,
  "maestro_reference_declared": "糸井 | 岩崎 | 眞木 | 谷山 | none",
  "target_tradition": "JP-emotional | Anglo-benefit-clear | hybrid | unclear",
  "summary": "1-3 sentence overall assessment + next-step priority"
}
```
