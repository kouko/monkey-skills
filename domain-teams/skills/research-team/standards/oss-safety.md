---
title: OSS Safety and Licensing
tier: 2
---

# OSS Safety and Licensing

Single source of truth for open-source dependency evaluation — which
licenses are acceptable, how to judge production-readiness, how to
interpret supply-chain safety signals, and which measurement
frameworks (OpenSSF Scorecard, NIST SSDF, SLSA, CVSS, SPDX) research-
team relies on. Tier 2: LLMs know the framework names but routinely
muddle version numbers (CVSS v3.1 vs v4.0), miscount NIST SSDF
practice groups, and conflate SLSA levels. The body spells out each
framework's enumerated items.

## Primary Sources

- OpenSSF Scorecard Project (2020-current). https://scorecard.dev/. The OSSF's automated checks that evaluate the security posture of an open-source project across 18 checks in 3 themes; produces a 0-10 aggregate score per repository.
- National Institute of Standards and Technology (2022) *Secure Software Development Framework (SSDF) Version 1.1*. NIST Special Publication 800-218. https://csrc.nist.gov/pubs/sp/800/218/final. The US federal government's canonical software supply-chain framework, structured as 4 practice groups (PO / PS / PW / RV) with specific tasks under each.
- Supply-chain Levels for Software Artifacts Project (2024) *SLSA v1.1 Specification*. https://slsa.dev/. A four-level maturity model (L0 through L3) describing progressively stronger build-provenance and supply-chain integrity guarantees, originally seeded by Google's internal Binary Authorization for Borg practices.
- FIRST.org (2023) *Common Vulnerability Scoring System (CVSS) v4.0 Specification Document*. https://www.first.org/cvss/v4.0/. The current-generation vulnerability severity scoring standard; CVSS v4.0 (2023-11) supersedes v3.1 (2019) with an expanded 4-metric-group structure.
- SPDX Working Group (2024) *SPDX Specification v3.0*. https://spdx.dev/. The Linux Foundation's open standard for Software Bill of Materials (SBOM), license identifiers, and provenance declarations; v3.0 (2024) adds security, build, and AI profiles to the pre-v3 core license-identifier scope.

## Critical Attribution Corrections

### Stack-evaluation thresholds are internal convention, not CHAOSS / Scorecard

The numerical thresholds in `protocols/stack-evaluation.md` — notably
**>500 open issues**, **>12 months with no commit**, **<1000 weekly
downloads** — are **research-team internal operational heuristics**,
NOT values pulled from CHAOSS metrics or OpenSSF Scorecard. CHAOSS
publishes qualitative metric definitions (activity, responsiveness,
contributor strength) without prescribed numerical thresholds;
OpenSSF Scorecard produces continuous 0-10 scores rather than binary
cutoffs. The thresholds are retained as internal convention because
they match the kinds of decisions research-team makes in practice,
but they MUST be disclosed as such in any deliverable — do not cite
them as if they came from a standards body.

## Acceptable Licenses

License categories follow the SPDX identifier vocabulary (SPDX v3.0).
When listing a license, use the SPDX short identifier (e.g.,
`Apache-2.0`) rather than the long name, so automated SBOM tooling
can parse the declaration.

### Permissive (always acceptable)

- `MIT`, `ISC`, `BSD-2-Clause`, `BSD-3-Clause`, `Apache-2.0`,
  `Unlicense`, `CC0-1.0`, `0BSD`
- No copyleft obligation; compatible with proprietary use without
  source-disclosure requirements.

### Weak copyleft (acceptable with conditions)

- `LGPL-2.1`, `LGPL-3.0`, `MPL-2.0`
- **Condition**: dynamic linking or module-boundary isolation only;
  no static linking into proprietary code without triggering copyleft
  obligations for the linked portion.

### Strong copyleft (requires explicit approval)

- `GPL-2.0`, `GPL-3.0`, `AGPL-3.0`
- These require the entire derivative work to be distributed under
  the same license.
- **`AGPL-3.0`** is triggered by **network use** (SaaS) — flag
  immediately for any server-side deployment. The "network copyleft"
  clause is what distinguishes AGPL from GPL and is the single most
  common misread license in practice.

