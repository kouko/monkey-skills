---
name: 4dx-d1-wig-formulation
description: |
  Coaches the user to formulate a Wildly Important Goal in From-X-to-Y-by-When form across solo / team-leader / team-member scopes, plus audit-mode diagnosis of an existing WIG draft. Use when the user is about to declare a goal lacking lag-measurable finish line, deadline, or clear scope (personal vs team), BEFORE the goal gets committed.
  EN: "Define my personal WIG", "Pick our team's Primary WIG", "Audit our WIG — too abstract"
  JP: 「自分の WIG を決めたい」「Primary WIG をどう選ぶ」「WIG を診断して」
  zh-TW: 「幫我訂個人 WIG」「team 選 Primary WIG」「WIG 哪裡有問題」
  Do NOT use for cascading Primary WIG to sub-teams (→ 4dx-d1-wig-cascade) or pre-D1 strategy fit (→ 4dx-meta-strategy-triage).
source_book: "The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker"
source_chapter: "Chapter 2 — Discipline 1: Focus on the Wildly Important; Chapter 6 — Choosing Where to Focus; Chapter 7 — Defining the WIG; Chapter 12 — Applying Discipline 1"
source_language: en
tags: [d1, wig, multi-scope, goal-setting, focus, from-x-to-y-by-when, 4dx, personal, team-leader, team-member, audit-mode, coach-mode]
related_skills:
  - 4dx-meta-strategy-triage
  - 4dx-meta-whirlwind-triage
  - 4dx-d1-wig-cascade
  - 4dx-d2-lead-measures
  - 4dx-d3-scoreboard
  - 4dx-d4-cadence
  - 4dx-audit
  - using-four-dx-coach
---

# 4dx-d1-wig-formulation — Formulate a WIG across all roles (multi-scope, two interaction modes)

## Mission

Coach or audit the user through the D1 act of **formulating a Wildly
Important Goal**. The skill supports two interaction protocols across
three actor-scopes:

- **Coach-mode** (Socratic, from zero) — runs in three scopes: solo
  defining a personal WIG; team-leader selecting Primary WIG; team-
  member comprehending an inherited WIG.
- **Audit-mode** (consultant, on existing artifact) — runs when the
  user provides a WIG draft / candidates for D1-only diagnostic, with
  optional stakeholder critique mapped to 4DX rules.

The same shared *From X to Y by When* sentence form anchors every
protocol; what differs is **who acts** (solo / team-leader / team-
member), **what verb they apply** (define / select / comprehend /
audit), and the **agent voice** (personal coach / consultant-to-
leader / personal-coach-to-member / consultant-audit).

## When this skill activates

### Multilingual trigger phrasings (covering all 3 scopes)

**Personal-define (solo individual, agent = personal coach):**
- EN: "I want to be healthier / get in shape / grow my business / finish my book", "Help me set a personal goal / WIG", "I have too many priorities — where should I focus?", "Define my personal WIG"
- JP: 「目標がぼんやりしている」「優先順位が多すぎる」「やりたいことが多すぎて決められない」「自分の WIG を決めたい」「個人目標の立て方を教えて」
- zh-TW: 「目標太模糊」「想做的事太多」「不知道要專注哪個」「幫我訂個人目標 / WIG」「我有太多優先事項」

**Team-select (team-leader, agent = consultant to leader):**
- EN: "Help me pick our team's Primary WIG", "We have too many strategic goals", "Where should our team focus this year?", "I'm leading a team and need to choose one breakthrough goal"
- JP: 「チームの Primary WIG をどう選ぶ？」「戦略候補が多すぎてチームの焦点が決まらない」「今年チームはどこに集中すべき？」「うちのチームの WIG は何にすべきか」
- zh-TW: 「幫我們團隊選 Primary WIG」「我們有太多戰略目標想做」「團隊今年該專注哪一個」「我帶團隊，要選一個突破目標」

**Member-comprehend (team-member, agent = personal coach to member):**
- EN: "I joined a team running 4DX — how do I understand my role in their WIG?", "My manager set a team WIG but I don't know what I'm supposed to do", "What does my work have to do with the team's goal?"
- JP: 「チームの WIG が降りてきたけど自分の役割が分からない」「上司が WIG を決めたが自分が何をすればいいか分からない」「チームの目標と自分の仕事のつながりが見えない」
- zh-TW: 「主管定了 WIG 但我不知道我這個位置該怎麼接」「團隊有 WIG 但我不知道我該做什麼」「團隊目標跟我的工作有什麼關係」

