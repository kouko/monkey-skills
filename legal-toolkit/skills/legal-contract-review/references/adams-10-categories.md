# Adams's 10 Categories of Contract Language

**Source**: Kenneth A. Adams, *A Manual of Style for Contract Drafting* (4th ed., American Bar Association, 2017)

These 10 categories describe what **linguistic form** each provision takes — the grammatical and modal-verb structure. Adams's taxonomy is orthogonal to Stark's 7 concepts (Stark = legal effect; Adams = linguistic form). L3 tags both, in parallel.

⚠️ **DO NOT translate the category names** — they are English-jurisprudence专有名詞 that lose their distinction in Chinese (e.g. "Language of Policy" vs "Language of Obligation" — both translate as "義務" naturally but Adams distinguishes them precisely).

---

## The 10 Categories

### 1. Language of Obligation

**Marker**: `shall`

**Definition**: Creates an enforceable affirmative duty on a specific party.

**Examples**:
- "Vendor shall deliver the Services in accordance with the SLA."
- "Customer shall pay all undisputed invoices within Net 30."

**Test**: substitute "has a duty to" — does it read naturally? If yes, this is Obligation.

---

### 2. Language of Discretion

**Marker**: `may`

**Definition**: Grants a choice to act, without creating duty.

**Examples**:
- "Customer may terminate this Agreement upon 60 days' notice."
- "Either Party may engage a third-party auditor at its own expense."

**Test**: substitute "is permitted to" — natural fit?

---

### 3. Language of Prohibition

**Marker**: `shall not` / `may not`

**Definition**: Bans an action.

**Examples**:
- "Vendor shall not subcontract without Customer's prior written consent."
- "Customer may not assign this Agreement except as provided herein."

**Note**: `shall not` is generally preferred over `may not` (which is more common in BigLaw US practice but ambiguous — could read as "Customer is not permitted to but might anyway" vs "is prohibited").

---

### 4. Language of Policy

**Marker**: `will` (used as future indicative)

**Definition**: A future statement of intention or factual prediction, **without** the duty-force of `shall`.

**Examples**:
- "The Services will be available 24/7 except during scheduled maintenance windows."
- "Payments will be due on the first day of each calendar month."

**⚠️ The will-vs-shall trap**: many drafters use `will` when they mean `shall`. The legal effect is weaker — `will` may be read as a forward-looking factual statement, not a binding duty. L3's `will_disguised_obligation` flag catches this.

**Test**: substitute "is expected to" vs "has a duty to":
- Reads naturally as "is expected to" → genuine Language of Policy
- Reads more like "has a duty to" → will-disguised Obligation; flag

---

### 5. Language of Performance

**Marker**: present-tense indicative ("hereby") / "delivery of"

**Definition**: Describes the act of performing or having performed.

**Examples**:
- "Vendor hereby delivers the deliverable to Customer."
- "By signing below, Customer acknowledges receipt of the Services."

Often paired with Stark's Performance concept.

---

### 6. Language of Declaration

**Marker**: declarative present ("is", "means", "shall mean")

**Definition**: A statement that takes legal effect by being declared.

**Examples**:
- '"Confidential Information" means information disclosed in writing and marked confidential...'
- "This Agreement is the entire agreement between the Parties."

Often paired with Stark's Declaration concept.

---

### 7. Language of Recommendation

**Marker**: `should`

**Definition**: A non-binding recommendation — neither duty nor pure choice.

**Examples**:
- "Customer should provide Vendor with reasonable cooperation."
- "Notices should be sent to the addresses listed in Schedule A."

**⚠️ Adams says: avoid `should` in operative provisions** — it's ambiguous between "is recommended to" and "has a soft duty to". If you mean Obligation, use `shall`; if you mean Discretion, use `may`.

---

### 8. Language of Belief

**Marker**: `believes` / `understands` / `acknowledges`

**Definition**: A soft assertion of mental state, often used in recitals or representations.

**Examples**:
- "Customer acknowledges that the Services depend on third-party infrastructure."
- "Vendor believes that the Services will meet Customer's needs."

Weaker than Representation (which is a hard statement of fact); often appears in soft-law contexts.

---

### 9. Language of Intention

**Marker**: `intends to` / `agrees in principle`

**Definition**: Forward-looking statement of intent, without duty.

**Examples**:
- "The Parties intend to enter into a long-term partnership."
- "Customer intends to refer additional customers if pleased with the Services."

⚠️ Generally non-binding. Often appears in recitals or MOUs / non-binding term sheets — be careful: a clause that uses Language of Intention in the operative section may be unenforceable.

---

### 10. Language of Representation

**Marker**: `represents` / `represents and warrants`

**Definition**: A statement of fact made for the other party's reliance.

**Examples**:
- "Vendor represents that it has all necessary licenses to operate."
- "Customer represents and warrants that the data being processed is accurate."

Often paired with Stark's Representation concept (and Warranty if also forward-looking).

---

## Cross-reference table (Adams ↔ Stark)

| Adams category | Typical Stark concept |
|---|---|
| Language of Obligation (`shall`) | Obligation |
| Language of Discretion (`may`) | Discretion |
| Language of Prohibition (`shall not`) | Obligation (negative) |
| Language of Policy (`will`) | (none — not an enforceable duty; flag if disguised Obligation) |
| Language of Performance (`hereby`) | Performance |
| Language of Declaration (`means`) | Declaration |
| Language of Recommendation (`should`) | (ambiguous — Adams says avoid) |
| Language of Belief (`acknowledges`) | (weak; often paired with Representation) |
| Language of Intention (`intends to`) | (non-binding; flag if in operative section) |
| Language of Representation (`represents`) | Representation (and Warranty if forward-looking) |

L3 tags both axes; L4 / L6 / L7 use the cross-product (e.g. Stark Discretion + Adams Language of Obligation = unusual combination, often an error).

---

## Why both Stark + Adams?

Stark tells you what the **legal effect** is. Adams tells you whether the **linguistic form** matches that effect. Most drafting errors fall in the gap between the two: drafter intends Obligation (Stark) but writes Language of Policy (Adams) — `will` instead of `shall`. L3 catches this by tagging both axes and flagging the mismatch.

---

## Reading guide

- Adams Ch. 3 — "Categories of Contract Language" (the original taxonomy)
- Adams Ch. 2 — "Drafting Conventions" (general style — semicolons, defined terms, etc.)
- Adams Appendix B — "Words to Watch" (lists problematic words like `endeavors`, `commercially reasonable`, `best efforts`)

For Taiwan-law overlay: Adams's English-language analysis carries through to English-translation drafts of TW contracts. For pure 中文 contracts, the underlying distinction (duty vs choice vs prediction) is still useful, even though the linguistic markers differ (應/須/得/必須/可 in Chinese map roughly to shall/may/should/will).
