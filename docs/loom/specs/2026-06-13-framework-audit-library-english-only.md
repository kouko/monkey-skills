# Brief — framework-audit library + consuming prompt → English-only

- **Date**: 2026-06-13
- **Skill**: `research-toolkit/skills/deep-deep-research/`
- **Branch**: `feat/deep-deep-research-vs-angle-selector` (continue)
- **Trigger**: user decision "全英文化" (Q1 follow-up to the shipped lever ①)

## Problem

The lever-① framework-audit resource (`references/framework-audit-library.md`) and
its consuming prompt (`framework_audit.py:classify_prompt` / `audit_prompt`) are
**bilingual ZH/EN**. The skill ships in a public repo, is marketed as
agent-portable ("run inside any coding agent host"), and its SKILL.md body +
sibling code are English. The mixed register is inconsistent and the Chinese is
translation overhead (the frameworks are all English-native canonical terms).
Job: *make the framework-audit library and everything that reads its routing
vocabulary fully English, with no behavior change.*

## Users

The agent running the (opt-in) framework-audit pass. It Reads the library, the
`classify_prompt` output, and the `audit_prompt` output. English-only is more
universally consumable and marginally cheaper in tokens; an LLM maps a
Chinese-language research question to an English route label fine, so no routing
capability is lost.

## Smallest End State

Translate the **four coupled touchpoints** to English, preserving every
framework cell / structure / provenance / logic identically — language-only:
1. `references/framework-audit-library.md` — H1, routing-table 題型 column +
   header, framework-name 中譯 glosses, the "框架自身的集體盲點" header, and the
   12 blind-spot ZH item-names. This file is the **SSOT for the English
   routing-key vocabulary**.
2. `scripts/framework_audit.py` — `classify_prompt` + `audit_prompt` bodies +
   the `DEFAULT_FRAMEWORKS`/`select` comments, using the **exact same English
   routing keys** the translated library defines (consistency is load-bearing:
   classify tells the agent which library row to walk).
3. `scripts/test_framework_audit.py` — the three assertions with dead Chinese
   `or "路由表"/"格子"` OR-branches → assert the English term only.
4. `SKILL.md` — the one `萬用起手` reference (line ~175) → English.

All 69 tests stay green; no synced primitive touched.

## Current State Evidence

(Grepped — exact CJK touchpoints)
- **Library** `references/framework-audit-library.md:1` (H1), `:32` (routing-table header), `:34-69` (題型 column), framework blocks `:81-191` (`(EN / 中譯)` names), `:212` (blind-spots header), `:219-230` (12 blind-spot ZH names).
- **framework_audit.py** `:74,89-100,106` (classify_prompt: 題型/路由表/個股/產業/法規/UX/安全/萬用起手/走查格子), `:110,156,171` (audit_prompt: 一格一格走查格子 / 框架自身的集體盲點), `:114-115,290` (DEFAULT_FRAMEWORKS/select comments: 萬用起手). `DEFAULT_FRAMEWORKS = ["MECE/issue tree","5W1H","PMEST","SCQA"]` (`:117`) is already English — keep.
- **test_framework_audit.py** `:56,:82` (`"routing table" in lower or "路由表" in prompt`), `:107` (`"cell" in lower or "格子" in prompt`) — English branch already passes; drop the dead ZH OR-branch.
- **SKILL.md** `:175` (`the general 萬用起手 route`).
- **Reverse (SSOT)**: none of the 4 synced primitives (schemas/rank/prompts/dedup.py) are in scope — confirmed they carry no routing vocabulary.

## Decision

Behavior-preserving **language refactor**: translate the four touchpoints to
English. The translated **library is the SSOT** for the English routing-key
names; `classify_prompt`/`audit_prompt`/`SKILL.md` mirror that exact vocabulary.
Framework cells, provenance citations, dedup notes, the 12 blind-spot *content*,
and all deterministic logic are unchanged — only surface language. Tests updated
only to drop now-dead Chinese OR-branches (assert the English term).

## Out of Scope

- **Q2 file-split** (index + per-framework files) — declined (premature at 20-framework scale).
- **`mode_route.py` / `test_mode_route.py` `§三-C 測試1` strings** — provenance citations to a Chinese-titled vault eval note; translating reduces traceability. Left as-is.
- Any change to framework cells, the routing-table framework choices, the 12 blind-spot substance, or any deterministic logic / schema.
- Any synced-primitive edit; any default/VS/synthesis path change.

## Alternatives Considered

- **Keep bilingual** — rejected by user (consistency + portability for a public skill).
- **Translate names but keep ZH routing keys** — rejected: the routing keys are exactly the agent-facing match surface; half-translation re-introduces the mixed register the change exists to remove.
