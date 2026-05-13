# Systems Thinking Toolkit Roadmap

## v0.1.0 (initial release, 2026-05-12)

- 9 skills via Profile B merge (5 compose-with pairs + 4 standalone) + 1 entry/router
- Tri-lang per-skill + plugin-level READMEs
- Stage 0/1.5/3 audit trail under `references/`
- 10 slash commands (router + 9 per-skill)

## v0.2.0 (body-level fixes + JA/zh-TW normalization, 2026-05-12)

- A1-A5 body fixes (cld-craft halt OR-clause; stakeholder energy-pump operationalization; variance Step 0 SPC + 1.5× delay heuristic; manager-quadrant observable-cue table + Guides circularity; simulation Stage-2 sensitivity sweep)
- A8 JA/zh-TW description hint normalization (2 of 10 descriptions)
- A9 skill-judge re-baseline (5 body-fixed skills, plugin mean 108.4 → 109.3/109.7)

## v0.3.0 (prose→Mermaid diagram emission, 2026-05-12)

- `cld-craft` Step 11 emits Mermaid CLD as required deliverable
- `loop-and-link-primitives` Step 11 emits annotated Mermaid CLD (R/B classification)
- NEW `cld-craft/references/cld-mermaid-emit.md` — canonical CLD Mermaid convention (S/O edge labels, R/B `%%` annotation, 5 dangle shapes, R/B color palette). Adapted from `obsidian/skills/obsidian-mermaid-visualizer/flow/circular-flow.md`
- Spot-test 3 prose cases (SaaS retention / engineering team / inventory oscillation) — all clean Mermaid CLDs

## v0.4.0 (R3 most-complete CLD-centric restructure, 2026-05-12)

CLD-centric reorganization based on practical-utility analysis (memory `project_systems_thinking_toolkit_v0.3_anchor`):

- **R3-1 merge** — `limits-to-growth` + `variance-target-action` → **`cld-archetypes`** (recognize Sherwood archetype on classified CLD + intervention playbook)
- **R3-2 split** — `stakeholder-and-team-thinking` → **`cld-overlay`** (Protocol O multi-CLD overlay) + **`team-mental-model`** (Protocol I leadership-energy proxies)
- **R3-3 absorb** — `loop-and-link-primitives` → into `cld-craft` Step 11 (carry-1 mega-skill); classification protocol extracted to `cld-craft/references/loop-classification-protocol.md`
- **R3-4 cross-cutting** — INDEX.md re-derive (10 → 9 nodes); using-* router table; commands (delete 4, create 3); plugin README skill list
- **R3-5 re-baseline** — skill-judge on changed skills; target ≥ A grade, no dimension regression vs v0.3.0
- Net: 9 functional + router → 8 functional + router (-1 dir overall)

## v0.5.0 (i18n trigger coverage + language policy + Case B5, 2026-05-13)

- 6 v0.5 items scoped from PR #274 Chinese-input dogfood audit
- zh-TW + JA symptom keywords added to cld-craft + cld-archetypes (+20 zh-TW + +12 JA)
- Router table cells gain EN + zh-TW + JA parenthetical examples
- Tier-1 reversibility test zh-TW + JA phrasings in loop-classification-protocol.md
- Language handling policy subsection in cld-craft SKILL.md
- zh-TW worked example in cld-mermaid-emit.md
- New Case B5 — Algorithm-Belief Pseudo-Target (modern platform variant; NOT in Sherwood 2002)
- Side-fix: plugin.json + marketplace.json descriptions had been stale at v0.4 (still described v0.1.x 9-skill structure)

## v0.6.0 (sk13 absorption + sk14 strengthened Boundary, 2026-05-13)

V1-weak resolution per Bundle C "split decision":

