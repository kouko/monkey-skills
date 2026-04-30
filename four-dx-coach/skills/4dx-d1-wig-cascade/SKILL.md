---
name: 4dx-d1-wig-cascade
description: |
  Coach a **leader-of-leaders** (manages 3+ subordinate teams, each with its own leader) to translate an already-set org Primary WIG into Team WIGs across those subordinate teams via Ch 7's four cascade rules — Targets-not-Plans, Battles-to-win-the-war, Veto-don't-Dictate, one-WIG-per-individual. Output: cascade map (Primary WIG → 2-3 Key Battles → N Team WIGs) passing ladder-up + veto tests. EN: "How do I translate our Primary WIG to my **3-7 subordinate teams**?", "Cascade our Primary WIG **across direct-report team-leaders**", "Each of my managers leads their own team — how do they each pick a WIG?". JP: 「上から降りた WIG を**各チーム**に落とす」「Primary WIG を**各チーム**に翻訳」「直属マネージャー毎の Team WIG をどう決める」. ZH: 「上面定的 WIG，**我下面各個團隊**要怎麼接？」「Primary WIG 怎麼拆給**下面各個團隊**？」「**我帶的各位主管**要有自己的 Team WIG，怎麼選？」. Do NOT activate if org Primary WIG not yet set (→ `4dx-d1-wig-formulation`), leader runs only one team / no subordinate team-leaders (→ `4dx-d1-wig-formulation` for that single team's WIG), Chinese「我團隊」/「我們部門」query is ambiguous between single-team-leader vs leader-of-leaders (default → `4dx-d1-wig-formulation`; activate cascade only when query explicitly mentions multiple sub-teams or sub-leaders), generic "Cascade plan" / "Cascade rollout" without 4DX context (→ `using-four-dx-coach`), **OKR / quarterly objectives / KR cascade** (out-of-4DX → `using-four-dx-coach`), cascade depth >2 layers (rerun this skill per layer), or solo goal (→ `4dx-d1-wig-formulation`).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker
source_chapter: Chapter 7 — Translating Organizational Focus Into Executable Targets
source_language: en
tags: [wig-cascade, team-wig, leader-of-leaders, key-battles, targets-not-plans, 4dx]
related_skills: []
---

# 4dx-d1-wig-cascade — Translate the Org Primary WIG into Team WIGs

## R — Reading

> Rule 1. No individual focuses on more than one WIG at a time.
> Rule 2. The battles you choose must win the war.
> Rule 3. Leaders of leaders can veto, but not dictate.
> Rule 4. All WIGs must have a finish line in the form of *From X to Y by When.*
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 7 (four rules for a leader of leaders applying Discipline 1)

> Opryland didn't create *plans,* they created *targets*. … A target specifies the outcome you want without dictating how you want the team to do it.
>
> — McChesney et al., *Ch. 7, "What Is Different About Opryland's Approach?"*

---

## I — Interpretation

Once the org has a Primary WIG (X→Y→When), the leader-of-leaders has done only the first step of focus. *Focusing the organization* requires translating that Primary WIG into Team WIGs at the front line — a contribution-shaped target each subordinate team commits to. Ch 7 makes this a four-rule operating system, not an art.

The cascade has two architectural layers and three behavioral commitments.

**Layer A — Key Battles (sub-WIGs to the Primary WIG).** Between the org Primary WIG and the front-line Team WIGs sits an intermediate layer: the smallest set of battles whose victory wins the war. The book's discipline is to ask "*what is the fewest possible battles necessary to win?*" — Opryland went from 17 candidates to 3; the retailer evaluated dozens before landing on 3. Two or three battles is the typical landing zone; if you have 7+ Battle WIGs, the leadership team has not yet done the strategic work. (Note: Battles are still lag measures, not lead measures — Ch 7 explicitly warns this confusion.)

**Layer B — Team WIGs (front-line ownership).** Each subordinate team picks its own contributing Team WIG that ladders up to one of the Battles. For *functionally diverse* organizations (Opryland's 75 different teams: bellstand, housekeeping, F&B, etc.) Team WIGs look very different from each other — the bellstand chose "reduce luggage delivery from 106 to 20 minutes", front-desk chose "improve speed of check-in". For *functionally similar* organizations (multi-store retail, manufacturing, sales territories) every team adopts the *same* Battle structure but customizes its own *From X to Y by When* numeric finish line per unit.

**Behavioral commitment 1 — Targets, not plans.** The leader gives each subordinate team the target (the X→Y→When result the team owes the war), not the plan (how to get there). Plans are senior-leader-tells-team-what-to-do — fine for stroke-of-pen and whirlwind work, fatal for breakthrough. Targets pull engagement; plans push compliance.

**Behavioral commitment 2 — Veto, don't dictate (Rule 3).** The subordinate team-leader proposes the Team WIG; the leader-of-leaders can veto a proposal that doesn't ladder up, doesn't pass From-X-to-Y-by-When, or violates mission. The leader-of-leaders cannot impose a Team WIG. The retailer's region leader explicitly let district leaders own their own *From X to Y by When* numbers — the regional leader could "ask for adjustments" but could not dictate the targets.

**Behavioral commitment 3 — Each Team WIG is the team's, not a smaller copy of the org WIG.** Sub-team WIGs are *contributions*, not miniaturizations. The bellstand WIG is "delivery time from 106 to 20 min", not "improve guest satisfaction by 1%". The contribution shape is what gives the team an actually-winnable game.

The output of this skill is a cascade map: org Primary WIG → 2-3 Key Battles → N Team WIGs (one per subordinate team), each in *From X to Y by When* form, each laddering up to a named Battle, each owned by its team-leader.

**Cascade depth caveat (book-implicit, agent-explicit).** Beyond two cascade layers the leader-of-leaders has no direct line of sight; veto authority degrades into report-out theater. When more than two layers are needed (e.g. region → district → store, as in the retailer case), do not run a single-pass cascade — run *this skill at each layer*, treating each intermediate leader as the leader-of-leaders of the layer below. This is how the retailer cascade in Ch 7 is structured: region cascades to districts (one pass), then each district cascades to its stores (a second, independent pass).

---

## A1 — Past Application

### Case 1: Opryland Hotel — functionally diverse cascade (Ch 7)
- **Problem**: Opryland (Nashville, 2,000-room convention hotel) had a confirmed Primary WIG ("improve guest satisfaction from 42% to 55% top-box by Dec 31") but 75 operating teams across radically different functions (engineers, housekeepers, front-desk, bellstand, restaurants, finance, HR) and no way to translate the WIG into team-level commitments.
- **Methodology applied**: Leadership team narrowed 17 candidate Battle WIGs to 3 (arrival experience, problem resolution, F&B quality). Each of the 75 teams then chose its own Team WIG, in From-X-to-Y-by-When form, that contributed to one of the three Battles. Bellstand owned "luggage delivery from 106 min to 20 min"; front-desk owned check-in speed; housekeeping owned room-availability for early check-in (closely aligned with arrival experience). Targets were given, plans were left to the teams.
- **Conclusion**: Functionally diverse organizations cascade by *contribution shape* — every Team WIG is different in unit and verb, but all ladder up to a named Battle, which ladders up to the Primary WIG.
- **Outcome**: 9 months later, Opryland reached 61% top-box (vs 55% target, vs all-time-historical-high of 45%); bellstand exceeded its own WIG and reduced luggage delivery to 12 minutes.

### Case 2: Large multi-outlet retailer — functionally similar cascade (Ch 7)
- **Problem**: A national retailer with hundreds of stores had a Primary WIG ("increase Likelihood-to-Recommend"); needed to cascade to regions → districts → stores where every unit performs the same function.
- **Methodology applied**: Leadership chose 3 Battle WIGs (improve customer engagement, reduce out-of-stocks, increase speed of checkout). The region picked an overall From-X-to-Y-by-When; each district leader chose their own district-specific From-X-to-Y-by-When numbers (regional leader could request adjustments but did not dictate); each store chose its own per-store numbers AND was given the choice — with district oversight — of *which* of the 3 Battles to focus on, depending on where the store had the most opportunity (e.g. an already-strong out-of-stocks store could focus on engagement + checkout).
- **Conclusion**: Functionally similar organizations adopt the *same* Battle structure across all units, but each unit owns its own numeric finish line, and at the deepest layer leaf units may be given Battle-selection autonomy. The veto-not-dictate rule was the operating constraint that made district + store ownership genuine.
- **Outcome**: The cascade gave each store a winnable game shaped to its own gap, raising store-leader ownership and, in turn, LTR contribution to the Primary WIG.

### Case 3: 50-person Sydney accounting firm — small-company cascade (Ch 7)
- **Problem**: A small firm had only two teams (sales, delivery) and was about to assign 9 Battle WIGs to those two teams to chase "total revenue". The cascade was strangling itself before it began.
- **Methodology applied**: The leadership reframed total revenue from a WIG to a *strategy line* on the Strategy Map; identified that two stroke-of-pen items (new products, hired marketing agency) plus normal whirlwind would deliver ~85% of total revenue; selected the most-strategic 15% gap (advisory services) as the actual Primary WIG; cascaded into two Team WIGs — sales: "advisory-services revenue from *new* accounts X→Y"; delivery: "advisory-services revenue from *existing* accounts X→Y".
- **Conclusion**: For small organizations, the cascade often reveals that the *original* Primary WIG was overscoped. Cascade fails not because translation is hard but because "total revenue" wasn't a WIG to begin with. Going *smaller* on the Primary WIG is sometimes the more strategic choice. The skill must allow upstream re-scoping when cascade reveals the WIG was wrong.
- **Outcome**: Two clean, contribution-shaped Team WIGs that each team-leader could own; demonstrates that when N=2 teams the Battle-WIG layer often collapses (no intermediate layer needed) and Team WIGs come directly from the Primary WIG.

---

## A2 — Future Trigger ★

### When will the leader need this skill?

1. The leader-of-leaders has a confirmed org Primary WIG (in From-X-to-Y-by-When form) and is now asking how to give each direct-report team-leader their own commitment.
2. A leader has been handed a WIG from above and is asking "how do I translate this into something my team-leaders can actually own?".
3. A multi-team org is cascading from layer N to layer N+1 (region → district, division → team, etc.) and needs the cascade rules for this single hop.
4. A leader's first attempt at cascade produced 7+ Battle WIGs or assigned the same WIG verbatim to every team — both signs the cascade is incorrect.
5. A leader has dictated Team WIGs to subordinate team-leaders ("you'll own this WIG") and is now seeing compliance theater rather than ownership — re-cascade under the veto-don't-dictate rule.

### Language signals (multilingual — match any)

- EN: *"How do I translate the org WIG to my team?"*, *"How do I cascade our Primary WIG to my direct-report teams?"*, *"Each of my managers needs a WIG — how do we pick them?"*, *"How do I break the company WIG into team WIGs?"*, *"Should every team have the same WIG or different ones?"*
- JP: 「上から降りた WIG をチーム単位に落とす」「会社の Primary WIG を各チームに翻訳する」「直属マネージャー毎の Team WIG をどう決める」「全チーム同じ WIG にすべき、それとも別々？」「Primary WIG をどう分解する？」
- ZH: 「上面定的 WIG，我團隊要怎麼接？」「Primary WIG 怎麼拆給下面各個團隊？」「每位主管要有自己的 Team WIG，怎麼選？」「每個團隊要不要用同一個 WIG，還是各自不同？」「公司 WIG 怎麼往下展開？」

### Non-activation signals (do NOT trigger when…)

- Org Primary WIG hasn't been selected yet → route to `4dx-d1-wig-formulation`. Cascade requires an upstream WIG to translate.
- Leader runs only ONE team (no subordinate team-leaders) → use `4dx-d1-wig-formulation` directly; there is no cascade hop.
- Solo / individual goal → use `4dx-d1-wig-formulation`. Cascade is a multi-team concept; it does not exist for one person.
- Methodology-fit unclear → route to `4dx-meta-strategy-triage` first.
- User asking about lead measures or scoreboards → route to D2 / D3 skills; cascade is a D1-only operation.

### Distinction from neighboring skills

- vs. `4dx-d1-wig-formulation`: that skill chooses the *upstream* Primary WIG (single team or org-level); this skill *translates* a chosen Primary WIG downward into N Team WIGs. Selection comes before cascade.
- vs. `4dx-d1-wig-formulation`: personal scope, no cascade. If the user has no subordinate team-leaders, cascade is a category error.
- vs. `4dx-meta-strategy-triage`: triage decides whether 4DX *fits at all* for a single team. Cascade assumes triage already greenlit each subordinate team.
- vs. doing the cascade more than 2 layers deep: the book is explicit only about cascade *at each hop*; deep cascade is not a special protocol — it is *this skill, run again, at each layer*. Treat layer-N as a leader-of-leaders for layer-N+1.

---

## E — Execution

When this skill activates, the agent acts as a consultant to a leader-of-leaders. The leader will be tempted to dictate Team WIGs because dictation feels efficient. **The skill's primary work is enforcing Rule 3 — veto, don't dictate.**

1. **Confirm the upstream Primary WIG.**
   - Ask: *"State your org's Primary WIG as it stands now: From X to Y by When."*
   - Completion criterion: leader produces a single sentence in From-X-to-Y-by-When form.
   - **Halt condition**: if the Primary WIG isn't yet in this form, stop and route to `4dx-d1-wig-formulation`. Cascade has nothing to translate.

2. **Enumerate subordinate teams.**
   - Ask: *"How many direct-report team-leaders do you have, and what does each team do? One line per team."*
   - Completion criterion: a list of N teams with named functions.
   - **Halt condition**: if N=1, stop — there is no cascade. Route to `4dx-d1-wig-formulation` for that single team. If N>7 at this hop, flag span-of-control concern and ask whether an intermediate leadership layer exists; if yes, run cascade for *that* intermediate layer first.

3. **Classify cascade shape: functionally diverse vs functionally similar.**
   - Ask: *"Do these teams perform the SAME function (multi-store retail, sales territories, manufacturing units) or DIFFERENT functions (one runs marketing, one runs ops, one runs support)?"*
   - Completion criterion: leader picks one. This determines whether all teams will share the same Battle structure (similar) or each team will have a uniquely shaped Team WIG (diverse).

4. **Identify Key Battles — the fewest possible battles to win the war.**
   - Ask: *"What is the SMALLEST number of battles — sub-WIGs to the Primary WIG, each a lag-measure — whose victory would ensure the Primary WIG is hit? Start by listing every candidate, then cut ruthlessly. Opryland went from 17 to 3."*
   - Completion criterion: leader lands on 2-3 Battle WIGs, each in From-X-to-Y-by-When form, each laddering up arithmetically to the Primary WIG.
   - **Halt condition**: if leader cannot get below 5 Battles, do not proceed — strategic narrowing is incomplete. Push: *"if every battle won EXCEPT one, would you still hit the Primary WIG? If yes, that one is not a Battle."*
   - **Caveat**: explicitly remind the leader these are still *lag* measures. Battles are not lead measures (Ch 7 warns this is the most common confusion at this stage).

5. **Solicit Team WIG proposals from each subordinate team-leader (Rule 3 — pull, not push).**
   - Instruct the leader: *"Do not assign Team WIGs. For each subordinate team-leader, ask them: 'Given the Primary WIG and these N Battles, what is the SPECIFIC contribution your team can commit to, in From-X-to-Y-by-When form?' Their team — their proposal."*
   - Completion criterion: one proposed Team WIG per subordinate team, in From-X-to-Y-by-When form, with a named Battle it ladders up to.
   - For *functionally similar* shape: each team adopts the same Battle structure; the proposal is a per-unit numeric finish line. At the leaf layer, leaf-team-leaders may also be given Battle-selection autonomy ("which 1-2 of the N Battles will you focus on, given where your unit's gap is?") — Ch 7 retailer pattern.
   - For *functionally diverse* shape: each Team WIG can have a different unit, verb, and Battle assignment — bellstand's "luggage delivery 106→20 min" looks nothing like front-desk's "check-in speed".

6. **Apply the ladder-up test.**
   - Ask: *"If every team hits its proposed Team WIG, do the Battles win? If every Battle wins, does the Primary WIG hit? Do the math, not the vibe."*
   - Completion criterion: arithmetic shows that the sum of Team WIG contributions to a Battle ≥ that Battle's target, and the sum of Battle outcomes ≥ Primary WIG target.
   - **Halt condition**: if the math doesn't close, send the leader back to step 5 to renegotiate proposals (NOT to dictate replacements). The retailer's region leader could "ask for adjustments" — that's the move.

7. **Apply the veto test (Rule 3).**
   - For each proposed Team WIG, ask the leader: *"Does this Team WIG (a) ladder up to a Battle, (b) pass From-X-to-Y-by-When form, (c) align with the team's stated mission, (d) leave the team-leader genuine ownership of HOW? If yes — accept. If any 'no' — VETO and ask the team-leader to re-propose. You cannot rewrite it for them."*
   - Completion criterion: every Team WIG has been either accepted or returned for re-proposal.
   - **Halt condition**: if the leader insists on dictating a replacement, surface Rule 3 directly and stop the cascade — dictation here destroys ownership and converts the entire D1 install into compliance theater.

8. **Apply the one-WIG-per-individual rule (Rule 1).**
   - Ask: *"Does any individual on any team end up owning more than one Team WIG? If yes, that's overload — split the role or drop the second WIG."*
   - Completion criterion: each individual owns at most one Team WIG (book is firm).

9. **Cascade-depth check.**
   - Ask: *"Does the cascade need to continue downward — do any of these subordinate team-leaders themselves have subordinate team-leaders (region → district → store)?"*
   - If no → cascade complete; output the map.
   - If yes → flag the deep-cascade rule: each layer runs THIS skill again with the layer above's Team WIG as the new Primary WIG. Do not attempt single-pass deep cascade.

10. **Output the cascade map.**
    - Render: org Primary WIG (X→Y→When) → 2-3 Key Battles (each X→Y→When) → N Team WIGs (each X→Y→When, each tagged to one Battle, each owned by a named team-leader).
    - Show it back: *"For each subordinate team-leader: read your Team WIG aloud. On the deadline, could a stranger tell whether your team won or lost? Does your contribution add to the Battle? Does your Battle add to the Primary WIG?"*
    - Completion criterion: every team-leader confirms their Team WIG is binary, contribution-shaped, and arithmetically tied to the war above.

---

## B — Boundary ★

### Do NOT use this skill in:

- **Org Primary WIG not yet set.** Cascade has nothing to translate. Route to `4dx-d1-wig-formulation`.
- **Leader runs only one team.** No subordinate team-leaders → no cascade hop. Use `4dx-d1-wig-formulation` for that single team's WIG directly.
- **Solo / individual goals.** Cascade is a multi-team operation; it has no meaning at solo scope. Use `4dx-d1-wig-formulation`.
- **Personal-scope misfire (single-team-leader misfire).** A leader who leads ONE team but says "I want to cascade to my team members" is conflating Team WIG (one per team, owned by team-leader) with individual commitments (Discipline 4, weekly WIG Session). Cascade does not push individual-level WIGs to direct reports. If a leader has ONE team, the team has ONE Team WIG; individuals make weekly commitments inside D4, not Team-WIG-clones inside D1. Route to `4dx-d1-wig-formulation` for the single Team WIG, then to D4 for individual commitments.
- **Single-shot project cascade.** If the work is a fixed-end-state project (build-and-ship), use project-management decomposition (work breakdown structure, Gantt) — not 4DX cascade. The continuous-cadence operating system is overhead when there's a finite task list with a known sequence.
- **Cross-functional matrix where one team's WIG forces another team's daily work.** Cascade gives each team autonomous ownership of its Team WIG. If team A's WIG can only be hit by dictating team B's daily actions, the cascade is wrong-shaped; back up to step 5 and renegotiate proposals.

### Author-warned failure modes

- **Plan dictation (Ch 7 "Targets-not-Plans" violation)**. Leader cascades by telling each team "here are the actions you'll take" instead of "here is the result you'll commit to". Targets pull engagement; plans push compliance and kill innovation. The skill must catch any phrasing that smuggles HOW into the cascade.
- **Imposed Team WIGs (Rule 3 violation)**. Leader rewrites the team-leader's proposal "for clarity" and hands it back. This destroys ownership — Ch 7 is explicit: leaders of leaders can VETO, but not DICTATE. Veto = reject and ask for a new proposal; dictate = author the replacement yourself. Hard rule.
- **Battle-WIGs-as-lead-measures confusion (Ch 7 explicit caveat)**. Treating the Battles as if they were lead measures because winning a Battle predicts winning the Primary WIG. Lead measures must also be directly influenceable by the team day-to-day; Battles are still lag outcomes. Lead measures show up in D2, not in cascade.
- **Too-many-Battles drift**. Landing on 5+ Battle WIGs is not strategic narrowing; it's a thinly disguised plan list. Opryland landed on 3 from 17. The retailer landed on 3 from dozens. The accounting firm collapsed to 0 intermediate Battles (cascading directly Primary → 2 Team WIGs). Two or three Battles is the typical landing zone. 7+ Battles means the strategic work isn't done.
- **Team-WIG-as-miniature-Primary-WIG**. Every team gets the *same* Team WIG verbatim, just with smaller numbers. Misses the contribution-shape principle entirely. Bellstand's WIG is luggage delivery time, not "improve guest satisfaction by 1.3%". Differentiated contribution is the point.
- **Cascade-too-deep-in-one-pass**. Leader-of-leaders tries to cascade through 3+ layers in a single facilitation. The book describes the retailer cascade explicitly as region → district (one cascade pass), then district → store (a second, independent pass). Single-pass deep cascade collapses fidelity; veto authority degrades into report-out theater. Re-run this skill at each layer.

### Author's blind spots / period limitations (apply with care)

- **Cascade case studies skew commercial-operational.** Ch 7's three worked examples (hotel, retailer, small accounting firm) are all customer-facing or revenue-driven; less coverage of R&D, knowledge work, or matrixed-product cascades where ownership is genuinely shared. For these, the cascade may need explicit dual-team co-ownership (which the book does not formalize).
- **High-context cultures and the "veto, don't dictate" ritual.** In JP / ZH / KR organizational cultures, a public proposal-and-veto cycle in front of peers can read as face-loss. The leader may need to run the proposal cycle 1:1 first, then surface the cascade map in the leadership-team meeting. The intent of Rule 3 is preserved; the ritual is adapted.
- **Span-of-control 3-7 is heuristic.** The book doesn't give a hard cap, but cascade hops with 8+ subordinate team-leaders strain veto-cycle bandwidth and degrade ownership review. Treat 3-7 as the productive band; outside it, structural redesign should precede cascade.
- **Selection bias.** All FranklinCovey case studies are paying clients; failed cascades are absent. Don't assume "if Opryland did it this way, our cascade will work" — run all four rules every time.

### Easily-confused neighboring methodologies

- **OKR cascade**. OKR also cascades from company-level Os to team-level Os, but allows 3-5 Os per team and 3-5 KRs per O. 4DX cascade is firm: ONE Team WIG per team, max one per individual. Don't smuggle multi-objective OKR habits into a 4DX cascade.
- **Hoshin Kanri (方針管理)**. Catchball-style negotiation between layers is similar in spirit to Rule 3; differs in cadence (annual hoshin review vs 4DX weekly) and in tooling (X-matrix vs From-X-to-Y-by-When). If the org already runs hoshin, the cascade map can be slotted into the X-matrix, but the one-WIG-per-individual rule and the weekly cadence are non-negotiable for 4DX.
- **Project work-breakdown-structure (WBS)**. WBS decomposes a fixed scope into tasks-and-subtasks. Cascade decomposes a *target* into smaller targets owned by autonomous teams. Don't confuse the two: a WBS row is *what* the org owes; a Team WIG is what *that team* commits to.
- **Strategy maps (Kaplan & Norton)**. The book's Strategy Map is its own visual — left column stroke-of-pen, right column whirlwind, middle column behavioral-change zone. It is not the Kaplan-Norton Balanced-Scorecard strategy map. Naming collision; don't treat them as interchangeable.

### NOT for: solo / single-team-leader / unset-Primary-WIG

NOT for solo / individual goals — use `4dx-d1-wig-formulation`. NOT for a leader who runs only ONE team (no cascade exists; individual D4 commitments ≠ Team WIG cascade) — use `4dx-d1-wig-formulation` for the single Team WIG. NOT for cascading when the org Primary WIG hasn't been chosen yet — use `4dx-d1-wig-formulation` first.

### Industry-experience addendum (cascade-methodology peers)

The book treats cascade as a 4DX-native discipline; three older frameworks teach the same problem differently and most cascade misfires come from importing their habits. Primary citations in `references/industry-grounding.md`:

- **Hoshin Kanri** (Akao 1991, Productivity Press) — catchball + X-matrix; bidirectional iteration. 4DX is veto-only, not iterative; one Team WIG, not "vital few".
- **OKR** (Doerr 2018, Portfolio) — bidirectional negotiation, 3-5 Os per team, quarterly cycles. 4DX rejects multi-objective cascade and consensus.
- **Balanced Scorecard** (Kaplan & Norton 2001, HBSP) — four-perspective cascade replicated at every level. 4DX requires *differentiated* contribution, not miniature-Primary-WIG replication. The book's "Strategy Map" is a different artifact than Kaplan-Norton's despite the name collision.

Cascade misfires usually look like one of these three habits leaking in: rewriting a subordinate's proposal "for clarity" (hoshin/OKR habit), giving each team three WIGs to "cover the space" (OKR habit), or cloning the Primary WIG verbatim with smaller numbers (BSC habit). Resist all three.

---

## Related skills

- `4dx-d1-wig-formulation` — depends-on — org Primary WIG must exist before cascade
- `4dx-meta-strategy-triage` — depends-on — each subordinate team must clear team-fit triage
- `4dx-meta-team-leader-onboarding` — composes-with — cascade only commits when leaders are onboarded
- `4dx-d1-wig-formulation` — contrasts-with — solo scope, no cascade dynamics

---

## Audit metadata

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Test pass rate**: pending (see `test-prompts.json` and `test-results.md`)
- **Distilled at**: 2026-04-29
- **Output language**: body — English (team-coach plugin rule); A2 trigger phrasings — multilingual EN/JP/zh-TW; metadata — English