**Audit-mode (any scope, agent = consultant on existing artifact):**
- EN: "Here's our WIG draft — what's wrong?", "Audit my Primary WIG against 4DX", "Got feedback our WIG isn't quite right — can you diagnose?", "Stakeholder wants to revisit our WIG framing", "Manager flagged we should sharpen this WIG", "Boss says our WIG is too abstract — diagnose", "Is this WIG well-formed?", "Diagnose this WIG against 4DX rules"
- JP: 「うちの WIG を診断して」「上司にフィードバックされた、WIG どこ直すべき？」「マネージャーから方向性を直したいと言われた、WIG 見て」「上司が WIG ダメ出ししてるけど何が原因？」「この WIG、4DX 的に OK？」「Primary WIG をチェックして」
- zh-TW: 「我們的 WIG 你看一下哪裡有問題」「主管覺得 WIG 需要再調整，幫我看哪裡」「review 後 stakeholder 想討論 WIG 方向」「老闆說 WIG 不行，幫我診斷」「幫我審核這個 WIG 有沒有過 4DX 規則」「這個 WIG 寫得對嗎？」

### Non-activation signals (DO NOT fire when…)

- **Strategy fit not yet decided** (user hasn't classified the situation as behavioral-change vs stroke-of-pen vs reactive whirlwind) → `4dx-meta-strategy-triage` first
- **Whirlwind / capacity audit** (the question is "do I have time?", not "what's the goal?") → `4dx-meta-whirlwind-triage`
- **Cascading an already-set Primary WIG to N sub-teams** (translation downward, not selection or definition) → `4dx-d1-wig-cascade`
- **WIG already well-formed** (X / Y / When all explicit) — skip D1 entirely; route to D2 lead-measure discovery
- **Habit design** ("help me meditate daily") — no fixed lag-measurable end-state; not a WIG
- **Stroke-of-pen decisions** ("Should I switch CRMs? Buy a sit-stand desk?") — 4DX overkill; just decide
- **Reactive / on-call domains** where the whirlwind IS the strategic value → `4dx-meta-strategy-triage`
- **Lead measure / scoreboard / cadence queries** → `4dx-d2-lead-measures` / `4dx-d3-scoreboard` / `4dx-d4-cadence`
- **Multi-team rollout / Leader-of-Leaders coordination** → out of plugin scope; hand off via `using-four-dx-coach`
- **Cross-layer / full-stack audit** (user provides WIG + lead measures + scoreboard + cadence and wants the whole 5-layer diagnosed) → `4dx-audit`. This skill's audit-mode is D1-only.

## Mode + scope detection

When this skill activates:

1. Determine **interaction mode**: coach-mode (no artifact, Socratic from zero) vs audit-mode (artifact provided + diagnostic intent, OR artifact + stakeholder critique).
2. If coach-mode: determine **scope** (personal-define / team-select / member-comprehend) and **verb** (define / select / comprehend).
3. If audit-mode: determine artifact scope (personal / team-select / member-inherited) — but the audit protocol handles all three uniformly via the rule-check matrix.
4. Load the matching protocol file from `protocols/`.
5. Follow that protocol's E section step-by-step.

### Mode triage (apply first)

| Signal in user query | Mode |
|---|---|
| User pastes / quotes a WIG sentence (or candidate list) and asks "what's wrong?" / "diagnose" / "audit" / 「診断して」/「哪裡有問題」 | **audit-mode** |
| User pastes a WIG + a stakeholder complaint ("boss says…" / "got feedback…" / "manager flagged…", 「上司が…」/「フィードバックされた」/「指摘を受けた」, 「老闆說…」/「主管覺得要調整」/「review 後需要修正」) | **audit-mode** |
| User has no draft, asks to be coached / guided / "help me set" / 「決めたい」/「訂個 WIG」 | **coach-mode** |
| Vague / ambiguous on whether artifact exists | ask ONE clarifying question (below) |

If ambiguous after reading the user's query, ask ONE Socratic question:

> EN: "Two quick checks: (a) **who is the WIG for** — yourself solo, your team (you lead), or you-as-team-member receiving someone else's? (b) **are you defining a new WIG, selecting from candidates, or making sense of one given to you?** I'll route to the right protocol."
>
> JP: 「2 点確認: (a) **WIG は誰のため** — 自分一人、率いる team、それとも所属 team の member として？ (b) **新規定義 / 候補から選定 / 既に降りてきた WIG の把握** のどれ？適切な protocol に振り分けます。」
>
> zh-TW: 「兩個快速確認：(a) **WIG 是給誰的** — 你自己（solo）、你帶的 team、還是你所在的 team（別人定的）？(b) **要新訂、要從候選裡挑、還是要搞懂上面給的**？我幫你導到對的 protocol。」

If the signal in the original query is strong, skip the question and load the protocol directly.

## Protocol routing table

| Mode | Detected scope | Verb | Load protocol | Agent voice |
|---|---|---|---|---|
| Coach | Personal (solo individual) | Define | `protocols/personal-define.md` | personal coach |
| Coach | Team-leader | Select | `protocols/team-select.md` | consultant-to-leader |
| Coach | Team-member | Comprehend | `protocols/member-comprehend.md` | personal coach to member |
| Audit | Any (personal / team-select / member-inherited) | Diagnose | `protocols/audit-mode.md` | consultant-audit |

After loading the protocol, follow its E section step-by-step. Each protocol carries its own R / I / A1 / A2 / E / B sections; this orchestrator does not run any WIG content directly.

### Edge-case routing

- **Solo + "select from candidates"** — the personal-define protocol handles candidate evaluation internally (its count test in step 7 narrows multiple aspirations to one). Fire `protocols/personal-define.md`; do NOT misroute to team-select.
- **Leader + cascade to N sub-teams** — that's translation, not selection. Hand off to `4dx-d1-wig-cascade`. This skill does NOT run cascade.
- **Member + "I disagree with the WIG, want to redefine it"** — member doesn't redefine. Load `protocols/member-comprehend.md` to surface the rationale first, then route the disagreement upward to the leader as a 1:1 conversation (out of this skill's scope).
- **Already-well-formed WIG (X / Y / When explicit) + no diagnostic intent** — skip D1; route directly to D2.
- **Already-well-formed WIG + diagnostic intent** ("audit this") — load `protocols/audit-mode.md`; the audit will likely PASS the rule-check, and the recommendation is to route to D2.
- **Mission / vision not yet defined (team)** — Trap 4 (mission alignment) cannot be evaluated; advise the leader to establish mission first, then return.
- **Artifact-rich + cross-layer (lead / scoreboard / cadence too)** — route to `4dx-audit` (full-stack), not this skill's audit-mode.
- **Artifact present but vague + user wants rebuild from scratch** — confirm with one question; if user wants to rebuild rather than revise, prefer coach-mode protocol.

