# Loom doc language layering — brief

> **Phase**: brainstorming output（`brainstorming` → `writing-plans` handoff）
> **Date**: 2026-08-14
> **Author**: agent（kouko — 2026-08-13..14 研究建議分層語言政策，勝過全面翻英文）

## Problem

When the loom family writes plan and spec documents, one file serves two readers with opposite language needs: agents execute the precision fields (acceptance criteria, requirement lines, task bodies) — where frontier-model reasoning accuracy is highest in English — while kouko reads and judges the sense-making fields (problem framing, decisions) in her own language. Today neither `writing-plans` nor `loom-spec` states any language rule for the machine-executed fields, so authors default to the emergent conversation-language-everything pattern, the two repos have already diverged (kumiko plan/spec prose is fully Chinese; monkey-skills' own briefs are ~99% English), and the existing display layer (`adjudication-view`) has no stated policy to hook into.

## Users

- **kouko（做裁定的人）** — reads/judges plans and specs in Traditional Chinese; writes sense-making content in her own language; `adjudication-view` already renders English artifacts for careful sign-off.
- **Implementer / spec-reviewer / code-quality-reviewer subagents** — execute the machine-executed fields: plan task Description + Acceptance, spec requirement lines + Scenario criteria.
- **plan-document-reviewer / spec reviewers** — read Acceptance and requirement lines against the brief; `plan-document-reviewer-prompt.md:12` already accepts Gloss in conversation language.
- **Future loom-family users** — the plugin ships to the marketplace; every plan/spec written after this change follows the stated policy.

## Smallest End State

A layered language policy is stated in the two artifact-producing skills (`writing-plans`, `loom-spec`) plus a pointer in brainstorming's brief-format, so plan/spec content is deliberately split: machine-executed precision content in English, human sense-making content in the session's conversation language, and the existing `adjudication-view` named as the display layer for reading the English precision content in zh-Hant/ja. Success criteria: a fresh-context cold-reader following the policy produces a sample plan whose language layering lands correctly (quality-floor §5 rule-text row); existing enforcement tests stay green. Non-criteria: no blanket English flip, no rewrite of existing documents, no new display mechanism.

- BI-1 — writing-plans declares the layered policy: task **Description** bodies and **Acceptance** (RED/GREEN) are written in English; **Steps** titles, **Gloss**, **Goal**, task titles, and **Notes** stay in the session's conversation language.
- BI-2 — loom-spec declares the layered policy: spec-delta **requirement lines** (RFC-2119) and **Scenario** GIVEN/WHEN/THEN criteria are written in English; proposal.md narrative (Problem/Users/Smallest End State/Decision reasoning) stays in conversation language.
- BI-3 — brainstorming's brief-format carries a pointer: **BI statements** are machine-executed precision content → English (they seed the spec).
- BI-4 — the policy cites `adjudication-view` as the display layer for careful reading of English precision content in zh-Hant/ja, and is stated inline in each skill (no new shared reference file).
- BI-5 — verification: a fresh-context cold-reader dogfood writes a sample plan following the policy and the language layering lands correctly.

## Current State Evidence

- **Forward**: `writing-plans/SKILL.md:131-137` declares only Steps-titles/Gloss in conversation language; task Description and Acceptance (the execution contract at `writing-plans/references/plan-format.md:39-42,126-130`) carry **no** language annotation — the English layer is entirely unstated. `loom-spec/skills/spec-expansion/SKILL.md:362-442` (§The hybrid output format) has **no** language policy; English is implied only structurally (RFC-2119 at :389-394, GIVEN/WHEN/THEN at :391-394). The `adjudication-view` protocol (`loom-code/skills/using-loom-code/protocols/adjudication-view.md:13-21,263-265`) already implements the "machine-precise English + disposable localized view" model this policy names.
- **Reverse**: `references/plan-format.md` is the schema SSOT; the three READMEs (`README.md`/`README.ja.md`/`README.zh-TW.md`) are orientation mirrors pinned by `loom-code/scripts/test_writing_plans_readme_sync.py:1-5` (READMEs must not misinform, field names untranslated, README routes to plan-format.md as owner). Enforcement tests restate the current Steps/Gloss convention verbatim: `loom-code/scripts/test_plan_format_progress_fields.py:82,88,100,188`, `test_wp_extraction_pointers.py:196,204`; the reviewer prompt accepts Gloss at `plan-document-reviewer-prompt.md:12`.
- **Error**: content language is not structurally checkable — no test can assert "Description is English"; enforcement is the repo's rule-text quality floor (cold-reader executes the skill blind on one real case). The 44.4% wrong-language-turn leak (`docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md:82-84,97-99`) is a conversation-narration concern governed by `family-relay.md` — the policy adds English precision content to artifacts, which is exactly what adjudication-view was built to serve; no new failure path, but the leak boundary is noted.
- **Data**: the two repos have diverged with no stated rule — kumiko plan/spec prose is fully Chinese (`docs/loom/plans/*.md` ×10, `docs/loom/specs/*.md` ×13), monkey-skills' own briefs are ~99% English (3 most recent: 2–21 CJK lines / 197–350 lines). plan-format.md's per-task field schema (`Description`/`Acceptance`/`Steps`/`Gloss`) is the field set the policy annotates.
- **Boundary**: `[FRAGILE]` cross-plugin — loom-code and loom-spec reference each other's SKILLs/scripts, never each other's `references/*.md` (`writing-plans/SKILL.md:209-255` invokes loom-spec scripts; `continuous-mode.md:59-62`); each plugin keeps references self-contained; the only shared reference is `loom-pipeline/hooks/family-relay.md:5-9`. adjudication-view supports zh-Hant/ja only (`adjudication-view.md:178-184`); English sessions read artifacts directly.
- **Evidence paths**: `loom-code/skills/writing-plans/SKILL.md:131-137,198,209-255`; `.../references/plan-format.md:39-42,126-130,303,320-322`; `.../references/plan-document-reviewer-prompt.md:12`; `loom-code/scripts/test_plan_format_progress_fields.py:82,88,100,188`; `loom-code/scripts/test_wp_extraction_pointers.py:196,204`; `loom-code/scripts/test_writing_plans_readme_sync.py` (full); `loom-spec/skills/spec-expansion/SKILL.md:362-442,389-400`; `loom-spec/skills/using-loom-spec/SKILL.md:22-27,71-73`; `loom-spec/skills/completeness-critic/SKILL.md:437`; `loom-code/skills/using-loom-code/protocols/adjudication-view.md:13-21,147,178-184,263-265`; `loom-code/skills/brainstorming/references/handoff-brief-format.md` (full); `loom-pipeline/hooks/family-relay.md:5-9,14-15,81`; `docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md:82-84,97-99`; `docs/loom/memory/a-semantics-change-needs-a-plugin-wide-contradiction-sweep-arm.md`; `docs/loom/memory/core-rule-removal-needs-plugin-wide-sweep.md`.

## Decision

We will add a layered language policy to `writing-plans` and `loom-spec` (plus a BI pointer in brainstorming's brief-format): machine-executed precision content (plan Description/Acceptance, spec requirement lines/Scenario criteria, BI statements) is written in English — where frontier-model reasoning accuracy is highest on the exact content that determines pass/fail; human sense-making content (Problem/Users/Smallest End State/Decision reasoning, Steps/Gloss/Goal/Notes) stays in the session's conversation language; and `adjudication-view` is cited as the display layer for reading the English precision content in zh-Hant/ja. The policy is stated inline in each skill — no new shared reference file (cross-plugin references point at SKILLs, never at each other's references; a short policy pins better inline). We will NOT blanket-flip everything to English (token savings are ~10-30%, second-order; authoring fidelity lives in the author's language), and we will NOT rewrite any existing plan/spec document.

- BI-6 — The umbrella outcome: both skills (plus the brief pointer) carry a consistent, inline layered language policy, with adjudication-view cited as the display layer.

## Out of Scope

- Rewriting existing plan/spec documents in either repo (kumiko's Chinese docs and monkey-skills' English docs stay as historical artifacts; the policy governs new output only).
- A validation script or test that asserts content language (structurally impossible; enforcement is the rule-text cold-reader gate).
- Changes to conversation-narration rules (`family-relay.md`) or the 44.4%-leak mitigation.
- Translating existing English skill bodies / reference files into conversation language.
- Touching the `[slats]`-adjacent config/schema or any non-language concern in either plugin.
- Adding any new display mechanism beyond citing the existing adjudication-view.

## Alternatives Considered

1. **All-English canonical + disposable localized renders for every read** — the display-layer-only model (industry norm for team-internal docs). Rejected: it sacrifices authoring fidelity on sense-making content — kouko writes and reads decisions most precisely in her own language; the layered split keeps sense-making in the author's language while still giving the model English precision content.
2. **Status quo (leave the language convention unstated)** — rejected: precision content stays wherever the author happened to write, the two repos have already diverged (kumiko Chinese, monkey-skills English) with no rule to reconcile them, and the existing display layer has no policy to hook into.
3. **A shared language-policy reference file both skills point to** — rejected on the plugin's own cross-plugin convention: loom-code/loom-spec reference each other's SKILLs/scripts but keep `references/*.md` self-contained (the only shared reference is `family-relay.md` in loom-pipeline); a short policy is better pinned inline in each skill, transcribed verbatim per the `pin-shared-wording` practice memory.

(Evidence base — prior-session research: EN+JA WebSearch consensus that internal docs are English-canonical with localize-only-user-facing-surface; token savings ~10-30% "rarely justifies switching"; frontier models reason internally in English, so Chinese input degrades precision-critical comprehension ~2-5% normal / up to 30-60% adversarial (ACL 2025, GPT-4o & Claude-3.5); counterweight = authors write most precisely in their own language.)

## What Becomes Obsolete

- BI-7 — `writing-plans/SKILL.md:131-137`'s per-field conversation-language statements, consolidated into the umbrella policy in the same change (reworded, not deleted).

## Open Questions

(empty)

## Diagrams

N/A — no flow/state/architecture-shaped content: the change is a text-convention declaration in two skill files plus a brief pointer and a dogfood verification; the section-mapping table belongs in the skill text, not here.
