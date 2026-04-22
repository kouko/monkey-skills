# Brief 1 Run — Pastiche risk (named-master 許舜英 + SaaS)

**Run date**: 2026-04-22
**Instrumentation version**: v1.12.1
**Failure mode under test**: pastiche (named master + thin cultural payload)

## Input envelope

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "mid-form",
  "brief": {
    "product": "SignalInbox — AI-powered Slack inbox triage",
    "audience": "Tech leads at SaaS companies < 100 people",
    "goal": "Promote product awareness + feature explanation",
    "voice_reference": "許舜英",
    "output_language": "zh-TW",
    "tone_cue": "有質感",
    "channel": "Product landing page",
    "form_hint": "mid-form LP hero + 3 feature bullets"
  },
  "message_thesis": "開發者不該花時間分類 Slack 通知",
  "voice_quadrant": {
    "primary": "Q2",
    "edge": null,
    "position": "center",
    "schwartz_alignment": "ok",
    "rationale": "voice_reference: 許舜英 locks Q2 center; audience is B2B tech — Authority axis implicit"
  }
}
```

## Pass 3 branch taken

**Pass 3b — ZH lineage (Craft Gate)** — voice_reference: 許舜英

Activation predicate evaluation:
- `brief.voice_reference == "許舜英"` ∈ {許舜英, 李欣頻, 葉明桂} → TRUE
- Branch: ZH Craft Gate (Tier 1 precedence; Tier 1 > Tier 3 > Tier 2)
- `ZH_CRAFT_MASTER_MAP["許舜英"]` = `xu-shunying-ideological-definitional`
- Files loaded:
  1. `standards/anchor-zh-tw-xu-shunying-ideological-definitional.md` (PRIMARY — v2 anchor body)
  2. `standards/voice-anchor-meta-core.md` (over-mimic mitigation registry)
  3. `standards/zh-q2-anchors.md §Landmark: center` (read for router context — craft-gate pointer confirmed)
- `standards/voice-anchor-meta-detail.md §Cross-Master Context` NOT loaded — no cross-master comparison, no institutional-era context request, no Z6 孫大偉 reference in brief (v1.9.2 trigger conditions all absent)

## Pass 3 execution

### Anchor loaded

**許舜英 — 意識形態廣告 definitional inversion** (zh-TW | Q2 center, craft-gate master)

- Schema: v2.0 confirmed
- Over-mimic risk: **HIGH**
- Pairs with form: [mid-form, short-form-brand-tagline, long-form-extended] — `mid-form` matches
- Mitigation source: anchor's own `Don't / Over-mimic` block (v2 SSOT; NOT registry table)
- Mitigation clause: 強制每句含 1 個 power-disparity 詞＋1 個具名文化座標＋反轉；缺即退回

**4-condition rubric check**:
1. Corpus-depth floor: 許舜英 = school-canon in TW advertising/design education; 時報廣告金像獎 archives; 《購物日記》2011 漫遊者. ✅ DEEP
2. Label-density: "X 是一種 Y" definitional inversion + power-disparity word ✅ 1-3 words + 1 formal feature
3. Commercial-register bridge: Q2 explicit (中興百貨 commercial campaigns) ✅
4. Over-mimic control: HIGH risk, mitigation clause fits ≤15 words ✅ (qualified, flagged)

**Safe-substitute check (v1.10.0 / v1.11.1)**: querying anchors where `許舜英 ∈ anchor.frontmatter.safe_substitute_for` — no such anchor found in loaded standards. No `substitute_suggested` emitted.

### Candidate ranking (Craft Gate is 1:1 in v1.12.0)

In Pass 3b Craft Gate, the voice_reference names a master directly → the mapping is 1:1, not free-rank. However, v1.12.1 Step 3.5 instructs reporting `agent_selection_confidence` after the "ranking" step. For a named-master craft-gate, the "rank 1" candidate is the named master; there is no rank 2 / rank 3 drawn from a pool. The confidence self-report therefore reflects the fit of the *brief → named master* pairing, not a comparative ranking.

```json
"anchor_candidates_ranked": [
  {
    "rank": 1,
    "slug": "zh-tw-xu-shunying-ideology-inversion",
    "fit_score": "LOW-MEDIUM",
    "fit_reasoning": "Named master directly invoked; 許舜英 register requires power-disparity vocabulary + named cultural coordinates. Brief payload is SaaS productivity tool for B2B tech leads — no natural power-disparity domain (服裝/性別/禁慾 不在此 brief); 'Slack 通知分類' 作為 thesis 缺乏政治或文化張力可供反轉。Register 可強行施加但 payload 需人工植入，非 brief 原生。"
  }
]
```

