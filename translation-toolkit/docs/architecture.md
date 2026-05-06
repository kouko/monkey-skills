# translation-toolkit Architecture

High-level overview of the plugin's topology, pipeline, and core conventions.
For full design rationale, see the spec at
`../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`.

## 1. Six-Skill Topology

The toolkit ships 6 skills organized as 1 router + 1 intake + 4 active
specialists:

| Skill                       | Role                                                         |
|-----------------------------|--------------------------------------------------------------|
| `using-translation-toolkit` | Router — picks the right specialist based on user intent.    |
| `translation-intake`        | Clarifies brief: pair, domain, register, length, audience.   |
| `translation-i18n`          | UI strings, JSON/YAML keys, ICU placeholders, length budgets.|
| `translation-doc`           | Technical docs, READMEs, API references, runbooks.           |
| `translation-creative`      | Marketing / narrative / transcreation; voice + tone fidelity.|
| `translation-audit`         | Audits an existing translation; produces gate verdicts only. |

## 2. Five-Layer Pipeline

Every active skill runs the same five-layer pipeline:

```
L1 Intake       → confirm pair, domain, register, constraints
L2 Preparation  → resolve glossary (4-tier), load typography rules, scope corpus
L3 Core Loop    → WRITER drafts → CRITIC critiques → REVISER revises (N rounds)
L4 Verification → 5 gates (M1, M2, S1, S2, I1); BACK-TRANSLATOR for S1
L5 Output       → final translation + verification report + glossary diff
```

L3 is the only layer that scales rounds with material difficulty;
L1/L2/L4/L5 each run once.

## 3. Four-Tier Glossary Fallthrough

Terminology resolution cascades through four tiers; the first hit wins:

```
L1  project glossary   →  <your-repo>/docs/i18n/glossary-{a}--{b}.md
L2  bundled glossary   →  this plugin's vendor-attributed entries
L3  web search         →  runtime fetch (flagged in glossary diff)
L4  LLM fallback       →  model knowledge (flagged for human review)
```

Cross-pair pivot through `en-US` is attempted at L1+L2 before falling to L3.
See `glossary-format-spec.md` for project-level override authoring.

## 4. Five Verification Gates

L4 runs five gates with distinct severities:

| Gate | Name              | Severity                                 |
|------|-------------------|------------------------------------------|
| M1   | Placeholder       | HARD — ICU/printf/{{var}} parity.        |
| M2   | Glossary          | HARD — terminology adherence to L1/L2.   |
| S1   | Back-translation  | SHOULD (MUST in transcreation).          |
| S2   | Register          | SHOULD — formality / tone consistency.   |
| I1   | Untranslatability | INFO — flags culturally-bound items.     |

S1 dispatches a **BACK-TRANSLATOR** subagent to preserve blindness — the
back-translator never sees the source, only the target.

## 5. SSOT-and-Functional-Copy Pattern

To keep skills self-contained while avoiding drift:

```
scripts/canonical/<rule>.md              ← single source of truth (SoT)
skills/<skill>/<subfolder>/<rule>.md     ← functional copy bundled per skill
.github/workflows/verify-drift.yml       ← CI gate; fails on copy ≠ canonical
```

Same-PR rule: any edit to a canonical file MUST also update every functional
copy in the same commit. CI rejects drifted copies.

## 6. Roles, Not Models

Skill prompts describe **roles** (WRITER, CRITIC, REVISER, BACK-TRANSLATOR,
JUDGE) — not specific models. Runtime decides which model fills each role.
This keeps the toolkit portable across Claude Code, Gemini, and Codex without
prompt rewrites.

## 7. Reference

- Full design spec:
  `../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`
- Glossary authoring: `glossary-format-spec.md`
- Bundled-source attributions: `../NOTICES.md`
