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

**THE CLASS IS NOT SPECIFIC TO NORMALIZATION HELPERS, and rule 1 above is not
executable enough to stop it** (branch feat-spine-chain-coverage, 2026-07-26 —
**14 instances in one arc**, across six different authors including the
orchestrator, four reviewers and five implementers). The observed forms:

| where | the claim | why it was false |
|---|---|---|
| module docstring | "both modules answer the same question" | suffix SETS differ (5 vs 2) |
| module docstring | "EVERY entry is pinned by a test" | one entry knowingly unpinned, 37 lines below |
| test docstring | "all fixtures observed live" | seven were constructed |
| capture docstring | "the suite fails loudly on the missing rows" | a simulation showed it stays silent |
| capture note | "stores no score from these functions" | true for two of three |
| test docstring | "fails if the divergence is ever fixed" | it never reads the pipeline side |
| plan | "15 fields" ×3, brief ×9 | there are 14 |
| plan | "every filing from 2013 through 2017" | filed-vs-fiscal never stated |
| brief | "2-3 candidate totals" | scope (revenue-only vs calc roots) never stated |
| commit trailer | "the other three file separately" | two of them were never checked |
| test | "the prose cannot drift silently" | a bare `\b14\b` matched inside "13 of those 14" |

**Why rule 1 fails:** at writing time the author is thinking about the thing
they just got RIGHT, not the things they did not do. "Name the scope" asks them
to enumerate an absence. Nobody in this arc was careless; the shape is simply
invisible from the inside, which is why it recurred through six authors who had
all read this entry.

**Two executable replacements, both mechanical:**

1. **A universal word obliges an exception clause in the same paragraph.**
   `every` / `all` / `never` / `cannot` / `always` / `both … same` — if one
   appears, the same paragraph must either name the exceptions or say
   explicitly that there are none. This is greppable and needs no judgement.
   Nine of the fourteen would have been caught by it.
2. **A guard's claim is verified by RUNNING a mutation, never by re-reading.**
   Every instance found by mutation was found immediately; every instance found
   by reading took one to four rounds. The three that reading never found at all
   (the accession-only ordering, the unpinned tagged-vs-derived rule, the count
   matching inside a longer number) each survived a full review pass and died to
   a one-line mutation.

See also [[convergence-is-not-evidence-when-the-sample-is-shared]] — the same
defect in the EVIDENCE rather than the prose.
