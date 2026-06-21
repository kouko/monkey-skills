# Brief — product-principles-toolkit MVP (cross-cutting product constitution)

> Date: 2026-06-14 · Stage: brainstorming → (next) writing-plans
> Pipeline position: **cross-cutting constitution** above the whole pipeline (governs interface-design + spec-toolkit + code-toolkit)
> Split from the superseded `docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md` (1 plugin → 2).

## Problem

(Axis 1 — JTBD) When kouko starts a software product/feature from an idea, he wants to fix the **product's
original goal and non-negotiable design principles up front** — e.g. "target user = professional CG artists",
"interface must stay minimal" — as the **supreme principles that govern every downstream decision**: feature
design, interface (UI/UX) design, spec, and code. Today there is no generator for this: principles live only in
his head or scattered prose, so design/spec/code drift from the original intent and there is nothing concrete to
**check implementations against**. The gap is real and **cross-cutting** — it applies to **every** product,
including pure-headless / library / CLI work that has no UI at all.

## Users

(Axis 2) kouko — solo dev, macOS, Claude Code + Codex hosts, public `monkey-skills` marketplace, **key-free /
portable** ethos. His projects span **headless / CLI / TUI / GUI** — so the principles layer must be usable
**independently of any visual-design step**. This is exactly why principles is its own plugin, not folded into
the interface-design toolkit (pulling a UI/UX plugin into a headless project would be dead weight).

## Smallest End State

(Axis 3 — **minimal core**) **One skill** (`product-principles` / working name) that takes a sparse product idea
and emits a single **`PRINCIPLES.md`** — the product constitution — with two sections:

- **`## North Star`** — the product's original goal + a concrete definition of "success".
- **`## Principles`** — **3–7 non-negotiable principles, each carrying a falsifiable check.** Platitudes are
  rejected at generation: ❌ "be delightful" → ✅ "primary task completes in ≤3 steps", "never block the primary
  flow with a modal", "offline-readable". The falsifiable check is what makes the principle usable as a
  downstream gate later.

`PRINCIPLES.md` is **key-free, in-repo, git-diffable**, **product-level (one per product)**, and is the
**supreme input** that governs interface-design, spec-expansion (functional design), and code. A `validate_*`
script (mirror `spec-toolkit/scripts/validate_spec_output.py`) checks the two sections exist and every principle
carries a check. That's the whole MVP: idea → `PRINCIPLES.md`. Ship the portable core first.

**Runtime output location:** the skill writes `PRINCIPLES.md` into the **consumer project** under the established
`docs/<toolkit>/` convention → `docs/product-principles-toolkit/PRINCIPLES.md` (product-level, single file; not
per-feature). The repo's own dev brief/plan live in `docs/product-principles-toolkit/specs|plans/` in
monkey-skills.

## Current State Evidence

- **Prior art (not invented):** the constitution / steering pattern. **Spec Kit `constitution.md`** = "immutable
  principles that govern how specifications become code … the first thing you do … every subsequent command reads
  it automatically." **Kiro steering `product.md`** (purpose/objectives) with `inclusion: always` = the mechanism
  for loading principles at every downstream stage. We adopt the pattern, not a CLI dependency.
- **Load-bearing constraint:** principles must be **falsifiable / checkable** or they are dead text (the repo's
  "executable guards, not prose platitudes" lesson). The validator enforces a per-principle check.
- **Cross-cutting role (why a separate plugin):** `PRINCIPLES.md` feeds **interface-design + spec + code**, and
  applies to headless products with no UI. Burying it inside a visual-design plugin mis-scopes it (it is
  product-level, not design-craft). Same modular-plugin posture as the B/D = D decision (toolkit-per-concern +
  cross-plugin delegation).
- **Boundary (do not cross):** this is **product design principles + target user**, NOT a full
  market/business-model/strategy document — that stays `planning-team`'s `PRODUCT-SPEC.md` (CLAUDE.md §Two-Layer
  Spec). North Star = product goal as a decision filter, lightweight.
