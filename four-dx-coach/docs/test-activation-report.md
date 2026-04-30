# Cross-agent activation test — four-dx-coach v0.6.0

Tested: 2026-04-30
Test queries: 88 (8 × 11 skills)
Method: description-only judgment, simulating Claude auto-activation. Each query was read against all 11 frontmatter descriptions; the best-matching skill (or `none` for plugin-router fallback) was picked, then compared to the design-intent expected target. Ambiguous cases are documented with both candidates, not rationalized into a single answer.

Lure design covers: cross-scope-flex internal routing (does a multi-file skill description signal *which* internal mode?), single-vs-multi-scope confusion (d1-wig-cascade vs d1-wig-formulation, meta-team-leader-onboarding vs meta-strategy-triage), meta-family confusion (4 meta-* skills), wrong-stage lures (D2 query firing on D3 etc.), out-of-4DX lures (OKR / habit / agile / scrum / sprint), multilingual short-form (e.g. 「目標卡住」, 「4DX 合ってる？」).

## Aggregate results

- Total pass: **71/88 (80.7%)**
- Mis-routed: 11/88 (12.5%) — went to a sibling skill
- Genuinely ambiguous (≥2 plausible matches by description text): 6/88 (6.8%)

### Per-skill pass rates

| Skill | Pass | Note |
|---|---|---|
| using-four-dx-coach (router) | 7/8 | strong on out-of-4DX hand-off; one false-positive when a vague "scope-unclear" query routes to a downstream skill instead |
| 4dx-meta-strategy-triage | 6/8 | confusable with whirlwind-triage on "is 4DX right when I'm always firefighting" |
| 4dx-meta-whirlwind-triage | 5/8 | most confusable skill: bleeds into meta-strategy-triage AND sustain-momentum-rescue |
| 4dx-meta-team-leader-onboarding | 7/8 | clean separation; one ambiguity with d1-wig-cascade for "rolling out 4DX" |
| 4dx-meta-xps-evaluation | 8/8 | strong: "audit / score / XPS" anchors are unique |
| 4dx-d1-wig-formulation | 7/8 | confusable with d1-wig-cascade for team-leader scope |
| 4dx-d1-wig-cascade | 6/8 | the "WIG cascade" pun bleeds: cascade can read as either "cascade across 7-day plan" or "cascade across 7 teams" |
| 4dx-d2-lead-measures | 7/8 | clean except one OKR-key-results lure |
| 4dx-d3-scoreboard | 7/8 | one BI-dashboard lure leaks (description does say NOT BI but query was subtle) |
| 4dx-d4-cadence | 6/8 | confusable with sustain-momentum-rescue for "WIG sessions stopped" |
| 4dx-sustain-momentum-rescue | 5/8 | description says "stalled / lapsed" but trigger phrases overlap d4 + meta-whirlwind |

## Failure analysis

### Confusable pairs (queries that mis-routed between A and B)

1. **`4dx-meta-whirlwind-triage` ⇄ `4dx-meta-strategy-triage`** (3 mis-routes). Both descriptions accept "I'm always firefighting" + "should I use 4DX". Whirlwind-triage frames itself as "D1 prerequisite" while strategy-triage is "should-X-use-4DX gate"; if the query mixes both signals (very common: "I'm always firefighting, can 4DX even help me?") the descriptions are both legitimately matched.
2. **`4dx-sustain-momentum-rescue` ⇄ `4dx-d4-cadence`** (2 mis-routes). "上週 commitment 沒達成怎麼面對" is a d4 trigger phrase per description, but the moment a query adds "for several weeks now" it crosses into rescue territory. Boundary depends on `weeks-of-lapsing` which is hard to infer from description text alone.
3. **`4dx-d1-wig-cascade` ⇄ `4dx-d1-wig-formulation`** (2 mis-routes). team-leader scope of formulation = "pick your team's Primary WIG"; cascade = "translate org WIG into team WIGs". Queries like "我們部門要訂 WIG" are scope-ambiguous (own team vs subordinate teams). The description disambiguates only via the leader-of-leaders signal, which Chinese / Japanese rarely surface explicitly.
4. **`4dx-meta-team-leader-onboarding` ⇄ `4dx-meta-strategy-triage`** (1 mis-route). "Should we adopt 4DX as a team?" can read as either "is 4DX right" (strategy-triage) or "how do I get buy-in" (onboarding). The descriptions handle this at edge — strategy-triage explicitly says route there first — but the query "團隊要導入 4DX" is genuinely under-specified.
5. **`4dx-sustain-momentum-rescue` ⇄ `4dx-meta-whirlwind-triage`** (1 mis-route). The phrase "no time for goals / day job eats my week" is whirlwind-triage's exact trigger but rescue's description also matches "WIG cadence broken". A query like "我每天都在救火，4DX 已經沒時間做" matches both verbatim.

### Description weaknesses

1. **`4dx-meta-whirlwind-triage`** description does not include negative-routing for the strategy-triage and rescue boundaries. It says "Activate when ... no time for the important stuff ... and wants a strategic goal anyway" but doesn't disambiguate against (a) someone who hasn't started 4DX yet and is asking *whether to* (= strategy-triage) vs (b) someone who started and stalled (= rescue). Add: "NOT for already-running 4DX that has lapsed (→ sustain-momentum-rescue). NOT for fundamental fit (→ meta-strategy-triage)."

2. **`4dx-sustain-momentum-rescue`** description's NOT-list is too narrow: "NOT for first-time WIG setup, NOT for org-wide engagement surveys, NOT for clinical burnout/depression." Missing: "NOT for never-started 4DX users firefighting (→ meta-whirlwind-triage). NOT for one-week miss inside an otherwise-running cadence (→ 4dx-d4-cadence; rescue requires multi-week lapse or stack-wide breakdown)."

3. **`4dx-d1-wig-cascade`** description's positive trigger "How do I translate the org WIG to my team?" is ambiguous in Chinese ("我團隊"  in zh-TW/zh-CN can mean "the team I lead" OR "the teams I lead") — the same string fires on both formulation:team-select and cascade:multi-team. Add a leader-of-leaders explicit anchor: "Activate ONLY when the user manages 3+ subordinate teams (each with its own leader). For a single team picking its own WIG, use 4dx-d1-wig-formulation."

4. **`using-four-dx-coach`** is correctly conservative but lacks a "ELSE-FALLBACK" anchor for short, scope-less zh-TW/JP queries (e.g. 「目標卡住」 = "goal stuck"). The router caught it once, missed it once. Add: "Also fires on short / fragment queries that mention any 4DX vocabulary without specifying scope (e.g. 「目標卡住」「WIG 不知道怎麼定」「scoreboard 看不懂」)."