- **sk13 (`innovaction-martian-test`) ABSORBED** into `strategy-lever-and-cascade` Step 5 (Martian-test perturbation now inline 4-step procedure: 5a feature-list density bar / 5b one-feature dramatic perturbation / 5c consequence chain / 5d stop at 3-4 plausible futures). Skill folder + `/martian-test` command deleted. TRIZ + morphological analysis + SCAMPER cross-refs preserved as prior-art Boundary note. Net: 8 → 7 functional + 1 router
- **sk14 (`manager-personality-quadrant`) KEPT** with strengthened Boundary:
  - New PRIMARY USE CALLOUT at top of Boundary: "FACILITATION VOCABULARY ONLY — NOT a personality measurement instrument, NOT a leadership-development framework, NOT a hiring tool"
  - New "Graduate beyond this skill when" subsection with 6-row table mapping task → better-evidenced alternative (Big Five NEO-PI-R / Hogan PI / Heifetz adaptive leadership / Klein Sources of Power / Hofstede cultural dimensions / Tuckman + Lencioni)

## v0.7+ candidates (deferred)

### High ROI — already scoped

1. **6 items from PR #271 audit** (carried from v0.5): one-way-modifier halt rule in loop-classification-protocol; cld-archetypes Step-0 magnitude rule for "Both at once"; Branch L disambiguation vicious-R-as-brake vs standalone runaway; strategy STOP rule for low scenario uncertainty; HOLD lever named pattern; plugin self-analysis case (Case 11 + Case A4)
2. **CI check: plugin.json description ↔ actual skill folder contents** — catches the stale-description drift class (v0.4 + v0.5 + v0.6 all had stale-desc moments that CI's verbatim plugin↔marketplace match couldn't catch)
3. **Plugin-level README full rewrite to v0.6 state** (3 languages × 2 levels = 6 files) — v0.4 PR #271 missed README sync; v0.5 + v0.6 patched sk13 references but the broader skill tables still list v0.1.x skill names (`limits-to-growth-take-the-brakes-off` / `variance-target-action-template` / `stakeholder-and-team-thinking` — all merged/split in v0.4)
4. **sk14 graduate-paths formalization** — v0.6 added textual "Graduate beyond" subsection; v0.7 could add an actual measurement-instrument router pointing at external skills

### Companion skills

- **TRIZ skill** — independent skill for Altshuller's systematic
  innovation principles (40 inventive principles + contradiction
  matrix). v0.6 absorption preserves Martian-test logic inline; TRIZ
  remains a separate prior-art alternative worth its own skill if
  engineering-domain use-cases surface
- **Edmondson teaming-safety hand-off** — when
  `team-mental-model` detects psych-safety regime,
  hand off to a separate skill (sk10 author's blind-spot already
  flags this need)
- **Stock-flow simulation companion script** — Python or D3-based
  numerical simulator for `simulation-modeling` skill (cases.md
  references several historical simulations that could be reproduced)

### Domain expansion

- Senge archetypes (Fixes That Fail, Shifting the Burden, Tragedy
  of the Commons, etc.) as a separate sub-toolkit
- Sterman methods (Business Dynamics 2000) — formal stock-flow
  diagrams, simulation pipelines, group model-building protocols
- Meadows leverage points (1999 essay) — 12-level hierarchy of
  intervention points

### Operational

- Cross-skill router refinement based on actual usage telemetry
  from v0.1.0
- Per-skill `checklists/` extraction for common workshop runs
- Stock-flow Python companion for `simulation-modeling` (currently
  text-only — no executable simulator bundled)

## Known trade-offs (v0.1.0)

- **Cache vs plugin SoT divergence**: Plugin is canonical; re-distill
  flows to v0.x bumps with manual merge. See spec D1 decision and
  R7 risk acceptance.
- **V1-weak skills retained**: Per D2 user override, both `innovaction-
  martian-test` and `manager-personality-quadrant` ship despite weak
  V1 evidence. Each carries explicit prior-art disclosure in its
  Boundary section. Can be re-evaluated each minor release.
- **Single-file simulation**: `simulation-modeling` is text-only.
  Stock-flow numerical simulation requires manual translation to
  Vensim / iThink / spreadsheet / Python. Companion script deferred.
- **Description JA/zh-TW hints uneven**: Some skill descriptions
  include `システム思考 / 系統思考` hints, others don't. Aim for
  uniform coverage in v0.2.

## Source

Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey Publishing, 2002).

Distilled 2026-05-11 via `tsundoku:book-distill` RIA-TV++ pipeline; plugin
built 2026-05-12 via Profile B merge.
