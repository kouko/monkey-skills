"""Frozen copy of `@google/design.md`'s closed key sets.

The spec format is `alpha` with no compatibility promise, so this module
freezes the values in-repo rather than querying the spec live at check
time — CI must not depend on the network. Frozen-copy pattern per
`loom-code/scripts/canonical/README.md`.

Update procedure: re-run the derivation command below against a newer
spec version, diff the three sets, and bump `PROVENANCE` in the same
commit as any value change.

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