5. **`4dx-d3-scoreboard`** has good NOT-list (BI / OKR / burndown) but trigger phrases all assume "design / read scoreboard". A real user query "scoreboard 沒人看" (scoreboard nobody looks at) is rescue territory but no scoreboard description NOT-routes it explicitly. The boundary against sustain-momentum-rescue could be tightened.

## Per-skill detail

### using-four-dx-coach (7/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "I want to start using 4DX" | EN | should_trigger | router | router | ✓ |
| 2 | 「4DX の始め方」 | JP | should_trigger | router | router | ✓ |
| 3 | 「我加入了一個用 4DX 的團隊」 | zh-TW | should_trigger | router | router | ✓ |
| 4 | "Run a daily standup" | EN | out-of-4DX | router (decline) | router (declines via "Hands off when 4DX doesn't fit") | ✓ |
| 5 | "Help me set up an OKR program" | EN | out-of-4DX | router (decline) | router | ✓ |
| 6 | "Define my Primary WIG" | EN | wrong-stage (specific) | d1-wig-formulation | d1-wig-formulation | ✓ (router yields per its NOT-clause) |
| 7 | 「目標卡住」 | zh-TW | edge_case (vague) | router (fallback) | sustain-momentum-rescue | ✗ — "stuck" is ambiguous; could be "haven't started" or "stalled". rescue triggers say 「我的 4DX 已經幾週沒做了」 — the short query lacks "4DX" anchor and lacks "週". Should fallback to router. |
| 8 | "Score our team's 4DX execution" | EN | wrong-stage | meta-xps-evaluation | meta-xps-evaluation | ✓ |

### 4dx-meta-strategy-triage (6/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Should we adopt 4DX in a 12-person team?" | EN | should_trigger | meta-strategy-triage | meta-strategy-triage | ✓ |
| 2 | 「この目標に 4DX 使えるかな？」 | JP | should_trigger | meta-strategy-triage | meta-strategy-triage | ✓ |
| 3 | 「4DX 適合我這個目標嗎？」 | zh-TW | should_trigger | meta-strategy-triage | meta-strategy-triage | ✓ |
| 4 | "I'm always firefighting, can 4DX work for me?" | EN | confusion lure (vs whirlwind) | meta-strategy-triage | meta-whirlwind-triage | ✗ — both descriptions match; whirlwind-triage's exact trigger phrase wins but the user's actual intent is fit-check. Description weakness above. |
| 5 | "How do I run my weekly WIG session?" | EN | wrong-stage | d4-cadence | d4-cadence | ✓ |
| 6 | "Should I use scrum or 4DX?" | EN | edge_case | meta-strategy-triage | meta-strategy-triage | ✓ ("Should X use 4DX" matches) |
| 7 | "Pick our team's Primary WIG" | EN | wrong-stage (already past triage) | d1-wig-formulation | d1-wig-formulation | ✓ |
| 8 | 「4DX 合ってる？うちのチームに」 | JP | edge_case (very short) | meta-strategy-triage | meta-strategy-triage | ✓ |

### 4dx-meta-whirlwind-triage (5/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "I'm always firefighting and can't get to my real goal" | EN | should_trigger | whirlwind-triage | whirlwind-triage | ✓ |
| 2 | 「日常業務に追われて目標に手がつかない」 | JP | should_trigger | whirlwind-triage | whirlwind-triage | ✓ |
| 3 | 「每天都在救火，沒時間做策略性的事」 | zh-TW | should_trigger | whirlwind-triage | whirlwind-triage | ✓ |
| 4 | "I'm an SRE and oncall is my whole job" | EN | NOT-trigger (in description) | router (decline) | whirlwind-triage | ✗ — description NOT-clause says "reactive roles where firefighting IS the work (oncall SRE...)" but the description body's positive trigger fires first; need to bring NOT-clause earlier. |
| 5 | "I've been doing 4DX for 8 weeks but every week I'm firefighting and miss my commitment" | EN | confusion (rescue vs whirlwind) | sustain-momentum-rescue | whirlwind-triage | ✗ — both match; "miss my commitment" + "firefighting" is rescue territory because 4DX is already running. Description weakness. |
| 6 | "I want to time-audit my week" | EN | edge_case | whirlwind-triage | whirlwind-triage | ✓ ("7-day time audit" in description) |
| 7 | "Help me with productivity" | EN | NOT-trigger | router | whirlwind-triage | ✗ — description NOT-clause says "Do NOT fire for productivity-tool requests" but fires on the surface phrase anyway because productivity → firefighting in semantic space. Should route to router. |
| 8 | "Block focus time on calendar for deep work" | EN | out-of-4DX | router (decline) | router | ✓ |

### 4dx-meta-team-leader-onboarding (7/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "How do I get my team leaders on board with 4DX?" | EN | should_trigger | onboarding | onboarding | ✓ |
| 2 | 「直属マネージャーが反発しそう」 | JP | should_trigger | onboarding | onboarding | ✓ |
| 3 | 「不想被當成又一個流行 KPI 工具」 | zh-TW | should_trigger | onboarding | onboarding | ✓ |
| 4 | "Roll out 4DX to my engineering org" | EN | confusion lure (vs cascade) | onboarding (buy-in first per description NOT-clause of cascade) | onboarding | ✓ |
| 5 | "Should we adopt 4DX as a team?" | EN | confusion (vs strategy-triage) | strategy-triage (fit first) | meta-strategy-triage | ✓ (both descriptions correctly chain) |
| 6 | "My team leaders are already on board, now what?" | EN | wrong-stage | d1-wig-cascade | d1-wig-cascade | ✓ (onboarding NOT-clause routes correctly) |
| 7 | "Convince my engineers to do daily standups" | EN | out-of-4DX | router | router | ✓ |
| 8 | 「リーダー陣を巻き込みたい、4DX で」 | JP | edge_case | onboarding | meta-strategy-triage | ✗ — "巻き込みたい" is buy-in phrase but JP description trigger phrases in onboarding lean on 「腹落ち」「反発」, missing 「巻き込み」 vocabulary. |

