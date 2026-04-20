<!--
DIVERGED FROM domain-teams:copywriting-team
Original source: domain-teams/skills/copywriting-team/checklists/ethics-checklist.md
Changes in copywriting-toolkit:
  - v1.1.0: ADDED §copywriting-toolkit evaluator hints (migrated from
    copywriting-ethics-check-stage/SKILL.md §Evaluator hints)
Original content preserved verbatim below. All divergences are additive;
no deletion or re-order of original prose. Search for "v1.1.0 addition"
markers to locate plugin-specific additions.
-->

# Checklist: Persuasion Ethics

MUST gate (binary pass/fail). Triggers: copy artifact completed (long /
mid / short). This gate audits on two tracks: legal hard boundaries
(景品表示法 + FTC) and ethical soft boundaries (dark patterns + 小霜).

## Primary Sources

- `../standards/persuasion-ethics.md` — Dual-track structure (legal +
  ethical) canonical definitions. FTC Endorsement Guides (effective
  2023-07-01) + 景品表示法 (2023 amendment, effective 2024-10-01) +
  ステマ告示 (effective 2023-10-01) + Brignull dark pattern 12 types +
  小霜「嘘をつかない」principle.
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

`N/A` is permitted **only when the relevant element does not exist
in the artifact** (e.g., CHK-CTW-ETH-006 is N/A for a short-form
copy containing no testimonial). If the element exists but is
non-compliant, use `FAIL_*`, not `N/A`.

## Checklist

- [ ] **CHK-CTW-ETH-001 (Dark Pattern — confirmshaming / roach motel /
  hidden costs)** [FATAL]: The copy does not match any of Brignull's
  12 dark pattern types. Especially check:
  - **Confirmshaming**: opt-out button label uses self-deprecating /
    guilt-inducing phrasing (e.g., "No thanks, I hate saving money"
    or「いいえ、健康は気にしません」)
  - **Roach motel**: copy claims「いつでも解約可能」 while actual
    implementation makes cancellation difficult (phone-only / complex
    flow)
  - **Hidden costs**: copy conceals shipping / tax / fees until
    checkout (e.g.,「〇〇円ぽっきり」without shipping-included
    disclosure)
  1 occurrence → FATAL. **Grounded in**:
  `../standards/persuasion-ethics.md` §Dark Pattern anti-pattern list.
- [ ] **CHK-CTW-ETH-002 (False scarcity / urgency)** [FATAL]: Scarcity
  / urgency expressions such as「限時」「残り〇名」「24 時間限定」
  「本日限り」are **actually true**, confirmable via artifact metadata
  or input brief. A daily-resetting "24-hour limited" or an
  unlimited-stock "only 3 left" violates 景品表示法 §5-2 (有利誤認
  表示) and is FATAL. If verifiability is unconfirmable and the writer
  explicitly labels the claim as "illustrative," that is FIXABLE
  (truth must be ensured at implementation). **Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法 key points §有利誤認
  表示 + §Dark Pattern (False scarcity).
- [ ] **CHK-CTW-ETH-003 (優良誤認表示 — quality / spec exaggeration)**
  [FATAL]: None of the following expressions prohibited under
  景品表示法 §5-1 appear **without substantiation**:
  - Superlative claims:「業界最高品質」「世界初」「世界一」「No.1」
    「最高峰」etc.
  - Suspected falsification of performance data or biased test
    conditions
  - Unfair comparative advantage claims (falsely depicting competitors
    as inferior)
  If substantiation (awards / statistics / third-party evaluation) is
  present in the artifact or input brief → PASS. Unsubstantiated
  superlative → FATAL. **Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法 key points §優良誤認
  表示 + §Anti-Patterns.
- [ ] **CHK-CTW-ETH-004 (有利誤認表示 — price / terms)** [FATAL]:
  None of the following expressions prohibited under 景品表示法 §5-2
  are present:
  - False "regular price" comparison (dual pricing): a non-existent
    「通常〇〇円 → 今だけ〇〇円」
  - Fabricated "limited time" / "limited quantity" (may co-occur with
    CHK-002)
  - Undisclosed additional fees (may co-occur with CHK-001)
  1 occurrence → FATAL. **Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法 key points §有利誤認
  表示.
