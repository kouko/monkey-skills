# L3 — Categorize each provision (Stark 7 + Adams 10)

**Layer**: L3 (universal; runs after L2)
**Skipped**: mode == nda
**Reads**: no playbook (universal taxonomies; see [`references/stark-7-concepts.md`](../references/stark-7-concepts.md) + [`references/adams-10-categories.md`](../references/adams-10-categories.md))

---

## Purpose

L3 categorises every provision using two **orthogonal** taxonomies that together describe what a contract clause **is**:

- **Stark's 7 contract concepts** — what kind of legal effect does this provision create?
- **Adams's 10 language categories** — what verb / grammatical form is being used?

These taxonomies are **orthogonal**: a single provision has both one Stark concept and one Adams category (e.g. "Vendor shall deliver the Services" = Stark `Obligation` + Adams `Language of Obligation`).

The output of L3 powers:
- L4 (functional tier — money / risk / control / standards / endgame mapping)
- L6 (consistency check — does an Obligation appear without a corresponding Performance trigger?)
- L7 (escalation — Stark `Discretion` granted unilaterally is a frequent playbook walk-away pattern)

---

## Pipeline

### Step 1 — Apply Stark's 7 concepts to each provision

For each provision in the contract (per-clause-or-paragraph granularity per L2's anatomy map):

| Stark concept | Question to ask | Typical clause shapes |
|---|---|---|
| **Obligation** | Does someone have to do something? | "Vendor shall deliver..." / "Customer must pay..." |
| **Discretion** | Does someone have a choice? | "Customer may terminate..." / "At Vendor's sole discretion..." |
| **Representation** | A statement of present fact | "Vendor represents that it owns the IP..." |
| **Warranty** | A promise that a future / continuous state holds | "Services will meet the SLA..." / "Software is free of known defects..." |
| **Condition** | If-then; precondition to obligation | "Provided Customer pays the fee, Vendor shall..." / "Upon written notice, ..." |
| **Declaration** | Definition / statement of effect | '"Confidential Information" means...' / "This Agreement is governed by..." |
| **Performance** | The actual act — typically the trigger of obligation | "Vendor's delivery of the Services constitutes..." |

Multiple concepts can apply to one provision (an Obligation often carries an embedded Condition). Tag all applicable.

### Step 2 — Apply Adams's 10 categories

| Adams category | Detection |
|---|---|
| **Language of Obligation** | "shall" / "must" — creates a duty |
| **Language of Discretion** | "may" / "is entitled to" — grants choice |
| **Language of Prohibition** | "shall not" / "may not" — bans an action |
| **Language of Policy** | "will" used as future indicative without obligation force |
| **Language of Performance** | Defines what counts as completing an obligation |
| **Language of Declaration** | Definitions / assertions of legal effect |
| **Language of Recommendation** | "should" — non-binding |
| **Language of Belief** | "believes" / "understands" — soft assertion |
| **Language of Intention** | "intends to" — non-binding future |
| **Language of Representation** | "represents and warrants" — backwards-looking assertion |

Detection often hinges on the **modal verb**: shall / must / may / will / should / believes / intends / represents.

⚠️ Specific anti-pattern: many drafters use **"will"** when they mean **"shall"**. Adams calls this "Language of Policy disguising Obligation". Flag and note in L4 — these provisions may not be enforceable as obligations.

### Step 3 — Cross-product tagging

For each provision, output:

```yaml
provision: <ref to L2 anatomy location>
text_excerpt: "<verbatim>"
stark_concepts:
  - obligation     # primary
  - condition      # embedded
adams_categories:
  - language_of_obligation
party_carrying_burden: "Vendor"   # who carries the "shall"?
parties_benefiting: ["Customer"]
flags:
  - will_disguised_obligation     # if applicable
  - sole_discretion_unilateral    # if Discretion + only one party
```

### Step 4 — Output to internal pipeline state

```yaml
categorization:
  total_provisions: <count>
  by_stark_concept:
    obligation: <count>
    discretion: <count>
    representation: <count>
    warranty: <count>
    condition: <count>
    declaration: <count>
    performance: <count>
  by_adams_category:
    language_of_obligation: <count>
    # ... etc
  flags_count: <count of will_disguised + sole_discretion etc>
```

Consumed by L4 (functional tier) and L6 (consistency check — every Obligation should have a corresponding Performance trigger somewhere).

---

## Output contract

```
✅ L3 complete.
   Provisions categorised: <count>
   Stark concept distribution: <summary>
   Adams category distribution: <summary>
   Anti-pattern flags: <count> (will-disguised, sole-discretion-unilateral)
   Pass to: L4
```

---

## Edge cases

- **Provision spans multiple sentences with mixed concepts**: tag with the primary one + flag `mixed_concept_provision` so L4 can decide whether to treat as one clause or split.
- **Boilerplate with no clear Stark concept** (e.g. "Counterparts: This Agreement may be executed in counterparts."): tag as Declaration + Discretion (procedural mechanism, not substantive).
- **Recitals (whereas clauses)**: tag as Declaration of background facts (not Obligation / Representation). They are interpretive aids, not enforceable.
- **Mixed-language clause** (zh-TW + English in same provision): tag the Stark concept once based on substantive content; Adams category goes by the **operative verb's** language form.
- **NDA mode** skips L3; the bundled NDA-specific check at L4-L7 handles concept categorisation inline.

---

## References

- Full Stark concepts: [`references/stark-7-concepts.md`](../references/stark-7-concepts.md)
- Full Adams categories: [`references/adams-10-categories.md`](../references/adams-10-categories.md)
