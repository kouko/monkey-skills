# Baseline brainstorm — merge two open restaurant tables

Seed: "Let a restaurant server merge two open tables (each with in-progress orders) into one check."

## Requirements / behaviors

**Core merge action**
- Server selects a source table and a target table; all of the source table's open order items move onto the target table's check.
- After a successful merge, the source table's check is closed/emptied and the source table becomes available (or stays seated but billed under the target — needs a decision; see Open questions).
- The combined check on the target table shows every item from both tables, with quantities, modifiers, prices, and which seat/guest each item belongs to (if seat-level tracking exists).
- The merge is a single atomic operation: either everything moves or nothing does. No partial state where an item exists on neither or both tables.
- The merged check must recompute totals: subtotal, per-item tax, discounts, service charge, tip basis, and grand total — not a naive sum of the two prior totals (tax/discount rules may differ).
- The action should be reversible or at least correctable (unmerge / split back, or a void+re-fire path) because servers make mistakes mid-service.

**Pricing & financial correctness**
- Item-level discounts, promos, and comps already applied on the source table must carry over and not be silently dropped or duplicated.
- Check-level (whole-ticket) discounts must be re-evaluated against the new combined subtotal, not double-applied from both tables.
- Tax is recomputed on the combined taxable base; if the two tables had different tax treatments (e.g., one had a tax-exempt guest), that distinction must be preserved per item, not flattened.
- Service charge / auto-gratuity thresholds (e.g., auto-grat for parties of 6+) may now trigger because the merged party is larger — recompute.
- Any loyalty points / rewards accrual basis should reflect the final single check, counted once.

**Order / kitchen state**
- Items already sent to the kitchen ("fired") keep their fired status and timestamps; the merge must not re-fire them or duplicate KDS tickets.
- Items still in "new/unsent" state on the source remain unsent under the target.
- Course/firing sequence and any "hold" flags should be preserved.

**Identity, audit, concurrency**
- Record who performed the merge, when, and the source→target table mapping for audit/manager review.
- Seat/table ownership: the server assigned to the target table becomes responsible for the combined check (or original servers' sales attribution is split — see Open questions on tip pooling / sales credit).
- The operation must be safe under concurrent access (two servers, or server + manager, acting on the same tables at once).

**UI / workflow**
- Clear pre-merge confirmation showing both checks side-by-side and the resulting combined check before committing.
- Visual feedback that table A is now empty/available and table B holds the combined party.
- Guest count on the target updates to the sum of both parties' covers.

## Edge cases & failure modes

- **Merging a table with itself** (source == target) — reject.
- **One or both tables empty / no open order** — merging an empty table is a no-op or should be blocked depending on intent; merging two empty tables is meaningless.
- **Already-closed / paid check** — cannot merge a table whose check is paid or partially paid (a payment/tender already applied). Block, or handle the partial-payment case explicitly.
- **Partial payment already on one table** — guest at table A already paid for some items, or left a deposit; merging must account for the existing tender, not lose it or let items be paid twice.
- **Split-check in progress** — one of the tables is mid-split (items allocated to multiple sub-checks). Merge semantics here are ambiguous; likely block until split is resolved.
- **Different tax/exemption status** between the two checks — must not be flattened (covered above), and a conflict (e.g., both claim a single-use exemption) needs a rule.
- **Different service/ownership context** — tables in different revenue centers, different floor sections, or assigned to different servers; or one table is in a different order type (dine-in vs takeout/bar tab). Decide whether cross-type merges are allowed.
- **Auto-gratuity already manually overridden** on one check, then party size crosses the auto-grat threshold after merge — which wins?
- **Concurrency / double-merge** — server taps merge twice, or two devices merge the same source into different targets simultaneously. Must not duplicate items or leave the source half-moved. Idempotency / locking needed.
- **Network drop mid-merge** (POS offline / sync failure) — the atomic guarantee must hold; on reconnect there must be exactly one consistent result, no ghost items.
- **Item count / check size limits** — merged check exceeds a max-items or max-amount ceiling the system enforces.
- **Comps / voids / refunds** present on the source — must carry their state and not become re-chargeable.
- **Loyalty/member attached to source check** — which member is credited on the merged check if both had different members attached?
- **Open discounts requiring manager approval** on source carrying into a check the current server can't authorize.
- **Re-merge / chained merge** — merging an already-merged table again; the audit trail and unmerge path must still make sense.
- **Permissions** — server lacks authority to merge (e.g., crossing sections, or a manager-only action); must be enforced, not just hidden in UI.
- **Currency / rounding drift** — recomputed total differs from sum-of-parts by rounding; define the rounding rule so it's not a "lost cent" complaint.

## Open questions

- Does the **source table stay seated** (guests physically moved together) or become free for the next party? This drives whether table state goes to "available."
- Is the merge **reversible (unmerge)**, or one-way requiring void+re-enter to correct? Reversibility scope (full session? after kitchen fire? after partial payment?) needs a boundary.
- **Sales attribution / tip credit** when the two tables had different servers — does the original server keep credit for their items, or does the target server take the whole check? Affects payroll/tip pooling.
- How are **conflicting whole-check discounts** resolved — keep the more favorable, keep target's, or prompt the server to choose?
- **Partial-payment tables**: allowed to merge at all, or hard-blocked? If allowed, how is the prior tender represented on the combined check?
- Are **cross-revenue-center / cross-order-type** merges (dine-in + bar tab, two different sections) permitted, and do they need manager approval?
- What is the **permission model** — any server, only the owning servers, or manager-only? Is approval required for cross-section merges?
- Do we support **N-way merge** (3+ tables) or strictly pairwise? If pairwise only, is repeated pairwise merge the supported path for big parties?
- For **auto-gratuity recompute conflicts** (manual override vs new threshold), which rule wins, and is the server warned?
- What **audit/reporting** is required — does finance need the pre-merge checks preserved for the day's reconciliation, or only the final merged check?
