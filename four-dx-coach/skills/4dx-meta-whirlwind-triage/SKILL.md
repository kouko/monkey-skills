---
name: 4dx-meta-whirlwind-triage
description: |
  Pre-D1 capacity triage — whirlwind vs WIG split. Coach-mode (no artifact, vague firefighting): Socratic 7-day live time audit. Audit-mode (artifact provided + diagnostic intent): consultant verdict on existing time log / calendar export + stakeholder critique → protected-slot redesign + theater-reduction targets. Coach EN: "I'm always firefighting", "day job eats my whole week". Audit EN: "Audit my time log against 4DX", "Got feedback I'm focused on the wrong things — here's my calendar", "Stakeholder wants to revisit my time allocation", "Boss says I'm wasting time — here's my calendar". JP coach: 「日常業務に追われて目標に手がつかない」. JP audit: 「カレンダーを 4DX 視点で診断して」「上司にフィードバックされた、時間の使い方見て」「上司にダメ出しされた」. zh-TW coach: 「每天都在救火」. zh-TW audit: 「主管覺得我時間分配要調整」「review 後想討論時間配置」「老闆看我時間紀錄說亂忙」. NOT for productivity-tool requests, burnout / chronic overwork (→ professional support), reactive roles where firefighting IS the work (oncall SRE / ER / infant-care, CE-26), 4DX-fit questions (→ `4dx-meta-strategy-triage`), already-running 4DX cadence collapse (→ `4dx-sustain-momentum-rescue`), enterprise rollout audits (individual-scale only).
source_book: The 4 Disciplines of Execution — McChesney, Covey, Huling, Thele, Walker
source_chapter: Chapter 1 — The Real Problem with Execution
source_language: en
tags: [execution, focus, capacity-model, prerequisite, time-audit, 4dx, discipline-1]
related_skills:
  - 4dx-meta-strategy-triage
  - 4dx-d1-wig-formulation
  - 4dx-sustain-momentum-rescue
---

# 4dx-meta-whirlwind-triage — Pre-D1 capacity triage (multi-mode)

## Mission

Surface the whirlwind/WIG capacity reality before the user formulates a WIG. Same Ch. 1 anchor (~80% whirlwind / ~20% WIG; this skill sub-classifies the whirlwind portion as BAU-real vs BAU-theater — "BAU" is this skill's working synonym for the book's *whirlwind* term, sub-tagged because BAU-real / BAU-theater is more diagnostically actionable than a flat whirlwind tag); two delivery modes — Socratic coach over 7 days when the user starts from zero, structured consultant audit when the user already has a time-log artifact (often + a stakeholder critique).

## When this skill activates

### Multilingual trigger phrasings (covering both modes)

**Coach-mode (Socratic 7-day live audit, no artifact):**
- EN: "I'm always firefighting", "I want to do X but I never have time", "Every week the important stuff gets pushed", "My day job eats my whole week"
- JP: 「日常業務に追われて目標に手がつかない」「忙しすぎて自分の目標が進まない」「いつも雑用ばかりで本当にやりたいことが進まない」
- zh-TW: 「每天都在救火」「日常雜事吃掉所有時間」「想推進的事一直擱置」「想設目標但根本沒空執行」

**Audit-mode (consultant verdict on existing artifact, often + stakeholder critique):**
- EN: "Audit my time log against 4DX", "Got feedback I'm focused on the wrong things — here's my calendar", "Stakeholder wants to revisit my time allocation", "Manager flagged my time use — diagnose", "Boss says I'm wasting time on the wrong stuff — here's my calendar", "Diagnose my last 2 weeks of calendar — am I in whirlwind theater?", "Check my time log: do I actually have a protected WIG slot?"
- JP: 「カレンダーを 4DX 視点で診断して」「上司にフィードバックされた、時間の使い方見て」「マネージャーから方向性を直したいと言われた、calendar チェック」「上司に時間の使い方ダメ出しされた、何が違う？」「直近 2 週間の予定表を見て whirlwind 比率を出して」
- zh-TW: 「主管覺得我時間分配要調整，幫看哪裡」「review 後想討論時間配置」「老闆看我時間紀錄說亂忙，幫我用 4DX 診斷」「我的 calendar 在這，幫我看 whirlwind 比例」「過去兩週的時間表幫我審 4DX 角度看哪裡走樣」

### Non-activation signals (DO NOT fire when…)

- Productivity-system / app shopping (Notion vs Sunsama vs GTD-in-Notion) — that's tool selection, not capacity diagnosis
- Burnout / sustained overwhelm / depression / chronic 60+hr-wk overwork — clinical/coaching territory, time audit weaponizes awareness without solving it
- Genuinely reactive roles (oncall SRE rotation, ER triage, infant-care, frontline crisis-response) — whirlwind IS the strategic value, CE-26 boundary, route to `4dx-meta-strategy-triage`
- One-off / stroke-of-pen tasks ("file my taxes this weekend") — doesn't need 4DX at all
- 4DX-fit questions ("should I even use 4DX?") — `4dx-meta-strategy-triage`, not this skill
- 4DX cadence already collapsed for multiple weeks ("haven't done my 4DX in weeks", "WIG cadence broke") — `4dx-sustain-momentum-rescue`, this skill is first-time capacity audit only
- Enterprise rollout audits ("我們公司 50 個團隊要做時間稽核") — organizational cadence-setting, different (not-yet-built) skill; this skill is individual-scale only

## Mode detection

When this skill activates:

