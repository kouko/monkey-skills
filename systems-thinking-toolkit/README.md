# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Prose → CLD translator (carry-1) + 6 downstream consumer skills + 1 V1-weak personality auxiliary + 1 router. Grounded in Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey, 2002), packaged as the `systems-thinking-toolkit` plugin for monkey-skills.

## Skills

| Slug | Role | Description |
|---|---|---|
| `cld-craft` | Carry-1 producer | Prose → fully-annotated Mermaid CLD (12 hygiene rules + Rule 7 fuzzy elevation + S/O signing + R/B classification, all in Step 11) |
| `cld-archetypes` | CLD consumer | Recognize limits-to-growth (R+B coupling) or V/T/A (B-loop with delay) archetype + matching intervention playbook (Branch L + Branch V) |
| `cld-overlay` | CLD consumer | Multi-stakeholder CLD overlay + straddle-policy finding (outward conflict resolution) |
| `team-mental-model` | CLD consumer | Mental-model harmony + 4 observable leadership-energy proxies (cadence / active-listening / value-revisitation / symbol-narrative) — inward team protocol |
| `simulation-modeling` | CLD extension | Text-only CLD → stock-and-flow translation + learning-not-forecast discipline |
| `strategy-lever-and-cascade` | Non-CLD strategy | Lever-vs-outcome reframe + 3-timescale cascade + 3×N scenario table (Martian-test perturbation absorbed inline in v0.6 Step 5) |
| `manager-personality-quadrant` ⚠ V1-weak | Auxiliary | Framing-vs-analysis split + Gods/Gamblers/Grinders/Guides 2×2; **facilitation vocabulary only** (v0.6 Boundary strengthening); DiSC / Big Five / Hogan stronger alternatives exist for any personnel-touching work |
| `using-systems-thinking-toolkit` | Entry / router | Intent-uncertainty routing |

## Why this plugin

**Carry-1 thesis**: most systems-thinking value lies in the upstream translation step — turning messy prose into a structured causal loop diagram (CLD). This is the step where an LLM has the largest advantage over a human (parsing tangled narrative into nodes, links, and signed loops in seconds). Downstream applications (workshops, simulation, decision-making) are where LLMs are comparatively weak. So the plugin is intentionally biased toward the upstream step.

Sherwood's operational contribution is consolidated in `cld-craft`: 12 hygiene rules, Rule 7 fuzzy variable elevation, S/O link signing, and R/B loop classification all live inside Step 11. The output is a fully-annotated Mermaid CLD — readable, classifiable, and ready for any downstream consumer skill.

Downstream skills (cld-archetypes / cld-overlay / team-mental-model / simulation-modeling) consume the classified CLD that `cld-craft` produces. `strategy-lever-and-cascade` is the one non-CLD skill — it handles the strategic-reframe family of moves (lever-vs-outcome / cascade / scenarios) including the absorbed Martian-test perturbation. `manager-personality-quadrant` is retained as facilitation vocabulary only — for any real personnel work, route to Big Five / Hogan / DiSC / Hofstede etc. instead.

## How to use

1. Don't know which skill? Use `/systems-thinking-toolkit:using-systems-thinking-toolkit` for intent-routing.
2. Have prose / vicious cycle / death spiral language? Go directly to `/systems-thinking-toolkit:cld-craft`.
3. Have a CLD already? See the "I have a CLD — now what?" section in `/stt` for archetypes / overlay / simulation routing.
4. Doing strategy or team work? See `/strategy-lever-and-cascade` or `/team-mental-model`.
5. For systematic learning, follow the order in [`INDEX.md`](INDEX.md) — start with `cld-craft`.

## Provenance & limitations

- Distilled via `tsundoku:book-distill` RIA-TV++ pipeline (Adler → 5 parallel extractors → triple verification → RIA++ render → Zettelkasten linking → adversarial pressure test)
- Original 14-skill Stage-3 distill consolidated to 7 functional + 1 router via v0.4 R3 restructure + v0.6 sk13 absorption (zero content loss; all 14 original skill bodies recoverable from consolidated locations — see [`INDEX.md`](INDEX.md) mapping)
- One V1-weak skill remains: `manager-personality-quadrant`. v0.6 strengthened to "facilitation vocabulary only" Boundary; its "Graduate beyond" table routes to Big Five (NEO-PI-R) / Hogan / Heifetz / Edmondson / Klein / Hofstede / Tuckman / Lencioni for any personnel-touching work
- See [`references/`](references/) for Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3-original (`INDEX-original.md`) audit trail
- See [`ROADMAP.md`](ROADMAP.md) for v0.7+ candidates
- See `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-vs-original-book.md` for coverage audit vs original book (~85% methodology + ~70% illustrative material)

## License

MIT