## Shared standards

All four protocols reference the same three standards (load on demand). Coach-mode protocols use them as Socratic checkpoints; audit-mode uses them as the per-rule verdict matrix:

- `standards/from-x-to-y-by-when-grammar.md` — the WIG sentence form (lag-measurable starting state X, lag-measurable target Y, fixed calendar deadline When); rejects verb-less / number-less / deadline-less / activity-as-outcome forms
- `standards/wig-discipline.md` — the focus cap (≤1-3 WIGs per organizational layer; one WIG per individual, max 2 only when independent and non-conflicting; 1 Primary WIG per team is preferred, 2 acceptable only via Approach B with genuinely segmented teams)
- `standards/ladder-up-test.md` — every team WIG must demonstrably serve the org WIG, every individual's slice must demonstrably serve the team WIG; book's veto rule (Ch 7) on team WIGs that fail line-of-sight upward

Audit-mode applies the same standards but in **verdict mode** (PASS / FAIL / PARTIAL with cite) rather than coach-mode's step-by-step extraction. Same rules, different posture.

## Cross-skill relations

- **Upstream (prerequisite)** — `4dx-meta-strategy-triage` confirms the user's situation is behavioral-change (not stroke-of-pen, not whirlwind-as-strategic-value); this skill assumes triage already concluded "use 4DX." `4dx-meta-whirlwind-triage` is the capacity-side D1 skill (different topic — "do I have time?"); both can run before this one.
- **Downstream (sequels)** — `4dx-d2-lead-measures` finds the daily lever once the WIG is well-formed; `4dx-d3-scoreboard` builds the artifact the lead is tracked on; `4dx-d4-cadence` runs the weekly cadence that drives lead → lag.
- **Compose-with neighbour** — `4dx-d1-wig-cascade` runs *after* `team-select.md` produces a Primary WIG, when that WIG must be translated into Battle WIGs for sub-teams. Sharp boundary: this skill *selects* / *defines* / *comprehends*; cascade *translates downward*.
- **Plugin-router fallback** — `using-four-dx-coach` handles cold-start triage and out-of-4DX queries (SMART goals, OKR migration, generic alignment coaching); not a substitute for this skill, but the right hand-off when the user's question turns out not to be 4DX D1.

