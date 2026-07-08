# Brief — daily-news-digest: in-story multi-viewpoint (多空對照/分歧點) synthesis

Date: 2026-07-08
Skill: `obsidian/skills/daily-news-digest`
Type: increment to existing skill (skill-text; no code/tests)

## Design-side on-ramp

Not offered — this is a brownfield increment to an existing skill, not
product-shaped new work (Axis 0 negative guard). No principles/design/spec
upstream needed.

## Problem (Axis 1 — JTBD)

When kouko reads the daily digest on **disagreement-heavy topics**
(finance / stocks / investing / macro / geopolitics — topics with no single
correct answer), the job is *"show me the多方 bull/bear/divergence on the same
question so I can weigh them myself"* — not *"tell me what happened."* The
current digest under-serves this: its clustering keeps ~1 representative source
per story and **splits a single debate across tiers**, so the multi-view picture
the user actually wants is fragmented or lost.

Evidence (measured this session, over 19 digests × finance+economy references):
- **88 "漏引"** — sources that were on a digest-day but cited *nowhere* in that
  digest (not in a news story, not in the knowledge tier).
- **Fragmentation example, 2026-07-04**: the "correction healthy vs bubble"
  debate split into 3 disconnected items across 2 tiers — ロジャーパパ
  (technical/leverage risk) → news story A; Grantham/艾財說 (bubble, sell) →
  *separate* news story B; 有錢邏輯 (stay the course) → a one-line knowledge
  link. Three stances on one question, never placed side by side.
- Content-type routing skews stock-analysis/commentary channels (財報狗, 视野
  环球财经, 高校生でも分かる米国株) into knowledge-tier link-only even when the
  episode is about a live event.

## Users (Axis 2)

kouko — data analyst, reads the digest as a **multi-view reference** on
no-single-right-answer topics. Job story: *When I read the daily digest on a
market/macro/geopolitics topic where the KOLs I follow disagree, I want the
bull case, bear case, and the actual point of contention laid out together, so I
can form my own view instead of getting one channel's take.*

## Smallest End State (Axis 3)

Two changes, both in the existing skill's contract text:

**(a) In-story 多空對照/分歧點 block.** **Trigger = LLM judgment**, NOT a fixed
category gate: when the synthesizer — reading the cluster it already opened in
STEP 6 — finds **≥2 sources taking materially differing stances on the same
question**, the story carries a **compact** multi-view block (a small table, or a
`正方 / 反方 / 分歧點` three-row form; **not** N paragraphs). The category anchor
list (Financial Markets & Macro / AI & Technology / Business & Industry / Energy
& Commodities / Geopolitics) is an **anchored-open HINT** — "these are the
domains where real disagreement typically lives, actively look here" — **not a
hard gate**. Rationale: disagreement is a property of the *cluster*, not the
category (a signed ceasefire = no dispute; an oil-price outlook = big dispute,
both under Geopolitics); a category gate is both over- and under-inclusive; and
the "≥2 materially-differing stances" bar already self-concentrates the block in
the disagreement-heavy domains without a rigid list. The **分歧點** row is
mandatory and load-bearing (names *what they actually disagree on*, and whether
it's a genuine split vs one side being consensus — the false-balance guard that
the EN+JA research flagged). Over-firing is throttled by the "materially
differing on the *same* question" bar + the mandatory 分歧點 row, not by category.

**(b) Arc-book 機構觀點 → 觀點交鋒 stance tracking.** Extend the arc book's
optional 機構觀點 section so a recurring debate's **stance evolution over time**
is captured (who is bull/bear on the question, dated), not just sell-side price
targets. A lean tag (多/空/中性) per row.

**Plus two supporting rules:**
- **STEP 4 cluster-by-debate**: cluster by the same *event OR the same
  underlying question/debate*, so bull and bear on one question land in one
  cluster instead of separate stories.
- **Kill 漏引**: every source in a cluster MUST appear in the Source Index under
  that story (already implied by the Hard rules; make it explicit + tie the
  多空對照 sources into it).

## Current State Evidence

- **Forward (how the flow works at the touch points):**
  - STEP 4 clusters strictly "by the same underlying story/event"
    (`SKILL.md:117-123`) — no notion of clustering by *debate/question*.
  - STEP 6 point 2 has only a soft one-liner "surface the disagreement — that
    tension is signal" (`SKILL.md:243-246`); no structured output required.
  - STEP 6 point 4 "add a visual only when it earns its place"
    (`SKILL.md:263-264`) — a 多空對照 table would qualify but isn't specified.
  - The multi-view synthesis form that DOES exist lives only in the **knowledge
    tier**: STEP 7 "bull-case and bear-case → one bull-vs-bear synthesis"
    (`SKILL.md:298`) and the `**整合分析 — <主題,例:Nvidia 多空辯論>**`
    template (`references/digest-format.md:243`). It is not offered inside the
    news-story template.
- **Reverse (SSOT / what feeds what):** `references/digest-format.md`
  §Output template (`:105-283`) is the SSOT for the news-story structure the
  digest renders; `SKILL.md` STEP 6/8 point at it. `references/arc-tracking.md`
  §Book format 機構觀點 (`:66-95`) is the SSOT for arc-book house-views. The
  digest skill is NOT part of the `scripts/distribute.py` code-team mirror — no
  distribution-script SSOT applies here.
