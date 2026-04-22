# Brief 4 Run — Weak-pool risk (ja Q4-Q3 edge, 医療 + 温かい)

**Run date**: 2026-04-22
**Instrumentation version**: v1.12.1
**Failure mode under test**: weak-pool-best-available

## Input envelope

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "long-form-extended",
  "brief": {
    "product": "心拍マモリ — 家庭用自動血圧計 (70代+ 独居向け)",
    "audience": "70+ 独居高齢者 + 説明者としての家族",
    "goal": "製品の信頼性 + 導入ハードル低減",
    "voice_reference": null,
    "output_language": "ja",
    "tone_cue": "正確で信頼できる、でも温かい (冷たくない)",
    "channel": "製品パンフレット",
    "form_hint": "long-form sales"
  },
  "message_thesis": "医療機器は正確でなくてはならないが、毎日触る道具でもある",
  "voice_quadrant": {
    "primary": "Q4",
    "edge": "Q4-Q3",
    "position": "toward-Q3",
    "schwartz_alignment": "ok",
    "rationale": "医療 Authority × Reason base (Q4) + 温かい cue pulls toward Q3 (Affinity × Emotion) — Q4-Q3 edge; position: toward-Q3"
  }
}
```

**Phase 4 draft**:
```
[Opening]
家族が心配するから、置いてみようか。
そう思って買った血圧計が、毎朝少し重たかった経験はありませんか。

[Body]
心拍マモリは、医療機関と同じ測定精度を保ちながら、
家庭で毎日使うために設計されました。
ボタンは 3 つ。画面の文字は 18pt。
正しく測ること、それ自体が負担になってはいけない。

[Specification inline]
医療機器認証番号: XXXXX
測定精度: 収縮期血圧 ±3mmHg