1. Determine **interaction shape**: **coach-mode** (Socratic, live, 7-day; no artifact in user message) vs **audit-mode** (synthesis from provided artifact — calendar export / time-tracker dump / past-week summary, often + stakeholder critique). Audit signals: user pastes / attaches / references "my calendar", "time log", "last 2 weeks", "boss says...", "manager flags...".
2. **Audit-mode pre-check** — before loading audit-mode, screen for clinical-burnout markers (sustained 60+hr weeks, weekend bleed, exhaustion language). If present, decline audit and route to professional support.
3. Load the matching protocol from `protocols/`.
4. Follow that protocol's E section step-by-step.

If ambiguous after reading the user's query, ask ONE question:

> EN: "Quick check: do you already have a **time log / calendar export** I should diagnose (audit-mode), or are we starting from zero with a 7-day live audit (coach-mode)?"
>
> JP: 「確認: 既存の **time log / calendar export** を診断する（audit-mode）のか、ゼロから 7 日間の live audit を回す（coach-mode）のか、どちらでしょう？」
>
> zh-TW: 「快速確認：你已經有 **time log / calendar export** 要我診斷（audit-mode），還是要從零開始跑 7 天 live audit（coach-mode）？」

If the signal in the original query is strong (artifact attached or "Audit my..." phrasing → audit-mode; vague "I never have time" → coach-mode), skip the question and load the protocol directly.

## Protocol routing table

| Detected mode | Load protocol | Agent voice |
|---|---|---|
| Coach (Socratic 7-day live audit, no artifact) | `protocols/coach-mode.md` | personal coach |
| Audit (existing time log + critique → diagnostic) | `protocols/audit-mode.md` | consultant |

After loading the protocol, follow its E section step-by-step. Each protocol carries its own R / I / A1 / A2 / E / B sections; this orchestrator does not run any audit content directly.

### Edge-case routing

- **Audit-mode requested but no artifact attached** — ask once for the calendar / time log; if none available, decline audit-mode and load coach-mode for a fresh 7-day audit.
- **Coach-mode requested but artifact already attached** — load audit-mode instead (artifact present overrides surface phrasing); offer coach-mode as fallback if the audit reveals insufficient sample.
- **Clinical-burnout markers in artifact or message** — decline both modes, route to professional support.
- **CE-26 reactive role revealed mid-audit** — flag once, route to `4dx-meta-strategy-triage`; do not manufacture a 20% WIG slot.
- **Cadence already collapsed (multi-week skip of running 4DX)** — `4dx-sustain-momentum-rescue` first; this skill is first-time capacity audit only.

## Shared standards

No skill-internal standards files extracted at this time — both protocols rely on the same inline Ch. 1 framing (~80/20 capacity model, WHIRLWIND / WIG / NEITHER tags, BAU-real vs BAU-theater sub-classification, ~20% protected-slot anchor with named protector). If future drift surfaces between the two protocols, extract `standards/whirlwind-wig-tagging.md` and `standards/protected-slot-rule.md` at that point.

## Cross-skill relations

- **Upstream gate** — `4dx-meta-strategy-triage` decides whether 4DX is the right tool at all; this skill assumes that gate has cleared and asks "do you have spare capacity to use it?"
- **Downstream handoff** — `4dx-d1-wig-formulation` consumes the protected-slot output (numeric N + calendar blocks + protector ritual); this skill must clear before D1 WIG formulation, or the WIG becomes aspirational fantasy.
- **Sibling rescue path** — `4dx-sustain-momentum-rescue` runs *after* a 4DX cadence has collapsed; this skill runs *before* the first WIG. The boundary is sharp: multi-week skip of running 4DX → rescue, not capacity audit.

## Boundary (cross-mode common)

The mode-specific boundary lives in each protocol's B section. The cross-mode common boundary:

- **Capacity model is the load-bearing claim.** ~80/20 is a structural ratio, not a motivational target. Both modes refuse to "carve out time" without naming the protector ritual that defends it from Parkinson's-Law devouring.
- **Time audit weaponizes awareness if the user is in clinical burnout.** Both modes hard-decline when sustained overwork / despondency / sleep collapse is visible. Refer out to professional support; do not run a time audit.
- **CE-26 reactive role invalidates the 80/20 frame.** Both modes flag once and route to `4dx-meta-strategy-triage` when the user's role is intrinsically reactive (oncall SRE, ER, infant-care, crisis-response). The whirlwind IS the strategic value in those domains; manufacturing a 20% WIG slice degrades the actual job.
- **Most-important confusion is the trap downstream.** Even after a clean audit, users tend to pick a WIG that is the *most important* part of their job (whirlwind optimization, not breakthrough work). Both modes warn the trap is coming and that `4dx-d1-wig-formulation`'s P-04 rule (where-breakthrough-needed, not what-is-most-important) will catch it.
- **Calendar protection ≠ attention protection.** Newport's attention-residue finding applies to both modes: a calendar-protected slot without phone-out / notifications-off / single-task degrades to ~5–8% strategic output. Both modes name the protector ritual at audit-output time.

## Audit metadata

- **Skill type**: multi-file orchestrator (path B refactor — Wave 2). coach-mode = original SKILL.md content (Socratic 7-day live audit). audit-mode = added 2026-04-30 for artifact-based diagnostic with stakeholder-critique mapping.
- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓ for coach-mode (preserved verbatim from prior single-file SKILL.md). V1 partial for audit-mode (logic = symmetric inverse of coach-mode steps 1-4 applied to a static artifact + critique-to-rule mapping; anchored on Ch. 1 capacity model + Reinertsen / Goldratt / Newport industry grounding).
- **Distilled at**: 2026-04-29 (coach-mode), 2026-04-30 (audit-mode + orchestrator)
- **Output language**: SKILL.md body + protocols in English (source-book language); description + mode-detection prompts multilingual EN / JP / zh-TW; metadata English
