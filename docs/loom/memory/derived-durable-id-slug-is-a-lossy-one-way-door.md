---
name: derived-durable-id-slug-is-a-lossy-one-way-door
description: A durable identity mechanically slugged from a richer key (e.g. kpi_id from an XBRL dimensional signature) is a one-way door whose collision fails SILENTLY — two distinct sources merging into one series is data corruption — so guard it fail-loud at the producer AND key the guard on the CONSUMER's own identity normalization, not a finer raw key, or it over-fires on legitimate inputs
type: gotcha
origin: PR arc-d US XBRL→kpi_store producer (feat-kpi-xbrl-store-producer, 2026-07-25)
---

When a durable identity is derived by a lossy transform (strip suffixes,
lowercase, drop namespace) from a richer source key, the transform is
NOT guaranteed injective over arbitrary inputs even if it is over the
canonical ones you sampled. `derive_kpi_id` slugs a `kpi_id` from an
XBRL dimensional signature; `ns1:ProductMember` and `ns2:ProductMember`
both collapse to `product`. Since `kpi_id` is the append-only store's
series identity, a silent collision merges two DIFFERENT segments into
one series — a fabricated restatement `†`, i.e. data corruption in a
durable store, with no error.

**Why:** the corruption is SILENT and lands in durable history (a
one-way door — re-keying later fragments every stored series). The
repo's fail-loud anti-fabrication floor ("a >1-distinct-value
signature+period RAISES") already says ambiguity must be loud, not
guessed; a lossy id derivation is the same hazard one layer up.

**How to apply:**
1. Guard the derivation fail-loud at the producer: track `id → source`
   and RAISE (naming both sources + the id) when a *distinct* source
   claims an already-taken id — never silently pick/merge. Don't trust
   the source naming domain to stay injective just because today's real
   data doesn't collide.
2. Key the guard on the CONSUMER's identity normalization, not a finer
   raw key. If the store treats two source keys as the SAME series (e.g.
   `same_period` / a normalize-fold like `consolidation None == default`),
   a guard keyed on the raw un-normalized key OVER-FIRES — it rejects a
   legitimate pair the consumer would have merged correctly. The guard's
   notion of "distinct" must equal the consumer's notion of "same".

Relates to [[match-kpi-on-full-dimensional-signature-not-one-axis]] (the
signature IS the identity; ConsolidationItemsAxis is a qualifier, not a
breakdown axis) and [[required-identity-guard-must-reject-whitespace-not-just-empty]]
(identity guards must reject the near-miss, not just the empty case).
