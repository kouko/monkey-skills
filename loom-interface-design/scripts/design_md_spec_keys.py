"""Frozen copy of `@google/design.md`'s key sets.

The spec format is `alpha` with no compatibility promise, so this module
freezes the values in-repo rather than querying the spec live at check
time — CI must not depend on the network. Frozen-copy pattern per
`loom-code/scripts/canonical/README.md`.

`TOKEN_GROUPS` and `TYPOGRAPHY_PROPERTIES` are closed sets — the spec
defines no fallback for an unrecognized member of either. `COMPONENT_SUB_TOKENS`
is the spec's RECOGNISED set, not closed: the spec's Consumer Behavior for
Unknown Content table has a row for it — "Unknown component property |
Accept with warning | borderColor" — so an unrecognized component property
is accepted with a warning, not rejected.

Update procedure: re-run the derivation command below against a newer
spec version, diff the three sets AND re-check the Consumer Behavior for
Unknown Content row for `COMPONENT_SUB_TOKENS` (the "accept with warning"
behaviour this docstring and `design-md-schema.md` cite), and bump
`PROVENANCE` in the same commit as any value or behaviour change.

Stdlib only.
"""

PROVENANCE = (
    "Derived from @google/design.md version 0.4.0, verified 2026-08-10, "
    "via: npx @google/design.md@0.4.0 spec"
)

TOKEN_GROUPS = {
    "colors",
    "typography",
    "rounded",
    "spacing",
    "components",
}

TYPOGRAPHY_PROPERTIES = {
    "fontFamily",
    "fontSize",
    "fontWeight",
    "lineHeight",
    "letterSpacing",
    "fontFeature",
    "fontVariation",
}

COMPONENT_SUB_TOKENS = {
    "backgroundColor",
    "textColor",
    "typography",
    "rounded",
    "padding",
    "size",
    "height",
    "width",
}
