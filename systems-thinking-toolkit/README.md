# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Eight systems-thinking skills + 1 entry/router, distilled from Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey, 2002), packaged as the `systems-thinking-toolkit` plugin for monkey-skills. **v0.4 R3 restructure** organizes around `cld-craft` as the carry-1 prose→Mermaid CLD translator; everything else either consumes that CLD or extends to non-CLD outputs.

## What's included

| Skill | Role | Purpose |
|---|---|---|
| `cld-craft` | Carry-1 producer | Prose → fully-annotated Mermaid CLD (12 rules + fuzzy elevation + S/O signing + R/B classification absorbed in Step 11) |
| `cld-archetypes` | CLD consumer | Recognize limits-to-growth (R+B coupling) or V/T/A (B-loop with delay) archetype + matching intervention playbook |
| `cld-overlay` | CLD consumer | Multi-stakeholder CLD overlay + straddle-policy finding |
| `team-mental-model` | Practice | Mental-model harmony + 4 observable leadership-energy proxies (cadence / active-listening / value-revisitation / symbol-narrative) |
| `simulation-modeling` | CLD extension | Text-only CLD → stock-and-flow translation + learning-not-forecast discipline |
| `strategy-lever-and-cascade` | Non-CLD | Lever-vs-outcome reframe + 3-timescale cascade + 3×N scenario table (Martian-test perturbation absorbed inline in v0.6 Step 5) |
| `manager-personality-quadrant` ⚠ V1-weak | Auxiliary | Framing-vs-analysis split + Gods/Gamblers/Grinders/Guides 2×2; **facilitation vocabulary only** (v0.6 Boundary strengthening); DiSC / Big Five / Hogan stronger alternatives exist for any personnel-touching work |
| `using-systems-thinking-toolkit` | Entry / router | Intent-uncertainty routing to the right skill |

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
- One V1-weak skill remains (`manager-personality-quadrant`) per Stage 1.5 — kept with strengthened "facilitation vocabulary only" Boundary in v0.6. `innovaction-martian-test` was absorbed into `strategy-lever-and-cascade` Step 5 in v0.6 (Martian-test perturbation now inline). Stronger prior-art alternatives for personality work: DiSC, Big Five (NEO-PI-R), Hogan, Situational Leadership.
- See [`references/`](references/) for Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3-original (`INDEX-original.md`) audit trail
- See [`ROADMAP.md`](ROADMAP.md) for v0.7+ candidates (6 PR #271 audit body fixes; CI desc ↔ skill folder drift check; stock-flow simulation Python companion; Edmondson teaming-safety hand-off)

## License

MIT
