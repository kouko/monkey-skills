# Brief — deep-deep-research levers ① framework completeness-audit + ② meta-mode synthesis-stance routing

- **Date**: 2026-06-13
- **Skill under work**: `research-toolkit/skills/deep-deep-research/`
- **Branch**: `feat/deep-deep-research-vs-angle-selector` (continue same branch, stack on VS)
- **Design SSOT**: vault eval note §三-B / §三-C + framework library (both cross-model-validated)

## Problem

(Axis 1 — JTBD) The deep-deep-research pipeline reliably finds *non-obvious* angles
(VS lever, shipped) but two systematic gaps survive, both proven across 3 models:

1. **Coverage gap** — free-form/VS angle generation systematically *under-weights*
   structural / governance / legal-compliance dimensions. On the cross-model
   investment A/B, baseline angles covered 11/24 gold risk-dimensions; a
   framework **completeness-audit** pass lifted that to 20/24 (lift +9/+12/+18
   across opus/sonnet/haiku), recovering 5 of 7 blind-spots all three free-form
   arms missed (balance-sheet, FX, antitrust, governance, IP).
   → *"When I've generated my angle set, I want a cheap checklist pass that
   catches the structural dimensions I systematically forget, so my research
   isn't blind to governance/legal/financial-structure risk."*

2. **False-consensus gap** — the current `synthesis_prompt` instructs "write 3-5
   sentences **answering** the question + give consistent findings high
   confidence." On genuinely *contested* questions this manufactures a false
   verdict (cross-model test: mode-blind synthesis silently promoted a no-effect
   finding to "best identification" and demoted dissent on an evenly-split
   minimum-wage question). → *"When the evidence is genuinely split, I want the
   synthesis to map the debate honestly and calibrate confidence DOWN, not paper
   over it with a manufactured consensus."*

## Users

(Axis 2) The agent running deep-deep-research (any host: Claude Code / Codex /
Cursor) on a real research question, **opting in** to higher-rigor coverage and
honest-uncertainty synthesis. Job story: *When I run a high-stakes research
question (investment / policy / contested science) where missing a structural
dimension or over-claiming consensus is costly, I want to switch on a framework
audit and evidence-grounded synthesis stance, so the report is complete and
epistemically calibrated.* Both levers are **off by default** — the faithful
reproduction of the CC built-in stays the standard path.

## Smallest End State

(Axis 3) Two opt-in, text-only (zero extra fetch), additive passes — each a new
non-synced module + a bundled reference + an opt-in SKILL.md subsection — wired
into the existing pipeline at exactly one seam each, leaving every default path
byte-identical:

- **① Framework-audit** — new opt-in subsection **between Stage 1 (Scope) and
  Stage 2 (Search)**. Runs after *either* default scope or VS scope (both emit
  the same `{label, query, ...}` angle shape). Flow: classify question-type →
  routing-table picks 2–3 audit frameworks → walk each framework's cells against
  the existing angle set → propose gap-fill angles for uncovered cells →
  dedup + budget-cap to the top gaps within remaining `MAX_FETCH` → hand the
  augmented angle set (same shape) into unchanged Stage 2.
- **② Meta-mode** — new opt-in branch **inside Stage 6 (Synthesize)**, synthesis-
  stage only (upfront pre-classify deferred). Flow: classify epistemic mode
  **from the evidence** (confirmed/killed claim spread + verdict confidence, NOT
  question text) → emit a synthesis-**stance directive block** → prepend it to
  the base synthesis prompt (the synced `prompts.py synthesis` stays untouched).
  Stance: settled → give consensus clearly; complex/contested → map positions,
  calibrate confidence down, surface debate; chaotic → flag volatility.

Minimum modules: `framework_audit.py`, `mode_route.py`, two bundled reference
files, two SKILL.md opt-in subsections, full TDD test files for each module.

## Current State Evidence

(Grounded recon — `file:line` in the worktree)

