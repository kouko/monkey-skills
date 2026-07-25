---
name: unifying-a-normalization-has-a-scope
description: When you fix "two sites normalized a value differently" by extracting a shared helper, the fix covers exactly the sites you routed through it — and the summary sentence you write ("they can never drift apart again") is almost always broader than what you earned; three review rounds each found the same defect class at a different unrouted site
type: gotcha
origin: PR arc kpi_id injective identity (feat-kpi-id-consolidation-axis, 2.37.0, 2026-07-26)
---

An arc whose whole purpose was "make the durable id agree with itself" shipped
three consecutive whole-branch review rounds, each returning the SAME defect
class at a DIFFERENT site, each after a fix whose commit message claimed the
class was closed:

1. **Prefix ordering** — the digest and the collision guard both folded case
   then sorted; the readable prefix sorted by RAW case and compared the
   consolidation member to the default with a raw `!=`. Two ids for one
   identity, digest identical, guard silent.
2. **Suffix matching** — after routing the prefix through the shared fold,
   `_strip_axis_member_suffix` still matched `Axis`/`Member` case-SENSITIVELY,
   so drift landing on the suffix token (`DataCenterMEMBER`) again produced two
   ids for one digest.
3. **Axis membership** — after both fixes, `derive_kpi_id` excluded
   `ConsolidationItemsAxis` from the breakdown pairs while `_signature_key`
   kept it, so one id got two claim keys and the guard raised a FALSE collision
   on a pair the id derivation is explicitly tested to fold.

Each fix was correct. Each summary sentence ("the two can never drift apart
from each other again") was broader than the fix had earned, and the next round
found the defect living in exactly the gap between the claim and the fix.

**Why:** a shared helper unifies the sites you route through it, not the concept.
"Normalization" is not one decision — it is case folding AND ordering AND
suffix handling AND which axes participate AND which field a value is read
from. Extracting one of those and describing it as unification writes a claim
the code does not hold, and a false claim in a docstring is load-bearing: the
next reader designs against it, and the next reviewer checks the claim instead
of the property.

**How to apply:**
1. When you extract a shared normalization helper, write the claim with its
   SCOPE attached — "decides the CASE regime in one place", never "the two can
   never disagree again". If you cannot name the scope in one clause, you have
   not finished finding the sites.
2. Ask the reviewer for a **site-by-site enumeration that reports the agreeing
   sites too**, not just the failures. "These 14 sites agree, here is how I
   verified each; this 1 disagrees" is what found instance 3; "review this fix"
   found only instances 1 and 2, one round at a time.
3. Treat a guard as blind wherever its key differs from the identity it
   guards. Instance 2's split was invisible to the collision guard because
   `claimed_by` is keyed on the derived id: two DIFFERENT ids never meet, so
   the guard is never consulted. A guard only fires where its key collides.
4. Related: [[derived-durable-id-slug-is-a-lossy-one-way-door]] (the guard's
   notion of "distinct" must equal the consumer's notion of "same") and
   [[a-test-can-pin-behaviour-with-a-false-rationale]] (the same failure one
   layer up, in the test's stated reason).
