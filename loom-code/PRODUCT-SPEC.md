# loom-code — product spec

Superseded at 1.0.0. What loom-code is, in machine-readable form, is
`contract/manifest.yaml`: the stations, the actions, the artifact schemas
and their templates. What each station does is its own `SKILL.md`.
- Stations: `skills/{write-plan,build,review,ship,maintain}/SKILL.md`
- Contract: `contract/manifest.yaml`, `contract/README.md`,
  `contract/templates/`
- Deterministic layer: `scripts/loom_checker.py --list-rules`
- Engineering rules the implementer works under:
  `references/engineering-baseline.md`

The pre-1.0 product spec described a router, a 13-skill surface and a
per-task review layer, none of which exist. It is not migrated: read the
manifest and the five station files instead.