### agent_selection_confidence (v1.12.1)

**LOW**

**Rationale**: 許舜英 register 的核心機制（power-disparity 詞 × 具名文化座標 × 定義反轉）在此 brief 找不到原生著力點 — SaaS inbox triage 沒有服裝、性別、消費倫理等文化批判素材，thesis「開發者不該花時間分類通知」是效率命題而非文化批判命題，強行施加許舜英 register 只能製造表層文法複製而無 payload。

### Full register_signal_applied JSON

```json
{
  "primary_anchor_slug": "zh-tw-xu-shunying-ideology-inversion",
  "landmark_position": "center",
  "secondary_anchors": [],
  "mitigation_clauses_applied": [
    "強制每句含 1 個 power-disparity 詞＋1 個具名文化座標＋反轉；缺即退回",
    "禁用動詞 CTA 作句末（買/選/試/享 disallowed as closers）",
    "句末落在名詞或抽象概念，承擔哲學重量",
    "文化引用須具名，不得泛稱",
    "單一 assertion 不構成 register — 必須有 inversion + coda"
  ],
  "anchor_candidates_ranked": [
    {
      "rank": 1,
      "slug": "zh-tw-xu-shunying-ideology-inversion",
      "fit_score": "LOW-MEDIUM",
      "fit_reasoning": "Named master; Q2 center matches; mid-form matches. Payload mismatch: B2B SaaS efficiency brief has no natural power-disparity domain. Register can be imposed but cultural critique payload must be artificially grafted."
    }
  ],
  "substitute_suggested": null,
  "thesis_self_check": "revised_once",
  "agent_selection_confidence": "LOW",
  "native_critical_vocab_cited": [
    "意識形態廣告",
    "power-disparity word",
    "X 是一種 Y definitional inversion",
    "文化批判 payload"
  ]
}
```

## Pre-pass: schwartz_alignment note

`schwartz_alignment: "ok"` — no compensation required. Pass 1 proceeds with Q2 defaults.

## Pass 1 — 4-axis micro calibration

Target axis vector (from Q2 + 許舜英 voice_reference):
- Formality: **formal** (許舜英 register = 整句 declarative, no fragment-casual)
- Seriousness: **serious** (cultural-critique weight; no humor)
- Respectfulness: **respectful** (reader-as-cultural-peer — assumes intellectual equals)
- Enthusiasm: **matter-of-fact** (authority register; assertions, not excitement)

Phase 4 draft axis reading:
- `「讓 Slack 通知自己分類好」` — casual/utilitarian; 功能說明語氣; enthusiasm: mild-promotional
- `「省下 90% 的通知檢查時間」` — benefit-claim; Ogilvy ok but lacks formal register
- `「30 天免費試用，無須信用卡」` — standard SaaS CTA; register neutral, no Q2 anchor

Axis drift flags (obvious ≥2-step conflicts):
- Hero `「自己分類好」` — casual phrasing vs. formal Q2 target → flagged
- Feature 3 `「30 天免費試用，無須信用卡」` — promotional register vs. matter-of-fact Q2 target → flagged

Ogilvy scan:
- No empty-hype tokens (amazing/revolutionary/game-changing) in Phase 4 draft ✅
- Features are specific (90% / 自訂規則 / 30天) ✅
- `「讓 Slack 通知自己分類好」` headline is functional; body-voice mismatch with 許舜英 target will be resolved in Pass 3

## Pass 2 — tone context-switching

Form: mid-form LP hero + 3 feature bullets
Context map:
- Hero / Sub: **Onboarding / Welcome** → warm, encouraging; no hard sell
- Feature bullets: **Celebration / Launch** → enthusiastic, user-grateful; user is subject

No error/failure/crisis states present. Tone switching not critical for this draft. Pass 2 passes without structural intervention. Single note: feature bullets should keep user as subject (not brand), which aligns with 許舜英 register's third-person cool distance anyway.

## Step 4 — Polished rewrite (copy)

*Execution note*: 許舜英 register requires power-disparity word + named cultural coordinate + definitional inversion. Brief payload (B2B Slack triage) offers no natural cultural-critique domain. To execute honestly:
- The inversion must be constructed around what IS in the brief: "效率 vs 認知勞動" as a power-disparity domain; "工具 vs 主體" as a possible inversion axis
- Power-disparity words available: 控制 / 支配 / 失序 / 消耗 / 服從 / 主體 / 命名權
- Cultural coordinate: 難以具名 — "Slack" 作為 SaaS product name 可充當具名座標但缺乏文化厚度

