# Visual-complexity lens

Use this local lens when a GUI design system adds visual vocabulary, component
variants, themes, or exceptions. It supplements the existing `DESIGN.md`
schema; it never adds a ninth canonical section or describes interaction
behavior.

Ask:

- Which **new vocabulary** must people learn and keep coherent?
- Which **justified variants** inherit from a base token or component, and why
  is each non-inheriting fork worth its maintenance cost?
- Which **deleted or avoided exceptions** stay out of tokens or component
  rules?
- What **downstream component risk** remains for implementers when the visual
  rules meet new components or surfaces?

A smaller vocabulary or variant set is a valid simplification only when it
still delivers the intended visual outcome. Treat any lost outcome as an
explicit design trade-off rather than avoided complexity.

In `DESIGN.md`, place the assessment in the existing Overview / Brand and Do's
& Don'ts prose: name the added burden, why the surviving rules are worthwhile,
what was removed or avoided, and the downstream risk. When the work reuses
existing visual rules without a material new burden, write a **reasoned N/A**
there instead; do not omit the assessment silently.