### Not acceptable (reject)

- `SSPL`, `BSL` (Business Source License), `Commons Clause`, and any
  "source available" non-OSI license. These are **not OSI-approved**
  and impose use restrictions inconsistent with open-source norms.
- **No license specified** — treat as "all rights reserved" and do
  not use.

## Production Readiness Thresholds (internal convention)

A dependency is "production ready" when ALL of the following are
true:

- Has a stable release (≥1.0.0 or equivalent).
- Last commit within 12 months.
- At least 1 active maintainer responding to issues.
- CI pipeline visible and passing.
- No unpatched critical / high CVEs (per CVSS v4.0 — see below).

A dependency is "experimental" if any of the above are false.
Experimental dependencies may only be used in non-critical paths with
explicit user approval.

These thresholds are **internal convention** — see §Critical
Attribution Corrections above.

## Supply Chain Safety Signals

- Verify package name matches official repository (check for
  typosquatting — a package named `reqeusts` is not `requests`).
- Prefer packages published by verified organizations on registries
  (npm verified orgs, PyPI trusted publishers).
- Check for known compromised versions (npm advisories, PyPI malware
  reports, GitHub Security Advisories).
- Pin exact versions in production; use lockfiles.

## Version Policy

- Prefer latest stable release within the current major version.
- Flag dependencies more than 2 major versions behind.
- Check CHANGELOG for breaking changes before any upgrade.

## OpenSSF Scorecard — 18 Checks in 3 Themes

OpenSSF Scorecard evaluates a project against 18 automated checks,
organized into three themes. Each check produces a 0-10 score; the
aggregate is the project's Scorecard score.

### Theme 1: Source Code Risk

- **Binary-Artifacts** — are pre-built binaries checked into the
  repo? (risk: untrusted binaries may contain malware).
- **Branch-Protection** — are merges to main protected by required
  reviews and status checks?
- **CI-Tests** — do CI pipelines run on pull requests?
- **Code-Review** — are contributions reviewed before merge?
- **Contributors** — does the project have contributors from >1
  organization? (bus-factor proxy).
- **Dangerous-Workflow** — do CI workflows contain injection-prone
  patterns (untrusted `${{ }}` interpolation in GitHub Actions)?
- **License** — is a license file present?
- **Signed-Releases** — are release artifacts cryptographically
  signed?

### Theme 2: Build Process Risk

- **Dependency-Update-Tool** — is Dependabot, Renovate, or
  equivalent configured?
- **Fuzzing** — is the project integrated with OSS-Fuzz or an
  equivalent fuzzing system?
- **Packaging** — is the project published to a package registry?
- **Pinned-Dependencies** — are dependencies pinned to exact
  versions (hashes, not tags)?
- **SAST** — does CI run static application security testing
  (CodeQL, Semgrep, etc.)?
- **Token-Permissions** — are CI tokens scoped to minimum necessary
  permissions?
- **Webhooks** — are webhook secrets configured?

### Theme 3: Holistic Project Risk

- **Maintained** — has the project had commits in the last 90 days?
- **SBOM** — does the project publish a Software Bill of Materials?
- **Security-Policy** — is `SECURITY.md` present with a disclosure
  process?
- **Vulnerabilities** — are there unpatched known CVEs?

A project with a Scorecard of ≥7.0 is generally healthy; ≥8.5 is
strong. Aggregate scores below 5.0 correlate with significant risk
in at least one theme.

## NIST SSDF v1.1 — 4 Practice Groups

NIST SP 800-218 organizes secure software development into four
practice groups, each with 3-5 specific practices and a list of
example tasks.

| Group | Name | Focus |
|---|---|---|
| **PO** | **Prepare the Organization** | Organizational readiness: people, processes, tools, supply chain |
| **PS** | **Protect the Software** | Protect code and build infrastructure from tampering and unauthorized access |
| **PW** | **Produce Well-Secured Software** | Design, implement, and verify software with security built in |
| **RV** | **Respond to Vulnerabilities** | Identify, assess, respond to, and communicate about vulnerabilities |

