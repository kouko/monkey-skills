# ISTQB CTFL v4.0 Vocabulary (Shared Standard)

Authoritative testing vocabulary for qa-team. Both worker (when writing test plans)
and evaluator (when reviewing) reference this file. All terms trace to
ISTQB Certified Tester Foundation Level Syllabus v4.0.1.

Primary source: [ISTQB CTFL Syllabus v4.0.1 PDF](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)
Japanese equivalent: [JSTQB Foundation Syllabus V4.0.J02](https://jstqb.jp/dl/JSTQB-SyllabusFoundation_VersionV40.J02.pdf)

## Core Distinction: Levels vs Types vs Techniques

These are **three orthogonal axes**. Any type can be executed at any level using any technique.

- **Level** describes *when / at what granularity* testing happens
- **Type** describes *what characteristic* is being tested
- **Technique** describes *how* test cases are derived

## Test Levels (ISTQB CTFL v4.0 §2)

| Level | Scope | Typical concerns |
|-------|-------|-----------------|
| **Component** (unit/module) | Individual hardware or software component | Isolated logic, pure functions, algorithms |
| **Integration** | Interfaces and interactions between integrated components or systems | Service interactions, data flow across module boundaries |
| **System** | Integrated system as a whole verified against specified requirements | End-to-end behavior of the assembled product |
| **Acceptance** | Whether the system satisfies user needs, requirements, and business processes | User scenarios, business rule validation |

Component-Integration and System-Integration sub-levels exist for finer distinctions.
Levels may be combined or reorganized per project architecture — they are not rigid phases.

## Test Types (ISTQB CTFL v4.0 §2.3)

| Type | Definition | Examples |
|------|------------|----------|
| **Functional** | Based on functions/features — "what the system does" | Specification-based black-box, feature acceptance |
| **Non-functional** | Measures quantifiable characteristics — "how well the system works" | Performance, load, stress, usability, reliability, portability, maintainability |
| **Structural** (white-box) | Based on internal structure of the component or system | Statement coverage, branch/decision coverage, path coverage |
| **Change-related** | Verifies changes | Confirmation testing (fix verification), regression testing |

## Design Techniques (ISTQB CTFL v4.0 §4)

### Black-Box (Specification-Based) — §4.2

| Technique | What it produces | When to apply |
|-----------|------------------|---------------|
| **Equivalence Partitioning (EP)** §4.2.1 | Input domain divided into classes where all values produce equivalent behavior | First-line default for any input validation — one representative per class |
| **Boundary Value Analysis (BVA)** §4.2.2 | Tests at edges of ordered partitions (min, min+1, max−1, max) | Whenever partitions are ordered (numeric, sequential, date ranges). Combine with EP by default |
| **Decision Table Testing** §4.2.3 | Combinations of conditions and resulting actions | Complex business rules where output depends on input combinations |
| **State Transition Testing** §4.2.4 | Sequences of inputs with state-dependent outputs | Multi-step processes where order matters (login flows, checkout, document lifecycle) |
| **Use Case Testing** §4.2.5 | Scenarios derived from use cases (main + alternative + exception) | Business process flows from start to finish; best for acceptance testing |

### White-Box (Structural) — §4.3

| Technique | What it covers |
|-----------|----------------|
| **Statement Coverage** | Every executable statement is exercised at least once |
| **Branch/Decision Coverage** | Every decision outcome (true and false) is exercised |

### Experience-Based — §4.4

| Technique | Notes |
|-----------|-------|
| **Error Guessing** | Tester leverages knowledge of likely defects |
| **Exploratory Testing** | Concurrent test design, execution, and learning |
| **Checklist-Based Testing** | Testing guided by a checklist of conditions or rules |

## Test Case Naming Convention

Scenario-based, not method-based. Describe the situation and expected outcome
from the user's or system's perspective, not the function under test.

- Format: `{context} {action} {expected outcome}`
- Good: "User with expired token receives 401 and redirect to login"
- Bad: "test_validate_token_returns_false"

Rationale: scenario-based names survive refactoring because they describe
behavior, not implementation. Aligns with ISTQB's specification-based
testing philosophy and ISO/IEC/IEEE 29119-3 test case documentation format.

## Pass/Fail Criteria Format

Must be **binary**, **measurable**, and **specific**:

- Binary: pass or fail, no partial credit
- Measurable: concrete observation (response code, value comparison, timing threshold)
- Specific: no subjective judgments like "works correctly" or "behaves as expected"

Good: "Response status is 200 AND body contains `user_id` field"
Bad: "API returns the correct response"

## Mapping Legacy Vocabulary

When reading older documents or code that uses the following legacy terms,
map them to ISTQB vocabulary:

| Legacy term | ISTQB equivalent |
|-------------|------------------|
| Unit test | Component test, functional type |
| E2E test | System or acceptance test, functional type |
| Integration test | Integration test (same name) |
| Performance test | System or acceptance test, non-functional type |
| Regression test | Change-related type (can run at any level) |
| Smoke test | Acceptance or system test, functional type (subset for deployment sanity) |
| Load test / Stress test | Non-functional type (performance subcategory) |

## Sources

- [ISTQB CTFL Syllabus v4.0.1 (official English PDF)](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf) — primary source for §2 test levels/types, §4 design techniques
- [JSTQB Foundation Level Syllabus V4.0.J02 (Japanese equivalent)](https://jstqb.jp/dl/JSTQB-SyllabusFoundation_VersionV40.J02.pdf)
- [ISTQB Glossary](https://glossary.istqb.org/) — official term definitions
