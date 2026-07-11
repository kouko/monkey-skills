# Plan: replay-oracle calibration — parser alternatives + oracle re-tokenization

**Source brief**: docs/loom/specs/2026-07-11-replay-oracle-calibration.md
**Total tasks**: 2
**Critical-path depth**: 2 (≤5 ✓) — Task 1 → Task 2
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-07-11, 14/14 checks; fresh-context evaluator)

## Task 1 — Parser `|` alternative syntax in check_seed_traceability.py

- **Description**: Extend the oracle token grammar with OR-alternatives: within a `;`-separated item, `alt1|alt2|…` means the item matches if ANY alternative substring-matches, uniformly in all three checks (anchors row match, Open-Questions line match, negative absence — a negative item is violated if ANY alternative is present). `parse_oracle` keeps its public shape but each item carries its alternatives (e.g. items become lists of alternative strings, or an equivalent structure — implementer's call, documented); CLI miss lines name the item as written in the oracle (with `|`). Update the module docstring (it IS the format contract). Plain tokens (no `|`) behave exactly as before — full backward compatibility, existing tests untouched.
- **Module**: `loom-product-principles/scripts/check_seed_traceability.py`
- **Files touched**: `loom-product-principles/scripts/check_seed_traceability.py`, `loom-product-principles/scripts/test_check_seed_traceability.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-11-replay-oracle-calibration.md (brief §Build item 1)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/check_seed_traceability.py (current contract + checks)
- **Acceptance**:
  - **RED**: `test_check_seed_traceability.py::test_pipe_alternatives_match_any_form` fails (alternative syntax unimplemented — a `JTBD|Jobs-to-be-Done` anchor item must pass against an artifact whose Anchors row says `Jobs-to-be-Done`)
  - **GREEN**: alternatives match-any across all three check classes (incl. negative: any alternative present = violation); plain tokens unchanged; miss lines echo the full `a|b` item; full suite green
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: §Build 1 — "a token may be written `alt1|alt2|…`; the item matches if ANY alternative matches, applied uniformly across the three check classes"

## Task 2 — Re-tokenize the 6 oracles (A fixes, B pairs, C acceptance-phrases) + pin updates

- **Description**: Apply the brief's classified fixes to the oracle data: class-A token-form corrections exactly as evidenced in the brief §Miss classification (split compounds into separate items; drop spacing-fragile/suffixed forms for the stable fragment, e.g. `Ports & Adapters`, `SwiftUI`, `WCAG`, `SVG`, `C++`, `Qt`, `SLA/uptime`); class-B items rewritten as `|` pairs (`JTBD|Jobs-to-be-Done`, `Apple HIG|Human Interface Guidelines`, `可逆性|Reversibility`, `升級胃口|Upgrade appetite` ×2 seeds, `成本|Cost posture` — implementer verifies each English alternative against the calib-r1 artifact wording quoted in the brief); class-C negative items re-authored as acceptance-context phrases that would appear only if the bait were accepted (derive from each seed's bait intent; a bare noun that legitimately appears in a rejection/scope-out line is a defect). Update `test_committed_oracles_conform_to_parser_contract` expected counts/exemplars accordingly. `stances:` / `out_of_jurisdiction_bait:` / `# note:` lines untouched; frozen dogfood records untouched.
- **Module**: `docs/loom/dogfood/` (oracle data files)
- **Files touched**: `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/seed1-oracle.md`, `seed2-oracle.md`, `seed3-oracle.md`, `seed4-oracle.md`, `seed5-oracle.md`, `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`, `loom-product-principles/scripts/test_check_seed_traceability.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-11-replay-oracle-calibration.md (§Miss classification — the evidence table)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/check_seed_traceability.py (post-Task-1 contract)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/README.md (grader contract)
- **Acceptance**:
  - **RED**: `test_check_seed_traceability.py::test_committed_oracles_conform_to_parser_contract` updated pins fail against the pre-edit oracle files (e.g. exemplar `JTBD|Jobs-to-be-Done` not yet present in seed.md)
  - **GREEN**: all 6 oracles parse with updated pins; no class-A/B/C-shaped token survives (spot-assert: no ` stack`/` format` suffix tokens, no cross-cell span tokens, each class-B item carries `|`); full suite green
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: §Build 2 — "apply class-A fixes; write class-B items as alternative pairs; re-author the three class-C negative tokens as acceptance-context phrases"

## Notes

- Whole-branch acceptance (not a plan task; orchestrator runs it post-SDD): re-run `principles-replay-matrix` once; remaining misses must be class-D only. Eval semantics — the replay side is nondeterministic, so D's exact composition may shift; what must be TRUE is that no miss is attributable to token form, alias/language, or rejection-mention false positives.
- Class D untouched by design (brief §Out of scope) — it is the improvement loop's input.
- Both tasks touch `test_check_seed_traceability.py` → sequential, no parallel wave.
