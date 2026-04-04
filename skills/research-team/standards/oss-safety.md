# OSS Safety & Licensing Standards (Shared Standard)

This file is the single source of truth for open-source dependency evaluation rules.
Both worker (when evaluating) and evaluator (when reviewing) reference this file.

## Acceptable Licenses

### Permissive (always acceptable)
- MIT, ISC, BSD-2-Clause, BSD-3-Clause, Apache-2.0, Unlicense, CC0-1.0, 0BSD

### Weak copyleft (acceptable with conditions)
- LGPL-2.1, LGPL-3.0, MPL-2.0
- Condition: dynamic linking or module boundary isolation only; no static linking into proprietary code

### Strong copyleft (requires explicit approval)
- GPL-2.0, GPL-3.0, AGPL-3.0
- These require the entire derivative work to be distributed under the same license
- AGPL-3.0: triggered by network use (SaaS) — flag immediately for any server-side deployment

### Not acceptable (reject)
- SSPL, BSL (Business Source License), Commons Clause, or any "source available" non-OSI license
- No license specified (treat as "all rights reserved")

## Production Readiness Thresholds

A dependency is "production ready" when ALL of the following are true:
- Has a stable release (≥1.0.0 or equivalent)
- Last commit within 12 months
- At least 1 active maintainer responding to issues
- CI pipeline visible and passing
- No unpatched critical/high CVEs

A dependency is "experimental" if any of the above are false.
Experimental dependencies may only be used in non-critical paths with explicit user approval.

## Supply Chain Safety

- Verify package name matches official repository (check for typosquatting)
- Prefer packages published by verified organizations on registries
- Check for known compromised versions (npm advisories, PyPI malware reports)
- Pin exact versions in production; use lockfiles

## Version Policy

- Prefer latest stable release within the current major version
- Flag dependencies more than 2 major versions behind
- Check CHANGELOG for breaking changes before any upgrade
