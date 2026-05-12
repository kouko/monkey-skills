# L2 — Anatomy mapping (universal layer)

**Layer**: L2 (universal; runs after L1)
**Skipped**: mode == nda (NDA's 5-part anatomy is simple enough to fold into L4)
**Reads**: no playbook (pure structure mapping)

---

## Purpose

L2 maps the contract's text into the **standard 5-part contract anatomy** (per Stark / Burnham / Adams convention):

1. **Preamble** — title, date, parties, recitals (whereas clauses)
2. **Definitions** — terms with capitalised initial letter inside the doc
3. **Action sections** — what the parties will do (services, payment, term)
4. **Endgame sections** — termination, breach, dispute resolution, survival
5. **Boilerplate** — notices, assignment, severability, governing law, force majeure, counterparts

In addition, L2 performs a **簽約主體一致性檢查** (party consistency check): every named party in the preamble must appear consistently throughout the contract. Mismatches (e.g. "Customer" defined in preamble but "Client" used in §5) signal drafting errors that often hide substantive ambiguity.

---

## Pipeline

### Step 1 — Section identification

Scan the contract; for each section, classify into the 5 anatomy buckets. Use these heuristics:

| Bucket | Detection |
|---|---|
| **Preamble** | First sections / before "Now, therefore" / contain party identifications + recitals (whereas) |
| **Definitions** | Section titled "Definitions" / "Interpretation" / capitalised term blocks in §1-§3 |
| **Action** | Sections describing **what each party does** — "Services", "Payment Terms", "Delivery", "License Grant", "Term" |
| **Endgame** | Sections about **what happens at the end / when things go wrong** — "Termination", "Default", "Indemnification", "Limitation of Liability", "Survival" |
| **Boilerplate** | Standard administrative — "Notices", "Assignment", "Severability", "Governing Law", "Entire Agreement", "Force Majeure", "Counterparts" |

Output: every section in the contract tagged with its bucket.

### Step 2 — Definitions extraction

Extract every defined term:

- Look in the **Definitions** section first (if present)
- Look for any **Capitalised Term** used elsewhere (often an embedded definition like 'and the "Service Fee" shall mean...')
- Build a `definitions_index: { Term: Definition }` map

This index is consumed by L3 (Stark Declaration concept) and L6 (re-reading definitions).

### Step 3 — Party consistency check

For each named party in the **Preamble**:

1. Record the canonical name + the defined short label (e.g. `"AcmeCo, Inc." ("Vendor")`)
2. Search the rest of the contract for the short label
3. For each occurrence, verify it refers to the same canonical party (not a copy-paste error)
4. Detect inconsistencies:
   - Short label used for the **wrong** party (vendor obligations placed on customer)
   - Short label used **but not defined** (missing party definition)
   - **Multiple short labels for the same canonical party** (Customer / Client / Buyer used interchangeably)
   - **Same short label for different canonical parties** (catastrophic — flag immediately)

For each inconsistency, emit a finding:

```yaml
clause_id: party-consistency
source_type: advisory                # not a playbook check
severity: yellow                     # may indicate substantive ambiguity
subtype: party_label_inconsistency
contract_text: "<excerpt showing inconsistency>"
remediation: "Standardise party labels; clarify with counsel"
```

### Step 4 — Output anatomy map

Internal pipeline state (consumed by L3 / L4 / L6):

```yaml
anatomy:
  preamble:
    parties:
      - { canonical: "AcmeCo, Inc.", short: "Vendor" }
      - { canonical: "Beta Corp.", short: "Customer" }
    recitals_count: 4
    effective_date: "2026-05-01"
  definitions:
    count: 23
    terms_index: { Service Fee: "...", Subscription Term: "...", ... }
  action_sections:
    - { section: §2, title: "Services", clauses: [§2.1, §2.2, ...] }
    - { section: §3, title: "Payment", clauses: [...] }
  endgame_sections:
    - { section: §10, title: "Termination", clauses: [...] }
    - { section: §11, title: "Limitation of Liability", clauses: [...] }
  boilerplate:
    - { section: §15, title: "Governing Law" }
    - ...
  party_consistency:
    inconsistencies: [...]
```

---

## Output contract

```
✅ L2 complete.
   Anatomy buckets: preamble (N) / definitions (M) / action (P) / endgame (Q) / boilerplate (R)
   Defined terms indexed: <count>
   Party consistency: PASS / WARN: <count> inconsistencies
   Pass to: L3
```

---

## Edge cases

- **Mixed-language contract** (most boilerplate EN, definitions zh-TW): bucket by content function, not by language; cross-reference works.
- **Definitions inlined throughout** (no Definitions section): build the index lazily as terms appear; flag the structure as `definitions_layout: inlined` (less standard but acceptable).
- **Schedules / exhibits / annexes**: treat as separate sub-documents but run the same anatomy mapping on each; report results under `anatomy.schedules[i]`.
- **NDA mode** (`mode == "nda"`): skip L2 entirely; NDAs are short enough that L4-L7 can operate directly on raw text using a bundled NDA-specific expectation template.
- **Contract has unusual section numbering** (e.g. only 3 long sections with paragraph numbering inside): treat paragraph-level units as "clauses" for L3 / L4 / L7 purposes; record `anatomy.numbering_style: paragraph_native`.