- **Scaffold convention:** a new plugin = `.claude-plugin/plugin.json` + `skills/` + `scripts/` + `README.md` +
  a root `.claude-plugin/marketplace.json` entry. `spec-toolkit/` is the template.

### Evidence paths appendix
- `spec-toolkit/scripts/validate_spec_output.py` (validator pattern), `spec-toolkit/.claude-plugin/plugin.json` (template)
- Real consumer-project evidence for the `docs/<toolkit>/` runtime convention: a downstream consumer repo carries `docs/loom/{specs,plans}/` committed (verified locally)
- Research: Spec Kit `constitution.md` (github/spec-kit/blob/main/memory/constitution.md); Kiro steering (kiro.dev); Martin Fowler "SDD: Kiro, spec-kit, Tessl"

## Decision

Build a **new, separate `product-principles-toolkit` plugin** — the cross-cutting product constitution layer.
MVP = **one skill** (`product-principles`) that turns a sparse idea into `PRINCIPLES.md` (North Star + 3–7
falsifiable principles), **key-free**, **product-level**, governing all downstream stations. Separate plugin
(not part of interface-design-toolkit) because principles is product-level and used even on headless products.
We adopt the **constitution/steering pattern** but **not**: a downstream conformance gate yet (P2), a
multi-skill decomposition, or any CLI dependency.

## Out of Scope (MVP)

- **Downstream principles-conformance check (P2 seam).** `PRINCIPLES.md` flows downstream two ways: (A) steering
  — passed as always-on context to interface-design / spec / code (this much MAY ride MVP, it is just one more
  file path on the seam); (B) a writer≠judge **conformance gate** ("does this artifact violate a principle?").
  B is out of MVP scope and, when built, is added as a **lens to the existing critics**
  (`spec-toolkit:completeness-critic`, `code-toolkit:requesting-code-review`) — NOT a new gate engine. Re-trigger:
  a real run where drift from the stated principles bites.
- A second `principles-conformance` skill inside this plugin (defer with B above).
- Business/market/strategy framing (planning-team's `PRODUCT-SPEC.md` turf).
- Automated hand-off seam to interface-design / spec (MVP hands `PRINCIPLES.md` over by the shared
  `docs/<toolkit>/` convention; automate when manual proves painful).

## Alternatives Considered

(Axis 4 — research-grounded, EN+JP via WebSearch)
- **Constitution / steering pattern for `PRINCIPLES.md`** — *chosen.* Direct prior art (Spec Kit
  `constitution.md` auto-read by every command; Kiro steering `inclusion: always`). Con: only valuable if
  principles are falsifiable → enforced by the per-principle check rule.
- **Fold principles into the interface-design skill** — *rejected.* Principles is product-level and governs
  functional + spec + code + headless work, not just visual design; folding it mis-scopes it and makes it
  unusable on non-UI products.
- **Put principles in `planning-team`'s `PRODUCT-SPEC.md`** — *rejected for MVP.* That is heavier
  (business+design+tech) and audit-oriented; this is a lean, generate-first product-design-principles doc.

## What Becomes Obsolete

(Axis 5) Closes the "no stated product principles governing design + downstream implementation" gap. Nothing is
deleted. Purely additive → YAGNI risk acknowledged, justified by the real cross-cutting gap + kouko's explicit
multi-modality pipeline. Re-baseline if `PRINCIPLES.md` goes unused after a real product run.

## Open Questions

- **File/skill names:** `PRINCIPLES.md` vs `CONSTITUTION.md` (Spec-Kit-precedented); skill `product-principles`
  vs `product-charter`. Decide in writing-plans.
- **Falsifiability enforcement:** does the skill *require* each principle to carry a check (reject at generation)
  or just prompt for it? (Lean: require.)
- **Codex 1024-char description guardrail** applies (the new skill's description ≤1024).
- Does `PRINCIPLES.md` ride the downstream seam as steering context in MVP, or wait for the P2 conformance lens?
- **Governance:** synthetic examples only; no company/customer names in any committed file (run the
  identifiable-token grep before commit); explicit `git add <paths>`, never `-A`.