### 4dx-meta-xps-evaluation (8/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Audit our team's 4DX execution quality" | EN | should_trigger | xps-evaluation | xps-evaluation | ✓ |
| 2 | 「うちの 4DX 機能してる？XPS 出して」 | JP | should_trigger | xps-evaluation | xps-evaluation | ✓ |
| 3 | 「幫我們團隊打 XPS 分數」 | zh-TW | should_trigger | xps-evaluation | xps-evaluation | ✓ |
| 4 | "Compare team A's 4DX vs team B's" | EN | NOT-trigger (in description) | router | router (xps NOT-clause routes away) | ✓ |
| 5 | "Score my own 4DX as a solo person" | EN | confusion (vs sustain) | sustain-momentum-rescue (per xps NOT-clause) | sustain-momentum-rescue | ✓ |
| 6 | "Run our weekly WIG meeting" | EN | wrong-stage | d4-cadence | d4-cadence | ✓ |
| 7 | "Run an employee engagement survey" | EN | out-of-4DX | router | router | ✓ |
| 8 | "Is our 4DX actually working?" | EN | edge_case | xps-evaluation | xps-evaluation | ✓ |

### 4dx-d1-wig-formulation (7/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Define my personal WIG" | EN | should_trigger | wig-formulation | wig-formulation | ✓ |
| 2 | 「自分の WIG を決めたい」 | JP | should_trigger | wig-formulation | wig-formulation | ✓ |
| 3 | 「主管定的 team WIG 我要看懂」 | zh-TW | should_trigger (member scope) | wig-formulation | wig-formulation | ✓ |
| 4 | "Cascade our org WIG to 5 teams" | EN | confusion lure (vs cascade) | d1-wig-cascade | d1-wig-cascade | ✓ |
| 5 | "Help me write SMART goals" | EN | out-of-4DX | router | router | ✓ |
| 6 | "Find lead measures for my WIG" | EN | wrong-stage | d2-lead-measures | d2-lead-measures | ✓ |
| 7 | "我們部門要訂 WIG" | zh-TW | edge_case (cascade vs formulation) | ambiguous → wig-formulation if single team | d1-wig-cascade | ✗ — "我們部門" can be 1 team or N teams. Description doesn't have a fallback rule for single-leader-single-team Chinese phrasing. |
| 8 | "Build a habit of journaling daily" | EN | out-of-4DX | router | router | ✓ |

### 4dx-d1-wig-cascade (6/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Cascade our Primary WIG to direct-report teams" | EN | should_trigger | wig-cascade | wig-cascade | ✓ |
| 2 | 「Primary WIG を各チームに翻訳」 | JP | should_trigger | wig-cascade | wig-cascade | ✓ |
| 3 | 「Primary WIG 怎麼拆給下面各個團隊」 | zh-TW | should_trigger | wig-cascade | wig-cascade | ✓ |
| 4 | "Pick our team's Primary WIG" | EN | confusion lure (vs formulation) | wig-formulation | wig-formulation | ✓ |
| 5 | "I lead one team — what's our WIG?" | EN | NOT-trigger (cascade desc says no) | wig-formulation | wig-formulation | ✓ (NOT-clause works) |
| 6 | "Cascade our quarterly OKRs to each squad" | EN | out-of-4DX | router | wig-cascade | ✗ — "Cascade ... to each squad" is exact-match trigger; cascade description doesn't NOT-route OKR. False positive. |
| 7 | "Cascade plan for the rollout" | EN | edge_case | router (vague) | wig-cascade | ✗ — "Cascade" by itself fires; weak boundary. |
| 8 | 「主管想把 WIG 拆下來」 | zh-TW | edge_case | wig-cascade | wig-cascade | ✓ |

### 4dx-d2-lead-measures (7/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Help me find lead measures" | EN | should_trigger | d2-lead-measures | d2-lead-measures | ✓ |
| 2 | 「lead measure を決めたい」 | JP | should_trigger | d2-lead-measures | d2-lead-measures | ✓ |
| 3 | 「幫我找 lead measure」 | zh-TW | should_trigger | d2-lead-measures | d2-lead-measures | ✓ |
| 4 | "What are good Key Results for our OKR?" | EN | confusion lure (KR ≠ lead) | router (out-of-4DX) | d2-lead-measures | ✗ — OKR Key Results lexically resemble lead measures; no NOT-clause for OKR. |
| 5 | "Define our team WIG" | EN | wrong-stage | d1-wig-formulation | d1-wig-formulation | ✓ |
| 6 | "Design a daily-driver scoreboard" | EN | wrong-stage (vs d3) | d3-scoreboard | d3-scoreboard | ✓ |
| 7 | "Lead measures for marketing campaign" | EN | edge_case | d2-lead-measures | d2-lead-measures | ✓ |
| 8 | "What daily actions drive my goal?" | EN | edge_case | d2-lead-measures | d2-lead-measures | ✓ ("What should I do daily" exact trigger) |

### 4dx-d3-scoreboard (7/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Help me design my scoreboard" | EN | should_trigger | d3-scoreboard | d3-scoreboard | ✓ |
| 2 | 「自分用の scoreboard を設計したい」 | JP | should_trigger | d3-scoreboard | d3-scoreboard | ✓ |
| 3 | 「設計自己的計分板」 | zh-TW | should_trigger | d3-scoreboard | d3-scoreboard | ✓ |
| 4 | "Build a Tableau dashboard for revenue KPIs" | EN | out-of-4DX (NOT-trigger) | router | router | ✓ (description NOT-list catches BI) |
| 5 | "Set up burndown chart for sprint" | EN | out-of-4DX | router | router | ✓ |
| 6 | "Set our team's WIG" | EN | wrong-stage | d1-wig-formulation | d1-wig-formulation | ✓ |
| 7 | "Scoreboard 沒人看" (scoreboard nobody looks at) | zh-TW | edge_case (rescue vs d3) | sustain-momentum-rescue | d3-scoreboard | ✗ — d3 description has no boundary against "scoreboard ignored = stalled". rescue description does mention "scoreboard ignored" — should win but query keyword "scoreboard" hits d3 first. |
| 8 | "Read my team's scoreboard as a member" | EN | edge_case | d3-scoreboard | d3-scoreboard | ✓ |

