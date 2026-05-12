# Stark's 7 Contract Concepts

**Source**: Tina L. Stark, *Drafting Contracts: How and Why Lawyers Do What They Do* (2nd ed., Aspen, 2014)

These 7 concepts describe what kind of **legal effect** each provision in a contract creates. Every provision is one (sometimes more) of these. Used by L3 categorisation to tag each provision before the business-impact mapping in L4.

⚠️ **DO NOT translate the concept names** — they are English-jurisprudence专有名詞 with no clean Chinese equivalent. (Translating "Representation" as "陳述" loses the warranty-vs-representation distinction that lawyers actually use.)

---

## The 7 Concepts

### 1. Obligation

**Definition**: A duty to perform — a "shall" / "must" creating an enforceable affirmative or negative duty.

**Linguistic markers**: `shall` / `must` / `is obligated to` / `agrees to`

**Examples**:
- "Vendor shall deliver the Services in accordance with the SLA."
- "Customer must pay all undisputed invoices within Net 30 days."
- "Neither Party shall disclose Confidential Information except as permitted herein."

**L4 mapping**: usually **control** (defining what someone must do) or **standards** (defining the level of performance).

---

### 2. Discretion

**Definition**: A grant of choice — the party may or may not do something, at their election.

**Linguistic markers**: `may` / `is entitled to` / `at [Party]'s discretion` / `may elect to`

**Examples**:
- "Customer may terminate this Agreement upon 60 days' written notice."
- "At Vendor's sole discretion, Vendor may engage subcontractors..."
- "Either Party may, but is not required to, audit..."

**L4 mapping**: usually **control** (who decides) — and an audit point: discretion granted **unilaterally** (one party only) is a frequent playbook walk-away pattern (e.g. "unilateral termination for convenience").

---

### 3. Representation

**Definition**: A statement of **present** fact, backwards-looking, made as a basis for the other party's reliance.

**Linguistic markers**: `represents` / `represents and warrants` / `states that`

**Examples**:
- "Vendor represents that it has all necessary licenses to provide the Services."
- "Customer represents that it owns the data being processed."

**Distinguishing from Warranty**: a Representation is about a present fact at the time of signing; a Warranty is a continuous promise about future / ongoing state. Same sentence often makes both: "represents and warrants".

**L4 mapping**: usually **risk** (breach → misrepresentation claim, possibly fraud).

---

### 4. Warranty

**Definition**: A promise that a state of affairs **will continue** to be true throughout the term, or about future performance.

**Linguistic markers**: `warrants` / `warrants that` / future state with promise

**Examples**:
- "Vendor warrants that the Services will conform to the Documentation for the duration of the Term."
- "Software will be free from material defects for 90 days."

**L4 mapping**: **standards** (defining quality / level) + **risk** (breach → damages).

---

### 5. Condition

**Definition**: An event whose occurrence is necessary before an obligation becomes performable. "If X, then Y must happen."

**Linguistic markers**: `if` / `provided that` / `unless` / `upon [event]`

**Examples**:
- "Provided Customer pays the Subscription Fee, Vendor shall continue providing the Services."
- "If Customer fails to cure a material breach within 30 days, Vendor may terminate."
- "Upon written notice from Vendor, Customer's right to use the Services terminates."

**L4 mapping**: usually paired with another concept (Condition + Obligation, Condition + Discretion). The condition itself defines **what triggers** the paired effect.

---

### 6. Declaration

**Definition**: A statement that has **legal effect by virtue of being declared** — definitions, choice-of-law statements, severability, entire agreement.

**Linguistic markers**: `is defined as` / `means` / `shall mean` / `is governed by` / `is severable`

**Examples**:
- '"Confidential Information" means information disclosed by one Party to another that is identified as confidential...'
- "This Agreement is governed by the laws of the Republic of China (Taiwan)."
- "Each provision of this Agreement is severable."

**L4 mapping**: usually **control** (declaring scope) or **endgame** (governing law, dispute resolution).

---

### 7. Performance

**Definition**: The actual act that **fulfills** an obligation. Often appears as a description of what counts as having performed.

**Linguistic markers**: `delivery of` / `provision of` / `is deemed performed when` / `acceptance` / `completion`

**Examples**:
- "Vendor's delivery of the deliverable to Customer's designated FTP server constitutes performance."
- "Acceptance occurs when Customer either (a) provides written acceptance or (b) fails to reject within 14 days."

**L4 mapping**: usually **standards** (defining what counts as done) — and crucial for L6 if-breach-branch detection (every Obligation should have a corresponding Performance criterion somewhere).

---

## Anti-pattern (used by L3 flags)

### will-disguised obligation

Drafters frequently use `will` for what they mean as a `shall` (Obligation). Adams explicitly distinguishes these (see [`adams-10-categories.md`](adams-10-categories.md) §Language of Policy vs Language of Obligation). The legal effect may be weaker than the drafter intends — `will` is closer to "Language of Policy" (future indicative without enforceable duty force).

Flag and note in L4: provisions using `will` that contextually intend `shall` may not be enforceable as obligations.

### sole-discretion unilateral

When Discretion is granted to **only one party**, the other party has no symmetric ability. Common one-sided patterns:

- "Vendor may, in its sole discretion, modify the Services."
- "Customer may not terminate without cause."

These are not invalid per se but are frequent playbook walk-away triggers. Flag in L3 for L4 / L7 attention.

---

## How to use this reference

L3's protocol cites this file when tagging each provision. When you (the LLM) are deciding which Stark concept(s) apply:

1. Find the operative verb / modal in the provision
2. Match to the linguistic markers above
3. Apply the substantive test (does it create a duty? a choice? a fact statement? etc.)
4. Tag — multiple concepts can apply to one provision

Cross-reference [`adams-10-categories.md`](adams-10-categories.md) for the language-form categorisation (Stark = legal effect; Adams = linguistic form).

---

## Reading guide

- Stark Ch. 2 — "The Seven Drafting Concepts" (the original taxonomy)
- Stark Ch. 9-15 — application of each concept to specific clause types
- Anglo-American contract drafting canon

For Taiwan-law overlay, none of these concepts requires translation — Stark's English taxonomy works because legal effect is universal even when statutes differ.
