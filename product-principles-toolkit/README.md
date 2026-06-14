# product-principles-toolkit

The **cross-cutting constitution** layer that sits *above* the whole spec→code pipeline: turn a sparse product idea into a `PRINCIPLES.md` — a product constitution whose North Star and non-negotiable principles **govern every downstream station** (interface-design, spec, code).

```
                    PRINCIPLES.md  (this toolkit — the constitution)
                          │ governs ↓
  interface-design   →   spec   →   code
   (optional UI)        (GENERATE)   (VERIFY)
```

The constitution is **product-level** (one per product) and applies to **any** product — including pure-headless / library / CLI work that has no UI at all.

Agent-portable and key-free: the skill drives the host agent's own LLM — no external runtime, no API key, no install beyond the plugin.

## What it does

One skill:

- **`product-principles`** — takes a sparse product idea and emits a single **`PRINCIPLES.md`** with two sections:
  - **`## North Star`** — the product's original goal plus a concrete definition of "success".
  - **`## Principles`** — **3–7 non-negotiable principles, each carrying a falsifiable check.** Platitudes are rejected at generation: ❌ "be delightful" → ✅ "primary task completes in ≤3 steps", "never block the primary flow with a modal", "offline-readable". The falsifiable check is what makes a principle usable as a downstream gate.

## What it's for

`PRINCIPLES.md` is the **supreme input** that governs the rest of the pipeline. Downstream stations read it as always-on steering context, so feature design, interface (UI/UX) design, spec, and code stay anchored to the product's original intent instead of drifting from it.

The gap it closes is **cross-cutting**: today product principles live in your head or in scattered prose, and there is nothing concrete to **check implementations against**. Because the constitution is product-level — not design-craft — it applies to **headless / CLI / TUI / GUI** alike. Folding it into a visual-design step would mis-scope it and make it dead weight on non-UI products; hence its own plugin.

This is **product design principles + target user**, not a full market/business-model/strategy document. North Star is a lightweight decision filter, not a business plan.

## Output format

A single product-level file written into the **consumer project** under the established `docs/<toolkit>/` convention:

```
docs/product-principles-toolkit/PRINCIPLES.md
  ## North Star      # original goal + concrete definition of success
  ## Principles       # 3–7 non-negotiable principles, each with a falsifiable check
```

`PRINCIPLES.md` is **key-free, in-repo, git-diffable**, and **product-level** (one per product, not per-feature). A `validate_*` script (mirroring `spec-toolkit/scripts/validate_spec_output.py`) is the executable format contract: it checks both sections exist and that every principle carries a check (exit 0 = conformant).

## Honesty rails

A principle is only useful if it is **falsifiable / checkable** — otherwise it is dead text. The validator enforces a per-principle check at generation time, so a `PRINCIPLES.md` that *looks* authoritative but states unfalsifiable platitudes does not pass. Trust is earned by checkability, not by a document that looks decisive.

## Scope (v0.1)

In: the `product-principles` skill + the format validator. The constitution MAY ride the downstream seam as always-on steering context (it is just one more file path).

Out (deferred): a writer≠judge **conformance gate** ("does this artifact violate a principle?") — when built, it is added as a **lens** to the existing critics (`spec-toolkit:completeness-critic`, `code-toolkit:requesting-code-review`), not a new gate engine; a second `principles-conformance` skill; business/market/strategy framing (that stays `planning-team`'s `PRODUCT-SPEC.md` turf); an automated hand-off seam to interface-design / spec. See `docs/product-principles-toolkit/specs/2026-06-14-product-principles-toolkit-mvp.md` (brief).

## License

MIT.