- **Forward** (where new behavior attaches):
  - `skills/deep-deep-research/SKILL.md:60-150` — Stage 1 Scope, incl. the
    `### Opt-in: Verbalized Sampling (VS) scope mode` subsection (the exact
    pattern + insertion idiom lever ① mirrors). Lever ① subsection inserts at
    `SKILL.md:151` (after VS opt-in, before `## Stage 2`).
  - `SKILL.md:296-342` — Stage 6 Synthesize. Lever ② opt-in branch attaches
    here, around the `prompts.py synthesis` call at `SKILL.md:310-318`.
- **Reverse** (SSOT ownership — read the sync script, not folder hierarchy):
  - `research-toolkit/scripts/sync-primitives.sh:40-46` — the **synced SSOT set
    is exactly** `schemas.py / rank.py / prompts.py / dedup.py`. deep-deep-research
    is SSOT; fact-check/cite-check/deep-read carry byte-identical copies; CI
    `.github/workflows/check-script-sync.yml` MD5-gates drift. → **Do NOT edit
    those four.** New modules are non-synced and safe.
  - `synthesis.py / scope_vs.py / vs_select.py / metric_novelty.py` are **not**
    in the synced set → non-synced (but no need to touch them).
- **Data** (shapes new code must conform to):
  - Angle shape `{label, query, rationale?}` — `SKILL.md:106-138` (VS emits it;
    default scope emits `{label, query, ...}` at `SKILL.md:78-80`). Lever ①
    gap-angles MUST match this so Stage 2 is untouched.
  - Budget `MAX_FETCH = 15`, shared `seen`/`fetch_slots` threaded through
    `dedup.py` — `SKILL.md:176-196`. Lever ① gap-cap reads remaining budget.
  - Synthesis inputs `{confirmed_block, killed_block, confirmed_count}` +
    verdict lists — `SKILL.md:298-318`. Lever ② classifies from these.
- **Error / Boundary**:
  - Degradation contract `SKILL.md:344-364` — pipeline never crashes, always
    returns a partial report (3 empty-stage cases). New opt-in passes must not
    break this: if audit yields no gaps, proceed with the original angles; if
    mode-classify fails, fall back to the unmodified base synthesis prompt.
  - Module-naming boundary: **never name a module after a stdlib module**
    (`select.py` once shadowed stdlib `select` → whole-suite crash;
    `vs_select.py` is the fix). `framework_audit.py` / `mode_route.py` are clear.
  - `pytest.ini` sets `pythonpath=.`; run all `python scripts/…` and `pytest`
    from the skill's `scripts/` dir.

## Decision

Build **two opt-in, additive, text-only levers** as **new non-synced modules**
plus **bundled reference files** plus **opt-in SKILL.md subsections**, via the
code-toolkit flow (this brief → writing-plans → SDD, TDD iron law), stacked on
the existing VS branch.

- **Lever ① `framework_audit.py`** — carries its own prompt text + schema (VS
  pattern: a module may emit prompts without going through synced `prompts.py`):
  a `classify`/`audit` prompt pair, a gap-angle schema, and a stdin→stdout
  selector that dedups proposed gap-angles against the existing set and caps to
  the remaining `MAX_FETCH` budget (may *import* synced `dedup.py` read-only for
  URL/label normalization — import, never edit). Consumes a bundled
  `references/framework-audit-library.md` (distilled from the vault library:
  routing table + framework cells + cross-framework dedup notes + the 12
  collective blind-spots).
- **Lever ② `mode_route.py`** — carries the **load-bearing 4-mode taxonomy
  prompt verbatim** (context-dependent = complex / loud-opinion ≠ contested), a
  mode-verdict schema whose **only robust field is `settled` vs `unsettled`**
  (the clear/complicated/complex/chaotic label rides as a low-confidence soft
  signal — no hard switch on complicated↔complex), and a stdin→stdout step that
  emits the synthesis-stance directive block to prepend to the base synthesis
  prompt. Classifies **from evidence**, **fail-safe to complex** when unsure.