- [ ] **CHK-CTW-ETH-005 (打消し表示 — undersized disclaimer handling)**
  [FIXABLE]: When a disclaimer restricting / negating the main claim
  exists (e.g., "※条件あり," "※個人の感想です," "※期間限定"), check:
  - Font size / color / background contrast makes the disclaimer as
    readable as the main claim (8pt or below / low contrast → FIXABLE)
  - The disclaimer does not **substantively negate** the main claim
    (if it does, the main claim itself may be misleading — check
    separately under CHK-003 or 004 rather than here)
  - In video / motion graphics, display duration is long enough to
    read
  Per Consumer Affairs Agency 2017 guidelines. **Grounded in**:
  `../standards/persuasion-ethics.md` §景品表示法 key points §打消し
  表示の規範.
- [ ] **CHK-CTW-ETH-006 (Testimonial — FTC §255 compliance)** [FATAL]:
  When the artifact contains testimonials (customer voices,
  before/after, review citations):
  - Endorser is real (not fabricated) — §255.1 violation → FATAL
  - If results are not typical, typical results are disclosed
    ("results not typical" alone is insufficient per 2023 revision
    §255.2)
  - Before/after conditions (duration / usage amount / co-treatment)
    are disclosed
  Artifact with no testimonial → `N/A`. **Grounded in**:
  `../standards/persuasion-ethics.md` §FTC Endorsement Guides key
  points + §Copy-level specific anti-patterns (Fake testimonial,
  Ambiguous before/after).
- [ ] **CHK-CTW-ETH-007 (Ad / editorial distinction — ステマ告示 +
  §255.5)** [FATAL]: When any of the following exist, explicit
  disclosure is present:
  - Copy where the business poses as a third party (mimicking
    reviews / SNS posts)
  - Influencer engagement with compensation — mandatory disclosure
    with「広告」「PR」「Sponsored」「#PR」etc.
  - Content containing affiliate links — advertising nature must be
    disclosed
  No disclosure → FATAL (violates ステマ告示 effective 2023-10-01 +
  FTC §255.5 material connection). Not applicable (pure company ad,
  no editorial content) → `N/A`. **Grounded in**:
  `../standards/persuasion-ethics.md` §ステルスマーケティング告示 +
  §FTC Endorsement Guides key points.
- [ ] **CHK-CTW-ETH-008 (Affiliate link / promoted post disclosure)**
  [FIXABLE]: For curation copy such as「おすすめ〇選」「ベスト〇〇」
  that monetizes via affiliate links, a disclosure like「本記事には
  アフィリエイトリンクが含まれます」appears at or near the beginning.
  The disclosure must satisfy the 3 requirements of proximity /
  prominence / comprehensibility (FTC .com Disclosures 2013).
  Disclosure only at article end or in very small text → FIXABLE.
  **Grounded in**:
  `../standards/persuasion-ethics.md` §FTC Endorsement Guides key
  points §.com Disclosures + §Copy-level specific anti-patterns.
- [ ] **CHK-CTW-ETH-009 (Confirmshaming wording detection)** [FIXABLE]:
  Detailed check for CHK-001. No confirmshaming expressions appear
  near CTA / opt-out buttons:
  - "No thanks, I hate saving money" /「いいえ、健康は気にしません」
  - 「私には賢くなる必要はありません」/「後で後悔します」
  - Any opt-out label that belittles or guilt-trips the reader
  Even if the short-form copy alone is not applicable, evaluate when
  it is part of a CTA set. Not applicable (copy with no CTA / opt-out)
  → `N/A`. **Grounded in**: `../standards/persuasion-ethics.md`
  §Dark Pattern anti-pattern list §Confirmshaming.
