# PRESENTATION EVAL — seed: macOS MAS migration (DECISION question, has a mooting gate)

Question: Should we migrate our macOS app from Direct/Developer-ID (with Full Disk Access) to the Mac App Store (MAS)?
Three arms, SAME claims (see seed-4-macos.md). FLAT / FREE / HINT.

---
## ARM FLAT (verbatim)
# Should we migrate our macOS app from Direct/Developer-ID (with Full Disk Access) to the Mac App Store (MAS)?
## Summary
Migrating is a technical feasibility question before a business one. MAS mandates App Sandbox, and FDA (com.apple.security.files.all) is categorically not a declarable MAS entitlement — making migration architecturally impossible without removing that capability. Developer-ID notarization does NOT impose sandboxing, so the current path can stay notarized while retaining FDA. If the app can be rearchitected around user-initiated file access (NSOpenPanel + bookmarks), MAS becomes viable with real benefits — automatic updates, discoverability — alongside structural costs: 30% commission (15% SBP) and Apple-exclusive payment in most jurisdictions.
## Findings
- **MAS requires App Sandbox; FDA not a declarable MAS entitlement** *(high)*
- **Developer-ID notarization does not require sandboxing — can keep FDA outside MAS** *(high)*
- **Hardened Runtime + temporary-exception (Developer-ID) excluded from MAS; kexts/system-extensions unavailable** *(high)*
- **Document-centric workflows workable via NSOpenPanel + bookmarks; background/system-wide narrower** *(medium)*
- **MAS automatic updates eliminate self-managed infra (Sparkle)** *(high)*
- **30% commission (15% SBP <$1M/yr); Apple-exclusive payment most jurisdictions** *(medium)*
- **MAS 14,000+ apps discoverability; review ~1–2 days** *(medium)*
- **Some report improved trust/conversion, uncontrolled** *(low)*
## Caveats
Feasibility binary for FDA apps — architecturally impossible without removing it. Business-case secondary to the technical gate. EU DMA may alter payments, unsettled. Review stats crowd-sourced. Conversion claim single uncontrolled blog.
## Open Questions
- Can core be rewritten around user-initiated access, or needs background/system-wide?
- Does it use kext/system-extension/temporary-exception entitlements?
- Revenue impact of 30%/15% vs discoverability uplift; SBP eligible?
- EU DMA payment evolution impact?

---
## ARM FREE (structure summary — verbatim key elements)
- **"Bottom Line" lead**: if app requires FDA, migration architecturally impossible — stop, stay Developer-ID; else a real trade-off. Capability-first, business second.
- "The Hard Gate: FDA + System Entitlements" section — elevates the mooting factor prominently with a **diagnostic question**.
- "Partial Migration Path: Document-Centric Workflows" section.
- **"MAS Benefits (Real, but Second-Order)" markdown TABLE** (Benefit | Confidence | Caveat).
- "Structural Business Costs" section.
- **A "Decision Framework" ASCII decision-TREE** (Does the app use FDA/kexts/...? YES→stay; NO→is file access user-initiated? ...).
- "Open Questions to Resolve" numbered list.
Spontaneously elevates the mooting gate to the headline AND uses a table + ASCII decision tree. Strong decision aid.

---
## ARM HINT (structure summary — verbatim key elements)
- **Explicit "Decision Frame": 3 options (A Stay Developer-ID / B Migrate / C Hybrid).**
- **Large "Options × Criteria Matrix" markdown TABLE**: rows = FDA / system-extensions / file-access workaround / update infra / discoverability / review gate / commission / payment / trust / maintenance; columns = A/B/C; cells cite claim indices [N].
- "Analysis" prose (technical gate is binary; business case secondary; hybrid distributes-not-eliminates tension).
- **"Recommendation: Stay Developer-ID (A). Confidence: high"** conditional on FDA being load-bearing.
- **"Gates that would change the recommendation" markdown TABLE.**
- "Immediate audit action" — entitlement enumeration.
Most explicitly structured; the options×criteria matrix makes the 3-way comparison scannable and the mooting gate explicit in the FDA row.