## Boundary (cross-scope common)

The scope-specific boundary lives in each protocol's B section. The cross-scope common boundary:

- **Cross-mode disambiguation** — coach-mode is for users *without* a WIG artifact who need Socratic extraction; audit-mode is for users *with* an artifact (draft / candidates) who need verdict-style diagnostic. Artifact-rich → audit; vague / cold-start → coach-mode. When in doubt, ask one clarifying question (mode triage table above). Never run audit-mode on an absent artifact (no draft = nothing to grade); never run coach-mode on an artifact the user explicitly wants graded (the Socratic walk-through wastes their time and ignores their input).
- **A WIG is a *single-bet, lag-measurable, deadline-bound* outcome** — not a habit (no end-state), not a project tracked as % complete (use deliverables-list-with-deadline variant), not an activity ("exercise more"), not a stroke-of-pen decision, not the whole job. The shape is the discipline.
- **Discovery-vs-execution distinction matters across all 3 scopes** — 4DX assumes the right WIG is *discoverable*. In genuinely uncertain domains (early-stage research, novel creative work, post-pivot product), the right WIG may not yet be knowable; the OKR / lean-startup tradition would say *run small experiments first*. If the user's situation is exploratory, flag the mismatch rather than force a single-WIG commitment. (March 1991, Mintzberg 1994.)
- **Selection / definition / comprehension never substitutes for the user's own choice** — the agent does not pick the WIG (personal), name the Primary WIG (team-leader), or invent the rationale (member). Ownership is the load-bearing mechanism. The agent's job is to surface, sharpen, push back, route to ask — never to dictate.
- **Mission alignment is the final filter across all scopes** — a measurable / feasible / breakthrough WIG that is *disconnected from mission* produces an organization (or person) that "achieves goals but loses soul." (Ch 6 Trap 4 / thrift-store case.) Test against the user's stated mission (personal: deeper "why"; team: org charter; member: team purpose).
- **One WIG per individual is firm** — across all 3 scopes, the personal-bandwidth cap is 1 WIG (max 2 only when independent and non-conflicting). Multi-WIG drift (CE-03) is the most-warned failure mode in the book. A team-leader picking 2 Primary WIGs (Approach B) is structurally different from an individual juggling 3 personal goals.

## Audit metadata

- **Skill type**: multi-file orchestrator (Plan U merged from 4 source skills — 3 atomic D1-WIG coach skills + 1 topic-router; audit-mode added 2026-04-30 as path-B refactor)
- **Verification status**: V1 ✓ for personal-define + team-select scopes (book is leader-POV throughout Ch 6/7/12); V1 ⚠️ partial for member-comprehend scope (book authors the leader side of the line-of-sight conversation; member-side protocol is the symmetric inverse, with industry grounding from Edmondson / Grant / Meyer); V1 ✓ for audit-mode (D1-only application of Ch 2 grammar + Ch 6 four traps + Ch 7 four rules — all primary-source rules; consultant-from-artifact posture is derived per the same convention as `4dx-audit`)
- **Protocols**: `personal-define.md` (coach), `team-select.md` (coach), `member-comprehend.md` (coach), `audit-mode.md` (consultant)
- **Created**: 2026-04-30 (audit-mode added same day)
- **Output language**: SKILL.md body + protocols/standards in English; description + scope-detection prompts multilingual EN/JP/zh-TW
