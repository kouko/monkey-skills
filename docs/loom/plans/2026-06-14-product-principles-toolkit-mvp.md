# Plan: product-principles-toolkit MVP

**Source brief**: docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md
**Total tasks**: 6
**Critical-path depth**: 3 (≤5 ✓) — T1 → T5 → T6
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-14, 14/14 — 1 advisory: T3/T4 missed-parallel)

> **Scope:** SDD-able infra (reference doc, plugin scaffold + manifests, validator). The `product-principles`
> SKILL.md body is authored via `dev-workflow:skill-creator-advance` (T6, grep/activation RED), not bare TDD.
> New plugin dir: `product-principles-toolkit/`. Governance: synthetic examples; identifiable-token grep before
> any commit; explicit `git add <paths>`.

---

## Task 1 — Author principles-rules reference

- **Description**: Write `product-principles-toolkit/skills/product-principles/references/principles-rules.md` — the `PRINCIPLES.md` authoring contract: `## North Star` (product goal + success definition) + `## Principles` (3–7 non-negotiable rules, **each MUST carry a falsifiable check**; reject platitudes). Include constitution/steering grounding (Spec Kit `constitution.md`, Kiro steering) + 2–3 synthetic ✅/❌ examples ("primary task ≤3 steps" vs "be delightful").
- **Module**: `product-principles-toolkit/skills/product-principles/references/principles-rules.md`
- **Files touched**: `product-principles-toolkit/skills/product-principles/references/principles-rules.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -ci 'falsifiable\|north star\|check' principles-rules.md` returns <3.
  - **GREEN**: North Star + Principles format defined; per-principle falsifiable-check requirement stated; synthetic ✅/❌ examples present; constitution/steering prior art cited.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`## Principles` — 3–7 non-negotiable principles, each carrying a falsifiable check"

## Task 2 — Plugin manifest scaffold

- **Description**: Write `product-principles-toolkit/.claude-plugin/plugin.json` — name `product-principles-toolkit`, version `0.1.0`, key-free description ≤1024 chars (Codex limit), author/homepage/repo/license/keywords. Mirror `spec-toolkit/.claude-plugin/plugin.json`. Add `test_plugin_manifest.py`.
- **Module**: `product-principles-toolkit/.claude-plugin/plugin.json`
- **Files touched**: `product-principles-toolkit/.claude-plugin/plugin.json`, `product-principles-toolkit/scripts/test_plugin_manifest.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_plugin_manifest.py`
- **Acceptance**:
  - **RED**: `test_plugin_manifest.py::test_manifest_valid` fails.
  - **GREEN**: manifest parses; required fields present; description ≤1024; test passes.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Build a new, separate `product-principles-toolkit` plugin"

## Task 3 — Marketplace entry

- **Description**: Add a `product-principles-toolkit` entry to root `.claude-plugin/marketplace.json` (name/description/source) consistent with the manifest. Add `test_marketplace_entry.py`.
- **Module**: `.claude-plugin/marketplace.json`
- **Files touched**: `.claude-plugin/marketplace.json`, `product-principles-toolkit/scripts/test_marketplace_entry.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_marketplace_entry.py`
  - `/Users/kouko/GitHub/monkey-skills/product-principles-toolkit/.claude-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `test_marketplace_entry.py::test_entry_matches_manifest` fails.
  - **GREEN**: entry present + name/description match manifest; test passes.
- **Dependencies**: Task 2 completes first
- **Independent**: false  # mirrors the manifest authored in Task 2
- **Brief item covered**: "a root `.claude-plugin/marketplace.json` entry"

## Task 4 — README

- **Description**: Write `product-principles-toolkit/README.md` — what the plugin does (cross-cutting product constitution), `PRINCIPLES.md` output (North Star + falsifiable principles), that it governs design/spec/code incl headless, key-free posture. Mirror `spec-toolkit/README.md`.
- **Module**: `product-principles-toolkit/README.md`
- **Files touched**: `product-principles-toolkit/README.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/README.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `test -f product-principles-toolkit/README.md` fails.
  - **GREEN**: README documents `PRINCIPLES.md` output + cross-cutting governance + key-free.
- **Dependencies**: Task 2 completes first
- **Independent**: false  # describes the manifest's plugin
- **Brief item covered**: "a new plugin = `.claude-plugin/plugin.json` + `skills/` + `scripts/` + `README.md`"

## Task 5 — Validator: PRINCIPLES.md structure + falsifiable-check

- **Description**: Write `product-principles-toolkit/scripts/validate_principles_output.py` (check-runner pattern from `validate_spec_output.py`; CLI `python validate_principles_output.py <PRINCIPLES.md>` → exit 0/1): checks `## North Star` + `## Principles` exist, 3–7 principles, and **every principle bullet carries a falsifiable check marker** (per `references/principles-rules.md`). Add `test_validate_principles_output.py`.
- **Module**: `product-principles-toolkit/scripts/validate_principles_output.py`
- **Files touched**: `product-principles-toolkit/scripts/validate_principles_output.py`, `product-principles-toolkit/scripts/test_validate_principles_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/validate_spec_output.py`
  - `/Users/kouko/GitHub/monkey-skills/product-principles-toolkit/skills/product-principles/references/principles-rules.md`
- **Acceptance**:
  - **RED**: `test_validate_principles_output.py::test_principle_without_check_flagged` fails.
  - **GREEN**: validator flags a principle with no check + a missing North Star/Principles section + a count outside 3–7; complete fixture passes; CLI exit codes correct.
- **Dependencies**: Task 1 completes first
- **Independent**: false  # encodes the rules authored in Task 1
- **Brief item covered**: "A `validate_*` script … checks the two sections exist and every principle carries a check"

## Task 6 — Author product-principles SKILL.md (via skill-creator-advance)

- **Description**: Author `product-principles-toolkit/skills/product-principles/SKILL.md` — the one skill: sparse idea → elicit + write `PRINCIPLES.md` (North Star + 3–7 falsifiable principles per `references/principles-rules.md`) → run `scripts/validate_principles_output.py`. Output to consumer `docs/loom/PRINCIPLES.md`. Flat-skill; references by relative path. Iterated via `dev-workflow:skill-creator-advance`.
- **Module**: `product-principles-toolkit/skills/product-principles/SKILL.md`
- **Files touched**: `product-principles-toolkit/skills/product-principles/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/product-principles-toolkit/skills/product-principles/references/principles-rules.md`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/skills/spec-expansion/SKILL.md`
- **Acceptance**:
  - **RED**: grep diagnostic — SKILL.md absent, OR description >1024 chars, OR body doesn't reference `references/principles-rules.md` + `scripts/validate_principles_output.py`, OR not flat-skill.
  - **GREEN**: SKILL.md present; description ≤1024; declares `PRINCIPLES.md` output + the `docs/loom/` location; references the rules doc + validator; flat-skill; passes the skill-creator-advance activation harness.
- **Dependencies**: Tasks 1, 5 complete first
- **Independent**: false  # consumes the reference doc + validator contract
- **Brief item covered**: "One skill (`product-principles`) that turns a sparse idea into `PRINCIPLES.md`"

## Notes

- **Parallel leaves (level 1):** Tasks 1, 2 are `Independent: true`, disjoint files → may dispatch concurrently.
- **T6 (SKILL.md) routes to `dev-workflow:skill-creator-advance`**, not a bare implementer; RED is a grep/activation diagnostic (markdown-artifact convention).
- **Out of this plan (per brief Out of Scope):** the downstream principles-conformance lens (P2), a second `principles-conformance` skill, business-strategy framing.