We will **NOT** edit any of the four synced primitives, will **NOT** alter any
default path, will **NOT** touch the upstream-CC `deep-research` provenance prose.

## Alternatives Considered

(Axis 4 — research-grounded via the **cross-model eval arc**, not imagined;
stronger than WebSearch for this decision because it is the user's own 3-model
empirical A/B. Framework provenance is itself sourced in the library — Heuer &
Pherson SATs 2011, Snowden Cynefin HBR 2007, Meadows leverage points, Porter,
PESTEL etc.)

1. **Framework as the PRIMARY angle generator** (inject framework, generate one
   angle per cell) — **REJECTED**. Cross-model: framework-as-generator@5 lost
   (8/24 vs free-form 11/24) and was model-dependent (haiku reversed it).
   Cutting to one-angle-per-cell kills the keyword-dense breadth of free-form.
   → Framework is an **auditor**, not a generator; free-form/VS stays the generator.
2. **Meta-framework as the INITIAL problem decomposer** / stacking 5 meta-frameworks
   (AQAL+Stacey+Cynefin+Wardley+Dilts) — **REJECTED**. Meta-level analysis
   paralysis; impedance mismatch with research-question decomposition; violates
   Cynefin's own warning. → Meta is a thin synthesis-stance router only.
3. **Hard mode-switch on the complicated↔complex line** — **REJECTED**. Cross-model
   noise (3/6 agreement; even ground truth is arguable). → Only the
   settled-vs-unsettled binary is robust; sub-label stays low-confidence.
4. **Classify epistemic mode from question text alone** — **DOWNGRADED to a
   deferred upfront pre-classify**. "X vs Y" framing biases toward over-calling
   complex; evidence-grounded classify at synthesis is the safe primary.
   (Dilts Logical Levels → use Iceberg model instead; Stacey Matrix → skip,
   repudiated by its own author; AQAL → kernel only, no jargon.)

## What Becomes Obsolete

(Axis 5) Nothing is removed — both levers are purely additive opt-ins layered on
the faithful-copy base, by design (the base path must stay byte-identical to the
CC built-in reproduction). This is the rare legitimate additive case: the
"obsolete" target is the *implicit* false-consensus behavior of the current
synthesis on contested questions, which lever ② overrides **only when opted in**
(the default synthesis prose stays, because the faithful-copy contract forbids
editing the synced `prompts.py`).

## Out of Scope

- **Upfront question-only pre-classify** (Block 6 P3) — deferred; synthesis-stage
  stance routing only this build.
- **Multilingual angle-layer / source-layer EN+JP** (v2.1, regime-gated) — not this build.
- **Editing any synced primitive** (`schemas/prompts/dedup/rank.py`) — forbidden.
- **Altering default scope path or VS mode** — untouched.
- **Bundling the full 133-framework library verbatim** — distill to the routing
  table + the cells of the routable framework set + dedup notes + 12 blind-spots
  (keep the reference file token-bounded; see Open Questions).
- **Rigorous shared-pool re-eval / N≥6** (vault §七 todo) — separate eval RUN, not this code build.

## Open Questions

1. **Reference-file scope** — the vault framework library is ~1,400 lines / ~63k
   tokens. Bundle the **routing table + collective blind-spots in full** (compact)
   plus **a curated subset of framework cells** (the routable first-line +
   reinforcement frameworks), not all 133 verbatim. Exact curation set is a
   writing-plans decision; flag as the main sizing risk.
2. **`framework_audit.py` deterministic surface** — confirm the split: agent does
   LLM classification + cell-walk (prompts emitted by the module); module does
   the deterministic gap dedup + budget cap. (Mirrors VS: `scope_vs.py` emits
   prompt/schema; `vs_select.py` does deterministic selection.)
3. **mode_route stance-block wiring** — prepend vs wrap. Prepend a stance
   directive string ahead of the base synthesis prompt keeps `prompts.py`
   byte-identical; confirm the host can accept a composed prompt at `SKILL.md:310`.
