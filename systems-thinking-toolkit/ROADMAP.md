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

## v0.5+ candidates (deferred)

## v0.2+ historical candidate list (resolved across v0.2-v0.4)

### sk13 / sk14 V1-weak future

Both `innovaction-martian-test` and `manager-personality-quadrant` are
V1-weak per Stage 1.5. Three options for v0.2:

- **Option 1: absorb sk13 into `strategy-lever-and-cascade`** as a
  "facilitation extras" subsection. sk08 already lists sk13 as
  composes-with; the only reason sk13 stands alone in v0.1.0 is the
  user override to retain Stage 1.5 V1-weak candidates as discrete
  skills. Pro: solves V1-weak by demotion. Con: bloats `strategy-lever-
  and-cascade` past the 6K-token soft cap.
- **Option 2: replace sk13 with a dedicated TRIZ skill**
  (Altshuller 1946) — TRIZ has empirically-grounded 40 inventive
  principles + contradiction matrix tooling that subsume the
  Martian-test perturbation logic. Same for sk14: replace with a
  dedicated DiSC / Hogan / Situational Leadership skill (or just
  reference an external authority and remove sk14 entirely).
- **Option 3: keep both standalone with stronger Boundary disclaimers**
  + cross-link from auxiliary skills' triggers to the v0.2 prior-art
  replacement skills (when those exist). This is the lowest-risk
  option but the least value-add.

Defer decision until v0.1.0 use-feedback accumulates.

### Companion skills

- **TRIZ skill** — independent skill for Altshuller's systematic
  innovation principles (40 inventive principles + contradiction
  matrix), replacing or complementing sk13
- **Edmondson teaming-safety hand-off** — when
  `stakeholder-and-team-thinking` detects psych-safety regime,
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
