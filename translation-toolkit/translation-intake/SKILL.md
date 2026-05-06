---
name: translation-intake
description: Layer 1 of translation-toolkit. Clarifies translation parameters (5 axes — mode / register / strategy / locale / domain — plus skopos) via auto-detect or explicit user input. Output is an intake-spec consumed by downstream skills (translation-i18n / -doc / -creative / -audit).
version: 0.1.0
---

# translation-intake

> **TODO**: full prompt body lands in Task D2.

## Purpose

Translates user request into a structured 5-axis intake spec for downstream translation skills.

## Modes

- **auto** (default): single LLM source-analysis call infers all 5 axes from source content
- **explicit** (`--explicit` / `-e`): user is prompted for each axis + skopos

See `protocols/intake-auto.md` and `protocols/intake-explicit.md` (Task D2).

## 5 axes

- **mode**: literal | faithful | localized | transcreation
- **register**: formal | neutral | warm | playful
- **strategy**: domestication | foreignization
- **locale**: BCP-47 (e.g., ja-JP, zh-TW)
- **domain**: one or more from {general, ui, tech.{software,web,data,crypto}, gov, legal, medical, finance, marketing, statistics, typography}

## Output

Writes intake-spec.json to be consumed by next skill in the pipeline.
