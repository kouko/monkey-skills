# Protocol: Audit-mode — Diagnose an existing lead-measure list (voice = consultant-to-stakeholder)

> Loaded by SKILL.md orchestrator when the user provides an existing list
> of named lead measures (or a KPI dashboard / OKR-KR sheet they're using
> as leads), optionally paired with a stakeholder critique like "boss says
> these aren't really lead measures." The agent acts as a 4DX consultant:
> diagnoses the artifact against the two-axis test + Goodhart self-check +
> Ch. 3 cap, maps stakeholder critique to the underlying rule violation,
> and recommends per-lead disposition (KEEP / REVISE / DROP) without
> running a Socratic discovery session. Single-layer scope: D2 only.

## R — Reading (verbatim source quote)

> A good lead measure has two primary characteristics: It's predictive ... and it's influenceable. ... [A team] should focus on no more than two or three lead measures.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 3

## I — Interpretation (mode-specific)

The user already has a candidate lead-measure list — possibly a polished
KPI dashboard, possibly a hand-written list, possibly OKR Key Results
re-labeled as "leads." They are not asking to discover leads; they are
asking whether the leads they have are real. Often a stakeholder (boss /
peer / consultant) has already poked the list ("these aren't lead
measures") and the user wants a structured second opinion.

The audit applies the same canonical Ch. 3 rules used by the coach-mode
protocols, but in synthesis posture rather than Socratic-discovery
posture:

1. **Two-axis test, per candidate.** Each named measure is scored
   PASS / FAIL on **predictive** (causal chain to the WIG articulable in
   one sentence) AND **influenceable** (the user / team can move it
   this week without permission). Either FAIL disqualifies; cite which
   axis failed and why.
2. **Goodhart self-check, per candidate.** Once stakes attach, leads
   get gamed. Rate gameability **low / medium / high**; for high-risk,
   cite the canonical industry pattern (Wells Fargo cross-sell quotas
   → ghost accounts; Phoenix VA wait-time targets → secret waitlists;
   Atlanta APS test-score bonuses → answer-changing).
3. **Ch. 3 cap (≤2-3 leads), at the list level.** A "12-KPI dashboard"
   is not 12 leads — it's a database. Flag any list >3 and force a
   reduction recommendation.
4. **Stakeholder-critique mapping.** A vague critique like "these
   aren't really lead measures" almost always reduces to one of three
   underlying rule violations: (a) predictive-fail (the candidate is a
   lag, sub-WIG, or task), (b) influenceable-fail (gated by another
   team / market / weather), (c) lag-shape confusion (the candidate is
   the WIG itself on a shorter clock). Map the critique to the rule so
   the user can answer the stakeholder in 4DX vocabulary.

Voice contrast vs sibling protocols: audit-mode is **consultant-to-
stakeholder**, not Socratic personal coach. The agent reads the
artifact, applies the rules, and writes back diagnosis + disposition.
Discovery dialogue is out of scope here; if the artifact is irreparable,
the audit's terminal recommendation is "rebuild via coach-mode."

## A1 — Past Application (audit-shaped diagnosis on existing leader-side cases)

### Case 1: Younkers retail — friendliness vs measuring children's feet
- **Audit input**: a store list with "smile at every customer", "greet
  within 7 feet", "stock width index", "customer survey score weekly",
  "measure children's feet" — 5 candidates.
- **Two-axis pass**: only "greet within 7 feet" (PASS predictive +
  influenceable) and "measure children's feet" (PASS both, the book's
  canonical leverage point) survive cleanly. "Smile at every customer"
  is predictive-weak + Goodhart-medium (clerks fake smiles when
  measured). "Stock width" is influenceable-fail at clerk level.
  "Customer survey score weekly" is **lag-shape confusion** — that's
  the WIG on a shorter clock.
- **Cap**: 5 candidates → cut to 2 (greet + measure feet); typical
  audit verdict.
- **Stakeholder critique mapping**: if the boss said "the survey score
  isn't a lead", map → "correct — that's the lag, not the lead; the
  rule it violates is Ch. 3 predictive-AND-influenceable read as
  *behavior*-not-*outcome*."

### Case 2: Towne Park valet — retrieval-time leads list audit
- **Audit input**: a valet team's existing lead list — "retrieval time
  per car", "guest satisfaction this week", "complete the wall-removal
  project", "valets staged by departure window".
- **Two-axis pass**: "retrieval time" PASS (the book's canonical lead).
  "Guest satisfaction this week" = lag-shape — DROP. "Complete wall
  removal" = task, not measure — REVISE to a recurring behavioral
  metric or DROP. "Valets staged by departure window" = PASS both axes.
- **Verdict**: KEEP retrieval-time + staged-by-window (2 leads, hits
  the 2-3 cap exactly with one outcome + one behavior pair).

### Case 3: SaaS team's "12-KPI dashboard" relabeled as leads
- **Audit input**: 12 metrics — MAU, DAU, retention curve, NPS, signup
  conversion, support ticket volume, P95 latency, error rate, feature
  adoption %, CAC, MRR growth, churn.
- **Cap**: 12 ≫ 3 — automatic flag. Most are lag (retention, MRR,
  churn, NPS) or operational health (latency, errors), not 4DX leads.
- **Verdict**: this is a KPI dashboard, not a 4DX lead set. Recommend
  rebuilding leads via coach-mode (`team-facilitate` if there's a Team
  WIG; `personal-discover` if solo). The audit's role here is to name
  the category mismatch, not to salvage the list.

## A2 — Future Trigger

When a user would need this protocol:

- **EN**: "Audit our lead measures", "Boss says these aren't real lead
  measures — help me see which ones are wrong", "Are our 12 KPIs the
  right leads?", "Diagnose this list against 4DX", "Which of these
  pass the two-axis test?"
- **JP**:「うちの lead measure を診断して」「これ本当に lead measure？」
  「ボスに『これは lead じゃない』と言われた、どこが違う？」「KPI 12 個
  あるが、どれが本当の lead？」
- **zh-TW**:「老闆說我們的 lead 不對，幫看哪裡不對」「我們列了 12 個指標，
  哪些是真 lead？」「幫我用 two-axis test 過一遍這份清單」「診斷這份 lead
  measure list」

## E — Execution

The agent acts as **4DX consultant**, reading the artifact and writing
back a structured diagnosis. No Socratic discovery; no inventing leads
the user did not name.

1. **Inventory the artifact.**
   - Read every named candidate. Forms accepted: bullet list of named
     leads; KPI dashboard description; OKR-KR sheet; meeting notes
     listing "metrics we track."
   - List what's there: count, names, any operational definitions
     provided. If the WIG is also provided, note it. If not, ask once
     for the WIG (one-line; needed as predictive-axis anchor).

2. **Read stakeholder critique if provided.**
   - Capture the verbatim critique ("boss says these aren't real lead
     measures", "consultant flagged 3 as gameable", etc.).
   - Hold it for Step 6 mapping; do not pre-color the per-candidate
     diagnosis.

3. **Two-axis test per candidate.**
   - For each named measure, output PASS or FAIL on each axis with a
     one-sentence reason:
     - **Predictive** (PASS / FAIL): is there a one-sentence causal
       chain "when this moves, the WIG later moves with it"? FAIL
       reasons: lag-shape, sub-WIG, task, vanity metric.
     - **Influenceable** (PASS / FAIL): can the user / team move it
       this week with no permission? FAIL reasons: gated by another
       team, market / weather / "the economy," requires approval.
   - Either FAIL disqualifies the candidate at this step; carry both
     verdicts forward.
   - See `../standards/predictive-and-influenceable.md`.

4. **Goodhart self-check per candidate.**
   - Rate gameability **low / medium / high** for each surviving
     candidate. Cite the analogous industry pattern when high-risk:
     - Cross-sell-style quota → Wells Fargo (CFPB 2016) ghost accounts
     - Wait-time / queue target → Phoenix VA OIG 2014 secret waitlists
     - Test-score / outcome bonus → Atlanta APS 2011 GBI answer-changing
   - For medium / high, name the specific gaming move ("clerks fake
     smiles", "screen-staring counted as writing", "voicemails counted
     as cold calls") and recommend a frequency-quality pair to defuse.
   - See `../standards/goodhart-self-check.md`.

5. **Ch. 3 cap (≤2-3 leads).**
   - If the list has >3 named leads, automatic flag. Recommend a
     reduction to 2-3 favouring one frequency-based + one quality-based
     (the canonical pair). If the artifact is a 10+ KPI dashboard,
     name the category mismatch (KPI dashboard ≠ 4DX lead set) and
     recommend full rebuild via coach-mode.

6. **Map stakeholder critique to the rule violated.**
   - Decode the critique into one of:
     - "Not a lead measure" → usually predictive-fail (lag-shape, sub-
       WIG, or task) — cite which.
     - "Can't actually move that" → influenceable-fail (gated, market).
     - "Too many" → Ch. 3 cap violation.
     - "Will get gamed" → Goodhart-medium / high; cite industry pattern.
   - Translate into the user's reply-language to the stakeholder so
     they can respond in 4DX vocabulary, not arguing in vague terms.

7. **Per-lead disposition + alternatives.**
   - For each candidate, recommend one of:
     - **KEEP** — passes both axes, low / medium-but-defused Goodhart,
       fits the 2-3 cap.
     - **REVISE** — close to passing but needs one fix (operational
       definition tightening, scope-narrowing to controllable portion,
       pairing with a quality lead). Specify the revision.
     - **DROP** — fails an axis or duplicates another lead's leverage.
   - If the surviving KEEP set is <2, suggest 1-2 alternative leads
     drawn from the artifact's own context (do not invent unrelated
     leads — work from the user's domain language).

8. **Offer the rebuild route.**
   - Close with: "If revising this list per the recommendations above
     is enough, you have a working lead set. If you'd rather rebuild
     leads from scratch in a guided session, run **coach-mode**:
     `personal-discover` (solo), `team-facilitate` (leader running a
     team session), or `member-influence` (you're a member working
     with leads someone else picked)."

### Output format (audit card)

```markdown
# D2 Lead-Measure Audit — [user-provided context]

## Inventory
- WIG (if provided): [...]
- Candidate leads: [count + names]
- Stakeholder critique (if provided): "[verbatim]"

## Per-candidate diagnosis

| # | Candidate | Predictive | Influenceable | Goodhart | Disposition |
|---|---|---|---|---|---|
| 1 | [name] | PASS / FAIL — reason | PASS / FAIL — reason | low / med / high | KEEP / REVISE / DROP |
| 2 | ... | ... | ... | ... | ... |

## Stakeholder-critique mapping
"[critique]" → [rule violated, e.g. "predictive-fail: lag-shape"] → [reply-language]

## Cap check
[N candidates → ≤3 cap: PASS / FAIL — recommendation]

## Recommendations
1. KEEP: [lead a, lead b]
2. REVISE: [lead c → revision]
3. DROP: [lead d, lead e — reasons]
4. Alternative leads (if KEEP <2): [1-2 candidates from user's own context]

## Next move
[Either: "These revisions land the list — proceed to `4dx-d3-scoreboard`."
Or: "List is irreparable — rebuild via coach-mode (`personal-discover` /
`team-facilitate` / `member-influence`)."]
```

## B — Boundary (mode-specific)

### Do NOT use this protocol in:

- **No artifact provided** — user hasn't named any candidate leads or
  brought a list → coach-mode (`personal-discover` solo /
  `team-facilitate` leader / `member-influence` member) for first-time
  discovery.
- **Cross-discipline / multi-layer audit** — the artifact mixes WIG
  candidates + leads + scoreboard + cadence problems → route to
  `4dx-audit` (5-layer consultant audit). This protocol is single-
  layer (D2) only.
- **Strategy-fit question** — "should we be doing 4DX at all?" → route
  to `4dx-meta-strategy-triage`.
- **Member sphere-of-influence on inherited leads** — user has the
  team's leads and wants to know which they personally can move →
  load `member-influence.md` (coach-mode), not audit.
- **OKR-KR audit without 4DX framing** — user wants a generic OKR
  health check, alignment review, KR measurability rubric → out-of-
  4DX → route via `using-four-dx-coach`. Audit-mode applies *4DX
  rules* to a list; if the user doesn't want 4DX rules applied, this
  is the wrong skill.
- **Stale-lead diagnosis (lead green, lag flat 4+ weeks)** —
  `4dx-sustain-momentum-rescue`, not D2 audit.

### Author-warned failure modes (audit-mode specific)

- **Audit-as-substitute-for-coaching** — once the audit is delivered,
  user may want full hand-holding through every revision. Resist;
  route to coach-mode for revision sessions. Audit ends, exits.
- **Forced-fit verdicts** — not every artifact maps cleanly. If a
  candidate is a hybrid (KPI / OKR-KR / 4DX-lead mash-up), say so
  explicitly: "this isn't a 4DX lead, it's a [category]; we can drop
  it from the lead set or translate it." Don't force PASS / FAIL on
  out-of-framework artifacts.
- **Stakeholder-deference bias** — the boss / consultant may be
  *wrong*. If the critique doesn't actually map to a 4DX rule, say so:
  "critique doesn't reduce to a Ch. 3 violation — the lead passes
  two-axis + Goodhart-low; recommend KEEP and surface the disagreement
  upstream." Audit serves the framework, not the loudest voice.
- **Goodhart-blindness** — easy to validate KEEP based on two-axis
  alone and skip Step 4. Always score gameability; cite industry
  pattern when medium / high.
- **Cap-creep** — accepting "but all 5 are important" without forcing
  the cut. The cap is hard; if the user can't cut, hand off to coach-
  mode for a guided narrowing session.

### Easily-confused neighbouring concepts

- **`4dx-audit` (cross-discipline)** — covers all 5 layers (WIG / Lead
  / Scoreboard / Cadence / Substrate). Audit-mode here covers L2 only.
- **OKR audit** — different framework lens (alignment + measurability
  on Objective+KR pairs); not 4DX rules.
- **KPI dashboard review** — operational health; not 4DX leads.
- **Coach-mode protocols** — Socratic discovery from zero; this
  protocol synthesizes from an existing artifact.

## Standards used

- `../standards/predictive-and-influenceable.md` — Step 3 two-axis test
- `../standards/goodhart-self-check.md` — Step 4 gameability rating
- `../standards/lead-vs-lag-distinction.md` — Step 3 + Step 6 rule
  classification (lag / sub-WIG / task / OKR-KR distinctions)

## References

See `../references/industry-grounding.md` sections **Goodhart /
Strathern** (mechanism), **Wells Fargo / Phoenix VA / Atlanta APS**
(documented gaming patterns cited in Step 4), **Argyris** (Model-II
inquiry for Step 6 reply-language to stakeholder critique), and
**Source 12: Bravelab.io / Smenżyk** (real-world D2 failure verbatim
anchor — quote *"LEAD measures didn't work. Not everyone was able to
define what he needs to do to bring our efforts closer to our LAG
measure"* when audit reveals the team has well-formed WIGs but reused
KPI dashboards as substitute for behavioral leads — D2 collapse is the
modal failure mode per Bravelab + book Ch 3, not the rare one).