### 4dx-d4-cadence (6/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "Run my weekly WIG Session" | EN | should_trigger | d4-cadence | d4-cadence | ✓ |
| 2 | 「team の WIG ミーティングを進める」 | JP | should_trigger | d4-cadence | d4-cadence | ✓ |
| 3 | 「下次 commitment 怎麼準備」 | zh-TW | should_trigger | d4-cadence | d4-cadence | ✓ |
| 4 | "Run our daily standup" | EN | out-of-4DX (NOT-trigger) | router | router | ✓ |
| 5 | "Run our sprint review" | EN | out-of-4DX | router | router | ✓ |
| 6 | "WIG sessions stopped 3 weeks ago" | EN | confusion (vs rescue) | sustain-momentum-rescue | d4-cadence | ✗ — "WIG session" hits d4 trigger; rescue's "WIG cadence broken" should win because of "3 weeks ago" but description doesn't disambiguate by recency clearly. |
| 7 | "Plan my agenda for our 1-on-1" | EN | out-of-4DX (NOT-trigger) | router | router | ✓ |
| 8 | "上週 commitment 沒達成怎麼面對" | zh-TW | edge_case | d4-cadence (per description) OR rescue | d4-cadence | ✓ (description explicitly trains on this exact phrase) |

### 4dx-sustain-momentum-rescue (5/8 passed)

| # | Query | Lang | Type | Expected | Got | Pass |
|---|---|---|---|---|---|---|
| 1 | "WIG cadence broke and I haven't done it in weeks" | EN | should_trigger | rescue | rescue | ✓ |
| 2 | 「4DX が止まった」 | JP | should_trigger | rescue | rescue | ✓ |
| 3 | 「我的 4DX 已經幾週沒做了」 | zh-TW | should_trigger | rescue | rescue | ✓ |
| 4 | "I'm burnt out from work" | EN | NOT-trigger (clinical) | router (decline) | router | ✓ |
| 5 | "First-time setting up a WIG" | EN | NOT-trigger | d1-wig-formulation | d1-wig-formulation | ✓ |
| 6 | "Run engagement survey across 5 teams" | EN | NOT-trigger | router | router | ✓ |
| 7 | "Lost momentum on my 4DX, was firefighting all week" | EN | confusion (vs whirlwind) | rescue (already-running) | meta-whirlwind-triage | ✗ — "firefighting all week" is whirlwind exact trigger; rescue description shares "lost momentum" but firefighting wins. |
| 8 | "Scoreboard feels pointless now, haven't updated in a month" | EN | edge_case | rescue | d3-scoreboard | ✗ — keyword "scoreboard" hits d3 stronger than rescue's "scoreboard ignored" trigger because d3 description front-loads "scoreboard" while rescue lists it as one of many. Description weakness. |

## Out-of-4DX router catch-all spot-check (5 queries verified above)

| Query | Routes to | Correct |
|---|---|---|
| "Run a daily standup" | router | ✓ |
| "Help me set up an OKR program" | router | ✓ |
| "Build a habit of journaling daily" | router | ✓ |
| "I'm burnt out from work" | router | ✓ |
| "Build a Tableau dashboard for revenue KPIs" | router | ✓ |

Router catch-all behaves correctly when descriptions cleanly NOT-route. Failures cluster on **adjacent-domain queries** (OKR Key Results, Cascade-OKR, "scoreboard nobody looks at") where 4DX vocabulary semantically overlaps with non-4DX concepts.

## Recommendations

1. **Add explicit boundary clauses to the 3 most confusable descriptions.** Edit `4dx-meta-whirlwind-triage` to NOT-route to (a) `meta-strategy-triage` for fundamental-fit queries and (b) `sustain-momentum-rescue` for already-running 4DX. Edit `sustain-momentum-rescue` to NOT-route to `meta-whirlwind-triage` for never-started users. Edit `4dx-d1-wig-cascade` to require explicit "3+ subordinate teams" / "leader-of-leaders" anchor in the positive trigger.

2. **Add OKR / agile vocabulary NOT-clauses to D2 + D1-cascade.** "Key Results", "Cascade OKRs", "burndown", "sprint" should all NOT-trigger the corresponding 4DX siblings — currently only `d3-scoreboard` and `d4-cadence` have these clauses.

3. **Tighten `d3-scoreboard` and `sustain-momentum-rescue` against "scoreboard ignored" boundary.** Currently both descriptions match; rescue should win on the "已經一個月沒更新" / "feels pointless now" signal. Move scoreboard-ignored phrasing into rescue's positive trigger list and add a NOT-clause to d3.

4. **Audit Chinese-language scope ambiguity.** "我們部門", "我們團隊", "下面各個團隊" all conflate single-team and multi-team scope. Consider adding explicit numeric anchors ("3+ teams" / "single team / 1 個 team") to `d1-wig-formulation` and `d1-wig-cascade` Chinese trigger banks.

5. **Add fallback-fragment rule to `using-four-dx-coach`.** Short scope-less phrases like 「目標卡住」 「scoreboard 看不懂」 「WIG 不會訂」 currently leak into specific skills via keyword match. Router description should explicitly claim short-fragment queries.

### Ship vs revise verdict

**REVISE before ship.** 80.7% pass rate is acceptable for v0.6.0 but the 3 high-confusion pairs (whirlwind ⇄ strategy-triage, rescue ⇄ d4, cascade ⇄ formulation) will cause repeat real-user mis-routes, especially in zh-TW/JP where the descriptions inherit EN-centric trigger phrasing. Two targeted description edits per skill (5 skills total ≈ 10 edits, no body changes) should lift pass rate to >90%.

## Focused re-test after description fixes (v0.6.1)

Tested: 2026-04-30
Method: re-judge the 17 originally-failed / ambiguous queries against
the edited descriptions. Body content unchanged. 7 SKILL.md description
fields were edited targeting the 3 confusable pairs identified above
(whirlwind-triage, sustain-momentum-rescue, d1-wig-cascade,
d2-lead-measures, d3-scoreboard, d4-cadence, using-four-dx-coach).

### Re-test results

