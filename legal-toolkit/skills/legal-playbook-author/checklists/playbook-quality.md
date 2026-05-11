# playbook-quality — binary all-pass rubric for legal-playbook-author output

> **v0.3.0 (Phase 1.6)** rubric. Used to evaluate the quality of a
> playbook entry produced by `bootstrap-mode` / `extend-mode` /
> `revise-mode`. Same Harvey BigLaw Bench convention as contract-review's
> rubrics: binary all-pass, failed criteria listed explicitly, no
> averaging.

> **Use cases**:
> - After authoring a new clause, run this rubric to catch common gaps
>   before the user starts using it in `legal-contract-review`
> - After `revise-mode` to confirm the edit didn't regress quality
> - As part of `dogfood-procedure` to evaluate the bootstrap onboarding UX

---

## Criteria (N = 12)

### Tier: deterministic (Python-verifiable via validate_schema.py + grep)

| ID | Criterion (zh-TW) | Verification |
|---|---|---|
| **PBA-01** | Frontmatter passes JSON Schema (oneOf flat / variant / _clause) | `validate_schema.py <file>` returns PASS |
| **PBA-02** | `clause_id` kebab-case, starts with letter | regex `^[a-z][a-z0-9-]*$` |
| **PBA-03** | `walk_away_triggers` non-empty list of non-empty strings | `len(walk_away_triggers) >= 1` AND each item len > 0 |
| **PBA-04** | `escalate_to` non-empty | str(escalate_to).strip() != "" |
| **PBA-05** | `risk_default` ∈ {green, yellow, red} | enum check |
| **PBA-06** | `last_updated` is valid ISO date | `^\d{4}-\d{2}-\d{2}$` |
| **PBA-07** | Body has `## 偏好立場` section (non-empty) | regex search + content non-empty |
| **PBA-08** | Body has `## Fallback 1` section (non-empty) | regex search + content non-empty |
| **PBA-09** | Body has `## 為什麼這條重要` section (≥ 20 chars) | regex search + content length |
| **PBA-10** | If variant-folder, sibling `_clause.md` exists AND has `has_variants: true` | filesystem check + frontmatter check |

### Tier: semantic (LLM-judged)

| ID | Criterion (zh-TW) | LLM judgment prompt |
|---|---|---|
| **PBA-11** | `walk_away_triggers` 是具體 condition，非「any breach」這種空泛項 | "For each walk-away trigger, can you describe a specific contract clause shape that WOULD match and one that WOULDN'T? Generic triggers like 'any unfavourable term' fail this." |
| **PBA-12** | `## 為什麼這條重要` 用業務人員聽得懂的語言（不純法律術語）| "Could a non-legal Operations / Sales / CEO reader understand this paragraph without consulting a glossary? If it relies on §247-1 / consideration / privity unexplained, fail." |

---

## Anti-patterns the rubric is designed to detect

- **Placeholder leakage** (user committed entry with `[REPLACE_ME]` in walk_away) → PBA-03
- **Empty escalate_to** ("just figure it out") → PBA-04
- **Wrong risk_default** ("orange" / "high") → PBA-05
- **Body skipping** (no `## 偏好立場` so `legal-contract-review` L7 has nothing to compare against) → PBA-07
- **Variant-folder missing `_clause.md`** (orphaned variants) → PBA-10
- **Walk-away too vague** ("not in our favour") → PBA-11
- **Legal jargon in business translation** (forfeits Anti-Pattern "Static" defense) → PBA-12

---

## Output (consumed by self_grade.py + emitted to a `<entry>.quality.yml` companion)

For each criterion, emit:

```yaml
criterion_id: PBA-01
criterion_zh_tw: Frontmatter passes JSON Schema
tier: deterministic
result: pass / fail
evidence: "<schema-validator output OR file:line>"
```

After running all 12, aggregate:

```yaml
playbook_quality:
  file: legal-playbook/confidentiality.md
  passed: 10
  total: 12
  failed_criteria:
    - PBA-11: "walk_away trigger 'one-sided' is too generic; describe the asymmetry concretely"
    - PBA-12: "## 為什麼這條重要 uses '違反 §247-1' without business-friendly explanation"
```

When a `revise-mode` finishes, optionally rerun this rubric for the
revised file and surface any regression vs. the prior `playbook_quality`
on disk (Phase 2+ feature; v0.3.0 just emits the current score).

---

## Relationship to contract-review's rubric

- **playbook-quality** (this file) judges **the playbook entry itself**
- **answer-criteria + source-criteria** (in `legal-contract-review/checklists/`)
  judge **a contract-review output** that consumes the playbook

A playbook that scores well on this rubric → produces better
contract-review outputs → which score better on answer-criteria /
source-criteria. The two rubrics complement; neither subsumes the other.

When `legal-contract-review` runs with bundled fallback (no user
playbook), this rubric still applies to the **bundled fallback files**
(which are authored just like user entries) — used during
`build_baseline.py` checks to ensure the shipped baselines meet the
same quality bar we ask of users.