[Close]
「正しい」を、家の道具に。
```

---

## Pass 3 branch taken

**Pass 3d — Register Signal (Q4-Q3 edge)**

- `voice_reference` = null → not a craft-gate trigger
- `voice_quadrant.position` = `toward-Q3` → not axis-*
- Default branch: Tier 2 Register Signal

**Files loaded**:
- `standards/voice-anchor-meta-core.md` (schema + rubric + mitigation)
- `standards/jp-q4-anchors.md` §Landmark: toward-Q3 (primary quadrant Q4)
- `standards/jp-q3-anchors.md` §Landmark: toward-Q4 (cross-landmark read per Q4-Q3 edge instruction)

**Cross-landmark read justification**: brief specifies `edge: Q4-Q3`, `position: toward-Q3`. This means the anchor sits at Q4 base but leans toward Q3. Protocol requires loading both Q4 router §toward-Q3 AND Q3 router §toward-Q4 to cover the edge from both sides.

---

### Anchor pool loaded

**From jp-q4-anchors.md §Landmark: toward-Q3**:
- 青木耕平 / 北欧、暮らしの道具店 (`jp-kurashicom-aoki-kohei-lifestyle-narrative`) — Q4 center (actually labeled landmark: toward-Q3 in anchor file). Over-mimic: MEDIUM. Form: mid-form, long-form.

Note: §Landmark: toward-Q3 in jp-q4-anchors.md is empty of individual anchors — only a cross-reference note to 北欧、暮らしの道具店 Q3 warmth layer. The single named anchor (青木耕平) sits at §Landmark: center with internal position labeled "toward-Q3". No distinct toward-Q3 entry exists in Q4 router.

**From jp-q3-anchors.md §Landmark: toward-Q4**:
- 松浦弥太郎 `jp-matsuura-yataro-teinei-essay` — Q3 toward-Q4. Over-mimic: HIGH. Form: short-form, mid-form-essay.

**Additional candidates surfaced from Q3 §center (adjacent)**:
- 岩崎俊一 `jp-iwasaki-shunichi-yoyu-mujou` — Q3 center, craft-gate master. Mentioned in brief as candidate. Over-mimic: MEDIUM. Form: short-form-catchcopy, mid-form-brand-tagline.

**Total pool size for this edge**: 3 candidates.

---

### Top-3 candidates ranked

**Rank 1: 青木耕平 / 北欧、暮らしの道具店** (`jp-kurashicom-aoki-kohei-lifestyle-narrative`)
- fit_score: LOW-MEDIUM
- fit_reasoning: This anchor sits at Q4 toward-Q3 which matches the quadrant position. Form pairs include long-form. The register mechanic — embedding product specs as an afterthought in lived-scene narrative — structurally maps onto the thesis "medical device that is also a daily-use object." The 私一人称 + 生活情景冒頭 + 形容詞禁 discipline combats the Phase 4 draft's risk of becoming cold spec-speak. However, the anchor's native register is lifestyle/home goods (北欧 雑貨, リネン, キャセロール) and its implied reader is a 30-40s urban woman interested in Scandinavian living aesthetics. Transposing to 70+ 独居高齢者 + 家族 is a significant audience gap. The "手紙を友人に書く" intimacy mechanic also risks being condescending when the audience is elderly (not a peer relationship). This is the best structural fit in the pool but not a clean match.

**Rank 2: 松浦弥太郎** (`jp-matsuura-yataro-teinei-essay`)
- fit_score: LOW
- fit_reasoning: Warm Q3 toward-Q4 register with ですます調 + 短文句点 + 体言止め 1 章 1 回 — the warmth and daily-use framing aligns with the "毎日触る道具" half of the thesis. However: (1) pairs with short-form and mid-form-essay only — this is a long-form sales パンフレット, which is outside the anchor's native form; (2) Over-mimic risk HIGH with a mitigation clause that conflicts with the brief's need for Authority/Reason payload — the discipline "command form forbidden, everything as personal declaration" makes embedding medical specs and certification numbers feel awkward; (3) the 1人称「ぼく」register is 40-50s male essayist, not the 70+ elderly audience's voice register; (4) the self-improvement / daily gratitude framing ("今日もていねいに") applied to a blood pressure monitor risks sentimentalizing a clinical need. Weaker fit than Rank 1 due to form mismatch and spec-integration difficulty.

**Rank 3: 岩崎俊一** (`jp-iwasaki-shunichi-yoyu-mujou`)
- fit_score: LOW (and a category-boundary concern)
- fit_reasoning: The brief itself lists 岩崎 as a candidate for the 余韻 register, and the Phase 4 draft's closing line 「「正しい」を、家の道具に。」already reads like a 体言止め + abstract×concrete bridge — suggesting Phase 4 author was thinking in this direction. The 余韻 / 無常 register could render the "daily device" thesis evocatively. However: (1) anchor pairs with short-form-catchcopy and mid-form-brand-tagline; this brief is long-form sales パンフレット with embedded spec block — 余韻 mechanics work at catchcopy level, not across 4 structural stages; (2) 無常 undertone (「やがて」「いつか」「いのちに変わるもの」) applied to a 70+ audience medical device creates a mortality-salience risk — the brief's goal is to REDUCE adoption barrier, not invoke awareness of finitude; (3) this is a craft-gate master, and `voice_reference` is null — if the writer had wanted 岩崎 register, they would have named it; invoking craft-gate mechanics on a null voice_reference via Register Signal branch would be Tier precedence violation.岩崎 stays as a conceptual reference but cannot serve as the primary anchor via Pass 3d.

---

### Pool-strength assessment

**Overall pool fit strength for this brief: WEAK**

Reasoning: The JP Q4-Q3 edge anchor pool covers lifestyle warmth registers — home goods narrative (青木耕平), daily-life essayism (松浦弥太郎). Neither anchor has a native commercial register that bridges medical authority (Q4: certification, precision, clinical credibility) with warmth without invoking mortality or consumer-aesthetic frames mismatched to the 70+ independent-elderly audience. The pool was built around the Q3 warmth axis as it appears in lifestyle media and creative industries; the medical×warmth register (authority warmth, institutional care warmth — think NHK 健康番組 narration, or Dr. Mitsui home-care branding) has no individual-creator anchor in the library. This is a genuine gap, not a selection failure.

The closest structural analog — an anchor that normalizes spec-heavy content within lived warmth — is 青木耕平, but the audience and authority payload mismatches are not marginal. Selecting it requires being honest that it will supply discipline (形容詞禁, 生活シーン冒頭) without the full register fit.

---

### agent_selection_confidence (v1.12.1)

**LOW**

**Rationale**: All three candidates have documented mismatches with the brief's authority-warmth signal at 70+ medical-device context. Rank 1 (青木耕平) is the least-bad option structurally but the audience gap (30-40s lifestyle vs 70+ elderly) and the authority payload (医療機器認証番号 + 精度スペック) sit outside the anchor's native register. There is no Q4-Q3 edge anchor in the JP library for the 医療×温かい register. Rank 2 (松浦弥太郎) has form mismatch (short/mid-essay, not long-form sales). Rank 3 (岩崎俊一) has form mismatch (catchcopy-scale) and mortality-salience risk for a barrier-reduction goal. Selection of Rank 1 as primary is the best available, not a confident match.

---

### Full register_signal_applied JSON

```json
{
  "primary_anchor_slug": "jp-kurashicom-aoki-kohei-lifestyle-narrative",
  "landmark_position": "toward-Q3",
  "secondary_anchors": [
    {
      "slug": "jp-iwasaki-shunichi-yoyu-mujou",
      "role": "secondary-cadence",
      "rationale": "Borrow 体言止め + abstract×concrete bridge for the closing tagline only (not mortality-salience mechanics); applied at catchcopy-scale Close section, not structural level"
    }
  ],
  "mitigation_clauses_applied": [
    "形容詞禁止、生活シーン 1 つを具体描写、丁寧体は淡々と (青木耕平 primary)",
    "名指せる 1 つの瞬間・1 つの物を残し、感情語と CTA を削れ (岩崎 secondary, Close line only)",
    "スペック数字は段落中盤以降に遅延配置 — 冒頭 2-3 文は生活情景から入る (青木耕平 discipline applied to spec block)"
  ],
  "anchor_candidates_ranked": [
    {
      "rank": 1,
      "slug": "jp-kurashicom-aoki-kohei-lifestyle-narrative",
      "fit_score": "LOW-MEDIUM",
      "fit_reasoning": "Q4 toward-Q3 structural match; long-form form compatibility; 形容詞禁 + 生活シーン冒頭 discipline maps to thesis. Audience gap (lifestyle 30-40s vs elderly 70+) and authority-payload (医療機器 spec) outside native register."
    },
    {
      "rank": 2,
      "slug": "jp-matsuura-yataro-teinei-essay",
      "fit_score": "LOW",
      "fit_reasoning": "Q3 toward-Q4 warmth matches tone_cue. Form mismatch (short/mid-essay vs long-form sales パンフレット). Over-mimic HIGH conflicts with spec-integration need. 1人称「ぼく」inappropriate for elderly medical audience."
    },
    {
      "rank": 3,
      "slug": "jp-iwasaki-shunichi-yoyu-mujou",
      "fit_score": "LOW",
      "fit_reasoning": "余韻 / 体言止め register already present in Phase 4 draft close. Form mismatch (catchcopy-scale mechanics). Mortality-salience risk contradicts barrier-reduction goal for 70+ elderly. null voice_reference precludes craft-gate primary selection."
    }
  ],
  "substitute_suggested": null,
  "thesis_self_check": "clear",
  "agent_selection_confidence": "LOW",
  "native_critical_vocab_cited": [
    "生活情景冒頭",
    "形容詞禁",
    "丁寧体淡々と",
    "体言止めマキシム 1 章 1 回",
    "スペック数字の遅延配置"
  ]
}
```

---

## Step 4 — Polished rewrite (long-form sales パンフレット)

Primary anchor discipline applied: 青木耕平 `jp-kurashicom-aoki-kohei-lifestyle-narrative`
Secondary cadence applied at Close only: 岩崎俊一 体言止め + abstract×concrete bridge (mortality-salience mechanics explicitly suppressed)

Mitigation applied:
- 形容詞で褒めない → 具体的使用シーンで語る
- 冒頭は生活情景から入る（朝の習慣 → 機器へ）
- スペック数字は中盤以降に遅延配置
- 「限定」「最安」「すごい」等の煽り語禁止
- 命令形禁止 → 「〜できます」「〜になりました」で差し出す
- 丁寧体淡々と（「〜ですね」「〜なんですよ」の馴れ馴れしさ禁止）

---

```
[Opening]