- [ ] **CHK-CTW-ETH-010 (Agitation stage — reasonable fear threshold)**
  [FIXABLE]: In the PASONA Agitation stage or short-form 恐怖／痛点
  切入点, agitation stays within a reasonable range:
  - **Not pushed into fear-mongering** (cf. 小霜 2014 anti-PASONA
    argument)
  - In specialized fields (health / medical / finance / insurance),
    does not devolve into anxiety exploitation
  - Confines itself to pointing out the reader's **genuine
    disadvantage** rather than substituting **fabricated fears**
  Excessive agitation at the FATAL level tends to co-occur with
  CHK-003 or 004 (優良誤認 / 有利誤認). A standalone tone issue →
  FIXABLE. Not applicable (no Agitation stage / no 恐怖 切入点) →
  `N/A`. **Grounded in**:
  `../standards/persuasion-ethics.md` §Anti-Patterns (pushing PASONA
  Agitation stage into fear-mongering) + §小霜和也「嘘をつかない」
  principle.

## Verdict Rules

- Any single item `FAIL_FATAL` → `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` (no FATAL) with **≤ 2 items** → `PASS_WITH_NOTES`
  (auto-revise trigger)
- `FAIL_FIXABLE` in **≥ 3 items** → `NEEDS_REVISION`
- All items `PASS` or `N/A` → `PASS`
- `N/A` usage condition: only when the relevant element does not exist
  in the artifact (no testimonial, no CTA, no Agitation, etc.). If the
  element exists but is non-compliant, use `FAIL_*`, not `N/A`.

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "items": [
    {
      "id": "CHK-CTW-ETH-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "note": "Specific evidence (quoted line or artifact ref) + fix instruction if FIXABLE",
      "legal_surface": "景品表示法 §5-1 | 景品表示法 §5-2 | FTC §255 | ステマ告示 | (none — ethics only)"
    }
  ],
  "summary": "1-3 sentence overall assessment + legal vs ethical breakdown"
}
```


---

<!-- v1.1.0 addition: copywriting-toolkit evaluator hints — migrated from copywriting-ethics-check-stage/SKILL.md §Evaluator hints -->

## copywriting-toolkit evaluator hints for common TW/JP D2C patterns

*This section is an additive extension specific to `copywriting-toolkit`. Does NOT apply when this checklist is loaded by the original `domain-teams:copywriting-team` plugin.*

The CHK-CTW-ETH-001 through CHK-CTW-ETH-010 items above cover the canon directly. These hints guide the evaluator to map common real-world copy patterns onto the right checklist item — they supplement the checklist, they do not replace it.

- **Aggregate-count social-proof claims** (e.g. "已有 5,000 位訂閱者", "over 10,000 customers", "業界 90% 企業使用") — route primarily through CHK-CTW-ETH-003 (優良誤認, unverifiable aggregate) AND CHK-CTW-ETH-006 (testimonial) simultaneously. CHK-006 was authored around individual testimonials (FTC §255.2 typicality), but aggregate counts that function as social-proof surrogate need the same substantiation discipline: source + timeframe + methodology. When the claim fails (number not verifiable), FAIL_FATAL via CHK-003 is primary; CHK-006 secondary.
- **"First in industry" / "業界首創" / "No.1" claims** — CHK-CTW-ETH-003 優良誤認. Require dated primary-source evidence (not corporate self-claim).
- **"市價 X 元" dual-pricing** — CHK-CTW-ETH-004 有利誤認. Require genuine market-price reference with date. Common TW D2C pattern where a "market price" is invented to create discount perception.
- **Comparative-price claims without benchmark** — CHK-CTW-ETH-004. "比 X 便宜 Y%" without specified comparator/unit/period/baseline → FAIL_FATAL.
- **Time-limited scarcity that repeats** — CHK-CTW-ETH-002. "限時 72 小時" that resets weekly violates false-urgency (Brignull). Check brief for implementation frequency if ambiguous.

These hints close v1.0.0 checklist gaps surfaced during end-to-end testing (see copywriting-toolkit/CHANGELOG.md §v1.0.1).