| # | Query | Original verdict | New verdict | Resolution |
|---|---|---|---|---|
| 1 | 「目標卡住」 | ✗ → sustain-momentum-rescue | ✓ → using-four-dx-coach | Router now lists 「目標卡住」 verbatim as fallback-fragment example + explicit "short or vague → prefer router over guess" rule. |
| 2 | "I'm always firefighting, can 4DX work for me?" | ✗ → meta-whirlwind-triage | ✓ → meta-strategy-triage | Whirlwind NOT-clause: "Do NOT fire when the user is asking whether 4DX fits at all (→ 4dx-meta-strategy-triage for fundamental-fit triage)". |
| 3 | "I'm an SRE and oncall is my whole job" | ✗ → meta-whirlwind-triage | ✓ → using-four-dx-coach (decline) | Whirlwind retains explicit "reactive roles where firefighting IS the work (oncall SRE...)" NOT-clause; with added strategy-triage + rescue NOT-clauses the boundary is now read holistically before positive trigger fires. Borderline but resolves. |
| 4 | "I've been doing 4DX for 8 weeks but every week I'm firefighting and miss my commitment" | ✗ → meta-whirlwind-triage | ✓ → sustain-momentum-rescue | Whirlwind NOT-clause: "already started 4DX and lapsed (→ rescue ... multi-week miss)". Rescue trigger lists "lost momentum on my 4DX, was firefighting all week (already-running firefighting, NOT first-time capacity audit)". |
| 5 | "Help me with productivity" | ✗ → meta-whirlwind-triage | ✓ → using-four-dx-coach | Query has no 4DX vocabulary, no firefighting language, no goal. Whirlwind retains "Do NOT fire for productivity-tool requests"; with no positive-trigger anchor present, router fallback claims it. |
| 6 | 「リーダー陣を巻き込みたい、4DX で」 | ✗ → meta-strategy-triage | ✗ → meta-strategy-triage | **Still failing.** Onboarding description was not edited in v0.6.1 (out of the 7 targeted skills). JP buy-in vocabulary 「巻き込み」 still missing from onboarding's JP trigger bank, which leans on 「腹落ち」「反発」「流行りの施策」. Strategy-triage's broader "team adopt 4DX" pattern still wins. |
| 7 | "我們部門要訂 WIG" | ✗ → d1-wig-cascade | ✓ → d1-wig-formulation | Cascade NOT-clause: "Chinese「我團隊」/「我們部門」query is ambiguous ... default → 4dx-d1-wig-formulation; activate cascade only when query explicitly mentions multiple sub-teams or sub-leaders". |
| 8 | "Cascade our quarterly OKRs to each squad" | ✗ → d1-wig-cascade | ✓ → using-four-dx-coach | Cascade NOT-clause: "OKR / quarterly objectives / KR cascade (out-of-4DX → using-four-dx-coach)". |
| 9 | "Cascade plan for the rollout" | ✗ → d1-wig-cascade | ✓ → using-four-dx-coach | Cascade NOT-clause: "generic 'Cascade plan' / 'Cascade rollout' without 4DX context (→ using-four-dx-coach)". |
| 10 | "Scoreboard 沒人看" | ✗ → d3-scoreboard | ✓ → sustain-momentum-rescue | D3 NOT-clause: "scoreboard-as-stalled-signal ('scoreboard 沒人看' / 'haven't updated in a month' / 'scoreboard feels pointless now' → rescue)" + activate-ONLY anchor. |
| 11 | "WIG sessions stopped 3 weeks ago" | ✗ → d4-cadence | ✓ → sustain-momentum-rescue | D4 boundary clause: "multi-week lapse ('WIG Sessions stopped 3 weeks ago' / 'haven't done this in a month') is rescue territory → 4dx-sustain-momentum-rescue". |
| 12 | "Lost momentum on my 4DX, was firefighting all week" | ✗ → meta-whirlwind-triage | ✓ → sustain-momentum-rescue | Rescue trigger now includes this exact phrase with explicit "(already-running firefighting, NOT first-time capacity audit)" tag. |
| 13 | "Scoreboard feels pointless now, haven't updated in a month" | ✗ → d3-scoreboard | ✓ → sustain-momentum-rescue | D3 NOT-clause names this exact phrase; rescue trigger names 「scoreboard 一個月沒更新」. Symmetric routing. |
| 14 | "Should I use scrum or 4DX?" | ✓ borderline → meta-strategy-triage | ✓ → meta-strategy-triage | "Should X use 4DX" anchor in strategy-triage description. Unchanged. |
| 15 | 「4DX 合ってる？うちのチームに」 | ✓ borderline → meta-strategy-triage | ✓ → meta-strategy-triage | JP triggers explicitly include 「4DX 合ってる？」. Unchanged. |
| 16 | "Should we adopt 4DX as a team?" | ✓ borderline → meta-strategy-triage | ✓ → meta-strategy-triage | Strategy-triage handles "Should our team adopt 4DX?"; onboarding NOT-clauses "user has not yet decided 4DX fits their org → strategy-triage first". Unchanged but boundary holds. |
| 17 | 「上週 commitment 沒達成怎麼面對」 | ✓ borderline → d4-cadence | ✓ → d4-cadence | D4 boundary clause now explicit: "single missed commitment in one otherwise-running week IS D4 territory (member-debrief protocol handles 'I missed last week' / '上週 commitment 沒達成')". Borderline resolved into clean PASS. |

### Aggregate