朝、洗面所の鏡の前に置いておくだけでいい、と教えてもらったのですが、
最初の一週間は、結局一度も腕を通しませんでした。

使いかたがわからなくて、というよりも——
正しく測れているか、不安だったのです。

[Body]

心拍マモリは、その「測れているか」という不安を取り除くために設計しました。

ボタンは 3 つ。電源を入れて、腕を置いて、スタートを押す。
画面の文字は 18pt。老眼鏡をかけていても、はっきり読めます。
測定が終わると、数字だけが残ります。

測定精度は、医療機関で使われる機器と同じ水準です。
（医療機器認証番号: XXXXX / 収縮期血圧 ±3mmHg）
正しく測れているという安心を、家の中に持ち込んでほしかった。

毎朝、同じ時間に、同じ姿勢で。
その繰り返しが、自分の体のことを、少しずつ自分で知っていくことになります。

[Close]

正確さと、やさしさ。
家の道具として、毎日の習慣に。
```

---

## Thesis self-check

**Thesis**: 「医療機器は正確でなくてはならないが、毎日触る道具でもある」

Scan result: **clear**

- [Opening]: 「正しく測れているか、不安だった」= 医療機器の正確性への不安を認識 → thesis の "正確でなければならない" を読者の実感として先行配置。
- [Body]: 精度スペック（±3mmHg / 医療機器認証）= Authority×Reason Q4 base 維持。ボタン 3 つ / 18pt 文字 / 毎朝同じ時間 = "毎日触る道具" の具体化。
- [Close]: 「正確さと、やさしさ。」= thesis の 2 要素を体言止めで並置。「毎日の習慣に」= 日常道具化の着地。

Thesis の 2 軸（正確 + 毎日の道具）がどちらも本文に根拠を持ち、Close で収斂している。thesis-induced drift なし。

---

## Honest self-notes

**Clean fit があったか**: なかった。

青木耕平 anchor を選んだのは「最悪ではない」からであり、「最善」だからではない。正直に言えば、この briefに対して anchor library は wrong tool で応答している。

**何が問題か**:

JP Q4-Q3 edge の anchor pool は「暮らしの温かさ」を担う register として設計されており、担い手はライフスタイル・エディトリアル系（北欧雑貨、丁寧な暮らし、生活随筆）に偏っている。このゾーンの anchor が持つ「温かさ」は peer intimacy（同世代の生活者が友人に語る）であって、institutional warmth（信頼できる医療機関・専門家が日常に寄り添う）ではない。

今回の brief が求めているのは後者 — **医療 Authority を持ちながら温かい** register。これは：
- NHK「きょうの健康」式の専門家×日常語
- かかりつけ医が診察室で語る平易な医療言語
- 高齢者向け行政パンフの丁寧体 + 具体的手順記述

のような register であり、いずれも「有名コピーライター個人の声」ではなく「機関的な安心の声」に属する。この種の register は v2 inclusion criterion（individual-creator authorship）を満たさないため anchor としては存在しない — それ自体は正しいが、今回のような brief では anchor library のカバー範囲外として正直に認識する必要がある。

**Anchor gap の診断**:

| 欠けているもの | 影響 |
|---|---|
| JP 医療×温かい register アンカー（例: NHK 健康番組ナレーション / かかりつけ医の語り口 / 薬局チェーン公式コミュニケーション） | Pass 3d がライフスタイル系 anchor で代替せざるを得ない |
| 70+ 独居高齢者向けコミュニケーション register アンカー | 聴き手の語彙・文体の実態が anchor に反映されない |
| Q4 Authority warmth 系の個人 anchor（例: 日野原重明のような医師×エッセイスト） | Q4-Q3 edge の医療文脈でピボットできる個人がいない |

**routing の問題もあるか**: voice-quadrant-stage が Q4-Q3 edge (toward-Q3) を正確に判定していることは問題ない。ただし、もし Phase 5 が「医療 + 温かい」という signal を受けた時点で「この象限は anchor pool が thin である」という警告を発せられれば、Phase 6 での LOW 判定を事前に user に知らせることができる。現在その仕組みはない。

**「最も誠実な対応」は何だったか**:
1. anchor library にない register であることを宣言し、anchor なしで Pure 4-axis + Ogilvy discipline のみで Pass 3d を終了する（anchor が wrong tool の場合、強制適用よりも "no-apply" のほうが正直）— ただし現行 SKILL.md Pass 3d プロトコルに "no anchor found → skip" exit は明記されていない
2. 上記の代わりに今回とった approach: 最も harm の少ない anchor（青木耕平）を LOW 信頼で適用し、適用箇所を discipline-borrowing（形容詞禁、生活シーン冒頭）に限定する — anchor の voice signature 全体でなく、sentence-level rules のみを借りる

approach 2 は「anchor の voice を移植する」のではなく「anchor の discipline を借りて prose mechanics を補強する」という使い方であり、それ自体は合理的。ただし Step 3.5 が HIGH/MEDIUM/LOW を尋ねているのは、この区別を visible にするためであり、LOW を宣言したうえで理由を述べることが instrumentation の目的に沿っている。