- **Error (failure mode at touch point):** 88 漏引 + cross-tier fragmentation
  (above). Root cause is the STEP 4 clustering boundary + the disagreement
  handling being soft prose, not a required artifact.
- **Data:** source notes → STEP 4 cluster → STEP 6 story; STEP 5 reads arc books
  and writes milestone + (optionally) 機構觀點 rows. The 多空對照 block reads the
  same cluster's source notes already opened in STEP 6 point 1.
- **Boundary:** the STEP 4 clustering-granularity decision is where a debate
  gets split; the STEP 6 synthesis is where multi-view either surfaces or
  collapses to one representative.
- Evidence paths: `SKILL.md:114-148, 222-264, 266-310`;
  `references/digest-format.md:48-104, 105-283`;
  `references/arc-tracking.md:52-95`.

## Alternatives Considered (Axis 4 — research-grounded)

Industry approaches (via WebSearch, EN + JA):

1. **Side-by-side perspective panels** — AllSides "Balanced News" places
   left/center/right versions of the same story next to each other; Ground News
   dashboards synthesize multiple sources/ratings into visual cues.
   [AllSides](https://allsides.com/blog/how-does-allsides-create-balanced-news) (EN),
   [Ground News comparison](https://thisvsthat.io/allsidescom-vs-groundnews) (EN).
   • Pro: reader compares stances directly. • Con: both "simplify complex
   editorial behavior into ordinal labels → false precision."
2. **両論併記 (present-both-arguments)** — the established JP journalism
   convention for divided issues: show both sides for balance.
   [日本証券業協会 proverbs](https://www.jsda.or.jp/start/proverb/contents/proverb04.html) (JA),
   [両論併記 critique](https://radiation-sns.com/information/181/) (JA).
   • Pro: culturally standard, compact. • Con (documented): **false balance** —
   両論併記 can present a minority view as equal weight to consensus.
3. **Single synthesized narrative that names the tension in prose** — the
   digest's current soft "surface the disagreement." • Pro: no new structure.
   • Con: under-executed, invisible, no consistent shape (the status quo that
   produced the 88 漏引).

**EN + JA agreement (strong signal):** both cultures treat side-by-side
multi-viewpoint as the correct pattern for divided topics, AND both flag the
**same failure mode — false balance / false precision.** That agreement is why
the design makes the **分歧點 row mandatory** (it names the real axis of
disagreement and can flag "not actually a 50/50 split"), rather than a bare
正/反 two-column table that would risk exactly the false-balance trap both
traditions warn about.

Rejected in our discussion:
- A standalone "今日觀點交鋒" section (option b) — user wants it **inside** the
  story, not a separate section.
- Keeping single-representative — rejected as the core flaw for this user's job.
- Full N-paragraph multi-view — rejected for readability (the richness↔length
  trade-off; the compact block is the resolution).

## Decision

Add a **compact, in-story 多空對照/分歧點 block** to the news-story synthesis
(STEP 6 + digest-format.md story template), firing on **LLM-judged** presence of
≥2 materially-differing stances on the same question (category list is a hint,
not a gate); make the **分歧點 row mandatory** as the false-balance guard.
Extend STEP 4 to **cluster by debate**, extend the arc-book 機構觀點 section into
**觀點交鋒** stance-over-time tracking, and make the "all cluster sources → Source
Index" rule explicit to kill 漏引. We will NOT build a standalone opinion
section, N-paragraph expansions, or any automated stance classifier — stance is
judged by the synthesizer while reading the cluster (same read it already does).

## Out of Scope

- Backfilling digests on no-digest days (separate coverage问题; 83% of the loss,
  but a different task).
- Any change to the triage litmus test itself beyond routing event-tied
  stance-bearing sources into the debate cluster (no wholesale re-triage).
- A machine stance-classifier / sentiment model.
- Changing `cot_mermaid.py` / `digest_check.py` / `arc_check.py` gate scripts
  (the block is prose+table+existing CoT; gates already cover links/mermaid).
- The heavy-day subagent return contract beyond adding the block to the story
  object shape (touch only if the dogfood shows it's needed).

## What Becomes Obsolete (Axis 5)

- The current "keep ~1 representative source per story" **execution habit** —
  replaced by cluster-by-debate + mandatory Source-Index inclusion. (Habit, not
  a written rule, so nothing to delete; the new explicit rule supersedes it.)
- Partially overlaps the knowledge-tier `整合分析` template
  (`digest-format.md:243`) — the news-tier block reuses its shape, so the two
  should be written to share one "多空/分歧" house-style spec rather than diverge.

## Open Questions

None blocking. The block's exact rendering (table vs 正方/反方/分歧點 rows) is a
house-style detail to settle in the template edit; default to a small table when
≥3 stances, the 3-row form when exactly 2 — confirm during dogfood.

## Verification

Dogfood / cold-read on a real disagreement-heavy day (2026-07-04
semiconductor-correction debate is the canonical case; 07-03 Meta/半導體 is a
backup). Pass = the regenerated digest carries an in-story 多空對照/分歧點 block
for the correction debate, every cluster source appears in the Source Index
(zero 漏引 for that story), and the relevant arc book gains a 觀點交鋒/機構觀點
row. No unit test (skill-text).