Each group has numbered practices (e.g., PO.1 "Define Security
Requirements for Software Development", PW.7 "Review and/or Analyze
Human-Readable Code") that are the canonical checklist items for
compliance discussions.

## SLSA v1.1 — 4 Levels (L0 through L3)

SLSA is a maturity model for build provenance — the guarantee that a
released artifact actually came from the source code it claims to.

| Level | Requirement |
|---|---|
| **L0** | No provenance guarantees. No attestations, no reproducibility claims. |
| **L1** | **Documented build process** — build process is documented, produces provenance that describes how the artifact was built. Provenance may be unsigned. |
| **L2** | **Hosted, signed provenance** — build runs on a hosted build service (not a developer's laptop). Provenance is signed by the build service, so verifiers can confirm it was produced by an expected builder. |
| **L3** | **Hardened builds** — the build platform is hardened against tampering: build runs are isolated, secret material is controlled, and the provenance is strong enough to resist a compromised build worker. |

(The pre-v1.0 SLSA draft had a Level 4 that was removed in v1.0 as
out-of-scope; v1.1 retains the 4-level L0-L3 structure.)

Research-team uses SLSA levels as shorthand for "how much do I trust
that this artifact is what it claims to be?" — L0 / L1 is
developer-trust; L2 is hosted-builder-trust; L3 is
hardened-builder-trust.

## CVSS v4.0 — 4 Metric Groups

CVSS v4.0 (2023-11) supersedes v3.1 (2019). The key structural
change: v3.1 had **3 metric groups** (Base / Temporal / Environmental);
v4.0 has **4 metric groups** with a re-scoped middle group:

| Group | Purpose |
|---|---|
| **Base** | Intrinsic qualities of the vulnerability that are constant across environments: attack vector, attack complexity, privileges required, user interaction, scope, impact. |
| **Threat** | Dynamic threat landscape: exploit maturity, real-world exploitation activity. (v3.1 called this "Temporal".) |
| **Environmental** | Environment-specific modifiers: asset importance, local mitigations, user population. |
| **Supplemental** | (new in v4.0) Qualitative descriptors that do not affect the numerical score but provide context: automatable, recovery, provider urgency, etc. |

The numerical score is **0.0-10.0** and maps to the qualitative
severity rating: **None (0.0)**, **Low (0.1-3.9)**, **Medium
(4.0-6.9)**, **High (7.0-8.9)**, **Critical (9.0-10.0)**. "Critical
or high CVE" in the production-readiness threshold above refers to
the **Base** score at **7.0 or above**.

## SPDX v3.0 — License Identifiers and SBOM

SPDX v3.0 (2024) is the Linux Foundation open standard for SBOMs.
Two load-bearing uses for research-team:

- **SPDX License Identifiers** — a controlled vocabulary of short
  strings (e.g., `Apache-2.0`, `MIT`, `AGPL-3.0-or-later`) that
  unambiguously identify an open-source license. Use these whenever
  listing a license, so tooling can parse.
- **SBOM format** — SPDX v3.0 provides a machine-readable format for
  declaring the components of a software artifact, their licenses,
  their provenance, and their relationships. SPDX v3.0 adds
  security, build, and AI profiles to the pre-v3 core license-
  identifier scope. When a research-team deliverable recommends
  generating an SBOM, the SPDX v3.0 JSON-LD format is the default
  (CycloneDX is a competing standard; both are acceptable).

## Anti-Patterns

- Citing stack-evaluation thresholds (>500 issues, >12 months, <1000
  weekly downloads) as if they were CHAOSS or OpenSSF Scorecard
  values. They are research-team internal convention.
- Using CVSS v3.1 structure (3 metric groups) when reporting current
  vulnerabilities. v4.0 has 4 groups including the new Supplemental
  group.
- Confusing SLSA L3 with the removed SLSA L4 that appeared in
  pre-v1.0 drafts.
- Treating AGPL as equivalent to GPL for SaaS deployment — AGPL's
  network-use trigger is the load-bearing distinction.
- Citing a license by long name (e.g., "Apache License, Version 2.0")
  in automation contexts rather than SPDX identifier (`Apache-2.0`).
  Long names are fine for human prose; automation needs the SPDX ID.
