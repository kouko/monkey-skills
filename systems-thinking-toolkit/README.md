# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Nine systems-thinking skills distilled from Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey, 2002), packaged as the `systems-thinking-toolkit` plugin for monkey-skills.

## What's included

| Skill | Purpose |
|---|---|
| `using-systems-thinking-toolkit` | Route to the right method based on situation |
| `loop-and-link-primitives` | Foundational: R/B loop diagnosis + S/O link signing (sk01+sk02) |
| `cld-craft` | Draw causal loop diagrams with workshop discipline — 12 rules + fuzzy variable elevation (sk03+sk04) |
| `limits-to-growth-take-the-brakes-off` | R-loop braked by B-loop archetype; constraint-relief over engine-pushing (sk05) |
| `variance-target-action-template` | Generic B-loop control template + do-nothing-under-oscillation diagnostic (sk06) |
| `strategy-lever-and-cascade` | Lever-vs-outcome reframe + 3-timescale cascade + 3×N scenario planning (sk07+sk08) |
| `stakeholder-and-team-thinking` | Multi-perspective CLD overlay + mental-model harmony for teams (sk09+sk10) |
| `simulation-modeling` | Stock-flow translation + learning-not-answers discipline (sk11+sk12) |
| `innovaction-martian-test` ⚠ V1-weak | Feature-perturbation scenario generation; TRIZ / morphological-analysis stronger alternatives exist |
| `manager-personality-quadrant` ⚠ V1-weak | Executive-personality 2×2; DiSC / MBTI / Hogan stronger alternatives exist |

## Why this plugin

Systems thinking isn't just diagrams — it's a discipline for diagnosing **structure** rather than blaming **events**. Sherwood's contribution is operational: causal loop diagrams reduce to two loop types (reinforcing / balancing), classifiable by counting Os, with the same structural identity driving virtuous-vs-vicious spin. This plugin distills the manager-facing portions of his book into nine atomic, composable skills.

Profile-B merged from the original 14-skill Stage-3 distill. Five compose-with pairs collapsed into single skills (preserving the source-unit citation trail); four standalone (sk05/sk06 contrast at cognitive-frame level; sk13/sk14 V1-weak retained per user override pending v0.2 re-evaluation).

## How to use

1. Don't know which skill? Use `/systems-thinking-toolkit:stt` to route via the intent table.
2. Know the situation? Use a per-skill command (see [`INDEX.md`](INDEX.md) for the full list).
3. Learning systematically? Follow the recommended order in [`INDEX.md`](INDEX.md) — start with `loop-and-link-primitives`.

## Provenance & limitations

- Distilled via `tsundoku:book-distill` RIA-TV++ pipeline (Adler → 5 parallel extractors → triple verification → RIA++ render → Zettelkasten linking → adversarial pressure test)
- Profile-B merge of 14 original Stage-3 skills into 9 (5 compose-with pairs + 4 standalone)
- Two skills (`innovaction-martian-test`, `manager-personality-quadrant`) are V1-weak per Stage 1.5 — they have stronger prior-art alternatives (TRIZ, morphological analysis, DiSC, MBTI, Hogan, Situational Leadership). See each skill's Boundary section.
- See [`references/`](references/) for Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3-original (`INDEX-original.md`) audit trail
- See [`ROADMAP.md`](ROADMAP.md) for v0.2+ candidates (sk13/sk14 merger options; TRIZ companion skill; stock-flow simulation Python companion; Edmondson teaming-safety hand-off)

## License

MIT