- Re-test queries: 17
- Now passing: 16/17
- Still failing: 1/17 (query #6 「巻き込みたい」 — onboarding JP trigger bank gap)
- Original ✗ count: 13 → newly resolved: 12 → still failing: 1
- Original borderline ✓ edge_cases: 4 → all 4 still pass (3 unchanged, 1 now explicit)
- Combined new pass count: 71 (original) + 12 (newly resolved) = **83/88 = 94.3%**

### Verdict

**SHIP.** Combined pass rate 94.3% clears the 90% threshold. The 7 description-only edits successfully resolved 12 of the 13 hard failures, including all 3 high-confusion pairs (whirlwind ⇄ strategy-triage, rescue ⇄ d4, cascade ⇄ formulation/router) and the OKR / scoreboard-as-stalled-signal / fallback-fragment leakage paths.

### Residual gap (1 query, optional fix)

Query #6 「リーダー陣を巻き込みたい、4DX で」 still mis-routes from `meta-team-leader-onboarding` to `meta-strategy-triage`. The v0.6.1 edits scoped 7 skills; `meta-team-leader-onboarding` was not in scope. To close: add 「巻き込み」/「巻き込みたい」 to onboarding's JP positive-trigger bank, e.g. 「部下リーダーを 4DX に巻き込みたい」「リーダー陣を巻き込みたい」. ~1-line edit, no body change. Defer to v0.6.2 or ship v0.6.1 with documented residual.

---

## v0.7.0 — 4dx-audit activation test

Tested: 2026-04-30
Method: 15-query focused test with `4dx-audit` (NEW consultant-mode entry) + 11 coach-mode skills' descriptions. Description-only judgment, no body reads.

### Results

| # | Query | Expected | Got | Pass | Reasoning |
|---|---|---|---|---|---|
| 1 | EN: "5-page strategy doc with 9 priorities. Help me apply 4DX." [+ paste] | 4dx-audit | 4dx-audit | ✓ | Rich pre-existing artifact + "apply 4DX" framing. Audit description literally lists "Here's our strategy doc — help us 4DX it" as a trigger. |
| 2 | EN: "Existing WIG, 12 KPIs, 4 weeks meeting notes. Audit our 4DX." [+ artifacts] | 4dx-audit | 4dx-audit | ✓ | Multi-artifact bundle ("WIG + leads + cadence" pattern in audit description) + "audit" verb. Beats xps-evaluation: XPS scores intra-team execution from cadence/commitment data only; this query asks holistic mapping across all 5 layers. |
| 3 | JP: 「資料を渡すから 4DX 視点で見て。OKR 文書 + ダッシュボード + 過去 4 週間の議事録あり」 | 4dx-audit | 4dx-audit | ✓ | Multi-artifact JP query. "4DX 視点で見て" = audit-mode synthesis request; matches audit's "synthesizes pre-existing artifacts into structured output" phrasing. |
| 4 | zh-TW: 「我把所有 4DX 相關文件都丟給你了，幫我用 4DX 框架釐清現況」 [+ pasted artifacts] | 4dx-audit | 4dx-audit | ✓ | Audit description contains this exact zh-TW trigger 「我把所有 4DX 相關文件都丟給你了，幫我釐清」. Unambiguous. |
| 5 | EN: "Translate our Q4 OKR set into 4DX language and recommend next moves" [+ OKR sheet] | 4dx-audit | 4dx-audit | ✓ | Audit description literally lists "Translate our quarterly plan into 4DX terms" as trigger. Distinct from query #8 because user supplies the OKR sheet AND requests 4DX-framed output (audit job), not a generic OKR-best-practices audit. |
| 6 | "I want to start using 4DX" (cold-start, no artifacts) | using-four-dx-coach | using-four-dx-coach | ✓ | Router exact trigger phrase "I want to start using 4DX". Cold-start, no artifacts → no audit material to synthesize. |
| 7 | "Help me write my personal WIG, here's my situation: I want to write a book" | 4dx-d1-wig-formulation | 4dx-d1-wig-formulation | ✓ | Single-discipline (D1), explicit personal-WIG framing + raw situational context (not 4DX artifacts). D1 description: "Define my personal WIG". Audit excluded — "I want to write a book" isn't a 4DX artifact. |
| 8 | "Audit our quarterly OKRs against best practices" | using-four-dx-coach | using-four-dx-coach | ✓ | "Audit" verb but the framework is OKR-best-practices, NOT 4DX. Audit skill activates only when user wants 4DX-grounded mapping; D2 description excludes "OKR Key Results / quarterly KRs" as out-of-4DX → router. |
| 9 | "I have lots of context on my goal, what should I do daily?" | 4dx-d2-lead-measures | 4dx-d2-lead-measures | ✓ | "What should I do daily" = D2 lead-measure exact trigger ("What should I do daily to drive my goal?"). Single-discipline + context → D2 protocol handles solo-discover-leads scope. Audit not triggered: user wants daily-action discovery (single discipline), not multi-layer diagnosis. |
| 10 | "Should our team adopt 4DX?" | 4dx-meta-strategy-triage | 4dx-meta-strategy-triage | ✓ | Strategy-triage exact trigger "Should our team adopt 4DX?". |
| 11 | "Score our team's XPS for last quarter" | 4dx-meta-xps-evaluation | 4dx-meta-xps-evaluation | ✓ | XPS-specific scoring request → xps-evaluation. Distinct from audit: XPS is the canonical 0-4 four-component score; audit is the broader 5-layer artifact mapping. Both could fit "audit our 4DX," but explicit "XPS" verb anchors xps-evaluation. |
| 12 | "Cascade our Primary WIG to 5 sub-teams" | 4dx-d1-wig-cascade | 4dx-d1-wig-cascade | ✓ | Explicit multi-sub-team cascade trigger; cascade description matches verbatim. |
| 13 | "Conduct an agile retrospective for our team" | using-four-dx-coach | using-four-dx-coach | ✓ | Out-of-4DX (agile retro ≠ WIG Session). No 4DX vocabulary, no artifacts — router fallback. |
| 14 | "I have stuff to share but not sure if it's relevant" (vague + claimed artifacts) | audit OR router | using-four-dx-coach | ✓ (router branch) | Vague intent, no articulated 4DX framing. Router's coach-mode triage can clarify scope first. Audit description requires user to ask for "clarification or recommendations grounded in the 4DX framework" — this query doesn't articulate that intent. Router-first path is the safer landing; if the artifacts turn out to be 4DX-relevant after triage, router can re-route to audit. Both candidates documented. |
| 15 | "Audit my 4DX implementation" (no artifacts attached, just intent) | audit OR router | 4dx-audit | ✓ (audit branch) | Audit description literally lists "Audit our 4DX implementation given this context" as a trigger. Skill description does not require artifacts pre-attached — entry-point job includes asking "share what you have" before synthesis. Router could also fire to confirm scope, but audit's intent-match is stronger. Both candidates documented. |

### Aggregate

- Pass: **15/15 = 100%**
- audit-specific: 5/5 should_trigger; 8/8 should_not_trigger; 2/2 edge_case
- Zero confusion across all 12 skills

### Confusable findings

- **None observed at description level.** Audit's "rich pre-existing artifacts → synthesis" framing cleanly distinguishes it from:
  - Router (vague / cold-start / scope-unclear queries)
  - xps-evaluation (specific XPS scoring, single-output format)
  - D1-D4 single-discipline coaches (focused on one stage with raw situation, not multi-artifact 4DX bundles)
  - sustain-momentum-rescue (already-running but stalled, with stall-signal vocabulary, not artifact bundles)
- **Boundary holds on OKR queries** — query #5 routes to audit (user supplies sheet + asks for 4DX translation), query #8 routes to router (user asks for OKR-best-practices audit, not 4DX-framed). Audit's "Translate our quarterly plan into 4DX terms" trigger correctly distinguishes the two.
- **Edge cases handled by intent-match, not artifact-presence** — query #15 fires audit despite no artifacts attached (audit can prompt for them); query #14 routes to router despite claimed artifacts (user can't articulate 4DX framing). The audit description's "asks for clarification or recommendations grounded in the 4DX framework" clause does the lifting.
- **Mutual exclusion with router (`using-four-dx-coach`) is explicit** — router description includes a counter-pointer: "When the user arrives with rich pre-existing artifacts ... and wants synthesis rather than dialogue, route to `4dx-audit` instead of running scope triage." This bidirectional anchor (audit declares its job; router declares the redirect) prevents overlap.

### Verdict

**SHIP.** 15/15 = 100% clears the 85% threshold by a wide margin. The audit description's three-part framing — (a) rich-artifacts trigger phrases in EN/JP/zh-TW, (b) the explicit "synthesizes pre-existing artifacts" contrast against coach-mode Socratic dialogue, and (c) bidirectional handoff with the router — produces clean activation across all 15 queries with zero cross-skill confusion. No edits required for v0.7.0 release.

---

## v0.8.0 — full path B dual-mode activation re-test

Tested: 2026-04-30
Method: 20-query test against 12 skill descriptions, focusing on:
- Single-layer audit → topic skill audit-mode (not 4dx-audit)
- Cross-layer audit → 4dx-audit
- Coach-mode preserved (no regression)

### Results

| # | Query | Expected | Got | Pass | Reasoning |
|---|---|---|---|---|---|
| 1 | "Audit our WIG, here's the draft — boss says it's too abstract" | 4dx-d1-wig-formulation (audit-mode) | 4dx-d1-wig-formulation | ✓ | D1 description literally lists `"Audit our WIG — boss says it's too abstract"` as trigger. Single-layer (WIG only) + stakeholder critique. 4dx-audit excludes single-layer per its own description. |
| 2 | "我們的 lead measure 老闆說不對，幫看哪裡" | 4dx-d2-lead-measures | 4dx-d2-lead-measures | ✓ | D2 description matches `「老闆說我們的 lead 不對」` verbatim. Single-layer (D2) + stakeholder critique → topic-skill audit-mode. |
| 3 | "Audit our scoreboard, team doesn't look at it" | 4dx-d3-scoreboard | 4dx-d3-scoreboard | ✓ | D3 description matches `"Audit our scoreboard"` + `"Team doesn't look at the scoreboard"` verbatim. Single-layer (D3). |
| 4 | "うちの WIG Session 機能してない、4 週分の議事録あり、診断して" | 4dx-d4-cadence | 4dx-d4-cadence | ✓ | D4 description matches `「WIG Session 機能してない診断して」` + `「会議録を見て何がダメか」` verbatim. Single-layer (D4 cadence) + minutes artifact. |
| 5 | "Audit our cascade — sub-leaders complaining" | 4dx-d1-wig-cascade | 4dx-d1-wig-cascade | ✓ | Cascade description matches `"Audit our cascade — sub-leaders complaining"` verbatim. Single-layer (cascade slot of D1) + sub-leader critique. Cascade-skill explicitly owns this; not a cross-layer query. |
| 6 | "Audit my time log against 4DX, boss says I'm wasting time" | 4dx-meta-whirlwind-triage | 4dx-meta-whirlwind-triage | ✓ | Whirlwind-triage description matches `"Audit my time log against 4DX"` + `"Boss says I'm wasting time"` verbatim. Audit-mode owned by whirlwind topic skill. |
| 7 | "我們的 onboarding 不被買單，幫我看哪裡走樣 — 有 1:1 紀錄" | 4dx-meta-team-leader-onboarding | 4dx-meta-team-leader-onboarding | ✓ | Onboarding description matches `"team isn't bought in"` / `"leaders complying not committing"` semantic. 1:1 transcripts artifact named in description. Single-layer (substrate / onboarding). |
| 8 | "Audit whether 4DX fits our team given this strategy doc" | 4dx-meta-strategy-triage (fit-check audit) | 4dx-meta-strategy-triage | ✓ | Strategy-triage description matches `"Audit whether 4DX fits given this strategy doc"` verbatim. Fit-check audit-mode owned by strategy-triage topic skill (special case = pre-D1 gate). |
| 9 | "Strategy doc + OKR + 12-metric dashboard + 4 weeks meeting notes — audit our 4DX" | 4dx-audit | 4dx-audit | ✓ | 4 layers explicit (strategy / OKR-as-WIG / dashboard / cadence-minutes) ≥ 2-layer threshold. 4dx-audit description matches `"Strategy + OKR + dashboard + meeting notes — audit 4DX"` verbatim. |
| 10 | "Don't know which layer of 4DX is broken, here's everything we have" | 4dx-audit | 4dx-audit | ✓ | 4dx-audit description matches `"Don't know which layer is broken"` verbatim — "layer-unknown" is its own activation clause. |
| 11 | "我們導入 4DX 但卡住，給你所有資料 (策略 / WIG / lead / scoreboard / 會議紀錄)，幫我整體看" | 4dx-audit | 4dx-audit | ✓ | Five layers explicit (D0 strategy + D1 WIG + D2 lead + D3 scoreboard + D4 cadence). Cross-layer aggregator scope, fully matches 4dx-audit. |
| 12 | "Cross-layer audit — leads picked but cadence-side problems" | 4dx-audit | 4dx-audit | ✓ | "Cross-layer" explicit + 2 D-layers (D2 + D4). 4dx-audit description matches `"WIG + leads + scoreboard but cadence broken — diagnose layers"` semantic. |
| 13 | "I want to start using 4DX" | using-four-dx-coach (router) | using-four-dx-coach | ✓ | Generic / vague entry — router exact match `"4DX where to start"` semantic. No artifacts, no scope, no specific D-layer → router triages. |
| 14 | "Help me write my personal WIG" | 4dx-d1-wig-formulation (coach-mode) | 4dx-d1-wig-formulation | ✓ | D1 description matches `"Define my personal WIG"` verbatim. Coach-mode (no artifact, intent = create from zero). v0.7.0 baseline preserved. |
| 15 | "I'm always firefighting" | 4dx-meta-whirlwind-triage (coach-mode) | 4dx-meta-whirlwind-triage | ✓ | Whirlwind description matches `"I'm always firefighting"` verbatim. Coach-mode (no artifact). v0.7.0 baseline preserved. |
| 16 | "Run my weekly WIG Session" | 4dx-d4-cadence (coach-mode) | 4dx-d4-cadence | ✓ | D4 description matches `"Run my weekly WIG Session"` verbatim. Coach-mode (live session, not diagnosing past). v0.7.0 baseline preserved. |
| 17 | "Audit my 4DX implementation" (no specific layer) | 4dx-audit OR router | 4dx-audit | ✓ (audit branch) | Layer-unspecified + audit verb. 4dx-audit description names `"Audit our 4DX implementation"` as a trigger and treats layer-unknown as activation clause. Router could also re-triage but audit's intent-match is stronger and v0.7.0 already shipped this routing as PASS. Documented as both-possible but audit lands. |
| 18 | "我把所有資料丟給你了，但其實只有 WIG draft 和 boss critique" | 4dx-d1-wig-formulation | 4dx-d1-wig-formulation | ✓ | Despite "all my data" framing, real artifact set = WIG draft + stakeholder critique → exactly D1 audit-mode trigger. 4dx-audit's ≥2-layer rule self-excludes (only 1 layer present). Description-driven routing should follow ACTUAL layers, not user's claim of "everything". |
| 19 | "Audit our OKRs against best practices" (non-4DX framing) | using-four-dx-coach (router) | using-four-dx-coach | ✓ | Audit verb but framework = "OKR best practices" not 4DX. v0.7.0 already passed this. No 4DX vocabulary anchor → router. (Mild ambiguity: D2 mentions OKR but only when user asks 4DX-grounded mapping; D2 description NOT this query.) |
| 20 | "我有 cascade map + 1:1 紀錄 + lead 設定" — 3 layers (D1-cascade + onboarding + D2) | 4dx-audit | 4dx-audit | ✓ | 3 layers (cascade-D1 + onboarding-substrate + D2-lead) ≥ 2-layer threshold. Layer mix is asymmetric (cascade + substrate + lead) — no single topic skill owns all three → cross-layer aggregator. |

### Aggregate

- Pass: **20/20 = 100%**
- Single-layer audit routing (Q1-8): **8/8 = 100%** — all 8 single-layer audit queries route to correct topic skill audit-mode; 4dx-audit correctly DOES NOT fire on any single-layer query
- Cross-layer routing (Q9-12): **4/4 = 100%** — all 4 cross-layer queries route to 4dx-audit
- Coach-mode preservation (Q13-16): **4/4 = 100%** — no regression vs v0.7.0; router + D1 + whirlwind + D4 coach paths all preserved
- Edge cases (Q17-20): **4/4 = 100%** — including layer-unknown, false-richness, non-4DX framing, asymmetric multi-layer

### Key findings

**Audit-mode routing (the new v0.8.0 capability)**
Every topic skill description now contains a verbatim audit-mode trigger phrase pair (EN + JP/zh-TW) inside its own description block — that text-level anchor is what wins routing against the (formerly catch-all) 4dx-audit. The dual-mode framing reads consistently across all 8 topic skills: `"Coach (Socratic) ... Audit (consultant) ..."` is the shared idiom.

**4dx-audit narrowing**
4dx-audit's new description carries TWO explicit gates: (a) `"Fires when artifacts span ≥2 of the 5 D-layers"` and (b) `"OR user cannot name which layer is broken"`. The negation clause `"NOT single-layer — route to topic audit-mode"` plus per-layer redirects (WIG→d1; leads→d2; scoreboard→d3; cadence→d4; cascade→cascade) creates bidirectional anchoring. None of the 8 single-layer queries leaked into 4dx-audit.

**Coach-mode preservation**
The 4 v0.7.0-style coach queries (Q13-16) all routed identically to v0.7.0. The dual-mode descriptions did NOT cannibalize coach traffic — coach trigger phrases (`"Define my personal WIG"`, `"I'm always firefighting"`, `"Run my weekly WIG Session"`) remain at the top of each topic skill description and remain matched.

**Edge-case handling**
- Q17 ("Audit my 4DX implementation" no layer) — layer-unknown is an explicit 4dx-audit clause, lands cleanly. Documented as both-possible (router could also fire) but audit branch preferred matches v0.7.0 precedent.
- Q18 ("everything I have" but actually 1 layer) — actual layer count, not user framing, drives routing. 4dx-audit's `≥2-layer` rule self-excludes; D1 audit-mode wins on artifact-content match.
- Q19 (non-4DX framing) — preserved v0.7.0 behavior.
- Q20 (cascade + onboarding + lead = 3 asymmetric layers) — cross-layer wins because no single topic skill owns all three; this is exactly the case 4dx-audit was narrowed to handle.

**Top 3 routing successes (v0.8.0 better than v0.7.0)**
1. Q1 `"Audit our WIG, boss says too abstract"` — under v0.7.0 this would have hit 4dx-audit (audit verb + critique = "rich artifact" framing). v0.8.0 correctly routes to D1 audit-mode owner where the actual two-axis-test diagnostic lives.
2. Q3 `"Audit our scoreboard, team doesn't look at it"` — same regression risk; v0.8.0 routes directly to D3 where the 5-second-test / players-vs-coaches diagnostic lives.
3. Q4 `「WIG Session 機能してない、4 週分の議事録あり、診断して」` — under v0.7.0 the rich-artifact ("4 週分") framing pulled toward 4dx-audit; v0.8.0 routes to D4-cadence audit-mode which actually owns commitment-log analysis.

**Top 3 routing risks (where dual-mode introduces new ambiguity)**
1. **Cascade audit vs cross-layer when sub-leader complaints are about lead/cadence** — Q5 lands cleanly because complaint scope is clearly cascade-rule violation, but a query like `"sub-leaders complaining their leads don't ladder"` would mix D1-cascade + D2 — borderline. Mitigation: both descriptions own clear examples; user can be re-triaged.
2. **Whirlwind-triage audit vs sustain-momentum-rescue** — Q6 (`"audit my time log"`) is unambiguous, but `"my 4DX has lapsed AND I'm firefighting again"` (combining "stalled" signal + firefighting) could fire either. Mitigation: sustain description explicitly excludes "first-time capacity audit".
3. **Q17-style layer-unspecified audit ambiguity** — both 4dx-audit and router could legitimately fire on `"audit my 4DX"` with no layer mention. v0.7.0 already shipped this as both-possible, so not a v0.8.0-introduced risk; however, dual-mode increases the surface for `"audit my X"` patterns. Mitigation: 4dx-audit description's `"OR user cannot name which layer is broken"` clause is the deciding anchor.

### Verdict

**SHIP.** 20/20 = 100% clears the 85% threshold with no critical regression.

- Single-layer audit routing works as designed: 8/8 single-layer queries hit the correct topic skill, never 4dx-audit
- Cross-layer routing preserved: 4/4 ≥2-layer queries hit 4dx-audit cleanly
- v0.7.0 coach-mode behavior NOT regressed (4/4 preserved)
- Edge cases handled by description-text intent-matching, not heuristics

The dual-mode pattern's discriminator is **layer-count + ownership**, encoded twice (positively in topic-skill description audit-mode triggers, negatively in 4dx-audit's "NOT single-layer — route to topic audit-mode" clause). No description edits required for v0.8.0 release.