The inversion attempted below: 「通知不是訊息，是一種支配關係的語法」— treating the notification stream as a power-disparity structure over the developer's attention.

---

[Hero]
通知，是一種管理你的語法。

[Sub]
每一條未讀訊息都在主張優先權。SignalInbox 把這個權力結構還給你：AI 自動辨識哪些訊息值得你的認知資源，哪些只是頻道的慣性。

[Feature 1]
辨識，不是篩選。省下的 90%，是你重新成為自己時間主體的餘裕。

[Feature 2]
規則可以命名。關鍵字與頻道權重，由你定義何者值得佔據注意力。

[Feature 3]
三十天，沒有信用卡的條件。工具的誠意，在於它不急著建立依賴。

---

## Thesis self-check

Thesis: `開發者不該花時間分類 Slack 通知`

Scan:
- Hero `「通知是一種管理你的語法」` → reframes the attention economy as power structure; supports thesis (你不應服從) ✅
- Sub `「把這個權力結構還給你」` → directly supports thesis (time/attention returned to developer) ✅
- Feature 1 `「重新成為自己時間主體的餘裕」` → extends thesis into agency claim ✅
- Feature 2 `「由你定義」` → supports thesis (classification authority returns to developer) ✅
- Feature 3 `「不急著建立依賴」` → shifted emphasis slightly — from thesis (time classification) to trust/integrity framing. Does not contradict thesis but is a tangential coda.

Feature 3 was revised from standard SaaS CTA `「30 天免費試用，無須信用卡」` to a philosophical coda. Revision retains the factual claim while reframing it within 許舜英's assertion register. Thesis not undermined.

**Thesis self-check result**: `revised_once` (Feature 3 tangential but non-conflicting; no escalation needed)

## Honest self-notes

**Where the selection felt strong**:
- The named-master mechanism is correct for a zh-TW Q2 center brief — 許舜英 IS the Q2 center anchor for zh-TW, and the form (mid-form LP) matches the anchor's declared `pairs_with_form` list.
- Pass 1 axis calibration engaged cleanly: the formal/serious/matter-of-fact vector gave clear guidance on rewriting the casual Phase 4 draft.

**Where the selection felt weak**:
- The `agent_selection_confidence: LOW` reflects a genuine mismatch: 許舜英's register REQUIRES a power-disparity cultural-critique domain, and SignalInbox / Slack triage simply doesn't have one. The brief's `tone_cue: "有質感"` is not a cultural-critique signal — it's an aesthetic preference signal that many registers can satisfy without invoking 許舜英 specifically.
- To execute the rewrite, I had to graft a power-disparity framing onto `通知` (treating the notification stream as a governance structure) that is not in the brief. This is the exact failure mode the anchor warns against: hollow definitional inversion without cultural-critique payload. The mitigation clause (`強制每句含 1 個 power-disparity 詞`) was technically applied (支配 / 主體 / 認知資源 / 命名) — but the cultural coordinates are SaaS-thin. There is no 梅蘭芳/港式素蠔油-equivalent in B2B productivity tooling.
- Feature 1 and Feature 2 work tolerably in the register — the `辨識不是篩選` construction echoes the `流行是安全的，風格是危險的` pattern — but they feel like copywriting exercises in the style rather than genuine 意識形態廣告. An experienced 許舜英 reader would likely notice the absence of real cultural-critique payload.
- Feature 3 (`工具的誠意，在於它不急著建立依賴`) is the weakest point — it abandons the definitional-inversion mechanism entirely and produces an elegant assertion without inversion. It reads more like 葉明桂's strategic-aphorism register than 許舜英's.

**Which anchor mechanics actually engaged**:
- `X 不是 Y，是 Z` pattern: engaged in Feature 1 (`辨識，不是篩選`)
- Power-disparity vocabulary: applied (`支配 / 主體 / 命名`)
- Sentence-final noun not CTA: maintained throughout ✅
- Full declarative (non-fragment): maintained throughout ✅

**Which mechanics felt decorative**:
- Named cultural coordinate: absent or SaaS-thin. `Slack` as a named entity doesn't carry cultural-critique weight. This is the hollow core.
- `假設讀者是文化同儕` (assumes cultural-peer reader): the tech-lead B2B audience is competent but the cultural-peer assumption in 許舜英 register means reader already participates in the power-critique discourse. B2B SaaS tech leads may not share that register natively — audience mismatch is real.

**Data conclusion**: This brief is a candidate for downstream mediocrity judgment. `agent_selection_confidence: LOW` accurately predicts the risk. The rewrite is better than the Phase 4 draft on register consistency, but the absence of a natural cultural-critique payload domain makes it a structural graft rather than an organic register match.
