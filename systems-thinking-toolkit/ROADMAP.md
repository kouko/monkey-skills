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

## v0.7.0 (body refinements + CI desc-drift check + READMEs v0.6 sync, 2026-05-13)

- 5 body fixes from PR #271 audit:
  - loop-classification-protocol halt rule for "candidate loop = one-way modifier chain"
  - cld-archetypes Step-0 magnitude-comparison rule (3× threshold) for "Both at once" case
  - cld-archetypes Branch L disambiguation (vicious-R-as-brake vs standalone runaway)
  - strategy-lever-and-cascade STOP-after-Step-4 rule for low scenario uncertainty
  - strategy-lever-and-cascade HOLD-lever named pattern (pedal-harder anti-pattern)
- NEW `scripts/check-plugin-description-skill-coherence.py` + CI workflow — closes the stale-description drift class (v0.4 + v0.5 + v0.6 had drift moments)
- 6 plugin/router READMEs (EN/JA/zh-TW × plugin-level + router-level) rewritten to v0.6 7-skill state (deferred since v0.4 PR #271)

## v0.8.0 (CLD falsifiability protocol + 3 new cases, 2026-05-13)

- NEW `cld-craft/references/cld-falsifiability-protocol.md` — 6 falsification tests (sign / loop closure / magnitude / behavioral signature / fuzzy proxy / regime split); MANDATORY for regulatory / compliance / financial-decision-grade / litigation / safety-critical; **plugin's FIRST methodological improvement OVER Sherwood Rule 10 social-validation** (super-Sherwood affordance)
- Case 11 (cld-craft) + Case A4 (cld-archetypes Branch L) — Plugin self-analysis (modern agent-orchestration domain filling Sherwood's pre-2010 blind spot)
- Case 12 (cld-craft) — Reductionism Failure meta-case (Sherwood Ch 1-3 pattern operationalized)

## v0.9.0 (platform-economy R-loop bundle + sk14 Graduate Routing decision tree, 2026-05-13)

- 4 new cases filling Sherwood's pre-2010 platform-economy blind spot (Parker/Van Alstyne 2005, Eisenmann 2006):
  - Case 13 — Network Effects R-loop (Metcalfe pattern)
  - Case 14 — Two-Sided Market Chicken-and-Egg (Uber / Airbnb / OpenTable)
  - Case 15 — Winner-Take-Most via Algorithm Concentration (TikTok / Google triple-R-loop)
  - Case A5 — Platform Saturation Limits-to-Growth (Facebook 2017+ deceleration)
- sk14 Graduate Routing 5-question decision tree (`## Graduate Routing ★` section before Boundary):
  - Q1 personnel decisions → Hogan PI / Big Five NEO-PI-R / structured-interview
  - Q2 leadership development → Heifetz / Edmondson / Kegan / ICF/EMCC
  - Q3 decision-style → Klein 1998 / Kahneman 2011 / Thaler/Sunstein/Camerer
  - Q4 cultural reception → Hofstede / GLOBE / Erin Meyer
  - Q5 team-stage dynamics → Tuckman / Lencioni / plugin-internal team-mental-model + cld-overlay

## v0.10.0 (executable Python stock-flow simulator companion, 2026-05-13)

Closes Sherwood Ch 12-13 ithink/Stella quantitative-simulation gap (largest single scope reduction since v0.1):

- NEW `simulation-modeling/scripts/cld_simulator.py` (412 lines, PEP-723 single-file, stdlib only) — Euler integration, JSON CLD spec input, CSV + ASCII-chart output
- NEW `simulation-modeling/examples/` — 4 example specs (exponential / goal-seeking / logistic / Lotka-Volterra)
- NEW `simulation-modeling/tests/test_cld_simulator.py` (321 lines pytest) — 30 tests covering analytical tolerance (4) + eval safety (5) + error handling (5) + CLI + format (5) + Euler discipline (2) + multi-flow + circular-ref (2) + conservation (1) + v0.10 hardening (6)
- AST-walk eval whitelist (6 guard rails) safe against `__import__()` / dunder / attribute / method-chain / etc.
- Honest caveats: Euler not RK4; single-file not PySD; pedagogical not research-grade

## Resolved / merged v0.7+ candidates (historical record)

The following v0.7+ candidate items shipped through PRs #280/#282/#283/#284:

| v0.7+ candidate | Shipped in | PR |
|---|---|---|
| 6 PR #271 body-fix items (halt rule / magnitude rule / Branch L disambiguation / STOP rule / HOLD pattern / plugin self-analysis case) | v0.7 + v0.8 | #280 + #282 |
| CI check for plugin desc ↔ skill folder coherence | v0.7 | #280 |
| Plugin-level README rewrite to v0.6+ state | v0.7 | #280 |
| sk14 graduate-paths formalization (Graduate Routing decision tree) | v0.9 | #283 |
| Stock-flow simulation companion (Python, executable) | v0.10 | #284 |

## v0.11+ candidates (still deferred)

### Companion skills (independent skill folders; reach for when domain demand surfaces)

- **TRIZ skill** — Altshuller's systematic-innovation framework (40 inventive principles + contradiction matrix). v0.6 absorbed Martian-test inline already covers part of this; TRIZ separate skill worth its own folder if engineering-domain use-cases surface.
- **Edmondson teaming-safety hand-off** — when `team-mental-model` detects psych-safety regime, hand off to a separate skill. `team-mental-model` author's-blind-spot section already flags the need.

### Domain expansion (separate sub-toolkits)

- **Senge archetypes sub-toolkit** — Fixes That Fail / Shifting the Burden / Tragedy of the Commons / Drifting Goals / etc. as 8-10 named archetypes beyond Sherwood's Branch L + Branch V.
- **Sterman methods** (Business Dynamics 2000) — formal stock-flow diagrams, simulation pipelines, group model-building protocols.
- **Meadows leverage points** (1999 essay) — 12-level hierarchy of intervention points (paradigm > goals > rules > information > feedback > etc.).

### Simulator extensions (v0.10 follow-ups)

- **RK4 integration mode** — optional 4th-order Runge-Kutta replacing Euler for users needing tighter long-run fidelity (v0.10 already documents Euler drift caveat).
- **matplotlib image-chart output** — optional `--output png` replacing ASCII chart for non-terminal contexts; would lift the stdlib-only constraint (acceptable trade-off for v0.11).
- **Stiff-equation comparison framework** — test harness for verifying simulator behavior on stiff systems with known fixed-points.
- **PySD / BPTK-Py integration mode** — optional "import existing Vensim model" path for users coming from research-grade tooling.

### Operational (telemetry-dep / low-priority)

- Cross-skill router refinement based on actual usage telemetry (post-v0.x adoption period).
- Per-skill `checklists/` extraction for common workshop runs (post-usage-pattern-stability).

### 2002-vintage inherited gaps (book itself has them; plugin only partial)

Per `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-vs-original-book.md`:

- **2008-style cross-firm systemic contagion** — book pre-dates; plugin has nothing on it.
- **Behavioral economics biases internalized** — Klein / Kahneman / Thaler currently only as **external** Graduate-beyond pointers in sk14; could be internalized as `behavioral-bias-overlay` skill.
- **Modern facilitation tools** (Miro / FigJam / async-distributed workshop adaptation) — team-mental-model Boundary flags this as known blind spot; not implemented.
- **ABM (Agent-Based Modeling) comparison** — cld-craft Boundary mentions but doesn't deep-compare.
- **Pearl-style causal-inference DAG comparison** — cld-craft Boundary mentions but doesn't deep-compare.

## Resolved trade-offs (historical record)

These items from earlier "Known trade-offs (v0.1.0)" sections have been resolved:

- ✅ **Single-file simulation** → resolved in v0.10 (executable Python companion shipped; `simulation-modeling` no longer text-only).
- ✅ **V1-weak skills retained** → resolved in v0.6 (sk13 absorbed into strategy; sk14 strengthened to "facilitation vocabulary only") + v0.9 (Graduate Routing decision tree).
- ✅ **Description JA/zh-TW hints uneven** → resolved in v0.2 (A8 normalization) + v0.5 (symptom-phrase coverage +20 zh-TW + 12 JA).

## Still-active trade-offs

- **Cache vs plugin SoT divergence**: plugin is canonical; re-distill flows to v0.x bumps with manual merge. See spec D1 decision and R7 risk acceptance.
- **vs-original-book ~92% methodology coverage**: 5 inherited 2002-vintage gaps remain (see v0.11+ candidates section above). Closing these would require new V2 evidence per Stage-1.5 verification standards.

## Source

Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey Publishing, 2002).

Distilled 2026-05-11 via `tsundoku:book-distill` RIA-TV++ pipeline; plugin
built 2026-05-12 via Profile B merge.
