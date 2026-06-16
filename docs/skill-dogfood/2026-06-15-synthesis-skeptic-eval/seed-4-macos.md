# SEED 4 — macOS distribution (SWE / channel decision; has a near-mooting factor)

## QUESTION
Should we migrate our macOS app from Direct/Developer-ID distribution (with Full Disk Access entitlements) to the Mac App Store (MAS)?

## CONFIRMED CLAIMS BLOCK
### [0] MAS apps must run inside App Sandbox (restricts files/system/IPC to declared entitlements).
Vote: 5-0 · Source: developer.apple.com app_sandbox (primary)
Quote: "App Sandbox restricts your app to its own directory and prevents access to system resources unless you explicitly request entitlements."
Verifier evidence (high): consistent across WWDC + docs since 10.8.

### [1] 30% commission on paid MAS apps/IAP; 15% under Small Business Program (<$1M/yr).
Vote: 5-0 · Source: developer.apple.com small-business-program (primary)
Quote: "Developers earning up to $1 million per year qualify for a reduced 15 percent commission"
Verifier evidence (high): Apple's published terms.

### [2] Full Disk Access is NOT a declarable entitlement for MAS submissions.
Vote: 4-0 · Source: developer.apple.com entitlements (primary)
Quote: "The Full Disk Access entitlement is not listed among entitlements available to App Store apps."
Verifier evidence (high): entitlement tables exclude com.apple.security.files.all.

### [3] Certain kexts/system-extension entitlements available to Developer-ID are unavailable/limited in MAS sandbox.
Vote: 4-1 · Source: developer.apple.com/forums/thread/667452 (forum)
Quote: "Kernel extensions and many system-level entitlements aren't allowed through App Store review — you'd need Developer ID."
Verifier evidence (medium): forum consensus consistent with docs; one dissenter noted narrow temporary exceptions.

### [4] MAS hosts 14,000+ macOS apps with discoverability (editorial, rankings, search) unavailable to direct distribution.
Vote: 3-0 · Source: statista.com number-of-apps (secondary)
Quote: "The Mac App Store remains a primary channel consumers use to discover macOS software."
Verifier evidence (medium): Statista aggregation; count varies by period.

### [5] MAS apps get automatic updates via the App Store (no self-managed update infra e.g. Sparkle).
Vote: 5-0 · Source: developer.apple.com whats-new-in-the-mac-app-store (primary)
Quote: "Users receive updates automatically through the Mac App Store; developers no longer manage update servers."
Verifier evidence (high): well-established.

### [6] Average MAS review time ~1–2 days in 2024; entitlement-heavy apps may take longer.
Vote: 3-0 · Source: appreviewtimes.com (secondary)
Quote: "Median review time for Mac apps sits around 24–48 hours"
Verifier evidence (medium): crowd-sourced self-reported.

### [7] Developer-ID notarization (required since 10.15) does NOT impose sandbox requirements.
Vote: 5-0 · Source: developer.apple.com notarizing_macos_software (primary)
Quote: "Notarization does not require your app to be sandboxed, but requires a Developer ID certificate and passing automated checks."
Verifier evidence (high): official docs; notarization ≠ sandboxing.

### [8] Some devs report MAS migration improved trust + conversion, but no controlled study isolates the effect.
Vote: 2-1 · Source: blog.superstar.app macos-app-store-migration (blog)
Quote: "After moving to the App Store we saw roughly a 20% uptick in trial-to-paid conversion, attributed partly to the trust signal."
Verifier evidence (low): single uncontrolled developer blog; plausibly confounded.

### [9] Hardened Runtime + Developer-ID apps can request com.apple.security.temporary-exception entitlements — not available to MAS.
Vote: 4-0 · Source: developer.apple.com temporary-exception-entitlements (primary)
Quote: "Temporary exception entitlements grant access beyond the App Sandbox and are available only to Developer ID-signed applications."
Verifier evidence (high): documented; MAS binaries excluded per guidelines §2.4.

### [10] MAS sandboxed NSOpenPanel + security-scoped bookmarks allow read/write of user-chosen files without FDA, covering many document-centric workflows.
Vote: 4-0 · Source: developer.apple.com accessing_files (primary)
Quote: "Security-scoped bookmarks let your sandboxed app retain access to files the user previously selected through an open/save panel."
Verifier evidence (medium): documented; coverage for background/system-wide workflows significantly narrower than FDA.

### [11] MAS subscriptions/IAP subject to Apple payment processing exclusively; no alternative payment methods in most jurisdictions (mid-2024).
Vote: 4-1 · Source: developer.apple.com review/guidelines #payments (primary)
Quote: "Apps may not include buttons, external links, or calls to action directing customers to purchasing mechanisms other than IAP."
Verifier evidence (medium): clear guideline; one dissent noted EU DMA may create exceptions with unsettled enforcement.

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: Migrating from Developer-ID/Full Disk Access to the Mac App Store is a fundamental capability tradeoff, not merely a distribution choice. MAS imposes mandatory App Sandbox, which categorically excludes Full Disk Access and system-extension entitlements that are available to Developer-ID apps — making the migration technically infeasible for apps that require background file-system monitoring, kext/system-extension functionality, or other system-wide access. If the app's core functionality can be rewritten around user-initiated file access (NSOpenPanel + security-scoped bookmarks), MAS offers genuine benefits: automatic updates, App Store discoverability, and a trust signal that may improve conversion. The 30% commission (15% under the Small Business Program) and Apple-exclusive payment processing are structural business costs that must be weighed against any revenue upside from discoverability.

FINDINGS:
- [high] MAS requires App Sandbox; FDA (com.apple.security.files.all) is not a declarable entitlement → MAS incompatible with workflows needing unsolicited access to arbitrary paths. | evidence: [0] and [2] both primary, 4-5/0.
- [high] Developer-ID can use Hardened Runtime + temporary-exception to access protected resources; unavailable to MAS, and kexts/system-extensions restricted in MAS. | evidence: [9] (4-0 primary) + [3] (4-1 forum w/ doc corroboration).
- [high] Developer-ID notarization does not impose sandboxing; apps can stay notarized + keep FDA outside MAS. | evidence: [7], 5-0, primary.
- [medium] For document-centric workflows MAS is workable: NSOpenPanel + bookmarks; but background/system-wide access significantly narrower. | evidence: [10], 4-0 primary.
- [high] MAS provides automatic updates, eliminating self-managed infra. | evidence: [5], 5-0.
- [medium] 30% commission (15% SBP); no alternative payment methods most jurisdictions. | evidence: [1] 5-0, [11] 4-1; one dissent re EU DMA.
- [medium] MAS hosts 14,000+ apps + discoverability; review ~1–2 days. | evidence: [4] + [6], secondary/crowd-sourced.
- [low] Some report improved trust/conversion post-migration, uncontrolled. | evidence: [8], 2-1, single blog.

CAVEATS: Migration feasibility is binary for apps requiring FDA — currently architecturally impossible without removing that capability. Business-case findings are secondary to this technical gate. EU DMA may alter payment rules in EU, enforcement unsettled. Review stats self-reported.

OPEN QUESTIONS:
- Can core functionality be fully rewritten around user-initiated file access, or does it require background/system-wide access incompatible with the sandbox?
- Does the app use kext/system-extension/temporary-exception entitlements needing audit before any migration?
- What's the actual revenue impact of 30%/15% vs expected discoverability uplift; does it qualify for SBP?
- How will EU DMA payment rules affect MAS economics for EU users?
